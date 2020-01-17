#!/usr/bin/env python3

""" This script makes an animation about the process RNA splicing
    In the frame function is calls for the scenes and the scenes
     contain everything for the frame
    'scenes_mrna' is different from the other scenes because it itself is a big function too
     It gets spliceosome objects separate from the mRNA but adds them together"""

__author__ = "Reindert Visser and Vincent Talen"
__version__ = "2.0"

import random
from pypovray import my_models as models
from pypovray import pypovray, logger, SETTINGS
from vapory import Scene, Sphere, SphereSweep, Camera, Text


# ------------------[CONSTANTS]------------------
TOTAL_FRAMES = SETTINGS.Duration * SETTINGS.RenderFPS
TP_END, TP_START, TP_DUR = list(), list(), list()
TWITCH1, TWITCH2 = 0, 0

SPLICE_SIZE = 1  # The radius of the smaller spliceocome parts
BIG_SPLICE_SIZE = 3.5  # The radius of the big spliceosome part
THICKNESS = 0.1  # Thickness of the mRNA


# ------------------[Functions]------------------
def get_added_distance(start_time, duration, distance, step):
    """ This function gets the distance PER FRAME that you want.
            - start_time: when the scene starts (in seconds)
            - duration: how long the scene/movement takes (in seconds)
            - distance: a list with the distances over the axi [x, y, z]
            - step: the basic 'step' variable bound to every frame
        It returns the list with the x, y, z per frame calculated times the frame number
        This means that this is already finished and can be used with multi-thread rendering """
    used_frames = SETTINGS.RenderFPS * duration
    curr_frame = (step + 1) - (SETTINGS.RenderFPS * start_time)
    dist_list = [x / used_frames * curr_frame for x in distance]
    return dist_list


def make_random_int():
    """ To simulate movement of proteins this function is used to add variation in the location
        It returns a random float of -0.25, -0.125, 0, 0.125 or 0.25 """
    rnd = random.choice([-0.25, -0.125, 0, 0.125, 0.25])
    rnd2 = random.choice([-0.25, -0.125, 0, 0.125, 0.25])
    return rnd, rnd2


def get_time_point_data(tp_end):
    """ This function will output two lists.
        One with the start time of the scenes and one with the duration of the scenes """
    tp_start = list()
    start_point = 0
    for i in range(len(tp_end)):
        tp_start.append(start_point)
        start_point = tp_end[i]

    tp_dur = [TP_END[i] - tp_start[i] for i in range(len(tp_start))]
    return tp_start, tp_dur


def make_exon(control_outside, main_outside, center_point, main_inside, control_inside):
    """ This function creates an exon, it takes 5 locations as arguments.
            - control_outside: The control point on the outside
            - main_outside: The physical point to the outside
            - center_point: The middle physical point
            - main_inside: The physical point to the inside
            - control_inside: The control point on the inside
        All locations need to be a list with an x, y and z -> [x, y, z] """
    exon = SphereSweep('cubic_spline', 5,
                       # Control point 1: Controls the bends
                       control_outside, THICKNESS,

                       # Physical points: Where the shape runs through
                       main_outside, THICKNESS,
                       center_point, THICKNESS,
                       main_inside, THICKNESS,

                       # Control point 2: Controls the bends
                       control_inside, THICKNESS,
                       'tolerance', 0.1, models.cyl_model)
    return exon


def make_intron(main_left, main_right, x_list, y_list):
    """ This function creates the intron, it takes 4 arguments that decide the shape.
                - main_outside: the location on the left side of the intron
                - main_middle: the location on the right side of the intron
                - x_list: A list with 7 x-coordinates
                - y_list: A list with 7 y-coordinates
            Locations all need to be a list with an x, y and z -> [x, y, z]"""
    intron = SphereSweep('cubic_spline', 11,
                         # Control point 1: Controls the bends
                         main_left, THICKNESS,

                         # The main physical point on the left
                         main_left, THICKNESS,

                         # The 7 middle physical points
                         [x_list[0], y_list[0], 0], THICKNESS,
                         [x_list[1], y_list[1], 0], THICKNESS,
                         [x_list[2], y_list[2], 0], THICKNESS,
                         [x_list[3], y_list[3], 0], THICKNESS,
                         [x_list[4], y_list[4], 0], THICKNESS,
                         [x_list[5], y_list[5], 0], THICKNESS,
                         [x_list[6], y_list[6], 0], THICKNESS,

                         # The main physical point on the right
                         main_right, THICKNESS,

                         # Control point 2: Controls the bends
                         main_right, THICKNESS,
                         'tolerance', 0.1, models.nucleus_model)
    return intron


