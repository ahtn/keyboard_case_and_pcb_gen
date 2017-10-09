#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 jem@seethis.link
# Licensed under the MIT license (http://opensource.org/licenses/MIT)

from __future__ import absolute_import, division, print_function, unicode_literals

from pyparsing import *

import pcb_obj

# Main identifier and keyword types
Identifier = Word(alphas + '_')

Integer = Optional(Literal('-')) + Word(nums)
Integer.addParseAction(lambda toks: int("".join(toks)))

UnsignedInt = Word(nums)
UnsignedInt.addParseAction(lambda toks: int(toks[0]))
Float = Optional(Literal('-')) + Word(nums) + Optional(Literal('.') + Optional(Word(nums)))
Float.addParseAction(lambda toks: float("".join(toks)))
HexString = Word(hexnums)
HexString.addParseAction(lambda toks: int(toks[0],base=16))

UnquotedString = ZeroOrMore(White()).suppress() + CharsNotIn("()\"\'" + " \r\n")
UnquotedString.addParseAction(lambda toks: "".join(toks).strip())

QuotedString = Group(dblQuotedString() ^ sglQuotedString())
QuotedString.addParseAction(lambda toks: "".join(toks[0]).strip('"'))

Anystring = QuotedString ^ UnquotedString
LeftParen = Literal('(').suppress()
RightParen = Literal(')').suppress()

BoolTrue = Keyword("yes", caseless=True) | Keyword("true", caseless=True)
BoolTrue.addParseAction(lambda : True)
BoolFalse = Keyword("no", caseless=True) | Keyword("false", caseless=True)
BoolFalse.addParseAction(lambda : False)
Boolean = BoolTrue | BoolFalse

def _paren_stmt(keyword, *values, store=True):
    """
    Create a parser for a parenthesized list with an initial keyword.
    """
    # result  = LeftParen + Keyword(keyword, caseless=True).suppress()
    result  = LeftParen + Keyword(keyword, caseless=True).suppress()
    for value in values:
        result += value
    result += RightParen
    if store:
        return result(keyword)
    else:
        return result

def _paren_data(*values):
    result = LeftParen
    for value in values:
        result += value
    result += RightParen
    return result

def _float_param(keyword):
    return _paren_stmt(keyword, Float())
def _uint_param(keyword):
    return _paren_stmt(keyword, UnsignedInt())
def _int_param(keyword):
    return _paren_stmt(keyword, Integer())
def _hex_param(keyword):
    return _paren_stmt(keyword, HexString())
def _str_param(keyword):
    return _paren_stmt(keyword, Anystring())
def _vec2_param(keyword, store=False):
    return _paren_stmt(keyword, Float(), Float(), store=store)
def _bool_param(keyword):
    return _paren_stmt(keyword, Boolean())

def OptionalList(*values):
    value_iter = iter(values)
    result = Optional(next(value_iter))
    for val in value_iter:
        result &= Optional(val)
    return result


# start = _paren_stmt("start", ("x",Fnum), ())
TEdit = _hex_param("tedit")
TStamp = _hex_param("tstamp")
# Point like
At = _vec2_param("at")
At.addParseAction(pcb_obj.Pos.from_tokens)
At = Group(At)("at")

Start = _vec2_param("start", store=False)
Start.addParseAction(pcb_obj.Pos.from_tokens)
Start = Group(Start)("start")

End = _vec2_param("end", store=False)
End.addParseAction(pcb_obj.Pos.from_tokens)
End = Group(End)("end")

Offset =  _vec2_param("offset", store=False)
Offset.addParseAction(pcb_obj.Offset.from_tokens)
Offset = Group(Offset)("offset")

Size = _vec2_param("size", store=False)
Size.addParseAction(pcb_obj.Size.from_tokens)
Size = Group(Size)("size")

Size1D = _paren_stmt("size", Float())
Size1D.addParseAction(lambda tokens: pcb_obj.Size.from_tokens(list(tokens) + [0.0]))
#
Layer = _str_param("layer")
Width = _float_param("width")
Descr = _str_param("descr")
Tags = _str_param("tags")
Attr = _str_param("attr")

# Drill = _paren_stmt("drill",
#     Group(Keyword("oval", caseless=True) + Float("x") + Float()) |
#     Group(Float("r")),
#     Optional(Offset)
# )
Drill = _paren_stmt("drill", Float("r"))

