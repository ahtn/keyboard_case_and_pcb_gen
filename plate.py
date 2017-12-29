#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 jem@seethis.link
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from __future__ import absolute_import, division, print_function, unicode_literals

from solid import *
from solid.utils import *

import os
import sys
import math
import numpy as np

import alpha_shape
from pykicad import pcbnew
import kle
import directives

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


def create_switch_hole(pos_x, pos_y, angle, thickness, spacing=19.0, hole_size=14.0,
                hole_extra=0.0):
    switch_hole = switch_hole_local(
        thickness + 0,
        spacing=spacing,
        hole_size=hole_size,
        hole_extra=hole_extra
    )
    return translate([pos_x, pos_y, -0])(rotate([0, 0, angle])(
        translate([-hole_size/2, -hole_size/2, 0])(switch_hole)))

def create_hex_hole(pos_x, pos_y, size, thickness, pos_z=0.0, angle=0.0):

    outside_circle_r = size / math.sqrt(3)
    hex_hole = render()(
        cylinder(r=outside_circle_r, h=thickness, segments=6)
    )

    return translate([pos_x, pos_y, pos_z])(
        rotate([0, 0, angle])(
            hex_hole
        )
    )

def create_rect_hole(pos_x, pos_y, l, w, h, pos_z=0.0, angle=0.0):
    return translate([pos_x, pos_y, pos_z + h/2])(
        rotate([0, 0, angle])(
            cube([l, w, h], center=True)
        )
    )

def create_screw_hole(pos_x, pos_y, radius, thickness, pos_z=0):

    screw_hole = render()(
        cylinder(r=radius, h=thickness, segments=20)
    )

    return translate([pos_x, pos_y, pos_z])(
        screw_hole
    )

class HoleBuilder(object):
    def __init__(self, top_plate_thickness=5.0, pcb_thickness=1.6, segments=15):
        self.top_plate_thickness = top_plate_thickness
        self.pcb_thickness = pcb_thickness
        self.segments = segments

    def create_usb_c_hole(self, pos_x, pos_y, pos_z=0, flip=False):
        l = 9.5
        w = 3.6
        h = 10
        corner_raidus = 0.8
        segs = min(self.segments, 20)

        port_hole = render()(
            rotate([-90, 0, 0])(
                linear_extrude(height=h, center=True)(
                    rounding(r=corner_raidus, segments=segs)(
                        square([l, w], center=True)
                    )
                )
            )
        )


        z_offset = -self.pcb_thickness - w/2
        if flip:
            z_offset = +w/2

        return translate([pos_x, pos_y, pos_z + z_offset])(
            port_hole
        )

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

class PCBBuilder(object):

    def __init__(self, pcb_thickness=1.6):
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

        self.pcb.general.set_thickness(pcb_thickness)

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

class OpenSCADObjectBuilder(object):
    def __init__(self, obj=None):
        self.add_list = []
        self.del_list = []
        if obj:
            self.add_list.append(obj)

    def __add__(self, other):
        self.add_list.append(other)
        return self

    def __sub__(self, other):
        self.del_list.append(other)
        return self

    def generate(self):
        return union()(self.add_list) - self.del_list

