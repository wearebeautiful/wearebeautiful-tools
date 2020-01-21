import math
import sys
from random import random

import numpy as np
import pymesh
from scipy.spatial import Delaunay
from wearebeautiful.utils import save_mesh, mesh_from_xy_points, flip_mesh, get_fast_bbox_2d
from wearebeautiful.intersect import closed_segment_intersect
import matplotlib.pyplot as plt


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

#    print("check for self intersections")
#    count = check_for_self_intersections(opts, mesh, edges_xy, edges)

    faces = []
    for face in mesh.faces:
        faces.append((face[0], face[1], face[2]))
    for face in mesh.faces:
        faces.append((face[0] + num_vertices, face[2] + num_vertices, face[1] + num_vertices))

    panels = 0
    for i, edge in enumerate(edges):
#        p0t_xyz = list(vertices[edge[0]])
#        p0b_xyz = list(vertices[edge[0] + num_vertices])
#        ints0 = tree.rayIntersection(np.array([p0t_xyz, p0b_xyz],dtype=np.float32))

#        p1t_xyz = list(vertices[edge[1]])
#        p1b_xyz = list(vertices[edge[1] + num_vertices])
#        ints1 = tree.rayIntersection(np.array([p1t_xyz, p1b_xyz],dtype=np.float32))

#        ints0 = dedup_intersection_list(ints0, p0t_xyz, p0b_xyz)
#        ints1 = dedup_intersection_list(ints0, p0t_xyz, p0b_xyz)

#        if len(ints0):
#            for i in ints0:
#                print("0: %.4f " % (i.s), i.p)
#        if len(ints1):
#            for i in ints1:
#                print("1: %.4f " % (i.s), i.p)

        if True: #len(ints0) == 0 and len(ints1) == 0:
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