Solder_Mask_Margin = _float_param("solder_mask_margin")
Solder_Paste_Margin = _float_param("solder_paste_margin")
Solder_Paste_Margin_Ratio = _float_param("solder_paste_margin_ratio")
Clearance = _float_param("clearance")
Trace_Width = _float_param("trace_width")
Via_Dia = _float_param("via_dia")
Via_Drill = _float_param("via_drill")
UVia_Dia = _float_param("uvia_dia")
UVia_Drill = _float_param("uvia_drill")
Thickness = _float_param("thickness")

Add_Net = _str_param("add_net")
Net = _paren_stmt("net", UnsignedInt("net_num"), Anystring("net_name"))("net")
Net_Class = _paren_stmt("net_class", Anystring("name") + Anystring("description"),
    Optional(Clearance) & Optional(Trace_Width) &
    Optional(Via_Dia) & Optional(Via_Drill) &
    Optional(UVia_Dia) & Optional(UVia_Drill),
    ZeroOrMore(Add_Net)
)("net_class")

Page = _str_param("page")
LinkCount = _uint_param("links")
NoConnectCount = _uint_param("no_connects")
Area = _paren_stmt("area", Float("x0"), Float("y0"), Float("x1"), Float("y1"))
DrawingCount = _uint_param("drawings")
TrackCount = _uint_param("tracks")
ZoneCount = _uint_param("zones")
ModuleCount = _uint_param("modules")
NetCount = _uint_param("nets")
GeneralSettings = _paren_stmt("general",
    OptionalList(LinkCount, NoConnectCount, Area, DrawingCount, TrackCount,
        ZoneCount, ModuleCount, NetCount, Thickness
    )
)

Last_Trace_Width = _float_param("last_trace_width")
Trace_Clearance = _float_param("trace_clearance")
Zone_Clearance = _float_param("zone_clearance")
Zone_45_Only = _bool_param("zone_45_only")
Trace_Min = _float_param("trace_min")
Segment_Width = _float_param("segment_width")
Edge_Width = _float_param("edge_width")
PCB_Text_Width = _float_param("pcb_text_width")
PCB_Text_Size = _vec2_param("pcb_text_size")
Mod_Edge_Width = _float_param("mod_edge_width")
Mod_Text_Size = _vec2_param("mod_text_size")
Mod_Text_Width = _float_param("mod_text_width")
Pad_Size = _vec2_param("pad_size")
Pad_Drill = _float_param("pad_drill")
Pad_To_Mask_Clearance = _float_param("pad_to_mask_clearance")
Aux_Axis_Origin = _vec2_param("aux_axis_origin")
Visible_Elements = _hex_param("visible_elements")
Via_Size = _float_param("via_size")
Via_Min_Size = _float_param("via_min_size")
Via_Min_Drill = _float_param("via_min_drill")

UVias_Allowed = _bool_param("uvias_allowed")
UVia_Size = _float_param("uvia_size")
UVia_Min_Size = _float_param("uvia_min_size")
UVia_Min_Drill = _float_param("uvia_min_drill")

# PCB Plot Params
LayerSelection = _uint_param("layerselection")
UseGerberExtensions = _bool_param("usegerberextensions")
ExcludeEdgeLayer = _bool_param("excludeedgelayer")
LineWidth = _float_param("linewidth")
PlotFrameref = _bool_param("plotframeref")
ViasOnMask = _bool_param("viasonmask")
Mode = _uint_param("mode")
UseAuxOrigin = _bool_param("useauxorigin")
HpglPenNumber = _float_param("hpglpennumber")
HpglPenSpeed = _float_param("hpglpenspeed")
HpglPenDiameter = _float_param("hpglpendiameter")
HpglPenOverlay = _float_param("hpglpenoverlay")
PsNegative = _bool_param("psnegative")
Psa4Output = _bool_param("psa4output")
PlotReference = _bool_param("plotreference")
PlotValue = _bool_param("plotvalue")
PlotOtherText = _bool_param("plotothertext")
PlotInvisibleText = _bool_param("plotinvisibletext")
PadsOnSilk = _bool_param("padsonsilk")
SubtractMaskFromSilk = _bool_param("subtractmaskfromsilk")
OutputFormat = _uint_param("outputformat")
Mirror = _bool_param("mirror")
DrillShape = _uint_param("drillshape")
ScaleSelection = _uint_param("scaleselection")
OutputDirectory = _str_param("outputdirectory")
PCBPlotParams = _paren_stmt("pcbplotparams", OptionalList(
    LayerSelection, UseGerberExtensions, ExcludeEdgeLayer, LineWidth,
    PlotReference, ViasOnMask, Mode, UseAuxOrigin,
    HpglPenOverlay, HpglPenNumber, HpglPenDiameter, HpglPenSpeed,
    PsNegative, Psa4Output,
    PlotReference, PlotValue, PlotOtherText, PlotInvisibleText, PlotFrameref,
    PadsOnSilk, SubtractMaskFromSilk,
    OutputFormat, Mirror, DrillShape, ScaleSelection,
    OutputDirectory
))

