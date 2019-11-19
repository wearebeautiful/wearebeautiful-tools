import math
import sys
import numpy as np
import pymesh
from scipy.spatial import Delaunay
from transform import save_mesh, mesh_from_xy_points, flip_mesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from pyoctree import pyoctree as ot


def find_edges_with(i, edge_set):
    i_first = [j for (x,j) in edge_set if x==i]
    i_second = [j for (j,x) in edge_set if x==i]
    return i_first,i_second


def stitch_boundaries(edges):
    edge_set = edges.copy()
    boundary_lst = []
    while len(edge_set) > 0:
        boundary = []
        edge0 = edge_set.pop()
        boundary.append(edge0)
        last_edge = edge0
        while len(edge_set) > 0:
            i,j = last_edge
            j_first, j_second = find_edges_with(j, edge_set)
            if j_first:
                edge_set.remove((j, j_first[0]))
                edge_with_j = (j, j_first[0])
                boundary.append(edge_with_j)
                last_edge = edge_with_j
            elif j_second:
                edge_set.remove((j_second[0], j))
                edge_with_j = (j, j_second[0])  # flip edge rep
                boundary.append(edge_with_j)
                last_edge = edge_with_j

            if edge0[0] == last_edge[1]:
                break

        boundary_lst.append(boundary)

    return boundary_lst

TOLERANCE = .001

def find_missing_points_from_mesh(edges, mesh):
    missing = []
    for i, pt in enumerate(edges):
        found = False
        for v in mesh.vertices:
            diff_x = math.fabs(pt[0] - v[0]) 
            diff_y = math.fabs(pt[1] - v[1]) 

            if diff_x < TOLERANCE and diff_y < TOLERANCE:
                found = True
                break

        if not found:
            missing.append(pt)
            print("point %d" % i, pt, "not in index")

    return missing


def triangulate(edges, alpha, opts, extrude_mm, only_outer=True):

    edges = np.array(edges)
    poly = Polygon(edges)
    assert edges.shape[0] > 3, "Need at least four points"

    tri = Delaunay(edges)

    faces = []
    faces_xy = []
    for ia, ib, ic in tri.vertices:
        pa = edges[ia]
        pb = edges[ib]
        pc = edges[ic]

        centroid_x = (pa[0] + pb[0] + pc[0]) / 3.0
        centroid_y = (pa[1] + pb[1] + pc[1]) / 3.0
        if Point(centroid_x, centroid_y).within(poly):
            faces.append((ia, ib, ic))
            faces_xy.append((pa, pb, pc))

    if opts['debug']:
        plt.triplot(edges[:,0], edges[:,1], faces, linewidth=0.2)
        plt.savefig('debug/triangulation.png', dpi=1200)
        plt.clf()

    mesh = mesh_from_xy_points(faces_xy, extrude_mm)

    index = {}
    for i, pt in enumerate(mesh.vertices):
        index[(pt[0], pt[1])]  = i

    v = np.array((mesh.vertices[mesh.faces[0][0]], mesh.vertices[mesh.faces[0][1]], mesh.vertices[mesh.faces[0][2]]))
    normal = np.cross(v[1]-v[0], v[2]-v[0])
    if normal[2] > 0.0:
        mesh = flip_mesh(mesh)

    return mesh


def find_boundary(mesh):

    def inc(index, key):
        try:
            index[key] += 1
        except KeyError:
            index[key] = 1

    refcounts = {}
    for face in mesh.faces:
        if face[0] < face[1]:
            inc(refcounts, "%d-%d" % (face[0], face[1]))
        else:
            inc(refcounts, "%d-%d" % (face[1], face[0]))
        if face[0] < face[2]:
            inc(refcounts, "%d-%d" % (face[0], face[2]))
        else:
            inc(refcounts, "%d-%d" % (face[2], face[0]))
        if face[1] < face[2]:
            inc(refcounts, "%d-%d" % (face[1], face[2]))
        else:
            inc(refcounts, "%d-%d" % (face[2], face[1]))

    edges = set()
    points = set()
    for edge in refcounts:
        if refcounts[edge] == 1:
            p0, p1 = edge.split("-")
            edges.add((int(p0), int(p1)))
            points.add(int(p0))
            points.add(int(p1))
    
    if len(edges) == 0:
        print("Could not find edge of the surface. Is this a solid??")
        sys.exit(-1)

    return stitch_boundaries(edges)[0]

