import math
import numpy as np
import pymesh
from scipy.spatial import Delaunay


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


def find_boundary(points, alpha, only_outer=True):
    """
    Compute the alpha shape (concave hull) of a set of points.
    :param points: np.array of shape (n,2) points.
    :param alpha: alpha value.
    :param only_outer: boolean value to specify if we keep only the outer border
    or also inner edges.
    :return: set of (i,j) pairs representing edges of the alpha-shape. (i,j) are
    the indices in the points array.
    """
    assert points.shape[0] > 3, "Need at least four points"


    tri = Delaunay(points)
    edges = set()
    # Loop over triangles:
    # ia, ib, ic = indices of corner points of the triangle
    for ia, ib, ic in tri.vertices:
        pa = points[ia]
        pb = points[ib]
        pc = points[ic]
        # Computing radius of triangle circumcircle
        # www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle
        a = np.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b = np.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c = np.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        s = (a + b + c) / 2.0
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        if area:
            circum_r = a * b * c / (4.0 * area)
            if circum_r < alpha:
                add_edge(edges, ia, ib)
                add_edge(edges, ib, ic)
                add_edge(edges, ic, ia)

    return stitch_boundaries(edges)



def find_border(mesh):

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

    edges = stitch_boundaries(edges)[0]
    points = list(points)

    return edges, points

#    border = []
#    for pt in points:
#        border.append(pymesh.generate_icosphere(radius = 1, center = mesh.vertices[pt], refinement_order=1))
#
#    border.append(mesh)
#    return pymesh.merge_meshes(border)