class KeyboardBuilder(object):

    def __init__(self, json_object, options):
        self.opt = options

        self.kle_layout = kle.Keyboard.from_json(json_layout, spacing=self.opt.spacing)
        self.kb_pcb = PCBBuilder(self.opt.pcb_thickness)

        self.case = OpenSCADObjectBuilder()
        self.lid = OpenSCADObjectBuilder()

        if self.opt.fast:
            self.epsilon = 1e-4
        else:
            self.epsilon = 0

    def write_to_file(self, file_name):
        with open(file_name, "w") as out_file:
            out_file.write(self.generate_str())

    def edge_list_to_path(self, edge_list, point_list):
        path = []
        last_pos = edge_list[0][0]
        for edge in edge_list:
            if last_pos == edge[0]:
                path.append(list(point_list[edge[0]]))
                last_pos = edge[1]
            else:
                path.append(list(point_list[edge[1]]))
                last_pos = edge[0]
        return path

    def inset_path(self, path, inset_size):
        result = []

        for (i, _) in enumerate(path):
            # ignore the first and last point if they are the same
            last_point = kle.Point(*path[i-1])
            this_point = kle.Point(*path[i])
            next_point = kle.Point(*path[(i+1) % len(path)])

            # vectors pointing to and from the current point
            v0 = this_point - last_point
            v1 = next_point - this_point

            # perpendicular unit vectors to v0, v1 (to the interior)
            u0 = kle.Point(-v0.y, v0.x).normalize()
            u1 = kle.Point(-v1.y, v1.x).normalize()

            # if u0.cross_product(v0) > 0:
            #     u0 *= -1

            # if u1.cross_product(v1) > 0:
            #     u1 *= -1

            # s = a * (1- u0⋅u1) / (v1⋅u0)
            v1_dot_u0 = v1.dot_product(u0)
            if v1_dot_u0 != 0:
                s = inset_size * (1 - u0.dot_product(u1)) / v1_dot_u0
                new_point = this_point + inset_size*u1 + s*v1
            else:
                new_point = this_point + inset_size*u1
            result.append(tuple(new_point))
        return result

    def generate_str(self):
        scad_morphology_path = os.path.join("scad-utils", "morphology.scad")
        use(scad_morphology_path)

        outline_point_set = set()

        up_x = math.inf
        up_y = math.inf
        bot_x = -math.inf
        bot_y = -math.inf

        spacing = self.opt.spacing
        hole_size = self.opt.switch_hole_size

        for key in self.kle_layout.get_keys():

            def add_points(point1, point2, n):
                result = set()
                dv = point2 - point1

                for (i, t) in enumerate(np.linspace(0, 1.0, n+2)):
                    result.add(point1 + (float(t)*dv))
                return result

            points = key.get_rect_points()

            outline_point_set.update(set(points))

            n_w = math.floor(key.u_w()) + self.opt.alpha_density
            outline_point_set.update(add_points(points[0], points[1], n_w))
            outline_point_set.update(add_points(points[2], points[3], n_w))
            n_h = math.floor(key.u_h()) + self.opt.alpha_density
            outline_point_set.update(add_points(points[0], points[3], n_h))
            outline_point_set.update(add_points(points[1], points[2], n_h))


            for point in key.get_rect_points():
                up_x = min(point.x, up_x)
                up_y = min(point.y, up_y)

                bot_x = max(point.x, bot_x)
                bot_y = max(point.y, bot_y)
        margin = self.opt.margin
        margin = self.opt.margin
        size_x = abs(bot_x - up_x) + margin
        size_y = abs(bot_y - up_y) + margin

        case_outline = None

        top_thickness = self.opt.top_thickness
        bot_thickness = self.opt.bot_thickness

        # Use the outline points to determine the bounding polygons for the
        # case and the PCB
        outline_point_list = list(outline_point_set)

        _, case_perimeter = alpha_shape.alpha_shape(self.opt.alpha, outline_point_list)
        _, pcb_perimeter = alpha_shape.alpha_shape(self.opt.pcb_alpha, outline_point_list)

        case_path = self.edge_list_to_path(case_perimeter, outline_point_list)
        outline_poly = polygon(points=case_path)

        pcb_path = self.edge_list_to_path(pcb_perimeter, outline_point_list)
        inset_size = 2.5

        pcb_path = self.inset_path(pcb_path, inset_size)

        self.kb_pcb.add_edge_cuts(pcb_path)
        pcb_poly = polygon(points=pcb_path)

        # With the case outline, start constructing the 3D shape of the case
        if self.opt.corner_type == "spherical":
            corner_raidus = 1.5
            segs = self.opt.segments
            top_plate = translate([corner_raidus, corner_raidus, corner_raidus])(
                minkowski()(
                    cube([
                        size_x - corner_raidus*2,
                        size_y - corner_raidus*2,
                        top_thickness - corner_raidus*2,
                    ]),
                    sphere(r=corner_raidus, segments=segs)
                ),
            )
            bot_case = translate([corner_raidus, corner_raidus, corner_raidus-bot_thickness])(
                minkowski()(
                    cube([
                        size_x - corner_raidus*2,
                        size_y - corner_raidus*2,
                        bot_thickness - corner_raidus*2,
                    ]),
                    sphere(r=corner_raidus, segments=segs)
                ),
            )
        elif self.opt.corner_type == "cylinder":
            corner_raidus = 3
            segs = self.opt.segments
            case_outline = fillet(r=corner_raidus, segments=segs)(
                rounding(r=corner_raidus, segments=segs)(
                    outline_poly
                )
            )
        elif self.opt.corner_type == "rectangular":
            case_outline = outline_poly

        if self.opt.corner_type in ["cylinder", "rectangular"]:
            top_plate = linear_extrude(top_thickness)(case_outline)
            bot_case = translate([0, 0, -bot_thickness])(
                linear_extrude(bot_thickness)(case_outline)
            )
            lid_cutout_inset = 2.5-self.opt.pcb_tolerance
            lid_cutout_outline = inset(d=lid_cutout_inset,segments=self.opt.segments)(case_outline)
            lid_inset = lid_cutout_inset+self.opt.lid_tolerance
            lid_outline = inset(d=lid_inset,segments=self.opt.segments)(case_outline)
            self.lid += linear_extrude(self.opt.lid_thickness)(lid_outline)
            lid_cutout = linear_extrude(self.opt.lid_thickness)(lid_cutout_outline)
        if self.opt.pcb_tolerance == 0:
            pcb_cutout = pcb_poly
        else:
            pcb_cutout = outset(d=self.opt.pcb_tolerance, segments=self.opt.segments)(
                pcb_poly
            )

        bot_case_cavity = translate([0, 0, -bot_thickness])(
            linear_extrude(bot_thickness+self.opt.pcb_tolerance_z)(
                pcb_cutout
            )
        ) + translate([0, 0, -bot_thickness])(
            lid_cutout
        )