def get_objects(time_point, step, intron_pos_1, intron_pos_2):
    """ Gets the objects for the splicing """
    if time_point < TP_END[5]:
        splice_objects = splice_text_scene()
    elif time_point < TP_END[6]:
        splice_objects = splice_intro(step)
    elif time_point < TP_END[7]:
        splice_objects = splice_move_close(intron_pos_1, intron_pos_2)
    elif time_point < TP_END[8]:
        splice_objects = splice_prep(step, intron_pos_1, intron_pos_2)
    elif time_point < TP_END[9]:
        splice_objects = splice_cut(step, intron_pos_1, intron_pos_2)
    elif time_point < TP_END[10]:
        splice_objects = splicing_final()
    elif time_point < TP_END[11]:
        splice_objects = splicing_fadeout(step)
    return splice_objects


def get_old_distance(joint_x, joint_y, y_max):
    """ Get the old distances so the objects don't skip back """
    step_old = (TP_END[9] * SETTINGS.RenderFPS) - 1
    change = get_added_distance(TP_START[9], TP_DUR[9], [1, 1.5, 0], step_old)
    joint_move = [joint_x + change[0], joint_y + 0.15 * change[1]]
    add_intron_y = y_max + change[1]
    step_old2 = (TP_END[10] * SETTINGS.RenderFPS) - 1
    difference = get_added_distance(TP_START[10], TP_DUR[10], [2, 1, 0], step_old2)
    diff_x, diff_y = difference[0], difference[1]
    return joint_move, add_intron_y, diff_x, diff_y


def fly_away(step):
    change_list = get_added_distance(TP_START[11], TP_DUR[11], [35, 4, 0], step)
    x_fly = change_list[0]
    y_fly = change_list[1]
    return x_fly, y_fly


# -------------------[Scenes]--------------------
def s0_intro_text():
    """ This show the title of the animation with our names """
    title = Text('ttf', '"timrom.ttf"',
                 '"RNA Splicing"',
                 0, 0, 'translate', [-2.85, 0.9, -0], 'scale', [5, 5, 1], models.text_model)
    names = Text('ttf', '"timrom.ttf"',
                 '"Reindert Visser and Vincent Talen"',
                 0, 0, 'translate', [-7.2, -0.5, -0], 'scale', [3, 3, 1], models.text_model)
    return Scene(models.camera_scene0,
                 objects=[title, names] + models.lights_scene1)


