#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pyparsing as pp


class DirectiveParserError(Exception):
    pass

class DirectiveArgError(Exception):
    def __init__(self, name, num_need, num_has):
        self.name = name
        self.num_need = num_need
        self.num_has = num_has

    def __str__(self):
        return "Expected {} positional arg(s) but got {} for '{}'".format(
            self.num_need, self.num_has, self.name
        )

class DirectiveTypeError(Exception):
    def __init__(self, directive_name):
        self.directive_name = directive_name

    def __str__(self):
        return "Unknown directive '{}'".format(
            self.directive_name
        )


class Directive(object):
    @staticmethod
    def check_args(obj_class, args):
        if len(args.positional) != obj_class.NUM_POS_ARGS:
            raise DirectiveArgError(
                obj_class.KEYWORD,
                obj_class.NUM_POS_ARGS,
                len(args.positional)
            )

    def get_offset(self):
        return (self.x, self.y)

class HexDirective(Directive):
    KEYWORD = 'hex'
    NUM_POS_ARGS = 1

    def __init__(self, size, x=0, y=0, z=0, h=None, r=0, top=True, pcb=True, bot=True):
        assert(size > 0)
        self.size = size
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.h = h
        self.top = top
        self.bot = bot
        self.pcb = pcb

    @staticmethod
    def from_args(args):
        Directive.check_args(HexDirective, args)
        return HexDirective(args.positional[0], **args.keyword)

    def __str__(self):
        return "HexDirective(size={}, x={}, y={}, z={}, r={})".format(self.size, self.x, self.y, self.z, self.r)
    __repr__ = __str__

class RectDirective(Directive):
    KEYWORD = 'rect'
    NUM_POS_ARGS = 2

    def __init__(self, l, w, h=None, x=0, y=0, z=0, r=0, top=True, pcb=True, bot=True):
        assert(w > 0 and l > 0 and (h==None or h>0))
        self.w = w
        self.l = l
        self.h = h
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.h = h
        self.top = top
        self.bot = bot
        self.pcb = pcb

    @staticmethod
    def from_args(args):
        Directive.check_args(RectDirective, args)
        return RectDirective(args.positional[0], args.positional[1], **args.keyword)

    def __str__(self):
        return "RectDirective(w={}, l={}, h={}, x={}, y={}, z={}, r={})".format(
            self.w, self.l, self.h,
            self.x, self.y, self.z,
            self.r
        )
    __repr__ = __str__

class ScrewDirective(Directive):
    KEYWORD = 'screw'
    NUM_POS_ARGS = 1

    """
    ScrewSize   Tap     Clearance
    M1 	        0.75 	1.2
    M1.2 	    0.95 	1.4
    M1.4 	    1.1 	1.6
    M1.6 	    1.5 	1.8
    M1.8 	    1.4 	2
    M2 	        1.6 	2.4
    M2.2 	    1.7 	2.8
    M2.5 	    2 	    2.9
    M3 	        2.5 	3.4
    M3.5 	    2.9 	3.9
    M4 	        3.3 	4.5
    M5 	        4.2 	5.5
    M6 	        5 	    6.6
    """

    # lower case -> for tapping
    # upper case -> for clearance
    SCREW_LOOKUP = {
        "m1"   : 0.75,
        "m1.2" : 0.95,
        "m1.4" : 1.1,
        "m1.6" : 1.5,
        "m1.8" : 1.4,
        "m2"   : 1.6,
        "m2.2" : 1.7,
        "m2.5" : 2,
        "m3"   : 2.5,
        "m3.5" : 2.9,
        "m4"   : 3.3,
        "m5"   : 4.2,
        "m6"   : 5,
        "M1"   : 1.2,
        "M1.2" : 1.4,
        "M1.4" : 1.6,
        "M1.6" : 1.8,
        "M1.8" : 2,
        "M2"   : 2.4,
        "M2.2" : 2.8,
        "M2.5" : 2.9,
        "M3"   : 3.4,
        "M3.5" : 3.9,
        "M4"   : 4.5,
        "M5"   : 5.5,
        "M6"   : 6.6,
    }

    def __init__(self, size, x=0, y=0, top=True, pcb=True, bot=True):
        if type(size) == str:
            if not size in self.SCREW_LOOKUP:
                raise DirectiveParserError("Unknown screw size '{}'".format(size))
            self.size = self.SCREW_LOOKUP[size]
        else:
            assert(size > 0)
            self.size = size
        self.x = x
        self.y = y
        self.top = top
        self.bot = bot
        self.pcb = pcb

    @staticmethod
    def from_args(args):
        Directive.check_args(ScrewDirective, args)
        return ScrewDirective(args.positional[0], **args.keyword)

    def __str__(self):
        return "ScrewDirective(radius={}, x={}, y={})".format(self.size, self.x, self.y)
    __repr__ = __str__

