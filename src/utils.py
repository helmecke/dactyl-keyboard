#! /usr/bin/env python
# -*- coding: utf-8 -*-

# uses https://github.com/SolidCode/SolidPython
# Assumes SolidPython is in site-packages or elsewhwere in sys.path
from solid import *
from solid.utils import *


def partition(n, step, coll):
    for i in range(0, len(coll), step):
        if (i + n > len(coll)):
            break
        yield coll[i:i + n]


def triangle_hulls(shapes):
    p = partition(3, 1, shapes)
    h = []
    for i in p:
        h.append(hull()(i))

    return union()(h)


def prism(width, length, height, taper_width, taper_length):
    return polyhedron(
        [
            [0, 0, 0],
            [taper_width, taper_width, height],
            [width - taper_width, taper_width, height],
            [width, 0, 0],
            [0, length, 0],
            [taper_width, length - taper_length, height],
            [width - taper_width, length - taper_length, height],
            [width, length, 0]
        ],
        [
            [0, 1, 2],
            [2, 3, 0],
            [3, 2, 6],
            [6, 7, 3],
            [7, 6, 5],
            [5, 4, 7],
            [4, 5, 1],
            [1, 0, 4],
            [1, 5, 2],
            [2, 5, 6],
            [4, 0, 3],
            [7, 4, 3]
        ]
    )
