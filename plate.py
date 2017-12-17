#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 jem@seethis.link
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from __future__ import absolute_import, division, print_function, unicode_literals

from solid import *
import os
import math
from math import (cos, sin)
import numpy as np

import alpha_shape
from pykicad import pcbnew
import kle

def switch_hole_local(thickness, spacing=19.0, hole_size=14.0, hole_extra=0.0):
    # switch hole
    switch_w = hole_size
    switch_h = hole_size
    main_switch_hole = translate([0, 0, -hole_extra/2])(
        cube([switch_w, switch_h, thickness + hole_extra])
    )
    if hole_extra != 0.0:
        offset = -( spacing - hole_size) / 2
        main_switch_hole += translate([offset, offset, thickness-0.01])(
            cube([spacing, spacing, 3])
        )


    # clip hole
    clip_w = 1.2
    clip_h = 1.7
    clip_depth = 1.5
    clip_hole = cube([clip_w, clip_depth, clip_h])

    top_plate_offset = 1.3
    clip_space = 1.9

    clip0_x = switch_w / 2 - clip_space / 2 - clip_w
    clip0_y = -clip_depth
    clip1_x = switch_w / 2 + clip_space / 2
    clip1_y = clip0_y

    clip2_x = clip0_x
    clip2_y = switch_h
    clip3_x = clip1_x
    clip3_y = clip2_y

    # main_switch_hole = translate([0, clip_depth, 0])(main_switch_hole)
    z = thickness - clip_h - top_plate_offset
    # z = thickness + clip_h + top_offset

    clip_0 = translate([clip0_x, clip0_y, z])(clip_hole)
    clip_1 = translate([clip1_x, clip1_y, z])(clip_hole)
    clip_2 = translate([clip2_x, clip2_y, z])(clip_hole)
    clip_3 = translate([clip3_x, clip3_y, z])(clip_hole)

    # combinded = union()(main_switch_hole, clip_0, clip_1, clip_2, clip_3)

    # return scale([1, 1, 1+epsilon])(combinded)
    return [main_switch_hole, clip_0, clip_1, clip_2, clip_3]


def create_hole(pos_x, pos_y, angle, thickness, spacing=19.0, hole_size=14.0,
                hole_extra=0.0):
    hole = (
        switch_hole_local(thickness,
                          spacing=spacing,
                          hole_size=hole_size,
                          hole_extra=hole_extra)
    )
    return translate([pos_x, pos_y, 0])(rotate([0, 0, angle])(
        translate([-hole_size/2, -hole_size/2, 0])(hole)))

def create_hex_hole(pos_x, pos_y, size, thickness, angle=0.0):

    outside_circle_r = size / sqrt(3)
    hex_hole = render()(
        cylinder(r=outside_circle_r, h=thickness, segments=6)
    )

    return translate([pos_x, pos_y, 0])(rotate([0, 0, angle])((hex_hole)))

def create_case_screw(pos_x, pos_y):
    m3_screw_r = 3.0 / 2
    shaft_r = 10.0 / 2
    screw_head_r = 7.0 / 2
    screw_head_h = 2.0

    size = 3.0 # total screw assembly size

    screw = cylinder(r=m3_screw_r, h=size, segments=20)
    shaft = cylinder(r=shaft_r, h=size, segments=20)
    counterbored_hole = cylinder(r=screw_head_r, h=screw_head_h, segments=20)

    # shaft = shaft - hole()(screw, counterbored_hole)
    shaft = shaft

    add_material = translate([pos_x, pos_y, 0])(shaft)
    del_material = translate([pos_x, pos_y, 0])(screw, counterbored_hole)
    return (add_material, del_material)