def dist(pt0, pt1):
    return math.sqrt(math.pow(pt1[0] - pt0[0], 2) + math.pow(pt1[1] - pt0[1], 2))


def walk_edges(mesh, edges_surface, floor, edges_floor):

    # find the point on the floor edge that matches to the first point in the surface edge
    floor_index = -1
    pt_s_xyz = mesh.vertices[edges_surface[0][0]]
    for i, edge in enumerate(edges_floor):
        pt_f_xyz = floor.vertices[edge[0]]
        if pt_f_xyz[0] == pt_s_xyz[0] and pt_f_xyz[1] == pt_s_xyz[1]:
            floor_index = i
            break

    floor_start = floor_index

    matched = 0
    point_pairs = []

    # Walk the two surfaces point by point, checking for new or missing points in the 
    # floor edge. If points match, create two triangles for the wall edge. If they
    # Do not create only one triangle for the wall.
    for i, edge in enumerate(edges_surface):
        floor_index %= len(floor.vertices)
        pt_s_xyz = mesh.vertices[edge[0]]
        pt_f_xyz = floor.vertices[edges_floor[floor_index][0]] 

        # Is the corresponding point there as we expect it?
        if pt_s_xyz[0] == pt_f_xyz[0] and pt_s_xyz[1] == pt_f_xyz[1]:
            floor_index += 1
            matched += 1

            point_pairs.append(((pt_s_xyz[0], pt_s_xyz[1], pt_s_xyz[2]), (pt_f_xyz[0], pt_f_xyz[1], pt_f_xyz[2])))
        else:
#            print("%s scan ahead on floor" % floor_index)
            # The point is not there. Either a new point as been added or the point we expected is gone.
            # scan ahead on the floor edge, can we find the point there?
            offset = 1
            found = False
            while True:
                pt_xyz = floor.vertices[edges_floor[(floor_index + offset) % len(edges_floor)][0]]
                if pt_s_xyz[0] == pt_xyz[0] and pt_s_xyz[1] == pt_xyz[1]:
#                    print("   found matching floor point %s points later." % offset)
                    floor_index += offset
                    found = True
                    matched += 1
                    point_pairs.append(((pt_s_xyz[0], pt_s_xyz[1], pt_s_xyz[2]), (pt_xyz[0], pt_xyz[1], pt_xyz[2])))
                    break

                point_pairs.append(((), (pt_xyz[0], pt_xyz[1], pt_xyz[2])))
                offset += 1
                if (floor_index + offset) % len(edges_floor) == floor_start:
#                    print("   not found")
                    break


            if found:
#                print("   Found point in floor %d points later, after matching %d points" % (offset, matched))
                if offset > 25:
                    print("Too many new points have been inserted in the floor. (%d)" % offset)
                    return None

            if not found:
#                print("   %s: scan ahead on surface" % i)
                # Scan ahead in the surface points and see if the point is there
                offset = 1
                found = False
                surface_index = i
                surface_start = surface_index
                while True:
                    pt_xyz = mesh.vertices[edges_surface[(surface_index + offset) % len(edges_surface)][0]]
                    if pt_f_xyz[0] == pt_xyz[0] and pt_f_xyz[1] == pt_xyz[1]:
#                        print("      found matching surface point %s points later." % offset)
                        surface_index += offset
                        matched += 1
                        found = True
                        point_pairs.append(((pt_xyz[0], pt_xyz[1], pt_xyz[2]), (pt_f_xyz[0], pt_f_xyz[1], pt_f_xyz[2])))
                        break

                    point_pairs.append(((pt_xyz[0], pt_xyz[1], pt_xyz[2]), ()))
                    offset += 1
                    if (surface_index + offset) % len(edges_surface) == surface_start:
                        print("      not found")
                        break

                if not found and offset > 10:
                    print("      Too many points have been deleted in the floor. (%d)" % offset)
                    return None

