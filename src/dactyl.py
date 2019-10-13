#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from math import sin, pi

# uses https://github.com/SolidCode/SolidPython
# Assumes SolidPython is in site-packages or elsewhwere in sys.path
from solid import *
from solid.utils import *

SEGMENTS = 58

keyswitch_width = 14.4
keyswitch_height = 14.4
mount_width = keyswitch_width + 3
mount_height = keyswitch_height + 3
plate_thickness = 4
key_cap_profile_height = 12.7
key_cap_profile_height = 8.4
key_cap_double_length = 37.5
columns = 6
rows = 5
alpha = pi / 12
beta = pi / 36
cap_top_height = plate_thickness + key_cap_profile_height


def plate(size=1, align='horizontal'):
    if size == 2:
        width = key_cap_double_length - 3
    else:
        width = keyswitch_width

    outer_wall = cube([width + 3, keyswitch_height + 3, plate_thickness], center=True)

    if align == 'vertical':
        outer_wall = rotate(90, [0, 0, 1])(outer_wall)

    inner_wall = cube([keyswitch_width, keyswitch_height, plate_thickness + 0.1], center=True)
    wall = difference()(outer_wall - inner_wall)

    nibble = hull()(
        translate([keyswitch_width / 2 + 1.5 / 2, 0, 0])(
            cube([1.5, 2.75, plate_thickness], center=True)
        ),
        translate([keyswitch_width / 2, 2.75 / 2, -1])(
            rotate(90, [1, 0, 0])(
                cylinder(r=1, h=2.75)
            )
        )
    )

    return wall + nibble + mirror([1, 0, 0])(nibble)


def offset(column, row):
    if column == 2:
        offset = [0, 2.82, -3.0]
    elif column == 4:
        offset = [0, -5.8, 5.64]
    elif column == 5 and row != 4:
        offset = [5, -5.8, 7.01]
    elif column == 5 and row == 4:
        offset = [0.5, -5.8, 5.7]
    else:
        offset = [0, 0, 0]

    return offset


def key_place(column, row, shape):
    row_radius = (mount_height + 0.5) / sin(alpha) + cap_top_height
    column_radius = (mount_width + 2) / sin(beta) + cap_top_height
    column_angle = 5 * (2 - column)

    placed_shape = translate(offset(column, row))(
        translate([0, 0, column_radius])(
            rotate(column_angle, [0, 1, 0])(
                translate([0, 0, -column_radius])(
                    translate([0, 0, row_radius])(
                        rotate(15 * (2 - row), [1, 0, 0])(
                            translate([0, 0, -row_radius])(
                                shape
                            )
                        )
                    )
                )
            )
        )
    )

    return translate([0, 0, 13])(
        rotate(15, [0, 1, 0])(
            placed_shape
        )
    )


def key_layout(shape):
    a = []
    for row in range(rows):
        for column in range(columns):
            if column == 5 and row != 4:
                a.append(key_place(column, row, shape(1.5)))
            elif column not in range(1) or not row == 4:
                a.append(key_place(column, row, shape()))

    return union()(a)