def create_power_switch_hole(pos_x, pos_y, lid_thickness):
    # pos_x, pos_y are center of smd slider switch on pcb

    w = 6.0
    h = 2.0

    slider_hole = cube([w, h, lid_thickness])

    x = (pos_x - w/2)
    y = (pos_y - h/2)

    slider_body_h = 3.6
    slider_body_w = 7.0
    slider_switch_slider_h = 1.0
    offset = slider_body_h/2 - slider_switch_slider_h/2

    slider_hole = translate([x, y - offset, 0])(slider_hole) # move hole into position

    body_hole_size = 0.8
    body_hole_w = slider_body_w + 0.4
    body_hole_h = slider_body_h + 0.4
    body_x = pos_x - body_hole_w/2
    body_y = pos_y - body_hole_h/2
    body_z = lid_thickness - body_hole_size
    slider_body_hole = cube([body_hole_w, body_hole_h, body_hole_size])
    slider_body_hole = translate([body_x, body_y, body_z])(slider_body_hole)

    return slider_hole + slider_body_hole

def create_nrf24_hole(pos_x, pos_y, lid_thickness):
    # pos_x, pos_y are center of smd slider switch on pcb

    w = 16
    h = 16

    hole_depth = 0.8

    nrf24_hole = cube([w, h, hole_depth])

    x = pos_x - w/2
    y = pos_y - h/2
    z = lid_thickness - hole_depth

    nrf24_hole = translate([x, y, z])(nrf24_hole) # move hole into position

    return nrf24_hole

def keyplus_mini_hole(wall_height=7, side_walls=False):
    shell_thickness = 2
    shell_thickness_bot = 5.40

    hole_w = 25
    hole_h = 24
    hole_z = 7

    if side_walls:
        main_hole = hole()(cube([hole_w, hole_h, hole_z+shell_thickness_bot]))
    else:
        main_hole = hole()(cube([hole_w+shell_thickness+0.1, hole_h+shell_thickness+0.1, hole_z+shell_thickness_bot]))

    shell = cube([hole_w+shell_thickness, hole_h+shell_thickness, hole_z+shell_thickness])


    if side_walls:
        shell += translate([shell_thickness/2, shell_thickness/2, shell_thickness_bot/2])(main_hole)
    else:
        shell += translate([0, shell_thickness/2, shell_thickness_bot/2])(main_hole)

    c_w = 10
    c_h = 3
    c_z = 3.6
    usb_c_hole = hole()(cube([c_w, c_h, c_z]))

    w = hole_w + shell_thickness
    # h = hole_h + shell_thickness
    z = hole_z + shell_thickness
    shell -= translate([w/2 - c_w/2, 0, z/2 - c_z/2])(usb_c_hole)

    screw_hole_offset_x = 18.15 / 2
    screw_hole_offset_y = 1.1 + shell_thickness

    screw_hole_1 = cylinder(r=1, h=7, segments=50)
    screw_hole_2 = cylinder(r=1, h=7, segments=50)

    shell += translate([w/2 - screw_hole_offset_x, screw_hole_offset_y, 0])(hole()(screw_hole_1))
    shell += translate([w/2 + screw_hole_offset_x, screw_hole_offset_y, 0])(hole()(screw_hole_2))

    total_x = hole_w+shell_thickness
    total_y = hole_h+shell_thickness
    total_z = hole_z+shell_thickness
    return translate([-total_x/2, -total_y/2, -total_z/2])(shell)

def create_cr2032_hole(pos_x, pos_y):
    thickness = 0.8
    diam = 25
    circle_r = diam / 2
    hole = cylinder(r=circle_r, h=thickness)

    return translate([pos_x, pos_y, 0])(hole)

def create_cr2032_lid_hole(pos_x, pos_y, lid_thickness, scale=1.0):
    thickness = 0.5
    diam = 20.8
    circle_r = diam / 2 * scale
    hole = cylinder(r=circle_r, h=thickness)

    z = lid_thickness - thickness

    return translate([pos_x, pos_y, z])(hole)

def create_mid_key_usb_c_hole(pos_x, pos_y, top_plate_thickness):
    w = 10
    h = 5
    tall = 4

    nrf24_hole = cube([w, h, tall])

    x = pos_x - w/2
    y = pos_y - h/2
    z = -tall

    nrf24_hole = translate([x, y, z])(nrf24_hole) # move hole into position

    return nrf24_hole



