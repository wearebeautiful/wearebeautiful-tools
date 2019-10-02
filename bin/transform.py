import pymesh
import numpy as np
import math

def get_fast_bbox(mesh):

    bbox= [[100000,100000,10000], [0,0, 0]]
    for vertex in mesh.vertices:

        if vertex[0] > bbox[1][0]:
            bbox[1][0] = vertex[0]
        if vertex[0] < bbox[0][0]:
            bbox[0][0] = vertex[0]

        if vertex[1] > bbox[1][1]:
            bbox[1][1] = vertex[1]
        if vertex[1] < bbox[0][1]:
            bbox[0][1] = vertex[1]

        if vertex[2] > bbox[1][2]:
            bbox[1][2] = vertex[2]
        if vertex[2] < bbox[0][2]:
            bbox[0][2] = vertex[2]

    return bbox


def rotate(mesh, offset, rotation_axis, rotation_angle):
    """
       mesh is the mesh to be rotated
       offset is a three axis vector
       rotation_matrix is a 3d rotation matrix
       angle is the rotation angle in degress

       returns rotated mesh
    """
    offset = np.array(offset);
    axis = np.array(rotation_axis);
    angle = math.radians(rotation_angle);
    rot = pymesh.Quaternion.fromAxisAngle(axis, angle);
    rot = rot.to_matrix();

    vertices = mesh.vertices;
    bbox = mesh.bbox;
    centroid = 0.5 * (bbox[0] + bbox[1]);
    vertices = np.dot(rot, (vertices - centroid).T).T + centroid + offset;

    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


def scale(mesh, scale_factor):
    """
       mesh is the mesh to be rotated
       scale_factor is how much to scale the model by.

       returns rotated mesh
    """

    vertices = []
    for vertex in mesh.vertices:
        vertices.append((vertex[0] * scale_factor, vertex[1] * scale_factor, vertex[2] * scale_factor))

    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


def translate(mesh, translation_vector):
    """
       mesh is the mesh to be rotated
       translation_vector the vectory by which the mesh should be translated by

       returns rotated mesh
    """

    vertices = []
    for vertex in mesh.vertices:
        vertices.append((vertex[0] + translation_vector[0], vertex[1] + translation_vector[1], vertex[2] + translation_vector[2]))

    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


def invert(mesh):
    """
       mesh is the mesh to be rotated
       translation_vector the vectory by which the mesh should be translated by

       returns rotated mesh
    """

    bbox = get_fast_bbox(mesh)
    bbox = pymesh.generate_box_mesh(bbox[0], bbox[1])
    return pymesh.boolean(mesh, bbox, operation="difference", engine="igl")
