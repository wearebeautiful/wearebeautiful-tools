import math
import random
import pymesh
import numpy as np
from pyoctree import pyoctree as ot

def intersect_line_triangle(q1,q2,p1,p2,p3):
    def signed_tetra_volume(a,b,c,d):
        return np.sign(np.dot(np.cross(b-a,c-a),d-a)/6.0)

    s1 = signed_tetra_volume(q1,p1,p2,p3)
    s2 = signed_tetra_volume(q2,p1,p2,p3)

    if s1 != s2:
        s3 = signed_tetra_volume(q1,q2,p1,p2)
        s4 = signed_tetra_volume(q1,q2,p2,p3)
        s5 = signed_tetra_volume(q1,q2,p3,p1)
        if s3 == s4 and s4 == s5:
            n = np.cross(p2-p1,p3-p1)
            t = np.dot(p1-q1,n) / np.dot(q2-q1,n)
            return q1 + t * (q2-q1)

    return []


def get_mesh_line_intersections(p0, p1, mesh):

    tree = ot.PyOctree(np.array(mesh.vertices),np.array(mesh.faces))
    print("Size of Octree               = %.3fmm" % tree.root.size)
    print("Number of Octnodes in Octree = %d" % tree.getNumberOfNodes())
    print("Number of polys in Octree    = %d" % tree.numPolys)
    ray_list = np.array([p0,p1],dtype=np.float32)
    for i in tree.rayIntersection(ray_list):
        print(i.p, i.s)


if __name__ == "__main__":
    mesh = pymesh.generate_icosphere(1, (.00001,.00001,.00001), refinement_order=5)
    get_mesh_line_intersections((-10,0,0), (10,0,0), mesh)
