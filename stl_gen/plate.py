#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 jem@seethis.link
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from solid import *
import solid.utils

from math import *
import math
import solid

import kle

from PySide.QtCore import QPointF

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
    # hole = render()(
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



# def test_grid():
#     spacing = 19
#     num_keys_x = 5
#     num_keys_y = 4
#     thickness = 3

#     size_x = spacing * num_keys_x
#     size_y = spacing * num_keys_y

#     body = cube([size_x, size_y, thickness])

#     for i in range(num_keys_y):
#         for j in range(num_keys_x):
#             pos_x = (j * spacing) + spacing/2
#             pos_y = (i * spacing) + spacing/2
#             body -= create_hole(pos_x, pos_y)

#     body =
#     print(scad_render([1, 0, 0])(translate([-size_x/2, -size_y/2, 0])(body)))


def test_kle(json_object, thickness, spacing=19.0, hole_size=14.0, margin=0, plate_only=False):
    import kle

    layout = kle.Layout.layout_from_json(json_layout)
    keys = layout.get_scaled_keys((spacing, spacing), (0, 0))

    up_x = 0
    up_y = 0
    bot_x = 0
    bot_y = 0


    outline_hull_list = []

    key_center = QPointF(0, 0)
    n = 0

    # find bounding box for keyboard switches
    for key in keys:
        rect = key.get_bounding_rect(margin, margin)
        x0 = rect.x()
        y0 = rect.y()
        x1 = rect.x() + rect.width()
        y1 = rect.y() + rect.height()

        key_center += rect.bottomLeft()
        key_center += rect.bottomRight()
        key_center += rect.topLeft()
        key_center += rect.topRight()
        n += 4

        up_x = min(x0, up_x)
        up_y = min(y0, up_y)

        bot_x = max(x1, bot_x)
        bot_y = max(y1, bot_y)

        outline_hull_list.append(
            translate([key.x, key.y,0]) (
                rotate([0,0,key.r]) (
                    square([key.w, key.h])
                )
            )
        )

    key_center = 1/n * key_center;

    outline_hull_list.append(translate([120, 20, 0])(square([16, 16])))

    size_x = abs(bot_x - up_x) + margin
    size_y = abs(bot_y - up_y) + margin

    # case outline ("rectangular", "circular", "spherical")
    corner_type = "spherical"
    case_outline = None

    top_plate_thickness = 5

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
    elif corner_type == "circular":
        corner_raidus = 3
        segs = 20
        case_outline = translate([corner_raidus, corner_raidus, 0])(
            linear_extrude(top_plate_thickness)(
                minkowski()(
                    square([size_x - corner_raidus*2, size_y - corner_raidus*2]),
                    circle(r=corner_raidus, segments=segs)
                )
            )
        )
    elif corner_type == "rectangular":
        case_outline = cube([size_x, size_y, top_plate_thickness])

    top_plate = None
    bot_case = None

    if 0:
        top_plate = linear_extrude(top_plate_thickness)(hull()(outline_hull_list))
        bot_case = translate([0, 0, -thickness])(top_plate)
    else:
        top_plate = translate([up_x-margin/2, up_y-margin/2, 0])(case_outline)
        bot_case = translate([up_x-margin/2, up_y-margin/2, -thickness])(case_outline)
        # case above and below
        bot_case_cavity = translate([2.2, 1.8, 0])(scale([0.97, 0.95, 1.01])(bot_case))


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
    # bot_case_lid = translate([bot_x, bot_y, 0])(
    #     cube([bot_size_x, bot_size_y, lid_thickness])
    # )

    lid_center_offset = (0, -100)

    bot_case_lid  = linear_extrude(lid_thickness)(
            translate([2.3,1.8, 0])(scale([0.97 - 0.0015, 0.95 - 0.0015, 1.00])(
                (hull()(outline_hull_list))
            )
        )
    )

    # take cavity out of botcase
    body = None
    if plate_only:
        body = hull()(top_plate)
    else:
        body = hull()(top_plate, bot_case) - bot_case_cavity

    hole_list = []

    # features that need to be added and subtracted from the lid
    lid_add_list = []
    lid_del_list = []

    for (i, key) in enumerate(keys):
        row = i // 6
        col = i % 6

        rect = key.get_rect()

        # center is the average of points
        rect_center_x = 0
        rect_center_y = 0
        for vert in rect:
            rect_center_x += 1/4 * (vert[0])
            rect_center_y += 1/4 * (vert[1])

        # create hex holes
        # if False:
        if (row, col) in [
                # (0, 0), (0, 2), (0, 4),
                # (3, 0), (3, 2), (3, 4),

                # (3, 1),
                # (3, 2),
                # (0, 1),
                # (2, 1),
                # (1, 2),
                # (2, 0),
            ]:
            # hex_x = rect_center_x + spacing / 2
            # hex_y = rect_center_y
            angle = 30
            if (row, col) == (3,1):
                hex_x = rect_center_x + spacing / 2 + 2
                hex_y = rect_center_y
            elif (row, col) == (3,2):
                hex_x = rect_center_x + spacing / 2 + 1
                hex_y = rect_center_y + 9
            elif (row, col) == (0, 1):
                hex_x = rect_center_x + 2
                hex_y = rect_center_y - spacing / 2 - 2
                angle = 0
            elif (row, col) == (2, 1):
                hex_x = rect_center_x
                hex_y = rect_center_y - spacing / 2 - 1
                angle = 0
            elif (row, col) == (2, 0):
                hex_x = rect_center_x - 2
                hex_y = rect_center_y - spacing / 2 - 8
            elif (row, col) == (1, 2):
                hex_x = rect_center_x - spacing/2
                hex_y = rect_center_y + spacing
                angle = 0
            hex_hole = create_hex_hole(hex_x, hex_y, 4.7, 3, angle)
            hole_list.append(hex_hole)

            if (row, col) == (1, 2):
                lid_del_list.append(translate([hex_x-5, hex_y-13.5, lid_thickness])(cube([10, 10, lid_thickness], center=False)))
                lid_del_list.append(translate([hex_x-14.0, hex_y-5, lid_thickness])(cube([10, 10, lid_thickness], center=False)))

            (shaft, drill) = create_case_screw(hex_x, hex_y)
            lid_add_list.append(shaft)
            lid_del_list.append(drill)

        if (row, col) in [
                # (0, 3)
        ]:
            pos_x = rect_center_x + spacing / 2
            pos_y = rect_center_y + spacing / 2
            slider_hole = create_power_switch_hole(pos_x, pos_y, lid_thickness)
            lid_del_list.append(slider_hole)
            # lid_add_list.append(slider_hole)

        if (row, col) in [
                # (1, 4)
        ]:
            pos_x = rect_center_x + spacing / 2
            pos_y = rect_center_y + spacing / 2
            slider_hole = create_nrf24_hole(pos_x, pos_y, lid_thickness)
            lid_del_list.append(slider_hole)

        # cr2032 battery hole
        if (row, col) in [
                # (1, 1)
            ]:
            bat_x = rect_center_x + spacing / 2
            bat_y = rect_center_y + spacing / 2
            hex_hole = create_cr2032_hole(bat_x, bat_y)
            hole_list.append(hex_hole)

            lid_del_list.append(create_cr2032_lid_hole(bat_x, bat_y, lid_thickness))

        if (row, col) in [
                # (1, 2)
            ]:
            bat_x = rect_center_x + spacing / 2
            bat_y = rect_center_y + spacing / 2 + spacing/4
            hex_hole = create_cr2032_hole(bat_x, bat_y)
            hole_list.append(hex_hole)

            lid_del_list.append(create_cr2032_lid_hole(bat_x, bat_y, lid_thickness, scale=1.2))

        if (row, col) in [
                # (0, 0),
                # (0, 1),
                # (0, 2),
                # (0, 3),
                # (0, 4),
                # (0, 5),

                # (1, 0),
                # (1, 1),
                # (1, 3),
                # (1, 4),
                # (1, 5),

                # (2, 1),
                # (2, 2),
                # (2, 3),
                # (2, 4),
                # (2, 5),
            ]:
            plus_x = rect_center_x + spacing/2
            plus_y = rect_center_y + spacing/2

            w = 4
            h = 12
            z = 3.5
            body += translate([plus_x-w/2, plus_y-h-4, -z])(cube([w, h, z]))

        if (row, col) in [
                # (0, 0),
                # (0, 1),
                # (0, 2),
                # (0, 3),
                # # (0, 4),
                # (0, 5),

                # (1, 0),
                # (1, 1),
                # (1, 3),
                # (1, 4),
                # # (1, 5),

                # (2, 1),
                # (2, 2),
                # (2, 3),
                # (2, 4),
                # (2, 5),
            ]:
            plus_x = rect_center_x
            plus_y = rect_center_y + spacing / 2

            w = 10
            h = 4
            z = 3.5
            body += translate([plus_x - w/2, plus_y-h/2, -z])(cube([w, h, z]))


        if (row, col) in [
                (2, 4)
            ]:
            bat_x = rect_center_x + spacing + 1.5 * spacing / 16
            bat_y = rect_center_y + spacing - 1.5
            body += translate([bat_x, bat_y, -0.5])(
                rotate([0, 180, 0])(
                    keyplus_mini_hole()
                )
            )

            y_len = 45
            z = -thickness
            body += translate([bat_x - 27 / 2, bat_y-y_len, z])(
                cube([27, y_len, 6.3])
            )

            x = 2
            y = -13
            body += translate([bat_x - 27 / 2 + x, bat_y-y_len+y, z-1.5])(
                hole()(cube([27, y_len, 6.3+3.5]))
            )

            xx = -2.1
            yy = 1.1
            bot_case_lid -= (translate([bat_x - 27 / 2 + x + xx, bat_y-y_len+y + yy, z-1.5])(
                cube([30, y_len, 6.3+3.5])
            ))

        if (row, col) in [
                (0, 0)
            ]:
            bat_x = rect_center_x + spacing / 2
            bat_y = rect_center_y + spacing / 2
            usb_c_hole = create_mid_key_usb_c_hole(bat_x, bat_y, top_plate_thickness)
            hole_list.append(usb_c_hole)
            lid_del_list.append(usb_c_hole)


        pos_x = rect_center_x
        pos_y = rect_center_y
        angle = key.r
        # all_holes += create_hole(pos_x, pos_y)
        hole_list.append(create_hole(pos_x, pos_y, angle, top_plate_thickness, hole_size=hole_size))

    body -= union()(hole_list)

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


    # return scad_render(parts)
    return scad_render(parts)


