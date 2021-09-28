import pymesh
import math
import os
import numpy as np

def get_fast_bbox(mesh):

    bbox = [[100000,100000,100000], [0,0,0]]
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

def get_fast_bbox_2d(points):

    bbox = [[100000,100000], [0,0]]
    for vertex in points:

        if vertex[0] > bbox[1][0]:
            bbox[1][0] = vertex[0]
        if vertex[0] < bbox[0][0]:
            bbox[0][0] = vertex[0]

        if vertex[1] > bbox[1][1]:
            bbox[1][1] = vertex[1]
        if vertex[1] < bbox[0][1]:
            bbox[0][1] = vertex[1]

    return bbox


def center_around_origin(mesh):

    bbox = get_fast_bbox(mesh)
    width_x = bbox[1][0] - bbox[0][0]
    width_y = bbox[1][1] - bbox[0][1]
    width_z = bbox[1][2] - bbox[0][2]
    trans_x = -((width_x / 2.0) + bbox[0][0])
    trans_y = -((width_y / 2.0) + bbox[0][1])
    trans_z = -((width_z / 2.0) + bbox[0][2])

    return translate(mesh, (trans_y, trans_x, trans_z))


def rotate(mesh, offset, rotation_axis, rotation_angle):
    """
       mesh is the mesh to be rotated
       offset is a three axis vector
       rotation_matrix is a 3d rotation matrix
       angle is the rotation angle in degress

       returns rotated mesh
    """
    offset = np.array(offset);
    axis = np.array((rotation_axis[1], rotation_axis[0], rotation_axis[2]));
    angle = math.radians(rotation_angle);
    rot = pymesh.Quaternion.fromAxisAngle(axis, angle);
    rot = rot.to_matrix();

    vertices = mesh.vertices;
    bbox = mesh.bbox;
    centroid = 0.5 * (bbox[0] + bbox[1]);
    vertices = np.dot(rot, (vertices - centroid).T).T + centroid + offset;

    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


def clear_color(file):
    mesh = pymesh.meshio.load_mesh(file);
    new_mesh = pymesh.form_mesh(mesh.vertices, mesh.faces)
    pymesh.meshio.save_mesh(file, new_mesh);


def scale(mesh, scale_factor):
    """
       mesh is the mesh to be rotated
       scale_factor is how much to scale the model by.

       returns rotated mesh
    """

    vertices = []
    for vertex in mesh.vertices:
        vertices.append((vertex[0] * scale_factor[0], vertex[1] * scale_factor[1], vertex[2] * scale_factor[2]))

    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


def translate(mesh, translation_vector):
    """
       mesh is the mesh to be rotated
       translation_vector the vectory by which the mesh should be translated by

       returns rotated mesh
    """

    vertices = []
    for vertex in mesh.vertices:
        vertices.append((vertex[0] + translation_vector[1], vertex[1] + translation_vector[0], vertex[2] + translation_vector[2]))

    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


def flip_mesh(mesh):
    new_faces = []
    for face in mesh.faces:
        new_face = list(face)
        new_face.reverse()
        new_faces.append(new_face)

    return pymesh.form_mesh(mesh.vertices, np.array(new_faces))


def make_3d(mesh, offset):
    vertices = [ (vertex[0], vertex[1], offset) for vertex in mesh.vertices]
    return pymesh.form_mesh(vertices, mesh.faces, mesh.voxels)


file_index = 0
def save_mesh(filename, mesh):
    global file_index

    filename = os.path.join("debug", "%02d-%s.stl" % (file_index, filename))
    file_index += 1
    pymesh.meshio.save_mesh(filename, mesh)
    print("wrote %s" % filename)


def mesh_from_xy_points(faces_xy, extrude_mm = 0.0):
    index = {}
    inverse = {}
    count = 0
    for face in faces_xy:
        for point in face:
            if tuple(point) not in index:
                index[tuple(point)] = count
                inverse[count] = point
                count += 1

    vertices = []
    for i in index.values():
        vertices.append(inverse[i])

    faces = []
    for face in faces_xy:
        new_face = []
        for point in face:
            new_face.append(index[tuple(point)])
        faces.append(new_face)

    if len(faces_xy[0][0]) == 2:
        return make_3d(pymesh.form_mesh(np.array(vertices), np.array(faces)), extrude_mm)
    else:
        return pymesh.form_mesh(np.array(vertices), np.array(faces))
