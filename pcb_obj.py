#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 jem@seethis.link
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from __future__ import absolute_import, division, print_function, unicode_literals

import parse_objs

def sanitize_str(s):
    for char in s:
        if char in [' ', '\n', '(', ')']:
            return '"{}"'.format(s)
    return s

def gen_indent(depth):
    return "  " * depth

class PCBObject(object):
    pass
    # def __str__(self):
    #     return self.generate()

class PCBObjectContainer(object):
    def __init__(self):
        self.objects = []

    def __iadd__(self, obj):
        self.add_object(obj)
        return self

    def add_object(self, obj):
        self.objects.append(obj)

    def _add_token_objects(self, tokens):
        for item in tokens:
            if isinstance(item, PCBObject):
                self.objects.append(item)

    def gen_objects(self, indent_depth=0):
        iter_obj = iter(self.objects)
        indent_str = gen_indent(indent_depth)
        indent_depth += 1
        result = next(iter_obj).generate(indent_depth=indent_depth)
        for obj in iter_obj:
            result += "\n" + obj.generate(indent_depth=indent_depth)
        return result

class PCBDocument(PCBObjectContainer):
    def __init__(self, version=4, host="pcbnew 4.0.7"):
        super(PCBDocument, self).__init__()
        self.version = version
        self.host = host

    def generate(self, indent_depth=0):
        # TODO: check what host field is used for
        result = "(kicad_pcb (version {version}) (host {host})\n".format(
            version = self.version,
            host = self.host
        )
        result += self.gen_objects(indent_depth=indent_depth)
        result += "\n)"
        return result

class General(PCBObject):
    def __init__(self):
        pass # TODO

    def generate(self):
        return ""

class Page(PCBObject):
    def __init__(self, page="A4"):
        self.page = page

    def generate(self):
        return "(page {page})".format(page=self.page)

class LayerList(PCBObject):
    def __init__(self, layers=[]):
        self.layers = layers

    @staticmethod
    def kicad_default_layers():
        return LayerList(layers=[
            (0  , "F.Cu"      , "signal"),
            (31 , "B.Cu"      , "signal"),
            (32 , "B.Adhes"   , "user"),
            (33 , "F.Adhes"   , "user"),
            (34 , "B.Paste"   , "user"),
            (35 , "F.Paste"   , "user"),
            (36 , "B.SilkS"   , "user"),
            (37 , "F.SilkS"   , "user"),
            (38 , "B.Mask"    , "user"),
            (39 , "F.Mask"    , "user"),
            (40 , "Dwgs.User" , "user"),
            (41 , "Cmts.User" , "user"),
            (42 , "Eco1.User" , "user"),
            (43 , "Eco2.User" , "user"),
            (44 , "Edge.Cuts" , "user"),
            (45 , "Margin"    , "user"),
            (46 , "B.CrtYd"   , "user"),
            (47 , "F.CrtYd"   , "user"),
            (48 , "B.Fab"     , "user"),
            (49 , "F.Fab"     , "user"),
        ])

    def generate(self):
        result = "(layers\n"
        for layer in self.layers:
            result += "({number} {name} {category})\n".format(
                number   = layer[0],
                name     = sanitize_str(layer[1]),
                category = layer[2],
            )
        result += ")"
        return result

class Net(PCBObject):
    def __init__(self, number, name):
        self.number = number
        self.name = sanitize_str(name)

    def generate(self):
        return "(net {number} {name})".format(
            number = self.number,
            name = sanitize_str(self.name),
        )

class NetClass(PCBObjectContainer):
    def __init__(self, name, description):
        self.name = name
        self.description = description

        self.clearance = 0.2
        self.trace_width = 0.25

        self.via_dia = 0.6
        self.via_drill = 0.4

        self.uvia_dia = 0.3
        self.uvia_drill = 0.1

        self.objects = []

    @staticmethod
    def kicad_default_net_class():
        return NetClass("Default", "This is the default net class.")

    def add_net(self, pcb_net):
        self.add_object(pcb_net)

    def generate(self):
        result = "(net_class {name} \"{description}\"\n".format(
            name = sanitize_str(self.name),
            description = self.description,
        )
        result += "(clearance {})\n".format(self.clearance)
        result += "(trace_width {})\n".format(self.trace_width)
        result += "(via_dia {})\n".format(self.via_dia)
        result += "(via_drill {})\n".format(self.via_drill)
        result += "(uvia_dia {})\n".format(self.uvia_dia)
        result += "(uvia_drill {})\n".format(self.uvia_drill)
        result += ")"
        return result