#         if 0:
#             # # bottom case cavity
#             safety_margin = 0.5
#             safety_margin = 1.5
#             gap_size = spacing - hole_size - safety_margin
#             bot_x = -margin/2 + gap_size/2
#             bot_y = -margin/2 + gap_size/2
#             bot_size_x = size_x - gap_size
#             bot_size_y = size_y - gap_size
#             bot_case_cavity = translate([bot_x, bot_y, -bot_thickness])(
#                 cube([bot_size_x, bot_size_y, bot_thickness])
#             )

        # take cavity out of botcase
        body = None
        if self.opt.plate_only:
            body = top_plate
        else:
            if self.opt.corner_type == "spherical":
                body = hull()(top_plate + bot_case) - bot_case_cavity
            else:
                body = (top_plate + bot_case) - bot_case_cavity

        self.case += body

        dParser = directives.DirectiveParser()
        hole_builder = HoleBuilder(
            top_plate_thickness = top_thickness,
            pcb_thickness = self.opt.pcb_thickness,
            segments = self.opt.segments
        )

        for (i, key) in enumerate(self.kle_layout.get_keys()):
            key_pos = key.get_center()
            x, y = key_pos
            w, h = key.w(), key.h()
            angle = key.r()

            self.kb_pcb.add_switch(
                x, y, w, h, angle,
                spacing=spacing
            )


            for (leg_pos, legend) in key.get_legend_list():
                leg_offset = kle.Point(leg_pos[0], leg_pos[1]) * spacing/2
                try:
                    directive_list = dParser.parse_str(legend)
                except Exception as err:
                    print("Warning: failed to parse directive: " + str(err), file=sys.stderr)

                for directive in directive_list:
                    dir_offset = kle.Point(*directive.get_offset())
                    item_pos = key_pos + leg_offset + dir_offset

                    if type(directive) == directives.HexDirective:
                        # Create a hex hole
                        if directive.h != None:
                            thickness = directive.h
                        else:
                            thickness = top_thickness
                        if  directive.top:
                            self.case -= create_hex_hole(
                                item_pos.x,
                                item_pos.y,
                                directive.size,
                                thickness,
                                angle=directive.r
                            )
                    elif type(directive) == directives.ScrewDirective:
                        # Create a screw hole
                        if directive.top:
                            self.case -= create_screw_hole(
                                item_pos.x,
                                item_pos.y,
                                radius = directive.size / 2,
                                thickness = top_thickness,
                            )
                        if directive.lid:
                            # screw_head_size = directive.h
                            screw_head_size = 1.8
                            screw_retain_thickness = 1.5
                            screw_retain_margin = 0.8
                            # main shaft for screw hole in lid
                            self.lid -= create_screw_hole(
                                item_pos.x,
                                item_pos.y,
                                radius = directive.size / 2,
                                thickness = max(
                                    screw_head_size+screw_retain_thickness,
                                    self.opt.lid_thickness
                                )
                            )
                            if directive.d2 != None:
                                # make inset hole for screw head in lid
                                self.lid -= create_screw_hole(
                                    item_pos.x,
                                    item_pos.y,
                                    radius = directive.d2 / 2,
                                    thickness = screw_head_size,
                                )
                                # add extra material on the lid to retain the inset
                                # screw hole
                                self.lid += create_screw_hole(
                                    item_pos.x,
                                    item_pos.y,
                                    radius = directive.d2 / 2 + screw_retain_margin,
                                    thickness = screw_head_size + self.opt.lid_thickness,
                                )
                    elif type(directive) == directives.USBCDirective:
                        # Creat a hole for a USB Type-C connector
                        if directive.top:
                            self.case -= hole_builder.create_usb_c_hole(
                                item_pos.x,
                                item_pos.y,
                                flip=directive.flip,
                                pos_z=directive.z,
                            )
                    elif type(directive) == directives.RectDirective:
                        # Create a rectangular hole
                        if directive.h != None:
                            h = directive.h
                        else:
                            h = top_thickness
                        rect = create_rect_hole(
                            item_pos.x, item_pos.y,
                            directive.l, directive.w, h,
                            pos_z=directive.z,
                            angle=directive.r
                        )
                        if directive.top:
                            self.case -= rect
                        if directive.lid:
                            self.lid -= rect
                        # if directive.pcb:
                    else:
                        print("Warning> Unknown directive: {}".format(directive), file=sys.stderr)
            # Create the hole for the key switch
            self.case -= create_switch_hole(x, y, angle, top_thickness, hole_size=hole_size)

        case = self.case.generate()
        lid = self.lid.generate()

        parts = part()(
            part()(color("yellow")(case)),
            down(self.opt.bot_thickness + self.opt.lid_thickness + 3)(
                part()(color("red")(lid))
            ),
        )

        # translate board to be centered on the origin
        parts = translate([0, 0, 0])(parts)

        # #
        parts = mirror([0, 1, 0])(parts)

        self.kb_pcb.write_to_file("test_pcb/test_pcb.kicad_pcb")
        scad_render_to_file(case, "test_pcb/test_case.scad")
        scad_render_to_file(lid, "test_pcb/test_lid.scad")
        return scad_render(parts)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description='KLE -> 3D printed plate generator')
    parser.add_argument('kle_json_file', type=str, action='store',
                        help='The hexfile to flash'),
    parser.add_argument('--top-thickness', type=float, action='store',
                        default=5.0,
                        help='The thickness of the plate'),
    parser.add_argument('--bot-thickness', type=float, action='store',
                        default=5.0,
                        help='The thickness of bottom of the case'),
    parser.add_argument('--lid-thickness', type=float, action='store',
                        default=1.5,
                        help='The thickness of lid'),
    parser.add_argument('--lid-tolerance', type=float, action='store',
                        default=0.4,
                        help='Tolerance gap for fitting the lid into the '
                        'bottom of the case.'),
    parser.add_argument('--margin', type=float, action='store',
                        default=0,
                        help='Extra space added around case'),
    parser.add_argument('--pcb-thickness', type=float, action='store',
                        default=1.6,
                        help='The thickness of the pcb'),
    parser.add_argument('--pcb-tolerance', type=float, action='store',
                        default=0.25,
                        help='When cutting out a region for the PCB, this much'
                        ' space is added on both sides to allow the PCB to fit.'),
    parser.add_argument('--pcb-tolerance-z', type=float, action='store',
                        default=0.2,
                        help='Tolerance gap between the top of the PCB and the '
                        'switch plate.'),
    parser.add_argument('--switch-hole-size', type=float, action='store',
                        default=14.0,
                        help='The size of the switch holes'),
    parser.add_argument('--spacing', type=float, action='store',
                        default=19.0,
                        help='The spacing between the switches (center-to-center)'),
    parser.add_argument('--alpha', type=float, action='store',
                        default=0.03,
                        help='Value used when generating the case outline. '
                        'Use smaller values for a more "convex shape."'),
    parser.add_argument('--pcb-alpha', type=float, action='store',
                        default=0.03,
                        help='Value used when generating the pcb outline. '
                        'Use smaller values for a more "convex shape."'),
    parser.add_argument('--alpha-density', type=int, action='store',
                        default=1,
                        help="Increases the point density for the case outline "
                        "algorithm."),
    parser.add_argument('--plate-only', type=bool, action='store',
                        default=False,
                        help="Only generate the plate"),
    parser.add_argument('--corner-type', type=str, action='store',
                        default='cylinder',
                        help="The type of corners to be used when constructing the case."),
    parser.add_argument('--segments', type=int, action='store',
                        default=20,
                        help="The type of corners to be used when constructing the case."),
    parser.add_argument('--fast', action='store_true',
                        help="The type of corners to be used when constructing the case."),

    args = parser.parse_args()

    json_layout = None
    with open(args.kle_json_file) as json_file:
        json_layout = json.loads(json_file.read())

    kb_builder = KeyboardBuilder(json_layout, args)
    scad_code = kb_builder.generate_str()


    with open("test_pcb/test_plate.scad", "w") as out_file:
        out_file.write(scad_code)
    print(scad_code)