#                if found:
#                    print("      Found point in surface %d points later, after matching %d points" % (offset, matched))
                
        if floor_index >= len(edges_floor):
            floor_index = 0


    # TODO: Handle case where single triangles need to be added
    wall_faces = []
    for i in range(len(point_pairs)):
        pair0 = point_pairs[i]
        pair1 = point_pairs[(i + 1) % len(point_pairs)]

        if len(pair0[0]) == 3 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 3:
            wall_faces.append((pair0[0], pair1[0], pair0[1]))
            wall_faces.append((pair0[1], pair1[0], pair1[1]))
            continue

        if len(pair0[0]) == 3 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 0:
            wall_faces.append((pair0[0], pair1[0], pair0[1]))
            continue

        if len(pair0[0]) == 3 and len(pair0[1]) == 3 and len(pair1[0]) == 0 and len(pair1[1]) == 3:
            wall_faces.append((pair0[0], pair1[1], pair0[1]))
            continue

        if len(pair0[0]) == 3 and len(pair0[1]) == 0 and len(pair1[0]) == 3 and len(pair1[1]) == 3:
            wall_faces.append((pair0[0], pair1[0], pair1[1]))
            continue

        if len(pair0[0]) == 0 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 3:
            wall_faces.append((pair1[0], pair1[1], pair0[1]))
            continue

        print("case %d %d %d %d" % (len(pair0[0]), len(pair0[1]), len(pair1[0]), len(pair1[1])))
        assert(0)

    return mesh_from_xy_points(wall_faces)


def create_walls_and_floor(mesh, opts, extrude_mm):

    # Find the edge of the surface
    edges_surface = find_boundary(mesh)

    # from the edges, create a new triangulated mesh
    edges_xy = []
    for edge in edges_surface:
        edges_xy.append((mesh.vertices[edge[0]][0], mesh.vertices[edge[0]][1]))

    print("create octree")
    #tree = ot.PyOctree(np.array(mesh.vertices),np.array(mesh.faces))

    print("triangulate")
    floor = triangulate(edges_xy, 2.0, opts, extrude_mm)

    # Find the edge of the surface
    edges_floor = find_boundary(floor)

    print("num points in floor edge %d" % len(edges_floor))
    print("num points in surface edge %d" % len(edges_surface))

    # refactor the following into a function that can be called and if it fails, we reverse
    # the floor points and try again
    walls = walk_edges(mesh, edges_surface, floor, edges_floor)
    if not walls:
        print("---------------------------------------------")
        print("Could not match edges, reversing floor points")
        edges_floor.reverse()
        walls = walk_edges(mesh, edges_surface, floor, edges_floor)
        if not walls:
            print("Could not zip up floor and surface edges.")
            sys.exit(-1)

    print("Walked edges successfully!")

    if 0: #opts['debug']:
        points = list(points)
        points_xy = [ (mesh.vertices[p][0], mesh.vertices[p][1]) for p in points ]
        x_points = [ x for x, y in points_xy ]
        y_points = [ y for x, y in points_xy ]
        plt.scatter(x_points, y_points, s = .1)
        plt.savefig('debug/points-edge.png', dpi=600)

        x_points = [ mesh.vertices[p0][0] for p0, p1 in edges ]
        y_points = [ mesh.vertices[p0][1] for p0, p1 in edges ]
        plt.plot(x_points, y_points, linewidth=1)

        x_missing = [ x for x, y in missing ]
        y_missing = [ y for x, y in missing ]
        plt.scatter(x_missing, y_missing, s = 1.0, c="#FF0000")

        plt.savefig('debug/edge.png', dpi=600)
        plt.clf()

    return walls, floor


def parked(mesh):
    # create the walls
    print("Size of Octree               = %.3fmm" % tree.root.size)
    print("Number of Octnodes in Octree = %d" % tree.getNumberOfNodes())
    print("Number of polys in Octree    = %d" % tree.numPolys)

    faces = []
    hist = {}
    dots = []
    for p0, p1 in edges:
        p2 = cross_index[p1] + vertex_offset
        p3 = cross_index[p0] + vertex_offset

        p0_xyz = list(mesh.vertices[p0])
        p1_xyz = list(mesh.vertices[p0])
        p1_xyz[2] = 0.0

        ints = set()
        for i in tree.rayIntersection(np.array([p0_xyz,p1_xyz],dtype=np.float32)):
            ints.add((tuple(i.p), i.s))

        ints = list(ints)
        if len(ints) > 100:
            continue
            for i in ints:
                dots.append(pymesh.generate_icosphere(.01, i[0]))

        # walls
        if opts['walls']:
            faces.append((p0, p1, p2))
            faces.append((p0, p2, p3))

    vertices = list(mesh.vertices)

    edges, edge_points, floor = find_border(mesh, opts, extrude_mm)

    cross_index = {}
    vertex_offset = len(vertices)
    for i, vertex in enumerate(edges):
        cross_index[vertex[0]] = i