def _bool_str(x):
    if x:
        return "yes"
    else:
        return "no"

class Setup(PCBObject):
    def __init__(self):
        self.trace_min = 0.2
        self.trace_clearance = 0.2

        self.segment_width = 0.2
        self.edge_width = 0.1

        self.zone_clearance = 0.50
        self.zone_45_only = False

        self.via_size = 0.6
        self.via_drill = 0.4
        self.via_min_size = 0.4
        self.via_min_drill = 0.3

        self.uvias_allowed = False
        self.uvia_size = 0.3
        self.uvia_drill = 0.1
        self.uvia_min_size = 0.2
        self.uvia_min_drill = 0.1

        self.aux_axis_origin = [0, 0]

    def generate(self):
        result  = "(setup\n"

        # via settings
        result += "(via_size {})\n".format(self.via_size)
        result += "(via_drill {})\n".format(self.via_drill)
        result += "(via_min_size {})\n".format(self.via_min_size)
        result += "(via_min_drill {})\n".format(self.via_min_drill)
        # μvia settings
        result += "(uvia_size {})\n".format(self.uvia_size)
        result += "(uvia_drill {})\n".format(self.uvia_drill)
        result += "(uvia_min_size {})\n".format(self.uvia_min_size)
        result += "(uvia_min_drill {})\n".format(self.uvia_min_drill)
        result += ")"
        return result

class Segment(PCBObject):
    def __init__(self, start, end, width, layer, net):
        self.start = start
        self.end = end
        self.width = width
        self.layer = layer
        self.net = net

    def generate(self):
        return "(segment {start} {end} (width {width}) (layer {layer}) (net {net}))".format(
            start = self.start.gen_start(),
            end = self.end.gen_end(),
            width = self.width,
            layer = self.layer,
            net = self.net.number
        )

class Via(PCBObject):
    def __init__(self, pos, size, drill, net, layers=["F.Cu", "B.Cu"]):
        self.pos = pos
        self.size = size
        self.drill = drill
        self.net = net
        self.layers = layers

    def generate(self):
        return "(via {pos} (size {size}) {drill} (layers {layers}) (net {net}))".format(
            pos = self.pos.generate(),
            size = self.size,
            drill = self.drill.generate(),
            layers = " ".join(self.layers),
            net = self.net.number,
        )

class Model(PCBObject):
    @staticmethod
    def from_tokens(tokens):
        result = Model()
        result.path = tokens.path
        result.pos = tokens.at[0]
        result.scale = tokens.scale[0]
        result.rotate = tokens.rotate[0]
        return result

    def __str__(self):
        return "Model({}, pos={}, scale={}, rotate={})".format(
            self.path,
            self.pos,
            self.scale,
            self.rotate
        )

    def generate(self, indent_depth=0):
        indent_str = gen_indent(indent_depth)
        return indent_str + "(model {path} {pos} {scale} {rotate})".format(
            path = sanitize_str(self.path),
            pos = self.pos.gen_pos(),
            scale = self.scale.gen_scale(),
            rotate = self.rotate.gen_rotate(),
        )

class Font(PCBObject):
    def __init__(self, size, thickness):
        self.size = size
        self.thickness = thickness

    def generate(self):
        return "(font {size} (thickness {thickness}))".format(
            size = self.size.generate()
        )

class Font(PCBObject):
    @staticmethod
    def from_tokens(tokens):
        result = Font()
        result.size = tokens.size[0]
        result.thickness = tokens.thickness[0]
        return result

    def generate(self):
        return "(font {size} (thickness {thickness}))".format(
            size = self.size.generate(),
            thickness = self.thickness,
        )