def s1_cell_overview():
    """ This scene is a single cell centered without any movement """
    cell_sphere = Sphere([0, 0, 0], 25, models.cell_model)

    text = Text('ttf', '"timrom.ttf"',
                '"To begin you first need to know that"',
                0, 0, 'translate', [-14.5, -5, -30], 'scale', [2.5, 2.5, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"RNA Splicing takes place in the cell"',
                 0, 0, 'translate', [-14.5, -6.25, -30], 'scale', [2.5, 2.5, 1], models.text_model)
    return Scene(models.camera_scene1,
                 objects=[cell_sphere, text, text2] + models.lights_scene1)


def s2_cell_zoom(step):
    """ This scene has the camera moving closer towards the cell and entering it """
    cell_sphere = Sphere([0, 0, 0], 25, models.cell_model)
    dpf = get_added_distance(TP_START[2], TP_DUR[2], [0, 0, 49.7], step)
    camera_scene2 = Camera('location', [0, 0, -75], 'look_at', [0, 0, 0],
                           'translate', [dpf[0], dpf[1], dpf[2]])
    return Scene(camera_scene2,
                 objects=[cell_sphere] + models.lights_scene1)


def s3_in_cell():
    """ This scene makes it clear that the splicing process takes place in the nucleus """
    nucleus = Sphere([20, 7.5, 0], 7.5, models.nucleus_model)
    nucleus_text = Text('ttf', '"timrom.ttf"', '"Nucleus"', 0, 0,
                        'translate', [6.75, 2.8, -7.6], 'scale', [2, 2, 0], models.text_model)

    text = Text('ttf', '"timrom.ttf"',
                '"To be even more specific, the RNA splicing"',
                0, 0, 'translate', [-13.25, -4.2, -0], 'scale', [2.35, 2.35, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"takes place in the nucleus of the cell"',
                 0, 0, 'translate', [-13.25, -5.4, -0], 'scale', [2.35, 2.35, 1], models.text_model)
    return Scene(models.camera_scene3,
                 objects=[nucleus, nucleus_text, text, text2] + models.spot_lights)


def s4_zoom_to_mrna(step):
    """ In this scene the camera moves into the nucleus
        to further illustrate that the splicing takes place in the nucleus """
    dpf_cam = get_added_distance(TP_START[4], TP_DUR[4], [0, 0, 22.5], step)
    camera_scene4 = Camera('location', [0, 0, -40], 'look_at', [0, 0, 0],
                           'translate', [dpf_cam[0], dpf_cam[1], dpf_cam[2]])

    dpf_nuc = get_added_distance(TP_START[4], TP_DUR[4], [-20, -7.5, -9.9], step)
    nucleus = Sphere([20, 7.5, 0], 7.5, models.nucleus_model,
                     'translate', [dpf_nuc[0], dpf_nuc[1], dpf_nuc[2]])
    return Scene(camera_scene4,
                 objects=[nucleus] + models.spot_lights)


def scenes_mrna(step, time_point):
    """ This function creates multiple scenes """
    x_exon1 = -15
    x_intron = -5
    x_exon2 = 5
    x_end = 15
    y_max = 6

    joint_x = 3.5
    joint_y = 0.2
    if time_point < TP_END[6]:
        add_intron_y = 0
        joint_move = [0, 0]
        diff_x, diff_y = 0, 0
    elif time_point < TP_END[7]:
        # Old Data
        diff_x, diff_y = 0, 0

        loc_change = get_added_distance(TP_START[7], TP_DUR[7], [0, y_max, 0], step)
        y_change = loc_change[1]
        add_intron_y = y_change

        joint_change = get_added_distance(TP_START[7], TP_DUR[7], [joint_x, joint_y, 0], step)
        joint_move = [joint_change[0], joint_change[1]]
    elif time_point < TP_END[8]:
        # Old Data
        diff_x, diff_y = 0, 0

        # Actual Scene
        change = get_added_distance(TP_START[8], TP_DUR[8], [1, 1.5, 0], step)
        add_intron_y = y_max + change[1]
        joint_move = [joint_x + change[0], joint_y + 0.15*change[1]]
    elif time_point < TP_END[9]:
        # Old Data
        joint_move, add_intron_y, diff_x, diff_y = get_old_distance(joint_x, joint_y, y_max)

        # Actual Scene
        difference = get_added_distance(TP_START[9], TP_DUR[9], [2, 1, 0], step)
        diff_x, diff_y = difference[0], difference[1]
    elif time_point < TP_END[10]:
        # Old Data
        joint_move, add_intron_y, diff_x, diff_y = get_old_distance(joint_x, joint_y, y_max)

        # Actual Scene
        meeting = get_added_distance(TP_START[10], TP_DUR[10], [2, 1, 0], step)
        x_meet, y_meet = meeting[0], meeting[1]
    else:
        # Old Data
        joint_move, add_intron_y, diff_x, diff_y = get_old_distance(joint_x, joint_y, y_max)
        old_step = (TP_END[10] * SETTINGS.RenderFPS) - 1
        meeting = get_added_distance(TP_START[10], TP_DUR[10], [2, 1, 0], old_step)
        x_meet, y_meet = meeting[0], meeting[1]

    joint_point1 = [x_intron + joint_move[0], 0 + joint_move[1], 0]
    joint_point2 = [x_exon2 - joint_move[0], 0 - joint_move[1], 0]

    if time_point < TP_END[9]:
        intron_pos_1 = joint_point1
        intron_pos_2 = joint_point2
        ja_x, ja_y = 0, 0
        x_fly, y_fly = 0, 0
    elif time_point < TP_END[10]:
        intron_pos_1 = [joint_point1[0] + x_meet,
                        joint_point1[1] + y_meet,
                        joint_point1[2]]
        intron_pos_2 = [joint_point2[i] for i in range(3)]
        change = get_added_distance(TP_START[10], TP_DUR[10], [1.5, 1.5, 0], step)
        ja_x = change[0]
        ja_y = change[1]

        henkie = 0.5 * (joint_point1[0] - joint_point2[0])
        jan = 0.5 * (joint_point1[1] - joint_point2[1])
        jolo = get_added_distance(TP_START[10], TP_DUR[10], [henkie, jan, 0], step)

        joint_point1 = [joint_point1[0] - jolo[0],
                        joint_point1[1] - jolo[1],
                        joint_point1[2]]
        joint_point2 = [joint_point2[0] + jolo[0],
                        joint_point2[1] + jolo[1],
                        joint_point2[2]]
        x_fly, y_fly = 0, 0

    else:
        x_fly, y_fly = fly_away(step)
        old_step = (TP_END[10] * SETTINGS.RenderFPS) - 1
        intron_pos_1 = [joint_point1[0] + x_meet - x_fly,
                        joint_point1[1] + y_meet + y_fly,
                        joint_point1[2]]
        intron_pos_2 = [joint_point2[0] - x_fly,
                        joint_point2[1] + y_fly,
                        joint_point2[2]]
        change = get_added_distance(TP_START[10], TP_DUR[10], [1.5, 1.5, 0], old_step)
        ja_x = change[0]
        ja_y = change[1]

        henkie = 0.5 * (joint_point1[0] - joint_point2[0])
        jan = 0.5 * (joint_point1[1] - joint_point2[1])
        jolo = get_added_distance(TP_START[10], TP_DUR[10], [henkie, jan, 0], old_step)

        joint_point1 = [joint_point1[0] - jolo[0],
                        joint_point1[1] - jolo[1],
                        joint_point1[2]]
        joint_point2 = [joint_point2[0] + jolo[0],
                        joint_point2[1] + jolo[1],
                        joint_point2[2]]

    add_intron_x = 1/(5 + 1) * (x_exon2 - x_intron)

    # X-coords
    list_x1 = [0.5, 1.0, 1.5, 3.0, 4.5, 5.0, 5.5]
    list_x2 = [0.2, -0.2, -0.5, -0.65, -0.8, -0.9, -1.3]
    list_x3 = [1.0, 0.1, -0.6, -0.3, 0, 0, 0]
    add_x = [list_x1[i] * add_intron_x + list_x2[i] * diff_x + list_x3[i] * ja_x for i in range(7)]
    x_list = [x_intron - x_fly + i for i in add_x]

    # Y-coords
    list_y1 = [0.2, 0.6, 0.8, 1.0, 0.8, 0.6, 0.2]
    list_y2 = [1.0, 0.8, 0.9, 0.8, 0.8, 0.7, 0.0]
    list_y3 = [-0.4, 0.35, 0.3, 0, 0, 0, 0]
    y_list = [list_y1[i] * add_intron_y + list_y2[i] * diff_y + list_y3[i] * ja_y
              + y_fly for i in range(7)]

    exon1 = make_exon([x_exon1, 0, 0], [x_exon1 + joint_move[0], 0, 0],
                          [x_intron * 1.5, 0, 0],
                          joint_point1, joint_point1)

    intron = make_intron(intron_pos_1, intron_pos_2, x_list, y_list)

    exon2 = make_exon(joint_point2, joint_point2,
                          [x_exon2 * 1.5, 0, 0],
                          [x_end - joint_move[0], 0, 0], [x_end, 0, 0])

    splice_objects = get_objects(time_point, step, intron_pos_1, intron_pos_2)

    return Scene(models.camera_scene5_plus,
                 objects=[exon1, intron, exon2] + models.spot_lights + splice_objects)


def splice_text_scene():
    text = Text('ttf', '"timrom.ttf"',
                '"Here we see pre-mRNA, it got created by duplicating a single strand of DNA"',
                0, 0, 'translate', [-15, 5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"In this pre-mRNA there are non-usable pieces, these are called introns"',
                 0, 0, 'translate', [-15, -5.5, 5], 'scale', [1, 1, 1], models.text_model)
    return [text, text2]


def splice_intro(step):
    """ Introduces both two splice complexes from the angles of the screen """
    change_list = get_added_distance(TP_START[6], TP_DUR[6], [12, 0, 0], step)
    x_change = change_list[0]

    splice_left = Sphere([-15 + x_change, TWITCH1, 0], SPLICE_SIZE,
                         "scale", [1.5, -1, 0], models.splice_model)
    splice_right = Sphere([15 - 0.95 * x_change, TWITCH2, 0], SPLICE_SIZE,
                          "scale", [2, -1, 0], models.splice_model)

    text = Text('ttf', '"timrom.ttf"',
                '"The removal of the introns is done by the spliceosome"',
                0, 0, 'translate', [-15, -4.5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"As can been seen here the spliceosome consists out of multiple proteins"',
                 0, 0, 'translate', [-15, -6, 5], 'scale', [1, 1, 1], models.text_model)
    return [splice_left, splice_right, text, text2]


def splice_move_close(pos_1, pos_2):
    """ Merges the two splice complexes holding the pre-mRNA """
    left, right = pos_1[:], pos_2[:]
    left[0] *= 0.75
    right[0] *= 0.65
    left[1] *= -1
    right[1] *= -1
    splice_left = Sphere(left, SPLICE_SIZE, "scale", [1.5, -1, 0], models.splice_model)
    splice_right = Sphere(right, SPLICE_SIZE, "scale", [2, -1, 0], models.splice_model)

    text = Text('ttf', '"timrom.ttf"',
                '"Two parts of the spliceosome seek out the beginning and the end of an intron"',
                0, 0, 'translate', [-15, -4.5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"Their job is to bring them closer together and hand them over"',
                 0, 0, 'translate', [-15, -6, 5], 'scale', [1, 1, 1], models.text_model)
    return [splice_left, splice_right, text, text2]


def splice_prep(step, pos_1, pos_2):
    """ Introduces the main body of the splicosome
        to assemble with the other parts and cut the intron """
    left, right = pos_1[:], pos_2[:]
    left[0] *= 0.94
    right[0] *= 0.89
    left[1] *= -1
    right[1] *= -1
    splice_left = Sphere(left, SPLICE_SIZE, "scale", [1.5, -1, 0], models.splice_model)
    splice_right = Sphere(right, SPLICE_SIZE, "scale", [2, -1, 0], models.splice_model)

    coord = get_added_distance(TP_START[8], TP_DUR[8], [0, 16, 0], step)
    y_loc = coord[1]
    splice_down = Sphere([0.5 * TWITCH1, 15 - y_loc, 2], BIG_SPLICE_SIZE,
                         "scale", [0, -1.25, 0], models.splice_model)

    text = Text('ttf', '"timrom.ttf"',
                '"Here you see the main part of the spliceosome entering the screen"',
                0, 0, 'translate', [-15, -4.5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"The smaller parts wil connect the intron ends to the main part"',
                 0, 0, 'translate', [-15, -6, 5], 'scale', [1, 1, 1], models.text_model)
    return [splice_left, splice_right, splice_down, text, text2]


def splice_cut(step, pos_1, pos_2):
    """ Moves both splice parts near each other and makes the cut """
    move = get_added_distance(TP_START[9], TP_DUR[9], [15, 5, 0], step)
    x_change, y_change = move[0], move[1]

    left, right = pos_1[:], pos_2[:]
    left[0] = 0.94 * left[0] - x_change
    right[0] = 0.89 * right[0] + x_change
    left[1] = -1 * left[1] - y_change
    right[1] = -1 * right[1] - y_change

    splice_left = Sphere(left, SPLICE_SIZE, "scale", [1.5, -1, 0], models.splice_model)
    splice_right = Sphere(right, SPLICE_SIZE, "scale", [2, -1, 0], models.splice_model)

    splice_down = Sphere([0, -1, 2], BIG_SPLICE_SIZE, "scale", [0, -1.25, 0], models.splice_model)

    text = Text('ttf', '"timrom.ttf"',
                '"Once the two smaller proteins have connected the intron ends"',
                0, 0, 'translate', [-15, -4.5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"to the bigger protein, they will leave the reaction site"',
                 0, 0, 'translate', [-15, -6, 5], 'scale', [1, 1, 1], models.text_model)
    return [splice_left, splice_right, splice_down, text, text2]


def splicing_final():
    """ Provides the spliceosome and the text whilst the mrna forms """
    splice_down = Sphere([0, -1, 2], BIG_SPLICE_SIZE, "scale", [0, -1.25, 0], models.splice_model)

    text = Text('ttf', '"timrom.ttf"',
                '"The spliceosome now disconnects the intron and binds one end of"',
                0, 0, 'translate', [-15, -4.5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"the intron to a suitable place on the other end of the intron."',
                 0, 0, 'translate', [-15, -6, 5], 'scale', [1, 1, 1], models.text_model)
    text3 = Text('ttf', '"timrom.ttf"',
                 '"Meanwhile the exons get put together to form the finished mRNA"',
                 0, 0, 'translate', [-15, -7.5, 5], 'scale', [1, 1, 1], models.text_model)
    return [splice_down, text, text2, text3]


def splicing_fadeout(step):
    """ Moves the whole spliceosome to the corner with the intron """
    x_fly, y_fly = fly_away(step)

    splice_down = Sphere([x_fly, -1 - y_fly, 2], BIG_SPLICE_SIZE, "scale", [0, -1.25, 0], models.splice_model)

    text = Text('ttf', '"timrom.ttf"',
                '"The intron later gets recycled so it can be used again,"',
                0, 0, 'translate', [-15, -4.5, 5], 'scale', [1, 1, 1], models.text_model)
    text2 = Text('ttf', '"timrom.ttf"',
                 '"the spliceosome goes to the next site and"',
                 0, 0, 'translate', [-15, -6, 5], 'scale', [1, 1, 1], models.text_model)
    text3 = Text('ttf', '"timrom.ttf"',
                 '"the mRNA will be used to make a protein"',
                 0, 0, 'translate', [-15, -7.5, 5], 'scale', [1, 1, 1], models.text_model)
    return [splice_down, text, text2, text3]


# -------------------[MAINS]---------------------
def frame(step):
    """ Makes an image/frame """
    time_point = (step / TOTAL_FRAMES) * SETTINGS.Duration
    logger.info(" @Time: %.4fs, Step: %d", time_point, step)

    # Declaration of the end times of the scenes
    global TP_END
    TP_END = [4, 8, 11, 15, 18, 26, 32, 38, 44, 50, 58, 64]
    # scene   0  1  2   3   4   5   6   7   8   9   10, 11

    # Globals that change per frame
    global TP_START, TP_DUR, TWITCH1, TWITCH2
    TP_START, TP_DUR = get_time_point_data(TP_END)
    TWITCH1, TWITCH2 = make_random_int()

    if time_point < TP_END[0]:
        scene = s0_intro_text()
    elif time_point < TP_END[1]:
        scene = s1_cell_overview()
    elif time_point < TP_END[2]:
        scene = s2_cell_zoom(step)
    elif time_point < TP_END[3]:
        scene = s3_in_cell()
    elif time_point < TP_END[4]:
        scene = s4_zoom_to_mrna(step)
    elif time_point < TP_END[11]:
        scene = scenes_mrna(step, time_point)
    else:
        text = Text('ttf', '"timrom.ttf"', '"Uh-oh, this ain\'t right"', 0, 0,
                    'translate', [-4, 0, 0], 'scale', [2, 2, 0], models.text_model)
        scene = Scene(models.default_camera,
                      objects=[models.default_light, text])
    return scene


if __name__ == "__main__":
    logger.info(" Total time: %ds (frames: %d)", SETTINGS.Duration, TOTAL_FRAMES)

    time_points = [56, 64]
    render_frames = [int(i * SETTINGS.RenderFPS) for i in time_points]

    pypovray.render_scene_to_mp4(frame)
    # pypovray.render_scene_to_mp4(frame, range(render_frames[0], render_frames[1]))
