#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from math import sin, pi

# uses https://github.com/SolidCode/SolidPython
# Assumes SolidPython is in site-packages or elsewhwere in sys.path
from solid import *
from solid.utils import *

from utils import *

SEGMENTS = 58

keyswitch_width = 14.4
keyswitch_height = 14.4
mount_width = keyswitch_width + 3
mount_height = keyswitch_height + 3
plate_thickness = 4
key_cap_profile_height = 12.7
key_cap_profile_height = 7.4
key_cap_double_length = 37.5
columns = range(-1, 6)
rows = range(5)
alpha = pi / 12
beta = pi / 36
cap_top_height = plate_thickness + key_cap_profile_height
row_radius = (mount_height + 0.5) / sin(alpha) + cap_top_height
column_radius = (mount_width + 2) / sin(beta) + cap_top_height

def plate(size=1, align='horizontal'):
    if size == 2:
        width = key_cap_double_length - 3
    elif size == 1.5:
        width = 27 - 3
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


def key_place(column, row, shape, size=1, align='horizontal'):
    if align == 'vertical':
        if size == 2:
            row += 1 / 2
        elif size == 1.5:
            row += 1 / 4
    else:
        if size == 2:
            column += 1 / 2
        elif size == 1.5:
            column += 1 / 4

    row_placed_shaped = translate([0, 0, row_radius])(
        rotate(15 * (2 - row), [1, 0, 0])(
            translate([0, 0, -row_radius])(
                shape(size, align)
            )
        )
    )

    if column == 2:
        column_row_offset = [0, 2.82, -3.0]
    elif column == 4:
        column_row_offset = [0, -5.8, 5.64]
    elif column >= 5:
        column_row_offset = [0.2, -5.8, 6.14]
    else:
        column_row_offset = [0, 0, 0]

    column_angle = 5 * (2 - column)

    placed_shape = translate(column_row_offset)(
        translate([0, 0, column_radius])(
            rotate(column_angle, [0, 1, 0])(
                translate([0, 0, -column_radius])(
                    row_placed_shaped
                )
            )
        )
    )

    return translate([0, 0, 14.5])(
        rotate(15, [0, 1, 0])(
            placed_shape
        )
    )


def key_layout(shape):
    placed_shape = []
    for row in rows:
        for column in columns:
            if column == 5 and row != 4:
                placed_shape.append(key_place(column, row, shape, 1.5))
            elif column == -1 and row >= 3:
                pass
            elif column >= 2 or row != 4:
                placed_shape.append(key_place(column, row, shape))

    return union()(placed_shape)


def thumb_place(column, row, shape, size=1, align='horizontal'):
    row_radius = (mount_height + 1) / sin(alpha) + cap_top_height
    column_radius = (mount_width + 2) / sin(beta) + cap_top_height

    if align == 'vertical':
        if size == 2:
            row += 1 / 2
        elif size == 1.5:
            row += 1 / 4
    else:
        if size == 2:
            column += 1 / 2
        elif size == 1.5:
            column += 1 / 4

    row_placed_shaped = translate([0, 0, row_radius])(
        rotate(15 * row, [1, 0, 0])(
            translate([0, 0, -row_radius])(
                shape(size, align)
            )
        )
    )

    if column == -1:
        column_row_offset = [mount_width, 0, -1]
    else:
        column_row_offset = [mount_width, 0, 0]

    column_angle = 5 * (column)

    placed_shape = rotate(11.25, [0, 0, 1])(
        translate(column_row_offset)(
            translate([0, 0, column_radius])(
                rotate(column_angle, [0, 1, 0])(
                    translate([0, 0, -column_radius])(
                        row_placed_shaped
                    )
                )
            )
        )
    )

    return translate([-54, -44, 37])(
        rotate(20, [1, 1, 0])(
            placed_shape
        )
    )


def thumb_layout(shape):
    placed_shape = []
    placed_shape.append(thumb_place(-1, -1, shape, 1.5, 'vertical'))
    placed_shape.append(thumb_place(0, -1, shape, 2, 'vertical'))
    placed_shape.append(thumb_place(1, -1, shape, 2, 'vertical'))
    placed_shape.append(thumb_place(1, 1, shape))
    placed_shape.append(thumb_place(2, -1, shape))
    placed_shape.append(thumb_place(2, 0, shape))
    placed_shape.append(thumb_place(2, 1, shape))

    return union()(placed_shape)