class Effects(PCBObject):
    @staticmethod
    def from_tokens(tokens):
        result = Effects()
        result.font = tokens.font
        return result

    def generate(self):
        return "(effects {font})".format(font = self.font.generate())

class FP_Text(PCBObject):
    # def __init__(self, text, kind, pos, layer='F.SilkS', width=0.1):
    def __init__(self):
        pass

    @staticmethod
    def from_tokens(tokens):
        result = FP_Text()
        result.pos = tokens.at[0]
        result.kind = tokens.kind
        result.text = tokens.text
        result.layer = tokens.layer[0]
        result.effects = tokens.effects
        return result

    def generate(self, indent_depth=0):
        indent_str = gen_indent(indent_depth)
        return indent_str + "(fp_text {kind} {text} {pos} (layer {layer}) {effects})".format(
            kind = self.kind,
            text = sanitize_str(self.text),
            pos = self.pos.generate(),
            layer = self.layer,
            effects = self.effects.generate(),
        )


class FP_Line(PCBObject):
    def __init__(self):
    # def __init__(self, start, end, layer='F.SilkS', width=0.1):
        # """@todo: to be defined1. """
        # self.start = start
        # self.end = end
        # self.layer = layer
        # self.width = width
        pass

    @staticmethod
    def from_tokens(tokens):
        result = FP_Line()
        if tokens.start:
            result.start = tokens.start[0]
        else:
            result.start = Pos()
        if tokens.end:
            result.end = tokens.end[0]
        else:
            result.end = Pos()
        result.layer = tokens.layer[0]
        result.width = tokens.width[0]
        return result

    def generate(self, indent_depth=0):
        indent_str = gen_indent(indent_depth)
        return indent_str + "(fp_line {start} {end} (layer {layer}) (width {width}))".format(
            start = self.start.gen_start(),
            end = self.end.gen_end(),
            layer=self.layer,
            width=self.width,
        )

    def __str__(self):
        return "FP_Line({}, {}, {}, {})".format(self.start, self.end, self.layer, self.width)

class Module(PCBObjectContainer):
    def __init__(self):
        super(Module, self).__init__()
        self.description = None
        self.tags = None
        self.attr = None
        self.layer = None

    @staticmethod
    def from_str(text):
        return parse_objs.Module.parseString(text).module

    @staticmethod
    def from_tokens(tokens):
        result = Module()
        result.component = tokens.component
        if tokens.at:
            result.pos = tokens.at
        else:
            result.pos = Pos()
        if tokens.descr:
            result.description = tokens.descr[0]
        if tokens.tags:
            result.tags = tokens.tags[0]
        if tokens.attr:
            result.attr = tokens.attr[0]
        if tokens.layer:
            result.layer = tokens.layer[0]
        result._add_token_objects(tokens)
        return result

    def generate(self, indent_depth=0):
        indent_str = gen_indent(indent_depth)
        result = "\n"
        result += indent_str + "(module {component} {pos} (layer {layer})\n".format(
            component = self.component,
            pos = self.pos.generate(),
            layer = self.layer,
        )
        indent_str = gen_indent(indent_depth+1)
        if self.description:
            result += indent_str + "(descr \"{}\")\n".format(self.description)
        if self.tags:
            result += indent_str + "(tags \"{}\")\n".format(self.tags)
        if self.attr:
            result += indent_str + "(attr {})\n".format(self.attr)
        result += self.gen_objects(indent_depth=indent_depth)
        indent_str = gen_indent(indent_depth)
        result += "\n" + indent_str + ")"
        return result

class Drill(PCBObject):
    def __init__(self, x, y=None, offset=None):
        self.x = x
        self.y = y
        self.offset = offset

    def generate(self):
        result = "(drill "
        if self.y == None: # Circular hole
            result += "{}".format(self.x)
        elif self.y != None: # Oval Hole
            result += "oval {} {}".format(self.x, self.y)
        if self.offset:
            result += " " + self.offset.generate()
        result += ")"
        return result

class PCBObjectVec(PCBObject):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y

    def __str__(self):
        return "{}({}, {})".format(type(self).__name__, self.x, self.y)
    __repr__ = __str__

