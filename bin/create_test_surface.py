import sys
import os
import math
import pymesh
import numpy as np

def create_surface():

    center = (0,0,0)
    steps = 128 

    faces = []
    vertices = [center]
    for step in range(steps + 1):
        theta0 = math.tau * step / steps
        theta1 = math.tau * (step + 1) / steps
        z_theta0 = 4 * math.tau * step / steps
        z_theta1 = 4 * math.tau * (step + 1) / steps

        x0 = math.cos(theta0)
        y0 = math.sin(theta0)
        z0 = math.sin(z_theta0) * .33

        x1 = math.cos(theta1)
        y1 = math.sin(theta1)
        z1 = math.sin(z_theta1) * .33

        vertices.append((x0,y0,z0))

        if step + 1 == steps:
            next = 0
        else:
            next = step + 1
        faces.append((next + 1, 0, step + 1))

    mesh = pymesh.form_mesh(np.array(vertices), np.array(faces))
    pymesh.meshio.save_mesh("test_surface.stl", mesh)

def create_floor():

    center = (0,0,0)
    steps = 20 

    faces = []
    vertices = [center]
    for step in range(steps + 1):
        theta0 = math.tau * step / steps
        theta1 = math.tau * (step + 1) / steps

        x0 = math.cos(theta0)
        y0 = math.sin(theta0)
        z0 = 0

        x1 = math.cos(theta1)
        y1 = math.sin(theta1)
        z1 = 0

        vertices.append((x0,y0,z0))

        if step + 1 == steps:
            next = 0
        else:
            next = step + 1
        faces.append((next + 1, 0, step + 1))

    mesh = pymesh.form_mesh(np.array(vertices), np.array(faces))
    pymesh.meshio.save_mesh("test_floor.stl", mesh)

create_surface()
create_floor()