class USBCDirective(Directive):
    KEYWORD = 'usb_c'
    NUM_POS_ARGS = 0

    def __init__(self, x=0, y=0, z=0, r=0, top=True, pcb=True, bot=True, flip=False):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.top = top
        self.bot = bot
        self.pcb = pcb
        self.flip = flip

    @staticmethod
    def from_args(args):
        Directive.check_args(USBCDirective, args)
        return USBCDirective(**args.keyword)

    def __str__(self):
        return "USBCDirective(x={}, y={}, z={}, r={}, flip={})".format(
            self.x, self.y, self.z, self.r, self.flip)
    __repr__ = __str__


directiveLookupTable = {
    'hex': HexDirective,
    'screw': ScrewDirective,
    'usb_c': USBCDirective,
    'rect': RectDirective,
}

class DirectiveArgs(object):
    def __init__(self, toks):
        split_pos = 0
        for tok in toks:
            if type(tok) == pp.ParseResults:
                break;
            split_pos += 1
        self.positional = toks[:split_pos]

        self.keyword = {}
        keyword_list = toks[split_pos:]

        for entry in keyword_list:
            key, value = entry[0], entry[1]
            self.keyword[key] = value


    def __str__(self):
        return "Positional({}), Keyword({})".format(self.positional, self.keyword)

    def __repr__(self):
        return "DirectiveArgs({})".format(self.__str__())

class DirectiveParser(object):
    def __init__(self):
        # directive grammar

        lparen = pp.Literal('(').suppress()
        rparen = pp.Literal(')').suppress()
        comma = pp.Literal(',').suppress()
        semicolon = pp.Literal(';').suppress()
        equalTok = pp.Literal('=').suppress()

        self.floatTok = pp.Optional((pp.Literal('-'))|pp.Literal('+')) + pp.Word(pp.nums) + pp.Optional(pp.Literal('.') + pp.Optional(pp.Word(pp.nums)))
        self.floatTok.addParseAction(lambda toks: float("".join(toks)))

        self.stringTok = pp.Group(pp.dblQuotedString() ^ pp.sglQuotedString())
        self.stringTok.addParseAction(lambda toks: "".join(toks[0]).strip('"').strip("'"))

        self.trueTok = pp.Keyword("true")
        self.trueTok.addParseAction(lambda _: True)

        self.falseTok = pp.Keyword("false")
        self.falseTok.addParseAction(lambda _: False)

        self.boolTok = self.trueTok | self.falseTok

        self.identifierTok = pp.Word(pp.alphas + '_', pp.alphanums + '_')('identifier')

        self.positionalArgTok = self.floatTok | self.stringTok | self.boolTok
        self.keywordArgTok = pp.Group(self.identifierTok + equalTok + self.positionalArgTok)
        self.keywordArgTok.addParseAction(lambda toks: [x for x in toks])

        self.argsTok = pp.Optional(
            (self.positionalArgTok + pp.ZeroOrMore(comma + self.positionalArgTok) + pp.ZeroOrMore(comma + self.keywordArgTok)) |
            (self.keywordArgTok + pp.ZeroOrMore(comma + self.keywordArgTok))
        )('args')
        # self.argsTok.addParseAction(lambda toks: [toks])
        self.argsTok.addParseAction(lambda toks: DirectiveArgs(toks))

        self.directiveTok = pp.Group(self.identifierTok + lparen + self.argsTok + rparen)
        self.mainTok = self.directiveTok + pp.ZeroOrMore(semicolon + self.directiveTok) + pp.Optional(semicolon)

    def parse_str(self, input):
        try:
            directives = self.mainTok.parseString(input, parseAll=True)
            result = []
            for directive in directives:
                if directive.identifier in directiveLookupTable:
                    dirClass = directiveLookupTable[directive.identifier]
                    result.append(dirClass.from_args(directive.args))
                else:
                    raise DirectiveTypeError(directive.identifier)
            return result
        except pp.ParseException as err:
            raise err

if __name__ == '__main__':
    dparser = DirectiveParser()

    in_str = "hex(5.0, x=10.0, y=10.0); screw(5.0, x=10.0, y=10.0)"
    try:
        result = dparser.parse_str(in_str)
    except DirectiveTypeError as err:
        print(err)
        exit(1)
    except pp.ParseException as err:
        print(err.line)
        print(" "*(err.col-1) + "^~~~~")
        # print(in_str.split("\n"))
        print(err)
        exit(1)

    for i in result:
        print(i)