class PCBObjectVec3(PCBObject):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        if key == 2:
            return self.z

    def __str__(self):
        return "{}({}, {}, {})".format(type(self).__name__, self.x, self.y, self.z)
    __repr__ = __str__

class Offset(PCBObjectVec):
    @staticmethod
    def from_tokens(tokens):
        return Offset(tokens[0], tokens[1])

    def generate(self):
        return "(offset {} {})".format(self.pos[0], self.pos[1])

class Pos(PCBObjectVec):
    @staticmethod
    def from_tokens(tokens):
        return Pos(tokens[0], tokens[1])

    def generate(self):
        return "(at {} {})".format(self.x, self.y)

    def gen_start(self):
        return "(start {} {})".format(self.x, self.y)

    def gen_end(self):
        return "(end {} {})".format(self.x, self.y)

class Vec3(PCBObjectVec3):
    @staticmethod
    def from_tokens(tokens):
        return Vec3(tokens[0], tokens[1], tokens[2])

    def generate(self):
        return "(xyz {} {} {})".format(self.x, self.y, self.z)

    def gen_pos(self):
        return "(at {})".format(self.generate())

    def gen_scale(self):
        return "(scale {})".format(self.generate())

    def gen_rotate(self):
        return "(rotate {})".format(self.generate())

class Size(PCBObjectVec):
    @staticmethod
    def from_tokens(tokens):
        return Size(tokens[0], tokens[1])

    def generate(self):
        return "(size {} {})".format(self.x, self.y)

class RectDelta(PCBObject):
    def __init__(self, x, y):
        self.delta = [x, y]

    def generate(self):
        return "(rect_delta {} {})".format(self.delta[0], self.delta[1])

class Pad(PCBObject):
    def __init__(self):
        self.pin_number = None
        self.kind = None
        self.shape = None
        self.net = None
        self.pos = None
        self.size = None
        self.drill = None
        self.layers = None
        self.rect_delta = None

    @staticmethod
    def from_tokens(tokens):
        result = Pad()
        result.pin_number = tokens.pin_number
        result.kind = tokens.kind
        result.shape = tokens.shape
        if tokens.at:
            result.pos = tokens.at[0]
        else:
            result.pos = Pos()
        if tokens.size:
            result.size = tokens.size[0]
        if tokens.drill:
            result.drill = tokens.drill
        if tokens.layers:
            result.layers = tokens.layers
        if tokens.net:
            result.net = tokens.net
        return result

    def generate(self, indent_depth=0):
        indent_str = gen_indent(indent_depth)
        result = indent_str + "(pad {net} {kind} {shape} {pos}".format(
            net = self.pin_number,
            kind = self.kind,
            shape = self.shape,
            pos = self.pos.generate(),
        )
        if self.size:
            result += " " + self.size.generate()
        if self.layers:
            result += " " + "(layers {})".format(" ".join(self.layers))
        if self.rect_delta:
            result += " " + self.rect_delta.generate()
        if self.drill:
            result += " " + self.drill.generate()
        if self.net:
            result += " " + self.net.generate()
        result += ")"
        return result

    def __str__(self):
        return "Pad({}, {}, {}, {}, {}, {})".format(
            self.pin_number,
            self.kind,
            self.shape,
            self.pos,
            self.size,
            self.layers,
        )

if __name__ == "__main__":
    mod = None
    with open("test.pretty/R_0805.kicad_mod") as mod_file:
        mod = Module.from_str(mod_file.read())
    # print(mod.component, type(mod), mod.pos.x, mod.pos.y, type(mod.pos))
    # print(mod.description, mod.tags, mod.attr)
    # print(mod.objects)
    # for obj in mod.objects:
    #     print(obj)


    from copy import copy

    newPCB = PCBDocument()
    mod.pos = Pos(30.0, 30.0)
    newPCB += copy(mod)
    mod.pos = Pos(100.0, 100.0)
    newPCB += mod
    with open("test_pcb.kicad_pcb", "w") as out_file:
        out_file.write(newPCB.generate())
