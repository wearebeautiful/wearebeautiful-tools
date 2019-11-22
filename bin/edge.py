import math
import sys
import numpy as np
import pymesh
from random import random
from scipy.spatial import Delaunay
from transform import save_mesh, mesh_from_xy_points, flip_mesh, get_fast_bbox_2d
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from pyoctree import pyoctree as ot
from intersect import closed_segment_intersect

TOLERANCE = .00001

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

    poly = Polygon(edges)
    edges.append((0,0))

    bbox = get_fast_bbox_2d(edges)
    width = bbox[1][0] - bbox[0][0]
    height = bbox[1][1] - bbox[0][1]

    for i in range(300):
        while True:
            x = (random() * width) - (width/2.0)
            y = (random() * height) - (height/2.0)
            if not Point(x, y).within(poly):
                continue
            edges.append((x,y))
            break


    edges = np.array(edges)
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


def walk_edges(mesh, edges_surface, floor, edges_floor, opts, extrude_mm):

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
#                    print("Too many new points have been inserted in the floor. (%d)" % offset)
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
#                        print("      not found")
                        break

                if not found and offset > 10:
                    print("      Too many points have been deleted in the floor. (%d)" % offset)
                    return None

#                if found:
#                    print("      Found point in surface %d points later, after matching %d points" % (offset, matched))
                
        if floor_index >= len(edges_floor):
            floor_index = 0


    wall_faces = []
    last_s_pt = ()
    last_f_pt = ()

    for i in range(len(point_pairs)):
        pair0 = point_pairs[i]
        pair1 = point_pairs[(i + 1) % len(point_pairs)]

        if len(pair0[0]) == 3 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 3:
             pass
#            wall_faces.append((pair0[0], pair1[0], pair0[1]))
#            wall_faces.append((pair0[1], pair1[0], pair1[1]))
        elif len(pair0[0]) == 3 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 0:
            wall_faces.append((pair0[0], pair1[0], pair0[1]))
        elif len(pair0[0]) == 3 and len(pair0[1]) == 3 and len(pair1[0]) == 0 and len(pair1[1]) == 3:
            # this clause causes errors to be added!
            print("case %d %d %d %d" % (len(pair0[0]), len(pair0[1]), len(pair1[0]), len(pair1[1])))
            wall_faces.append((pair0[0], pair1[1], pair0[1]))
#        elif len(pair0[0]) == 3 and len(pair0[1]) == 0 and len(pair1[0]) == 3 and len(pair1[1]) == 3:
#            print("case %d %d %d %d" % (len(pair0[0]), len(pair0[1]), len(pair1[0]), len(pair1[1])))
#            wall_faces.append((pair0[0], pair1[0], pair1[1]))
#        elif len(pair0[0]) == 0 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 3:
#            # this creates real shit 
#            wall_faces.append((pair1[0], pair1[1], pair0[1]))
#            print("case %d %d %d %d" % (len(pair0[0]), len(pair0[1]), len(pair1[0]), len(pair1[1])))
#        elif len(pair0[0]) == 0 and len(pair0[1]) == 3 and len(pair1[0]) == 0 and len(pair1[1]) == 3:
#            wall_faces.append(((last_s_pt[0], last_s_pt[1], last_s_pt[2]), pair1[1], pair0[1]))
#        elif len(pair0[0]) == 0 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 0:
#            wall_faces.append(((last_s_pt[0], last_s_pt[1], last_s_pt[2]), pair1[0], pair0[1]))
#        elif len(pair0[0]) == 3 and len(pair0[1]) == 0 and len(pair1[0]) == 3 and len(pair1[1]) == 0:
#            wall_faces.append(((last_f_pt[0], last_f_pt[1], last_f_pt[2]), pair0[0], pair1[0]))
#        else:
#            print("case %d %d %d %d" % (len(pair0[0]), len(pair0[1]), len(pair1[0]), len(pair1[1])))
#            assert(0)

        if len(pair0[0]) == 3:
            last_s_pt = pair0[0]
        if len(pair0[1]) == 3:
            last_f_pt = pair0[1]

    walls = mesh_from_xy_points(wall_faces)
    if opts['flip_walls']:
        walls = flip_mesh(walls)

    if opts['debug']:
        print(edges_surface[0])
        dot = pymesh.generate_icosphere(1, (mesh.vertices[edges_surface[0][0]][0],  
                                            mesh.vertices[edges_surface[0][0]][1], 
                                            mesh.vertices[edges_surface[0][0]][2]))
        save_mesh("walls", pymesh.merge_meshes([dot, walls]))

    return walls

#            wall_faces.append((last_s_pt, pair1[1], pair0[1]))
#        elif len(pair0[0]) == 0 and len(pair0[1]) == 3 and len(pair1[0]) == 3 and len(pair1[1]) == 0:
#            wall_faces.append((last_s_pt[0], pair1[0], pair0[1]))
#        elif len(pair0[0]) == 3 and len(pair0[1]) == 0 and len(pair1[0]) == 3 and len(pair1[1]) == 0:
#            wall_faces.append((last_f_pt, pair0[0], pair1[0]))