def test_sphere(thickness, spacing=19.0, hole_size=14.0, margin=0, full=False):

    R = 40

    size_x = 0
    size_y = 0

    switch_hole = create_hole(0, 0, 0, thickness, spacing=spacing, hole_size=hole_size,
                              hole_extra=2)
    switch_box = translate([-spacing/2, -spacing/2, 0])(cube([19.0, 19.0, thickness]))

    # take cavity out of botcase
    body = sphere(r=R)
    body -= sphere(r=R-thickness-0.5)

    # features that need to be added and subtracted from the lid
    add_list = []
    del_list = []

    phi_segments = 3
    theta_segments_list = [12,8,4,1, 1, 5]
    for j in list(range(phi_segments)) + [phi_segments]:
        phi = j * (math.pi/2) / phi_segments

        xy_r = R * cos(phi)
        xy_ring_diam = xy_r * math.pi * 2

        theta_segments = int(theta_segments_list[j])

        for i in range(theta_segments):
            theta = i * math.pi*2 / theta_segments
            curvature_adjustment = 1
            r = R - thickness - curvature_adjustment
            x = r * cos(phi) * cos(theta)
            y = r * cos(phi) * sin(theta)
            z = r * sin(phi)

            angle = degrees(theta)
            angle_z = degrees(-phi)

            add_list.append(
                translate([x, y, z])(
                    rotate([0, 0, angle])(
                    rotate([0, angle_z, 0])(
                    rotate([0, 90, 0])(
                    rotate([0, 0, 90])(
                        (switch_box)
                    )
                    )
                    )
                    )
                )
            )
            del_list.append(
                translate([x, y, z])(
                    rotate([0, 0, angle])(
                    rotate([0, angle_z, 0])(
                    rotate([0, 90, 0])(
                    rotate([0, 0, 90])(
                        (switch_hole)
                    ),
                        (switch_hole)
                    )
                    )
                    )
                )
            )

    body += union()(add_list)
    body -= union()(del_list)

    body -= translate([-R, -R, -R - 19/2])(
        cube([3*R, 3*R, R])
    )

    if full:
        body += mirror([0, 0, 1])(body)

    parts = part()(
        color("yellow")(body),
    )

    # translate board to be centered on the origin
    parts = translate([-size_x/2, -size_y/2, 0])(parts)

    # #
    parts = mirror([0, 1, 0])(parts)


    return scad_render(parts)