class PCBBuilder(object):

    def __init__(self):
        switch      = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_NoSilk_Back.kicad_mod")
        switch_1    = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u1_NoSilk_Back.kicad_mod")
        switch_1_25 = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u1.25_NoSilk_Back.kicad_mod")
        switch_1_5  = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u1.5_NoSilk_Back.kicad_mod")
        switch_1_75 = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u1.75_NoSilk_Back.kicad_mod")
        switch_2    = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u2_NoSilk_Back.kicad_mod")
        switch_2_25 = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u2.25_NoSilk_Back.kicad_mod")
        switch_2_5  = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u2.5_NoSilk_Back.kicad_mod")
        switch_2_75 = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u2.75_NoSilk_Back.kicad_mod")
        switch_3    = pcbnew.Module.from_file("mx.pretty/Cherry_MX_Matias_u3_NoSilk_Back.kicad_mod")

        self.key_footprints = {
            0:    switch,
            1.00: switch_1,
            1.25: switch_1_25,
            1.50: switch_1_5,
            1.75: switch_1_75,
            2.00: switch_2,
            2.25: switch_2_25,
            2.50: switch_2_5,
            2.75: switch_2_75,
            3.00: switch_3,
        }

        self.sw_ref_counter = 0

        self.pcb = pcbnew.PCBDocument()

    def add_switch(self, x, y, w, h, r, ref="SW{}", spacing=19.0):
        key_u = w / spacing
        key_u_h = h / spacing

        if key_u_h == 1.0 and key_u in self.key_footprints:
            key_foot = self.key_footprints[key_u]
        else:
            key_foot = self.key_footprints[0]

        self.pcb += key_foot.place(x, y, a=-r, ref=ref.format(self.sw_ref_counter))
        self.sw_ref_counter += 1

    def add_edge_cuts(self, path):
        for i in range(len(path) - 1):
            self.pcb += pcbnew.GR_Line(
                start = path[i],
                end = path[i+1],
                layer="Edge.Cuts"
            )
        self.pcb += pcbnew.GR_Line(
            start = path[len(path)-1],
            end = path[0],
            layer="Edge.Cuts"
        )

    def write_to_file(self, file_name):
        with open(file_name, "w") as out_file:
            out_file.write(self.generate_str())

    def generate_str(self):
        return self.pcb.generate()