def check_for_self_intersections(opts, mesh, points, points_int):

    si_points = set()

    count = 0
    for i in range(len(points)):
        for j in range(len(points)):
            if i == j:
                continue
            pt0 = points[i]
            pt1 = points[(i + 1) % len(points)]
            pt2 = points[j]
            pt3 = points[(j + 1) % len(points)]
            if closed_segment_intersect(pt0, pt1, pt2, pt3):
                if i < j:
                    si_points.add("%d-%d" % (i, j))
                else:
                    si_points.add("%d-%d" % (j, i))

    si_points = list(si_points)
    dots = []
    for pt in si_points:
        p0, p1 = pt.split('-')
        p_xyz = mesh.vertices[int(p0)]
        dots.append(pymesh.generate_icosphere(1, p_xyz))

    if opts['debug']:
        dots.append(mesh)
        mesh = pymesh.merge_meshes(dots)
        save_mesh("si", mesh);

    return len(si_points)


def create_walls_and_floor(mesh, opts, extrude_mm):

    print("Find boundary")
    # Find the edge of the surface
    edges_surface = find_boundary(mesh)

    # from the edges, create a new triangulated mesh
    edges_xy = []
    for edge in edges_surface:
        edges_xy.append((mesh.vertices[edge[0]][0], mesh.vertices[edge[0]][1]))

    print("check for self intersections")
    count = check_for_self_intersections(opts, mesh, edges_xy, edges_surface)
    if count:
        print("Found %d self intersections" % count)

    #tree = ot.PyOctree(np.array(mesh.vertices),np.array(mesh.faces))

    print("triangulate")
    floor = triangulate(edges_xy, 2.0, opts, extrude_mm)
    if opts['floor'] and opts['flip_floor']:
        floor = flip_mesh(floor)

    # Find the edge of the surface
    edges_floor = find_boundary(floor)

    if opts['debug']:
        dot = pymesh.generate_icosphere(1, (floor.vertices[edges_floor[0][0]][0], floor.vertices[edges_floor[0][0]][1], extrude_mm))
        new_floor = pymesh.merge_meshes([dot, floor])
        save_mesh("floor", new_floor);

    print("num points in floor edge %d" % len(edges_floor))
    print("num points in surface edge %d" % len(edges_surface))

    # refactor the following into a function that can be called and if it fails, we reverse
    # the floor points and try again
    walls = walk_edges(mesh, edges_surface, floor, edges_floor, opts, extrude_mm)
    if not walls:
        edges_floor.reverse()
        walls = walk_edges(mesh, edges_surface, floor, edges_floor, opts, extrude_mm)
        if not walls:
            print("Cannot walk edges. fail!")
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

# This may need to be improved -- it picks the last matching point which may not be ideal.
def dedup_intersection_list(ints, p0, p1):

#    print(p0)
#    print(p1)
#    print("before: ")
#    for i in ints:
#        print("  ", i.s,i.p)

    filtered = []
    for int in ints:
        d0 = dist(int.p, p0)
        d1 = dist(int.p, p1)
        if d0 > TOLERANCE or d1 > TOLERANCE:
            filtered.append(int)

    ints = filtered            

#    print("after")
#    for i in ints:
#        print("  ", i.s,i.p)


    dedup = []
    ints = sorted(ints, key=lambda i: i.s)

    for i in range(len(ints)):
        if i == len(ints) - 1 or ints[i+1].s - ints[i].s > TOLERANCE:
            dedup.append(ints[i])


    return dedup            


def simple_extrude(mesh, opts, extrude_mm):

    vertices = []
    for vertex in mesh.vertices:
        vertices.append((vertex[0], vertex[1], vertex[2]))

    num_vertices = len(vertices)
    for vertex in mesh.vertices:
        vertices.append((vertex[0], vertex[1], vertex[2]-extrude_mm))

    print("find boundary")
    edges = find_boundary(mesh)

    # from the edges, create a new triangulated mesh
    edges_xy = []
    for edge in edges:
        edges_xy.append((mesh.vertices[edge[0]][0], mesh.vertices[edge[0]][1]))

    print("check for self intersections")
    count = check_for_self_intersections(opts, mesh, edges_xy, edges)

    faces = []
    for face in mesh.faces:
        faces.append((face[0], face[1], face[2]))
    for face in mesh.faces:
        faces.append((face[0] + num_vertices, face[2] + num_vertices, face[1] + num_vertices))

    print("make octtree")
    tree = ot.PyOctree(np.array(vertices),np.array(faces, dtype=np.int32))

    panels = 0
    for i, edge in enumerate(edges):
        p0t_xyz = list(vertices[edge[0]])
        p0b_xyz = list(vertices[edge[0] + num_vertices])
        ints0 = tree.rayIntersection(np.array([p0t_xyz, p0b_xyz],dtype=np.float32))

        p1t_xyz = list(vertices[edge[1]])
        p1b_xyz = list(vertices[edge[1] + num_vertices])
        ints1 = tree.rayIntersection(np.array([p1t_xyz, p1b_xyz],dtype=np.float32))

        ints0 = dedup_intersection_list(ints0, p0t_xyz, p0b_xyz)
        ints1 = dedup_intersection_list(ints0, p0t_xyz, p0b_xyz)

        if len(ints0):
            for i in ints0:
                print("0: %.4f " % (i.s), i.p)
        if len(ints1):
            for i in ints1:
                print("1: %.4f " % (i.s), i.p)

        if len(ints0) == 0 and len(ints1) == 0:
            if opts['flip_walls']:
                faces.append((edge[0], edge[0] + num_vertices, edge[1]))
                faces.append((edge[1], edge[0] + num_vertices, edge[1] + num_vertices))
            else:
                faces.append((edge[0], edge[1], edge[0] + num_vertices))
                faces.append((edge[1], edge[1] + num_vertices, edge[0] + num_vertices))
            panels += 1

    print("created %d panels" % panels)

    solid = pymesh.form_mesh(np.array(vertices), np.array(faces))

    return solid
