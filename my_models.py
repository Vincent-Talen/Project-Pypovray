from vapory.vapory import *
import numpy as np

# Static Object and Model Library
# Cameras
default_camera = Camera('location', [0, 8, -26], 'look_at', [0, 2, -5])
camera_scene0 = Camera('location', [0, 0, -50], 'look_at', [0, 0, 0])
camera_scene1 = Camera('location', [0, 0, -75], 'look_at', [0, 0, 0])
camera_scene3 = Camera('location', [0, 0, -40], 'look_at', [0, 0, 0])
camera_scene5_plus = Camera('location', [0, 0, -17.5], 'look_at', [0, 0, 0])

# Lights
default_light = LightSource([2, 8, -20], 0.8)
lights_scene1 = [LightSource([25, 25, -50], 0.8, 'shadowless'),
                 LightSource([-25, -25, -50], 0.8, 'shadowless'),
                 LightSource([10, 10, -40], 0.6, 'shadowless')]
spot_lights = [LightSource([25, 25, -15], 1, 'shadowless'),
               LightSource([25, -25, -15], 0.6, 'shadowless'),
               LightSource([-25, 25, -15], 0.6, 'shadowless'),
               LightSource([-25, -25, -15], 0.6, 'shadowless')]


# Planes
checkered_ground = Plane([0, 1, 0], -1,
                         Texture(Pigment('checker',
                                         'color', [1, 1, 1],
                                         'color', [0.5, 0.5, 0.5],
                                         'scale', 5)))
# cell_temp_background = Plane([0, 1, 0], -6, 'rotate', [-90, 0, 0],
#                         Texture(Pigment('color', [1, 0.88, 0.35])))
# cell_background = Background([1, 0.88, 0.35])


# Default Models
default_sphere_model = Texture(Pigment('color', [0.9, 0.05, 0.05], 'filter', 0.2),
                               Finish('phong', 0.6, 'reflection', 0.4))
box_model = Texture(Pigment('color', [0, 0.35, 0.57], 'filter', 0.1),
                    Finish('phong', 0.6, 'reflection', 0.4))


# Custom Models:
cell_model = Texture(Pigment('color', [0.49, 0.71, 0.49], 'filter', 0.33),
                     Finish('phong', 0.6, 'reflection', 0.6))
cyl_model = Texture(Pigment('color', [0.04, 0.73, 0.71], 'filter', 0.2),
                    Finish('phong', 0.5, 'reflection', 0.1))
nucleus_model = Texture(Pigment('color', [0.7, 0.23, 0.93], 'filter', 0),
                        Finish('phong', 0.1, 'reflection', 0))
text_model = Texture(Pigment('color', [1, 1, 1], 'filter', 0.2),
                        Finish('phong', 0.3, 'reflection', 0))
splice_model = Texture(Pigment('color', [0.6, 0.7, 0.57], 'filter', 0.5),
                       Finish('phong', 0.6, 'reflection', 0.1, 'transmit', 1))


# Static atom definitions
# See the 'color.inc' povray file for more color examples and names.
atom_colors = {
    'C': [0.4, 0.4, 0.4],
    'H': [1, 1, 1],
    'N': [0, 0, 1],
    'O': [1, 0, 0],
    'P': [1, 0.5, 0],
    'S': [0.6, 0.8, 0.2],
    'OH': [1, 0, 0],
    'HH': [1, 1, 1],
    'Cr': [0, 1, 0]
}

atom_sizes = {
    'C': 1,
    'H': 0.65,
    'HH': 0.65,
    'N': 0.9,
    'O': 1,
    'S': 1.2,
    'OH': 1,
    'P': 1.25,
    'Cr': 1.0
}