Setup = _paren_stmt("setup", OptionalList(
    Last_Trace_Width, Trace_Clearance, Zone_Clearance, Zone_45_Only,
    Trace_Min, Segment_Width, Edge_Width,
    PCB_Text_Width, PCB_Text_Size,
    Mod_Edge_Width, Mod_Text_Size, Mod_Text_Width,
    Pad_Size, Pad_Drill, Pad_To_Mask_Clearance,
    Aux_Axis_Origin, Visible_Elements,
    Via_Dia, Via_Drill, Via_Size, Via_Min_Size, Via_Min_Drill,
    UVia_Dia, UVia_Drill, UVias_Allowed, UVia_Size, UVia_Min_Size, UVia_Min_Drill,
    PCBPlotParams
))

Layers = _paren_stmt("layers", OneOrMore(Anystring))
LayerDefinition = _paren_data(UnsignedInt("number") + Anystring("name") + Identifier("kind"))
LayerList = _paren_stmt("layers", ZeroOrMore(LayerDefinition))

# Text
Font = _paren_stmt("font", OptionalList(Size, Thickness, Identifier("italic")))
Font.addParseAction(pcb_obj.Font.from_tokens)
Effects = _paren_stmt("effects", Font)
Effects.addParseAction(pcb_obj.Effects.from_tokens)
FP_Text = _paren_stmt("fp_text", Identifier("kind"), Anystring("text"),
                        OptionalList(At, Layer, Effects, Identifier("hide"))("parameters")
                      )("fp_text")
FP_Text.addParseAction(pcb_obj.FP_Text.from_tokens)

FP_Line = _paren_stmt("fp_line", Start, End, Layer, Width)
FP_Line.addParseAction(pcb_obj.FP_Line.from_tokens)
# Pad related
Pad = _paren_stmt("pad", UnsignedInt("pin_number") + Identifier("kind") + Identifier("shape"),
                    OptionalList(At, Size, Drill, Layers, Net, Solder_Mask_Margin,
                    Solder_Paste_Margin, Solder_Paste_Margin_Ratio)
)
Pad.addParseAction(pcb_obj.Pad.from_tokens)
# Arc and Circles
Center = _paren_stmt("center", Float(), Float())
Angle = _paren_stmt("angle", Float())
GR_Circle = _paren_stmt("gr_circle", Center, End, Layer & Width)
GR_Arc = _paren_stmt("gr_arc", Start, End, Angle, Layer & Width)

At3D = _paren_stmt("at", _paren_stmt("xyz", Float(), Float(), Float(), store=False), store=False)
At3D.addParseAction(pcb_obj.Vec3.from_tokens)
At3D = Group(At3D)("at")

Scale3D = _paren_stmt("scale", _paren_stmt("xyz", Float(), Float(), Float()))
Scale3D.addParseAction(pcb_obj.Vec3.from_tokens)
Scale3D = Group(Scale3D)("scale")

Rotate3D = _paren_stmt("rotate", _paren_stmt("xyz", Float(), Float(), Float()))
Rotate3D.addParseAction(pcb_obj.Vec3.from_tokens)
Rotate3D = Group(Rotate3D)("rotate")

Model = _paren_stmt("model", Anystring("path"), OptionalList(At3D, Scale3D , Rotate3D))("model")
Model.addParseAction(pcb_obj.Model.from_tokens)

# Module = (LeftParen + Keyword("module") + Anystring("component") + CharsNotIn(""))("module")

Module = _paren_stmt("module", Anystring("component"),
    ZeroOrMore(Layer | FP_Text | TEdit | TStamp | At | Descr | Tags |
               Attr | FP_Line | Pad | Model)
)("module")
Module.addParseAction(pcb_obj.Module.from_tokens)

NetNumber = _paren_stmt("net", UnsignedInt())("net_num")
Via = _paren_stmt("via", OptionalList(At, Size1D, Drill, Layers, NetNumber))
Segment = _paren_stmt("segment",
    OptionalList(Start, End, Width, Layer, NetNumber, TStamp)
)

PCBElement = GR_Circle | GR_Arc | Module | Via | Segment | Net | Net_Class | \
    Page | LayerList | GeneralSettings | Setup