def dsa_key_cap(size=1, align='horizontal'):
    if size == 1:
        shape = translate([0, 0, plate_thickness + 5])(
            import_stl('../things/dsa_1u.stl')
        )
    elif size == 1.5:
        shape = translate([0, 0, plate_thickness + 5])(
            import_stl('../things/dsa_1.5u.stl')
        )
    elif size == 2:
        shape = translate([0, 0, plate_thickness + 5])(
            import_stl('../things/dsa_2u.stl')
        )

    if align == 'vertical':
        shape = rotate(90, [0, 0, 1])(shape)

    return color([0.85, 0.85, 0.8])(shape)


def web_post(size=1, align=None):
    post_size = 0.1
    post_adj = post_size / 2

    if size == 2:
        plate_width = (key_cap_double_length - mount_height) / 2
    elif size == 1.5:
        plate_width = (27 - mount_height) / 2
    else:
        plate_width = 0

    web_post = translate([0, 0, plate_thickness / -2])(
        cube([post_size, post_size, plate_thickness])
    )

    if align == 'tr':
        web_post_o = translate([mount_width / 2 - post_adj + plate_width, mount_height / 2 - post_adj, 0])(
            web_post
        )
    elif align == 'tl':
        web_post_o = translate([mount_width / -2 - post_adj - plate_width, mount_height / 2 - post_adj, 0])(
            web_post
        )
    elif align == 'bl':
        web_post_o = translate([mount_width / -2 - post_adj - plate_width, mount_height / -2 - post_adj, 0])(
            web_post
        )
    elif align == 'br':
        web_post_o = translate([mount_width / 2 - post_adj + plate_width, mount_height / -2 - post_adj, 0])(
            web_post
        )
    else:
        web_post_o = web_post

    return web_post_o


def web_post_tr(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, [0, 0, 1])(web_post(size, 'br'))

    return web_post(size, 'tr')


def web_post_tl(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, [0, 0, 1])(web_post(size, 'tr'))

    return web_post(size, 'tl')


def web_post_br(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, [0, 0, 1])(web_post(size, 'bl'))

    return web_post(size, 'br')


def web_post_bl(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, [0, 0, 1])(web_post(size, 'tl'))

    return web_post(size, 'bl')


