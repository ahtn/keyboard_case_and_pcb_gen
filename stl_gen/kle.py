#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 jem@seethis.link
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

import json
import copy
from pprint import pprint
from math import cos, sin
import math

from PySide.QtCore import QRectF

def dot_prod(v1, v2):
    return sum([v1[i]*v2[i] for i in range(len(v1))])

def rotate_vec(a, v):
    # rotate vector `v` about the origion by `a` degrees
    a = math.pi * a/180
    x = dot_prod((cos(a), -sin(a)), v)
    y = dot_prod((sin(a), cos(a)), v)
    return (x, y)

def rotated_rect(x, y, w, h, a):
    rect = [
        (0, 0),
        (w, 0),
        (w, h),
        (0, h),
    ]

    rotated_rect = []
    for v in rect:
        rv = rotate_vec(a, v)
        rotated_rect.append((x + rv[0], y + rv[1]))
    return rotated_rect

class Key:
    def __init__(self, x, y, w, h, properties=None, decal=False):
        # the coordinate system
        # the offset in the coordinate system
        self.x = x * 1.0
        self.y = y * 1.0
        self.w = w * 1.0
        self.h = h * 1.0
        self.decal = decal
        if properties == None:
            self.properties = KbProperties()
        else:
            self.properties = copy.copy(properties)
        self.r = properties.r
        self.rx = properties.rx
        self.ry = properties.ry

    def get_rect(self, marginX=0, marginY=0):
        x = self.x + self.rx
        y = self.y + self.ry
        return rotated_rect(self.x, self.y, self.w+marginX, self.h+marginY, self.r)

    def get_bounding_rect(self, marginX=0, marginY=0):
        rect = self.get_rect(marginX, marginY)
        minX = rect[0][0]
        minY = rect[0][1]
        maxX = minX
        maxY = minY

        for point in rect:
            minX = min(minX, point[0])
            minY = min(minY, point[1])
            maxX = max(maxX, point[0])
            maxY = max(maxY, point[1])

        w = maxX - minX
        h = maxY - minY
        return QRectF(minX, minY, w, h)

    def scale(self, valX, valY, offsetX, offsetY):
        """
        Returns a scaled copy of the key in global coordinates
        """
        result = copy.copy(self)

        # if valX >= 0:
        #     result.x *= valX
        #     result.w *= valX
        # else:
        #     result.w = abs(result.w * valX)
        #     result.x = (result.x*valX) - result.w

        # if valY >= 0:
        #     result.y *= valY
        #     result.h *= valY
        # else:
        #     result.h = abs(result.h * valY)
        #     result.y = (result.y*valY) - result.h

        # rvec = rotate(result.r, [result.x, result.y])
        rvec = [(result.x), (result.y)]
        rvec = rotate_vec(self.r, rvec)
        result.x = rvec[0] + self.rx
        result.y = rvec[1] + self.ry

        result.x *= valX
        result.y *= valY
        result.w *= valX
        result.h *= valY

        result.x += offsetX
        result.y += offsetY

        result.rx = 0
        result.ry = 0

        # return result
        return result