PCBElements = ZeroOrMore(PCBElement)

Version = _uint_param("version")
Host = _paren_stmt("host", Anystring("name"), Anystring("version"))
KiCAD_PCB = _paren_stmt("kicad_pcb", Version, Host, PCBElements)

if __name__ == "__main__":
    result = Start.parseString("(start 123.456 789)")
    print(result)
    print(result.x, result.y)
    result = FP_Line.parseString("(fp_line (start 1 1) (end 1 2) (layer F.Cu) (width 0.1))")
    print(result)
    print(result.start, result.end, result.layer, result.width)

    test_str = """(pad 1 thru_hole rect (at -0.95 0) (size 0.7 1.3) (drill 0.3) (layers *.Cu *.Mask) (net 2 VO))"""
    result = Pad.parseString(test_str)
    print(result)

    test_str = """(via (at 150.7 106.1) (size 0.6) (drill 0.4) (layers F.Cu B.Cu) (net 3))"""
    result = Via.parseString(test_str)
    print(result)

    test_str = """
  (net_class Default "This is the default net class."
    (clearance 0.2)
    (trace_width 0.25)
    (via_dia 0.6)
    (via_drill 0.4)
    (uvia_dia 0.3)
    (uvia_drill 0.1)
    (add_net GND)
    (add_net VI)
    (add_net VO)
  )
"""
    print("### Parsing Net_Class ###")
    result = Net_Class.parseString(test_str)
    print(result)

    test_str = """
  (general
    (links 3)
    (no_connects 2)
    (area 145.499999 98.399999 165 106.900002)
    (thickness 1.6)
    (drawings 2)
    (tracks 20)
    (zones 0)
    (modules 4)
    (nets 4)
  )
"""
    print("### Parsing GeneralSettings ###")
    result = GeneralSettings.parseString(test_str)
    print(result)



    test_str = """\
(kicad_pcb (version 4) (host pcbnew 4.0.7)
  (general
    (links 3)
    (no_connects 2)
    (area 145.499999 98.399999 165 106.900002)
    (thickness 1.6)
    (drawings 2)
    (tracks 20)
    (zones 0)
    (modules 4)
    (nets 4)
  )

    (setup
        (last_trace_width 0.254)
        (trace_clearance 0.254)
        (zone_clearance 0.2)
        (zone_45_only no)
        (trace_min 0.254)
        (segment_width 0.2)
        (edge_width 0.15)
        (via_size 0.889)
        (via_drill 0.635)
        (via_min_size 0.889)
        (via_min_drill 0.508)
        (uvia_size 0.508)
        (uvia_drill 0.127)
        (uvias_allowed no)
        (uvia_min_size 0.508)
        (uvia_min_drill 0.127)
        (pcb_text_width 0.3)
        (pcb_text_size 1.5 1.5)
        (mod_edge_width 0.15)
        (mod_text_size 1.5 1.5)
        (mod_text_width 0.15)
        (pad_size 0.0005 0.0005)
        (pad_drill 0)
        (pad_to_mask_clearance 0.2)
        (aux_axis_origin 0 0)
        (visible_elements 7FFFFFFF)
        (pcbplotparams
            (layerselection 3178497)
            (usegerberextensions true)
            (excludeedgelayer true)
            (linewidth 50000)
            (plotframeref false)
            (viasonmask false)
            (mode 1)
            (useauxorigin false)
            (hpglpennumber 1)
            (hpglpenspeed 20)
            (hpglpendiameter 15)
            (hpglpenoverlay 2)
            (psnegative false)
            (psa4output false)
            (plotreference true)
            (plotvalue true)
            (plotothertext true)
            (plotinvisibletext false)
            (padsonsilk false)
            (subtractmaskfromsilk false)
            (outputformat 1)
            (mirror false)
            (drillshape 1)
            (scaleselection 1)
            (outputdirectory "")
        )
    )

  (page A4)
  (layers
    (0 F.Cu signal)
    (31 B.Cu signal)
    (32 B.Adhes user)
    (33 F.Adhes user)
    (34 B.Paste user)
    (35 F.Paste user)
    (36 B.SilkS user)
    (37 F.SilkS user)
    (38 B.Mask user)
    (39 F.Mask user)
    (40 Dwgs.User user)
    (41 Cmts.User user)
    (42 Eco1.User user)
    (43 Eco2.User user)
    (44 Edge.Cuts user)
    (45 Margin user)
    (46 B.CrtYd user)
    (47 F.CrtYd user)
    (48 B.Fab user)
    (49 F.Fab user)
  )



    (net 0 "")
    (net 1 VI)
    (net 2 VO)
    (net 3 GND)

    (gr_circle (center 152.525 97.075) (end 153.175 96.525) (layer F.SilkS) (width 0.2))
    (gr_arc (start 154.925 97.7) (end 156 97.05) (angle 90) (layer F.SilkS) (width 0.2))

  (via (at 150.7 106.1) (size 0.6) (drill 0.4) (layers F.Cu B.Cu) (net 3))
  (segment (start 151.775001 105.024999) (end 150.7 106.1) (width 0.25) (layer F.Cu) (net 3) (tstamp 59D9A063))
  (segment (start 151.775001 102.075) (end 151.775001 105.024999) (width 0.25) (layer F.Cu) (net 3))
  (segment (start 151.775001 99.224999) (end 151.775001 102.075) (width 0.25) (layer F.Cu) (net 3) (tstamp 59D9C17F))
  (segment (start 151.8 99.2) (end 151.775001 99.224999) (width 0.25) (layer F.Cu) (net 3) (tstamp 59D9C17E))
  (via (at 151.8 99.2) (size 0.6) (drill 0.4) (layers F.Cu B.Cu) (net 3))
  (segment (start 151.8 103.4) (end 151.8 99.2) (width 0.25) (layer B.Cu) (net 3) (tstamp 59D9C16E))

  (module Resistors_SMD:R_0805 (layer F.Cu) (tedit 59D9D2FE) (tstamp 59D9D11A)
    (at 155.225001 101.675)
    (descr "Resistor SMD 0805, reflow soldering, Vishay (see dcrcw.pdf)")
    (tags "resistor 0805")
    (attr smd)
    (pad 1 thru_hole rect (at -0.95 0) (size 0.7 1.3) (drill 0.3) (layers *.Cu *.Mask)
      (net 2 VO))
    (model ${KISYS3DMOD}/Resistors_SMD.3dshapes/R_0805.wrl
      (at (xyz 0 0 0))
      (scale (xyz 1 1 1))
      (rotate (xyz 0 0 0))
    )
  )

    (module R_0805 (layer F.Cu) (tedit 58E0A804)
    (descr "Resistor SMD 0805, reflow soldering, Vishay (see dcrcw.pdf)")
    (tags "resistor 0805")
    (attr smd)
    (fp_text reference REF** (at 0 -1.65) (layer F.SilkS)
        (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value R_0805 (at 0 1.75) (layer F.Fab)
        (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text user %R (at 0 0) (layer F.Fab)
        (effects (font (size 0.5 0.5) (thickness 0.075)))
    )
    (fp_line (start -1 0.62) (end -1 -0.62) (layer F.Fab) (width 0.1))
    (fp_line (start 1 0.62) (end -1 0.62) (layer F.Fab) (width 0.1))
    (fp_line (start 1 -0.62) (end 1 0.62) (layer F.Fab) (width 0.1))
    (fp_line (start -1 -0.62) (end 1 -0.62) (layer F.Fab) (width 0.1))
    (fp_line (start 0.6 0.88) (end -0.6 0.88) (layer F.SilkS) (width 0.12))
    (fp_line (start -0.6 -0.88) (end 0.6 -0.88) (layer F.SilkS) (width 0.12))
    (fp_line (start -1.55 -0.9) (end 1.55 -0.9) (layer F.CrtYd) (width 0.05))
    (fp_line (start -1.55 -0.9) (end -1.55 0.9) (layer F.CrtYd) (width 0.05))
    (fp_line (start 1.55 0.9) (end 1.55 -0.9) (layer F.CrtYd) (width 0.05))
    (fp_line (start 1.55 0.9) (end -1.55 0.9) (layer F.CrtYd) (width 0.05))
    (pad 1 smd rect (at -0.95 0) (size 0.7 1.3) (layers F.Cu F.Paste F.Mask))
    (pad 2 smd rect (at 0.95 0) (size 0.7 1.3) (layers F.Cu F.Paste F.Mask))
    (model ${KISYS3DMOD}/Resistors_SMD.3dshapes/R_0805.wrl
        (at (xyz 0 0 0))
        (scale (xyz 1 1 1))
        (rotate (xyz 0 0 0))
    )
    )

)
"""
    print("### Parsing KiCAD_PCB ###")
    result = KiCAD_PCB.parseString(test_str)
    print(result)
    print(result.setup.via_size.value)
    # print(result.model)
