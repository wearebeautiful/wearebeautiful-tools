import math
import sys
import numpy as np
import pymesh
from scipy.spatial import Delaunay
from transform import save_mesh, mesh_from_xy_points, flip_mesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point


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


def triangulate(edges, alpha, opts, extrude_mm, only_outer=True):

    edges = np.array(edges)
    poly = Polygon(edges)
    assert edges.shape[0] > 3, "Need at least four points"

    tri = Delaunay(edges)

    vertices = []
    vertices_xy = []
    for ia, ib, ic in tri.vertices:
        pa = edges[ia]
        pb = edges[ib]
        pc = edges[ic]

        centroid_x = (pa[0] + pb[0] + pc[0]) / 3.0
        centroid_y = (pa[1] + pb[1] + pc[1]) / 3.0
        if Point(centroid_x, centroid_y).within(poly):
            vertices.append((ia, ib, ic))
            vertices_xy.append((pa, pb, pc))

    if opts['debug']:
        plt.triplot(edges[:,0], edges[:,1], vertices, linewidth=0.2)
        plt.savefig('debug/triangulation.png', dpi=1200)
        plt.clf()

    mesh = mesh_from_xy_points(vertices_xy, extrude_mm)

    v = np.array((mesh.vertices[mesh.faces[0][0]], mesh.vertices[mesh.faces[0][1]], mesh.vertices[mesh.faces[0][2]]))
    normal = np.cross(v[1]-v[0], v[2]-v[0])
    if normal[2] > 0.0:
        mesh = flip_mesh(mesh)

    return mesh


def find_border(mesh, opts, extrude_mm):

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

    edges = stitch_boundaries(edges)[0]

    edges_xy = []
    for edge in edges:
        edges_xy.append((mesh.vertices[edge[0]][0], mesh.vertices[edge[0]][1]))

    floor = triangulate(edges_xy, 2.0, opts, extrude_mm)

    if opts['debug']:
        points = list(points)
        points_xy = [ (mesh.vertices[p][0], mesh.vertices[p][1]) for p in points ]
        x_points = [ x for x, y in points_xy ]
        y_points = [ y for x, y in points_xy ]
        plt.scatter(x_points, y_points, s = .1)
        plt.savefig('debug/points-edge.png', dpi=600)

        x_points = [ mesh.vertices[p0][0] for p0, p1 in edges ]
        y_points = [ mesh.vertices[p0][1] for p0, p1 in edges ]
        plt.plot(x_points, y_points, linewidth=1)
        plt.savefig('debug/edge.png', dpi=600)
        plt.clf()

    return edges, points, floor