class KeyProperties:
    def __init__(self,
                 x=0, y=0,
                 w=1, h=1,
                 x2=None, y2=None,
                 w2=None, h2=None,
                 stepped=False,
                 homing=False,
                 decal=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.x2 = None
        self.y2 = None
        self.w2 = None
        self.h2 = None

        self.rx = None
        self.ry = None

        self.stepped = False
        self.homing = False
        self.decal = False

    def fromObject(obj):
        props = KeyProperties()
        if 'x' in obj:
            props.x = float(obj['x'])
        if 'y' in obj:
            props.y = float(obj['y'])
        if 'w' in obj:
            props.w = float(obj['w'])
        if 'h' in obj:
            props.h = float(obj['h'])
        if 'x2' in obj:
            props.x2 = float(obj['x2'])
        if 'y2' in obj:
            props.y2 = float(obj['y2'])
        if 'w2' in obj:
            props.w2 = float(obj['w2'])
        if 'h2' in obj:
            props.h2 = float(obj['h2'])
        if 'd' in obj:
            props.decal = bool(obj['d'])
        if 'l' in obj:
            props.stepped = bool(obj['l'])
        if 'n' in obj:
            props.stepped = bool(obj['n'])
        return props


class KbProperties:
    """
    KbProperties apply to all subsequent keycaps
    """
    def __init__(self,
                 keycap_color='#ffffff',
                 text_color='#000000',
                 ghosted=False,
                 profile=None,
                 text_alignment=None,
                 font_primary=3,
                 font_secondary=3,
                 r = 0,
                 rx = 0,
                 ry = 0
                 ):
        self.bg = keycap_color
        self.fg = text_color
        self.ghosted = False
        self.profile = None
        self.text_alignment = None
        self.font_primary = 3
        self.font_secondary = 3
        self.r = r
        self.rx = rx
        self.ry = ry

    def update(self, obj):
        if 'c' in obj:
            self.bg = str(obj['c'])
        if 't' in obj:
            self.fg = str(obj['t'])
        if 'g' in obj:
            self.ghosted = bool(obj['g'])
        if 'a' in obj:
            self.text_alignment = int(obj['a'])
        if 'f' in obj:
            self.font_primary = int(obj['f'])
        if 'f2' in obj:
            self.font_secondary = int(obj['f2'])
        if 'p' in obj:
            self.profile = str(obj['p'])
        if 'r' in obj:
            self.r = float(obj['r'])
        if 'rx' in obj:
            self.rx = float(obj['rx'])
        if 'ry' in obj:
            self.ry = float(obj['ry'])


class Layout:
    def __init__(self):
        self.keys = [[]]
        self.col = 0
        self.row = -1
        self.global_props = KbProperties()
        self.curX = 0
        self.curY = 0

    def reset_x(self, x):
        self.curX = x

    def reset_y(self, y):
        self.curY = y

    def prevKey(self):
        assert(self.col != 0)
        return self.keys[self.row][self.col-1]

    def addRow(self):
        self.curX = 0
        self.curY += 1
        self.col = 0
        self.row += 1
        self.keys.append([])

    def addKey(self, x=0, y=0, w=1, h=1, decal=False):
        if self.col == 0:
            self.curX += x
            self.curY += y
            posX = self.curX
            posY = self.curY
            key = Key(posX, posY, w, h, properties=self.global_props, decal=decal)
            self.keys[self.row].append(key)
            self.curX += w
        else:
            self.curX += x
            self.curY += y
            posX = self.curX
            posY = self.curY
            key = Key(posX, posY, w, h, properties=self.global_props, decal=decal)
            self.keys[self.row].append(key)
            self.curX += w
        self.col += 1

    def addFatKey(self, w=1, h=1, x=1, y=0, w2=1, h2=1, x2=1, y2=0):
        pass

    def get_scaled_keys(self, val, offset, decals=False):
        result = []
        for row in self.keys:
            for key in row:
                if not decals and key.decal:
                    continue
                result.append(key.scale(val[0], val[1], offset[0], offset[1]))
        return result

    def layout_from_json(json_layout):
        layout = Layout()
        props = KeyProperties()
        pos = 0
        for row in json_layout:
            for key in row:
                if type(key) == str:
                    x = props.x
                    y = props.y
                    w = props.w
                    h = props.h
                    d = props.decal
                    layout.addKey(x, y, w, h, decal=d)
                    # reset properties for next key
                    props = KeyProperties()
                elif type(key) == dict:
                    props = KeyProperties.fromObject(key)

                    old_rx = layout.global_props.rx
                    old_ry = layout.global_props.ry
                    layout.global_props.update(key)

                    if layout.global_props.rx != old_rx \
                        or layout.global_props.ry != old_ry:
                        layout.reset_x(0)
                        layout.reset_y(0)
                pos += 1
            layout.addRow()
        return layout


import tkinter
def show():

    def tk_draw_key(can, key, offset):
        verts = [
            (0    , 0),
            (key.w, 0    ),
            (key.w, key.h),
            (0    , key.h),
        ]
        rot_verts = [rotate(key.r, vert) for vert in verts]
        trans_verts = []
        for vert in rot_verts:
            trans_verts.append((vert[0] + key.x, vert[1] + key.y))

        # can.create_polygon(trans_verts, fill=key.bg)
        can.create_polygon(
            trans_verts,
            fill=key.properties.bg,
            outline=key.properties.fg
        )

    # def tk_draw_key(can, key, offset):
    #     can.create_rectangle(
    #         key.x,
    #         key.y,
    #         key.x + key.w,
    #         key.y + key.h,
    #         fill = key.properties.bg
    #     )

    #     margin = 20
    #     can.create_rectangle(
    #         key.x + margin,
    #         key.y + margin,
    #         key.x + key.w - margin,
    #         key.y + key.h - margin,
    #         fill = key.properties.fg
    #     )


    def tk_draw_layout(layout):
        main_win = tkinter.Tk()
        can = tkinter.Canvas(main_win, width=800, height=800)
        main_win.geometry("+400+400")
        can.pack()

        for key in layout.get_scaled_keys((30.0, 30.0), (100, 100)):
            # draw_key(t, key)
            tk_draw_key(can, key, (100, 100))
        tkinter.mainloop()

    json_layout = None
    with open("test-dox.json") as json_file:
    # with open("test-ansi.json") as json_file:
    # with open("test-numpad.json") as json_file:
        json_layout = json.loads(json_file.read())
    layout = Layout.layout_from_json(json_layout)

    tk_draw_layout(layout)
    # pprint.pprint(json_layout)

if __name__ == "__main__":
    show()
    # print(rotate(math.pi, [0, 1]))
    # print(rotate(math.pi, [1, 0]))