def thumb_place(column, row, shape):
    row_radius = (mount_height + 1) / sin(alpha) + cap_top_height
    column_radius = (mount_width + 2) / sin(beta) + cap_top_height

    a = translate([-52, -45, 40])(
        rotate(15, [1, 1, 0])(
            rotate(11.25, [0, 0, 1])(
                translate([mount_width, 0, 0])(
                    translate([0, 0, column_radius])(
                        rotate(5 * column, [0, 1, 0])(
                            translate([0, 0, -column_radius])(
                                translate([0, 0, row_radius])(
                                    rotate(15 * row, [1, 0, 0])(
                                        translate([0, 0, -row_radius])(
                                            shape
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )

    return a


def thumb_2x_column(shape):
    return thumb_place(0, -1 / 2, shape(2, 'vertical'))


def thumb_2x_1_column(shape):
    return union()(
        thumb_place(1, -1 / 2, shape(2, 'vertical')),
        thumb_place(1, 1, shape())
    )


def thumb_1x_column(shape):
    return union()(
        thumb_place(2, -1, shape()),
        thumb_place(2, 0, shape()),
        thumb_place(2, 1, shape())
    )


def thumb_layout(shape):
    return union()(
        thumb_2x_column(shape),
        thumb_2x_1_column(shape),
        thumb_1x_column(shape)
    )


def dsa_key_cap(size=1, align='horizontal'):
    if size == 1:
        a = translate([0, 0, plate_thickness + 5])(
            import_stl('../things/dsa_1u.stl')
        )
    elif size == 1.5:
        a = translate([0, 0, plate_thickness + 5])(
            import_stl('../things/dsa_1.5u.stl')
        )
    elif size == 2:
        a = translate([0, 0, plate_thickness + 5])(
            import_stl('../things/dsa_2u.stl')
        )
    if align == 'vertical':
        a = rotate(90, [0, 0, 1])(a)

    return color([0.85, 0.85, 0.8])(a)


def web_post(o, thumb=False):
    web_thickness = 3.5
    post_size = 0.1
    post_adj = post_size / 2

    if thumb:
        plate_height = (key_cap_double_length - mount_height) / 2
    else:
        plate_height = 0

    web_post = translate([0, 0, web_thickness / -2])(
        cube([post_size, post_size, web_thickness])
    )

    if o == 'tr':
        web_post_o = translate([mount_width / 2 - post_adj, mount_height / 2 - post_adj + plate_height, 0])(
            web_post
        )
    elif o == 'tl':
        web_post_o = translate([mount_width / -2 - post_adj, mount_height / 2 - post_adj + plate_height, 0])(
            web_post
        )
    elif o == 'bl':
        web_post_o = translate([mount_width / -2 - post_adj, mount_height / -2 - post_adj - plate_height, 0])(
            web_post
        )
    elif o == 'br':
        web_post_o = translate([mount_width / 2 - post_adj, mount_height / -2 - post_adj - plate_height, 0])(
            web_post
        )

    return web_post_o


def key_connectors():
    a = []
    t = []

    # row connections
    for row in range(rows):
        for column in range(columns - 1):
            if column not in range(1) or not row == 4:
                t.append(key_place(column + 1, row, web_post('tl')))
                t.append(key_place(column, row, web_post('tr')))
                t.append(key_place(column + 1, row, web_post('bl')))
                t.append(key_place(column, row, web_post('br')))
            a.append(triangle_hulls(t))
            t = []

    # column connectors
    for row in range(rows - 1):
        for column in range(columns):
            if column not in range(1) or not row == 3:
                t.append(key_place(column, row + 1, web_post('tl')))
                t.append(key_place(column, row + 1, web_post('tr')))
                t.append(key_place(column, row, web_post('bl')))
                t.append(key_place(column, row, web_post('br')))
            a.append(triangle_hulls(t))
            t = []

    # diagonal connectors
    for row in range(rows - 1):
        for column in range(columns):
            if column != 5:
                t.append(key_place(column + 1, row + 1, web_post('tl')))
                t.append(key_place(column, row + 1, web_post('tr')))
                t.append(key_place(column + 1, row, web_post('bl')))
                t.append(key_place(column, row, web_post('br')))
            a.append(triangle_hulls(t))
            t = []

    return union()(a)


def thumb_connectors():
    a = []
    t = []

    for row in [1]:
        for column in [2]:
            t.append(thumb_place(column - 1, row, web_post('tl')))
            t.append(thumb_place(column, row, web_post('tr')))
            t.append(thumb_place(column - 1, row, web_post('bl')))
            t.append(thumb_place(column, row, web_post('br')))
            a.append(triangle_hulls(t))
            t = []

    for row in range(2):
        for column in [2]:
            t.append(thumb_place(column, row - 1, web_post('tl')))
            t.append(thumb_place(column, row - 1, web_post('tr')))
            t.append(thumb_place(column, row, web_post('bl')))
            t.append(thumb_place(column, row, web_post('br')))
            a.append(triangle_hulls(t))
            t = []

    # connecting the two doubles
    t.append(thumb_place(0, -1 / 2, web_post('tl', True)))
    t.append(thumb_place(0, -1 / 2, web_post('bl', True)))
    t.append(thumb_place(1, -1 / 2, web_post('tr', True)))
    t.append(thumb_place(1, -1 / 2, web_post('br', True)))
    a.append(triangle_hulls(t))
    t = []

    # connecting the double to the one above it
    t.append(thumb_place(1, -1 / 2, web_post('tl', True)))
    t.append(thumb_place(1, 1, web_post('bl')))
    t.append(thumb_place(1, -1 / 2, web_post('tr', True)))
    t.append(thumb_place(1, 1, web_post('br')))
    a.append(triangle_hulls(t))
    t = []

    # connecting the 4 with the double in the bottom left
    t.append(thumb_place(1, -1 / 2, web_post('tl', True)))
    t.append(thumb_place(1, 1, web_post('bl')))
    t.append(thumb_place(2, 0, web_post('tr')))
    t.append(thumb_place(2, 1, web_post('br')))
    a.append(triangle_hulls(t))
    t = []

    # connecting the two singles with middle double
    a.append(hull()(
        thumb_place(1, -1 / 2, web_post('tl', True)),
        thumb_place(1, -1 / 2, web_post('bl', True)),
        thumb_place(2, 0, web_post('br')),
        thumb_place(2, -1, web_post('tr'))
    ))
    a.append(hull()(
        thumb_place(1, -1 / 2, web_post('tl', True)),
        thumb_place(2, 0, web_post('tr')),
        thumb_place(2, 0, web_post('br'))
    ))
    a.append(hull()(
        thumb_place(1, -1 / 2, web_post('bl', True)),
        thumb_place(2, -1, web_post('tr')),
        thumb_place(2, -1, web_post('br'))
    ))

    # connecting the thumb to everything
    t.append(thumb_place(0, -1 / 2, web_post('br', True)))
    t.append(key_place(1, 4, web_post('bl')))
    t.append(thumb_place(0, -1 / 2, web_post('tr', True)))
    t.append(key_place(1, 4, web_post('tl')))
    t.append(key_place(1, 3, web_post('bl')))
    t.append(thumb_place(0, -1 / 2, web_post('tr', True)))
    t.append(key_place(0, 3, web_post('br')))
    t.append(key_place(0, 3, web_post('bl')))
    t.append(thumb_place(0, -1 / 2, web_post('tr', True)))
    t.append(thumb_place(0, -1 / 2, web_post('tl', True)))
    t.append(key_place(0, 3, web_post('bl')))
    t.append(thumb_place(1, -1 / 2, web_post('tr', True)))
    t.append(thumb_place(1, 1, web_post('br')))
    t.append(key_place(0, 3, web_post('bl')))
    t.append(key_place(0, 3, web_post('tl')))
    t.append(thumb_place(1, 1, web_post('br')))
    t.append(thumb_place(1, 1, web_post('tr')))
    a.append(triangle_hulls(t))
    t = []

    a.append(hull()(
        thumb_place(0, -1 / 2, web_post('tr')),
        thumb_place(0, -1 / 2, web_post('tr', True)),
        key_place(1, 4, web_post('bl')),
        key_place(1, 4, web_post('tl'))
    ))

    return union()(a)


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


if __name__ == '__main__':
    a = key_layout(plate)
    a.add(thumb_layout(plate))
    a.add(key_connectors())
    a.add(thumb_connectors())
    a.add(key_layout(dsa_key_cap))
    a.add(thumb_layout(dsa_key_cap))

    scad_render_to_file(a, '../things/dactyl.scad', file_header='$fn = %s;' % SEGMENTS, include_orig_code=False)