def test_kle(json_object, thickness, spacing=19.0, hole_size=14.0, margin=0,
             plate_only=False, alpha_factor=0.07, alpha_point_density=0):
    scad_morphology_path = os.path.join("scad-utils", "morphology.scad")
    use(scad_morphology_path)

    keyboard = kle.Keyboard.from_json(json_layout, spacing=spacing)
    kb_pcb = PCBBuilder()

    outline_point_set = set()

    up_x = math.inf
    up_y = math.inf
    bot_x = -math.inf
    bot_y = -math.inf


    for key in keyboard.get_keys():

        def add_points(point1, point2, n):
            result = set()
            dv = point2 - point1

            for (i, t) in enumerate(np.linspace(0, 1.0, n+2)):
                result.add(point1 + (float(t)*dv))
            return result

        points = key.get_rect_points()

        outline_point_set.update(set(points))

        n_w = math.floor(key.u_w()) + alpha_point_density
        outline_point_set.update(add_points(points[0], points[1], n_w))
        outline_point_set.update(add_points(points[2], points[3], n_w))
        n_h = math.floor(key.u_h()) + alpha_point_density
        outline_point_set.update(add_points(points[0], points[3], n_h))
        outline_point_set.update(add_points(points[1], points[2], n_h))


        for point in key.get_rect_points():
            # print (point, up_x, up_y, bot_x, bot_y)

            up_x = min(point.x, up_x)
            up_y = min(point.y, up_y)

            bot_x = max(point.x, bot_x)
            bot_y = max(point.y, bot_y)

    size_x = abs(bot_x - up_x) + margin
    size_y = abs(bot_y - up_y) + margin

    # case outline ("rectangular", "cylinder", "spherical")
    corner_type = "cylinder"
    case_outline = None

    top_plate_thickness = 5


    # print(outline_hull.vertices)
    # print(outline_point_set)
    outline_point_list = list(outline_point_set)

    # print(len(outline_point_list), outline_point_list, len(outline_point_list))

    _, perimeter = alpha_shape.alpha_shape(alpha_factor, outline_point_list)
    # alpha_shape.draw(outline_indices, outline_point_set)

    # outline_verts = []
    # for ind in outline_indices:
    #     p0 = outline_point_list[ind[0]]
    #     p1 = outline_point_list[ind[1]]
    #     outline_verts.append([list(p0), list(p1)])
    # outline_indices = sorted(outline_indices.tolist())
    path = []
    last_pos = None
    for edge in perimeter:
        # print(last_pos, edge)
        if last_pos == edge[0]:
            path.append(list(outline_point_list[edge[0]]))
            last_pos = edge[1]
        else:
            path.append(list(outline_point_list[edge[1]]))
            last_pos = edge[0]
    # print(path)
    outline_poly = polygon(points=path)
    kb_pcb.add_edge_cuts(path)

    if corner_type == "spherical":
        corner_raidus = 1.5
        segs = 35
        case_outline = translate([corner_raidus, corner_raidus, corner_raidus])(
            minkowski()(
                cube([
                    size_x - corner_raidus*2,
                    size_y - corner_raidus*2,
                    top_plate_thickness - corner_raidus*2,
                ]),
                sphere(r=corner_raidus, segments=segs)
            )
        )
    elif corner_type == "cylinder":
        corner_raidus = 3
        segs = 50
        case_outline = linear_extrude(top_plate_thickness)(
            fillet(r=corner_raidus, segments=segs)(
                rounding(r=corner_raidus, segments=segs)(
                    outline_poly
                )
            )
        )
        case_outline2 = fillet(r=0.3, segments=segs)(
            rounding(r=0.3, segments=segs)(
                outline_poly
            )
        )
    elif corner_type == "rectangular":
        pos = kle.Point(up_x, up_y)
        case_outline = translate(list(-pos))(
            cube([size_x, size_y, top_plate_thickness])
        )
    # return scad_render(case_outline)

    top_plate = None
    bot_case = None

    if 0:
        bot_case = translate([0, 0, -thickness])(top_plate)
    else:
        top_plate = translate([up_x-margin/2, up_y-margin/2, 0])(case_outline)
        bot_case = translate([up_x-margin/2, up_y-margin/2, -thickness])(case_outline)
        # case above and below
        # bot_case_cavity = translate([2.2, 1.8, 0])(scale([0.97, 0.95, 1.01])(bot_case))
        bot_case_cavity = translate([up_x-margin/2, up_y-margin/2, -thickness])(
            linear_extrude(thickness)(
                inset(d=2.5)(
                    case_outline2
                )
            )
        )


    if 0:
        # # bottom case cavity
        safety_margin = 0.5
        safety_margin = 1.5
        gap_size = spacing - hole_size - safety_margin
        bot_x = -margin/2 + gap_size/2
        bot_y = -margin/2 + gap_size/2
        bot_size_x = size_x - gap_size
        bot_size_y = size_y - gap_size
        bot_case_cavity = translate([bot_x, bot_y, -thickness])(
            cube([bot_size_x, bot_size_y, thickness])
        )


    # define lid outline, case bottom lid
    lid_thickness = 1.5
    bot_case_lid = translate([bot_x, bot_y, 0])(
        linear_extrude(lid_thickness)(
            inset(d=2.5)(
                case_outline2
            )
        )
    )

    # lid_center_offset = (0, -100)

    # bot_case_lid  = linear_extrude(lid_thickness)(
    #         translate([2.3,1.8, 0])(scale([0.97 - 0.0015, 0.95 - 0.0015, 1.00])(
    #             (hull()(outline_hull_list))
    #         )
    #     )
    # )

    # take cavity out of botcase
    body = None
    if plate_only:
        body = top_plate
    else:
        body = (top_plate + bot_case) - bot_case_cavity

    hole_list = []

    # features that need to be added and subtracted from the lid
    lid_add_list = []
    lid_del_list = []

    for (i, key) in enumerate(keyboard.get_keys()):
        x, y = key.get_center()
        w, h = key.w(), key.h()
        angle = key.r()

        kb_pcb.add_switch(
            x, y, w, h, angle,
            spacing=spacing
        )

        # all_holes += create_hole(pos_x, pos_y)
        hole_list.append(create_hole(x, y, angle, top_plate_thickness, hole_size=hole_size))

    body -= union()(translate([0, -14, 0])(hole_list))
    # body -= union()(translate([0, 0, 0])(hole_list))

    # a = translate([lid_center_offset[0], lid_center_offset[1], 0])(
    #     bot_case_lid
    # )

    # # b = mirror([0, 0, 0])(a)
    # b = mirror([0, 1, 0])(
    #     translate([lid_center_offset[0], lid_center_offset[1], 0])(
    #         mirror([0, 1, 0])(
    #             bot_case_lid
    #         )
    #     )
    # )

    # bot_case_lid = union()(a, b)

    # bot_case_lid = resize([162, 97])(translate([-1, 2.5, 0])(bot_case_lid))
    # bot_case_lid = scale([1, 1, 1])(translate([0, 0, 0])(bot_case_lid))

    temp = union()(bot_case_lid)

    bot_case_lid += union()(lid_add_list)
    bot_case_lid -= union()(lid_del_list)
    bot_case_lid = intersection()(bot_case_lid, scale([1, 1, 5])(temp))
    bot_case_lid = translate([0, 0, -thickness*3-0])(bot_case_lid) # move into position
    bot_case_lid = intersection()(bot_case_lid, scale([1, 1, 5])(bot_case_cavity))
    # bot_case_lid = translate([100, size_y + 2, 0])(bot_case_lid) # move to the side

    parts = part()(
        part()(color("yellow")(body)),
        # part()(color("red")(bot_case_lid)),
    )

    # translate board to be centered on the origin
    parts = translate([-size_x/2, -size_y/2, 0])(parts)

    # #
    parts = mirror([0, 1, 0])(parts)

    kb_pcb.write_to_file("test_pcb/test_pcb.kicad_pcb")
    # return scad_render(parts)
    return scad_render(parts)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description='KLE -> 3D printed plate generator')
    parser.add_argument('kle_json_file', type=str, action='store',
                        help='The hexfile to flash'),
    parser.add_argument('--thickness', type=float, action='store',
                        default=5.0,
                        help='The thickness of the plate'),
    parser.add_argument('--hole_size', type=float, action='store',
                        default=14.0,
                        help='The size of the switch holes'),
    parser.add_argument('--spacing', type=float, action='store',
                        default=19.0,
                        help='The spacing between the switches (center-to-center)'),
    parser.add_argument('--alpha', type=float, action='store',
                        default=0.07,
                        help='Value used when generating the case outline. '
                        'Use smaller values for a more "convex shape."'),
    parser.add_argument('--alpha-density', type=int, action='store',
                        default=1,
                        help="Increases the point density for the case outline "
                        "algorithm."),

    args = parser.parse_args()

    json_layout = None
    with open(args.kle_json_file) as json_file:
        json_layout = json.loads(json_file.read())

    scad_code = test_kle(json_layout,
                         args.thickness,
                         spacing=args.spacing,
                         hole_size=args.hole_size,
                         margin=0,
                         alpha_factor=args.alpha,
                         alpha_point_density=args.alpha_density,
                         )

    print(scad_code)