def test_torus(thickness, spacing=19.0, hole_size=14.0, margin=0, full=False):

    R = 50
    r = 20

    switch_hole = create_hole(0, 0, 0, thickness, spacing=spacing, hole_size=hole_size,
                              hole_extra=2)
    switch_box = translate([-spacing/2, -spacing/2, 0])(cube([19.0, 19.0, thickness]))

    # take cavity out of botcase
    # body = sphere(r=R)
    # body -= sphere(r=R-thickness-0.5)
    body = rotate_extrude(convexity=10, segments=50)(
        translate([R, 0, 0])(
            circle(r=r, segments=100)
        )
    )
    body -= rotate_extrude(convexity=10, segments=50)(
        translate([R, 0, 0])(
            circle(r=(r - 4), segments=100)
        )
    )

    # features that need to be added and subtracted from the lid
    add_list = []
    del_list = []

    theta_segments = 8
    phi_segments = 6
    for theta_i in range(theta_segments):
        theta = theta_i * 360 / theta_segments
        # theta_x = R * cos(theta)
        # theta_y = R * sin(theta)
        for phi_j in range(phi_segments):
            phi = phi_j * 360 / phi_segments
            # phi_

            add_list.append(
                rotate([0, 0, theta])(
                    translate([R, 0, 0])(
                        rotate([0, phi, 0]) (
                            translate([r-thickness, 0, 0]) (
                                rotate([0, 90, 0])(
                                    rotate([0, 0, 90])(
                                        (switch_box)
                                    )
                                )
                            )
                        )

                    )
                )
            )

            del_list.append(
                rotate([0, 0, theta])(
                    translate([R, 0, 0])(
                        rotate([0, phi, 0]) (
                            translate([r-thickness, 0, 0]) (
                                rotate([0, 90, 0])(
                                    rotate([0, 0, 90])(
                                        (switch_hole)
                                    )
                                )
                            )
                        )

                    )
                )
            )

    body += union()(add_list)
    body -= union()(del_list)

    # body -= translate([-R, -R, -R - 19/2])(
    #     cube([3*R, 3*R, R])
    # )

    parts = part()(
        color("yellow")(body),
    )


    return scad_render(parts)

def test_battery():
    margin = 2

    hole_w = 11.0
    hole_h = 49.0
    hole_z = hole_w
    battery_hole = cube([hole_w, hole_h, hole_z+margin])

    shell = cube([hole_w+margin, hole_h+margin, hole_z+margin])

    shell -= translate([margin/2, margin/2, margin/2])(battery_hole)
    return scad_render(shell)

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
    h = hole_h + shell_thickness
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

    args = parser.parse_args()

    json_layout = None
    with open(args.kle_json_file) as json_file:
        json_layout = json.loads(json_file.read())

    scad_code = test_kle(json_layout,
                         args.thickness,
                         spacing=args.spacing,
                         hole_size=args.hole_size,
                         margin=0,
                         )


    # scad_code = test_battery()

    # scad_code = test_sphere(5,
    #                      spacing=19,
    #                      hole_size=14,
    #                      margin=0,
    #                      full=False,
    #                      )

    # scad_code = test_torus(5)

    # scad_code = test_keyplus_mini()

    print(scad_code)