def key_connectors():
    a = []
    t = []

    # row connections
    for row in rows:
        for column in columns[:-1]:
            if column == 4 and row != 4:
                t.append(key_place(column + 1, row, web_post_tl, 1.5))
                t.append(key_place(column, row, web_post_tr))
                t.append(key_place(column + 1, row, web_post_bl, 1.5))
                t.append(key_place(column, row, web_post_br))
            elif column == -1 and row >= 3:
                pass
            elif column <= 1 and row >= 4:
                pass
            else:
                t.append(key_place(column + 1, row, web_post_tl))
                t.append(key_place(column, row, web_post_tr))
                t.append(key_place(column + 1, row, web_post_bl))
                t.append(key_place(column, row, web_post_br))

            a.append(triangle_hulls(t))
            t = []

    # column connectors
    for row in rows[:-1]:
        for column in columns:
            if column == 5 and row != 3:
                t.append(key_place(column, row + 1, web_post_tl, 1.5))
                t.append(key_place(column, row + 1, web_post_tr, 1.5))
                t.append(key_place(column, row, web_post_bl, 1.5))
                t.append(key_place(column, row, web_post_br, 1.5))
            elif column == -1 and row >= 2:
                pass
            elif (column <= 1 or column == 5) and row >= 3:
                pass
            else:
                t.append(key_place(column, row + 1, web_post_tl))
                t.append(key_place(column, row + 1, web_post_tr))
                t.append(key_place(column, row, web_post_bl))
                t.append(key_place(column, row, web_post_br))
            a.append(triangle_hulls(t))
            t = []

    # diagonal connectors
    for row in rows[:-1]:
        for column in columns[:-1]:
            if column == 4 and row != 3:
                t.append(key_place(column + 1, row + 1, web_post_tl, 1.5))
                t.append(key_place(column, row + 1, web_post_tr))
                t.append(key_place(column + 1, row, web_post_bl, 1.5))
                t.append(key_place(column, row, web_post_br))
            elif column == -1 and row >= 2:
                pass
            elif (column <= 1 or column == 4) and row >= 3:
                pass
            else:
                t.append(key_place(column + 1, row + 1, web_post_tl))
                t.append(key_place(column, row + 1, web_post_tr))
                t.append(key_place(column + 1, row, web_post_bl))
                t.append(key_place(column, row, web_post_br))

            a.append(triangle_hulls(t))
            t = []

    # connect right 1u
    t.append(key_place(4, 3, web_post_br))
    t.append(key_place(5, 3, web_post_bl, 1.5))
    t.append(key_place(4, 4, web_post_tr))
    t.append(key_place(5, 4, web_post_tl))
    a.append(triangle_hulls(t))
    t = []

    t.append(key_place(5, 3, web_post_br, 1.5))
    t.append(key_place(5, 3, web_post_bl, 1.5))
    t.append(key_place(5, 4, web_post_tr))
    t.append(key_place(5, 4, web_post_tl))
    a.append(triangle_hulls(t))
    t = []

    t.append(key_place(5, 3, web_post_br, 1.5))
    t.append(key_place(5, 4, web_post_tr))
    t.append(key_place(5, 4, web_post_tr, 1.5))
    a.append(hull()(t))
    t = []

    t.append(key_place(5, 4, web_post_tr, 1.5))
    t.append(key_place(5, 4, web_post_tr))
    t.append(key_place(5, 4, web_post_br, 1.5))
    t.append(key_place(5, 4, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    return union()(a)


def thumb_connectors():
    a = []
    t = []

    for row in [1]:
        for column in [2]:
            t.append(thumb_place(column - 1, row, web_post_tl))
            t.append(thumb_place(column, row, web_post_tr))
            t.append(thumb_place(column - 1, row, web_post_bl))
            t.append(thumb_place(column, row, web_post_br))
            a.append(triangle_hulls(t))
            t = []

    for row in range(2):
        for column in [2]:
            t.append(thumb_place(column, row - 1, web_post_tl))
            t.append(thumb_place(column, row - 1, web_post_tr))
            t.append(thumb_place(column, row, web_post_bl))
            t.append(thumb_place(column, row, web_post_br))
            a.append(triangle_hulls(t))
            t = []

    # connecting the two doubles
    t.append(thumb_place(0, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(0, -1, web_post_bl, 2, 'vertical'))
    t.append(thumb_place(1, -1, web_post_tr, 2, 'vertical'))
    t.append(thumb_place(1, -1, web_post_br, 2, 'vertical'))
    a.append(triangle_hulls(t))
    t = []

    # connecting the double to the one above it
    t.append(thumb_place(1, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(1, 1, web_post_bl))
    t.append(thumb_place(1, -1, web_post_tr, 2, 'vertical'))
    t.append(thumb_place(1, 1, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    # connecting the 4 with the double in the bottom left
    t.append(thumb_place(1, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(1, 1, web_post_bl))
    t.append(thumb_place(2, 0, web_post_tr))
    t.append(thumb_place(2, 1, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    # connecting the two singles with middle double
    t.append(thumb_place(1, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(1, -1, web_post_bl, 2, 'vertical'))
    t.append(thumb_place(2, 0, web_post_br))
    t.append(thumb_place(2, -1, web_post_tr))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(1, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(2, 0, web_post_tr))
    t.append(thumb_place(2, 0, web_post_br))
    a.append(hull()(t))
    t = []

    t.append(thumb_place(1, -1, web_post_bl, 2, 'vertical'))
    t.append(thumb_place(2, -1, web_post_tr))
    t.append(thumb_place(2, -1, web_post_br))
    a.append(hull()(t))
    t = []


    # connecting the 1.5 with the doubles
    t.append(thumb_place(0, -1, web_post_tr, 2, 'vertical'))
    t.append(thumb_place(0, -1, web_post_br, 2, 'vertical'))
    t.append(thumb_place(-1, -1, web_post_tl, 1.5, 'vertical'))
    t.append(thumb_place(-1, -1, web_post_bl, 1.5, 'vertical'))
    a.append(triangle_hulls(t))
    t = []

    # connecting the thumb to everything
    t.append(key_place(2, 4, web_post_bl))
    t.append(thumb_place(-1, -1, web_post_tr, 1.5, 'vertical'))
    t.append(thumb_place(-1, -1, web_post_br, 1.5, 'vertical'))
    a.append(hull()(t))
    t = []

    t.append(key_place(2, 4, web_post_tl))
    t.append(key_place(2, 4, web_post_bl))
    t.append(thumb_place(-1, -1, web_post_tr, 1.5, 'vertical'))
    a.append(hull()(t))
    t = []

    t.append(thumb_place(-1, -1, web_post_tr, 1.5, 'vertical'))
    t.append(key_place(2, 4, web_post_tl))
    t.append(key_place(1, 3, web_post_br))
    t.append(key_place(2, 3, web_post_bl))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(-1, -1, web_post_tl, 1.5, 'vertical'))
    t.append(thumb_place(-1, -1, web_post_tr, 1.5, 'vertical'))
    t.append(key_place(1, 3, web_post_bl))
    t.append(key_place(1, 3, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(0, -1, web_post_tr, 2, 'vertical'))
    t.append(thumb_place(-1, -1, web_post_tl, 1.5, 'vertical'))
    t.append(key_place(0, 3, web_post_br))
    t.append(key_place(1, 3, web_post_bl))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(0, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(0, -1, web_post_tr, 2, 'vertical'))
    t.append(key_place(0, 3, web_post_bl))
    t.append(key_place(0, 3, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(0, -1, web_post_tl, 2, 'vertical'))
    t.append(thumb_place(1, -1, web_post_tr, 2, 'vertical'))
    t.append(key_place(0, 3, web_post_bl))
    t.append(thumb_place(1, 1, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(1, 1, web_post_br))
    t.append(thumb_place(1, 1, web_post_tr))
    t.append(key_place(0, 3, web_post_bl))
    t.append(key_place(0, 3, web_post_tl))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(1, 1, web_post_tr))
    t.append(key_place(0, 3, web_post_tl))
    t.append(key_place(-1, 2, web_post_br))
    t.append(key_place(0, 2, web_post_bl))
    a.append(triangle_hulls(t))
    t = []

    t.append(thumb_place(1, 1, web_post_tl))
    t.append(thumb_place(1, 1, web_post_tr))
    t.append(key_place(-1, 2, web_post_bl))
    t.append(key_place(-1, 2, web_post_br))
    a.append(triangle_hulls(t))
    t = []

    return union()(a)


# case
right_column = list(columns)[-1]
left_column = list(columns)[0]
front_row = list(rows)[-1]
back_row = list(rows)[0]

right_wall_offset = [-2, 0, -1]
left_wall_offset = [0, 0, -1]
front_wall_offset = [0, -2, -1]
back_wall_offset = [0, -2, -1]


def case_place(column, row, shape, size=1, align='horizontal'):
    if align == 'vertical':
        if size == 2:
            row += 1 / 2
        elif size == 1.5:
            row += 1 / 4
    else:
        if size == 2:
            column += 1 / 2
        elif size == 1.5:
            column += 1 / 4

    row_placed_shaped = translate([0, 0, row_radius])(
        rotate(15 * (2 - row), [1, 0, 0])(
            translate([0, 0, -row_radius])(
                shape
            )
        )
    )

    if column == 6:
        column_offset = [-7.25, -5.8, 0]
    else:
        column_offset = [0, -3.35, 4.9]

    if row == 0:
        row_offset = [0, 2.25, 0]
    else:
        row_offset = [0, 0, 0]

    if column == 6 and row == 0:
        column_row_offset = [0, 2.25, 0]
    else:
        column_row_offset = [0, 0, 0]

    column_angle = 5 * (2 - column)

    placed_shape = translate(row_offset)(
        translate(column_offset)(
            translate(column_row_offset)(
                translate([0, 0, column_radius])(
                    rotate(column_angle, [0, 1, 0])(
                        translate([0, 0, - column_radius])(
                            row_placed_shaped
                        )
                    )
                )
            )
        )
    )

    return translate([0, 0, 14.5])(
        rotate(15, [0, 1, 0])(
            placed_shape
        )
    )


def thumb_case_place(column, row, shape, size=1, align='horizontal'):
    row_radius = (mount_height + 1) / sin(alpha) + cap_top_height
    column_radius = (mount_width + 2) / sin(beta) + cap_top_height

    if align == 'vertical':
        if size == 2:
            row += 1 / 2
        elif size == 1.5:
            row += 1 / 4
    else:
        if size == 2:
            column += 1 / 2
        elif size == 1.5:
            column += 1 / 4

    row_placed_shaped = translate([0, 0, row_radius])(
        rotate(15 * row, [1, 0, 0])(
            translate([0, 0, -row_radius])(
                shape
            )
        )
    )

    placed_shape = rotate(11.25, [0, 0, 1])(
        translate([mount_width, 0, 0])(
            translate([0, 0, column_radius])(
                rotate(5 * column, [0, 1, 0])(
                    translate([0, 0, -column_radius])(
                        row_placed_shaped
                    )
                )
            )
        )
    )

    return translate([-54, -44, 37])(
        rotate(20, [1, 1, 0])(
            placed_shape
        )
    )


def wall_cube_at(coords):
    return translate(coords)(
        cube([3, 3, 3], True)
    )


def scale_to_range(start, end, x):
    return start + (end - start) * x


def wall_cube_bottom(front_to_back_scale):
    return wall_cube_at([0, scale_to_range(mount_height / -2 + -3.5, mount_height / 2 + 5, front_to_back_scale), -6])


wall_cube_bottom_front = wall_cube_bottom(0)
wall_cube_bottom_center = wall_cube_bottom(1 / 2)
wall_cube_bottom_back = wall_cube_bottom(1)


def wall_cube_top(front_to_back_scale):
    return wall_cube_at([0, scale_to_range(mount_height / -2 + -3.5, mount_height / 2 + 3.5, front_to_back_scale), 4])


wall_cube_top_front = wall_cube_top(0)
wall_cube_top_center = wall_cube_top(1 / 2)
wall_cube_top_back = wall_cube_top(1)


def front_wall():
    shape = []
    tmp = []

    for column in columns[4:]:
        if column == 5:
            tmp.append(case_place(column - 1 / 2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
            tmp.append(case_place(column + 1, front_row, translate(front_wall_offset)(wall_cube_bottom_front), 1.5))
            tmp.append(key_place(column, front_row, web_post_bl))
            tmp.append(key_place(column, front_row, web_post_br, 1.5))
        else:
            tmp.append(case_place(column - 1 / 2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
            tmp.append(case_place(column + 1 / 2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
            tmp.append(key_place(column, front_row, web_post_bl))
            tmp.append(key_place(column, front_row, web_post_br))
        shape.append(hull()(tmp))
        tmp = []

        tmp.append(case_place(column - 1 / 2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
        tmp.append(key_place(column, front_row, web_post_bl))
        tmp.append(key_place(column - 1, front_row, web_post_br))
        shape.append(hull()(tmp))
        tmp = []

    # left corner
    tmp.append(case_place(2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
    tmp.append(case_place(2 + 1 / 2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
    tmp.append(key_place(2, front_row, web_post_bl))
    tmp.append(key_place(2, front_row, web_post_br))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def back_wall():
    shape = []
    tmp = []

    for column in columns:
        if column == 5:
            tmp.append(key_place(column, back_row, web_post_tr, 1.5))
            tmp.append(case_place(column + 5 / 4, back_row, translate(back_wall_offset)(wall_cube_bottom_back)))
        else:
            tmp.append(key_place(column, back_row, web_post_tr))
            tmp.append(case_place(column + 1 / 2, back_row, translate(back_wall_offset)(wall_cube_bottom_back)))
        tmp.append(case_place(column - 1 / 2, back_row, translate(back_wall_offset)(wall_cube_bottom_back)))
        tmp.append(key_place(column, back_row, web_post_tl))
        shape.append(hull()(tmp))
        tmp = []

    for column in columns[1:]:
        tmp.append(case_place(column - 1 / 2, back_row, translate(back_wall_offset)(wall_cube_bottom_back)))
        tmp.append(key_place(column, back_row, web_post_tl))
        tmp.append(key_place(column - 1, back_row, web_post_tr))
        shape.append(hull()(tmp))
        tmp = []

    return union()(shape)


def right_wall():
    shape = []
    tmp = []

    for i in rows[1:-1]:
        tmp.append(case_place(right_column + 1, i - 1 / 2, translate(right_wall_offset)(wall_cube_bottom_center), 1.5))
        tmp.append(case_place(right_column + 1, i + 1 / 2, translate(right_wall_offset)(wall_cube_bottom_center), 1.5))
        tmp.append(key_place(right_column, i, web_post_br, 1.5))
        tmp.append(key_place(right_column, i, web_post_tr, 1.5))
        shape.append(hull()(tmp))
        tmp = []

    for i in rows[:-1]:
        tmp.append(case_place(right_column + 1, i + 1 / 2, translate(right_wall_offset)(wall_cube_bottom_center), 1.5))
        tmp.append(key_place(right_column, i, web_post_br, 1.5))
        tmp.append(key_place(right_column, i + 1, web_post_tr, 1.5))
        shape.append(hull()(tmp))
        tmp = []

    # top corner
    tmp.append(case_place(right_column + 1, back_row + 1 / 2, translate(right_wall_offset)(wall_cube_bottom_center), 1.5))
    tmp.append(case_place(5 + 5 / 4, back_row, translate(back_wall_offset)(wall_cube_bottom_back)))
    tmp.append(key_place(right_column, back_row, web_post_tr, 1.5))
    tmp.append(key_place(right_column, back_row, web_post_br, 1.5))
    shape.append(hull()(tmp))
    tmp = []

    # bottom corner
    tmp.append(case_place(right_column + 1, front_row - 1 / 2, translate(right_wall_offset)(wall_cube_bottom_center), 1.5))
    tmp.append(case_place(5 + 1, front_row, translate(front_wall_offset)(wall_cube_bottom_front), 1.5))
    tmp.append(key_place(right_column, front_row, web_post_tr, 1.5))
    tmp.append(key_place(right_column, front_row, web_post_br, 1.5))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def left_wall():
    shape = []
    tmp = []

    for i in rows[:-2]:
        tmp.append(case_place(left_column - 1 / 2, i, translate(left_wall_offset)(wall_cube_bottom_center)))
        tmp.append(key_place(left_column, i, web_post_tl))
        tmp.append(key_place(left_column, i, web_post_bl))
        shape.append(hull()(tmp))
        tmp = []

    for i in rows[:-3]:
        tmp.append(case_place(left_column - 1 / 2, i, translate(left_wall_offset)(wall_cube_bottom_center)))
        tmp.append(case_place(left_column - 1 / 2, i + 1, translate(left_wall_offset)(wall_cube_bottom_center)))
        tmp.append(key_place(left_column, i, web_post_bl))
        tmp.append(key_place(left_column, i + 1, web_post_tl))
        shape.append(hull()(tmp))
        tmp = []

    # top corner
    tmp.append(case_place(left_column - 1 / 2, back_row, translate(left_wall_offset)(wall_cube_bottom_center)))
    tmp.append(case_place(left_column - 1 / 2, back_row, translate(back_wall_offset)(wall_cube_bottom_back)))
    tmp.append(key_place(left_column, back_row, web_post_tl))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def thumb_front_wall():
    shape = []
    tmp = []

    for column in range(-1, 3):
        if column == -1:
            tmp.append(thumb_place(column, -1, web_post_bl, 1.5, 'vertical'))
            tmp.append(thumb_place(column, -1, web_post_br, 1.5, 'vertical'))
        elif column != 2:
            tmp.append(thumb_place(column, -1, web_post_bl, 2, 'vertical'))
            tmp.append(thumb_place(column, -1, web_post_br, 2, 'vertical'))
        else:
            tmp.append(thumb_place(column, -1, web_post_bl))
            tmp.append(thumb_place(column, -1, web_post_br))

        tmp.append(thumb_case_place(column, -1, wall_cube_bottom_front))
        shape.append(hull()(tmp))
        tmp = []

    tmp.append(thumb_case_place(-1, -1, wall_cube_bottom_front))
    tmp.append(thumb_case_place(0, -1, wall_cube_bottom_front))
    tmp.append(thumb_place(-1, -1, web_post_bl, 1.5, 'vertical'))
    tmp.append(thumb_place(0, -1, web_post_br, 2, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(thumb_case_place(0, -1, wall_cube_bottom_front))
    tmp.append(thumb_case_place(1, -1, wall_cube_bottom_front))
    tmp.append(thumb_place(0, -1, web_post_bl, 2, 'vertical'))
    tmp.append(thumb_place(1, -1, web_post_br, 2, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(thumb_case_place(1, -1, wall_cube_bottom_front))
    tmp.append(thumb_case_place(2, -1, wall_cube_bottom_front))
    tmp.append(thumb_place(1, -1, web_post_bl, 2, 'vertical'))
    tmp.append(thumb_place(2, -1, web_post_br))
    shape.append(hull()(tmp))
    tmp = []

    #  # left corner
    tmp.append(thumb_case_place(2, -1, wall_cube_bottom_front))
    tmp.append(thumb_case_place(5 / 2, -1, wall_cube_bottom_front))
    tmp.append(thumb_place(2, -1, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    #  # right corner
    tmp.append(thumb_case_place(-3 / 2, -1, wall_cube_bottom_front))
    tmp.append(thumb_case_place(-1, -1, wall_cube_bottom_front))
    tmp.append(thumb_place(-1, -1, web_post_br, 1.5, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def thumb_back_wall():
    shape = []
    tmp = []

    # right corner
    tmp.append(thumb_case_place(5 / 4, 1, wall_cube_bottom_back))
    tmp.append(thumb_place(1, 1, web_post_tl))
    tmp.append(key_place(left_column, 2, web_post_bl))
    tmp.append(case_place(left_column - 1 / 2, 2, translate(left_wall_offset)(wall_cube_bottom_center)))
    shape.append(hull()(tmp))
    tmp = []

    # center
    tmp.append(thumb_case_place(5 / 4, 1, wall_cube_bottom_back))
    tmp.append(thumb_case_place(2 + 1 / 2, 1, wall_cube_bottom_back))
    tmp.append(thumb_place(1, 1, web_post_tl))
    tmp.append(thumb_place(2, 1, web_post_tr))
    shape.append(hull()(tmp))
    tmp = []

    # left corner
    tmp.append(thumb_case_place(5 / 2, 1, wall_cube_bottom_back))
    tmp.append(thumb_place(2, 1, web_post_tr))
    tmp.append(thumb_place(2, 1, web_post_tl))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def thumb_inside_wall():
    shape = []
    tmp = []

    # front corner
    tmp.append(case_place(2, front_row, translate(front_wall_offset)(wall_cube_bottom_front)))
    tmp.append(thumb_case_place(-3 / 2, -1, wall_cube_bottom_front))
    tmp.append(key_place(2, front_row, web_post_bl))
    tmp.append(thumb_place(-1, -1, web_post_br, 1.5, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def thumb_left_wall():
    shape = []
    tmp = []

    shape.append(hull()(tmp))
    tmp = []

    for i in [1, 0, -1]:
        tmp.append(thumb_case_place(5 / 2, i, wall_cube_bottom_center))
        tmp.append(thumb_place(2, i, web_post_tl))
        tmp.append(thumb_place(2, i, web_post_bl))
        shape.append(hull()(tmp))
        tmp = []

    for i in [0, -1]:
        tmp.append(thumb_case_place(5 / 2, i + 1, wall_cube_bottom_center))
        tmp.append(thumb_case_place(5 / 2, i, wall_cube_bottom_center))
        tmp.append(thumb_place(2, i + 1, web_post_bl))
        tmp.append(thumb_place(2, i, web_post_tl))
        shape.append(hull()(tmp))
        tmp = []

    # front corner
    tmp.append(thumb_case_place(5 / 2, -1, wall_cube_bottom_center))
    tmp.append(thumb_case_place(5 / 2, -1, wall_cube_bottom_front))
    tmp.append(thumb_place(2, -1, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    # back corner
    tmp.append(thumb_case_place(5 / 2, 1, wall_cube_bottom_back))
    tmp.append(thumb_case_place(5 / 2, 1, wall_cube_bottom_center))
    tmp.append(thumb_place(2, 1, web_post_tl))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def case():
    return union()(
        front_wall(),
        back_wall(),
        right_wall(),
        left_wall(),
        thumb_front_wall(),
        thumb_back_wall(),
        thumb_inside_wall(),
        thumb_left_wall()
    )


if __name__ == '__main__':
    a = key_layout(plate)
    a.add(thumb_layout(plate))
    a.add(key_connectors())
    a.add(thumb_connectors())
    a.add(key_layout(dsa_key_cap))
    a.add(thumb_layout(dsa_key_cap))
    a.add(case())

    scad_render_to_file(a, '../things/dactyl.scad', file_header='$fn = %s;' % SEGMENTS, include_orig_code=False)
