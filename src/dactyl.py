#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from math import sin, pi

# uses https://github.com/SolidCode/SolidPython
# Assumes SolidPython is in site-packages or elsewhwere in sys.path
from solid import *
from solid.utils import *

from utils import triangle_hulls

SEGMENTS = 16

X = [1, 0, 0]
Y = [0, 1, 0]
Z = [0, 0, 1]

keyswitch_width = 14.4
keyswitch_height = 14.4
mount_width = keyswitch_width + 3
mount_height = keyswitch_height + 3
plate_thickness = 4
key_cap_profile_height = 12.7
key_cap_profile_height = 7.4
key_cap_double_length = 37.5
columns = range(7)
rows = range(5)
center_column = 3
center_row = 2
alpha = pi / 12
beta = pi / 36
cap_top_height = plate_thickness + key_cap_profile_height
row_radius = (mount_height + 0.5) / sin(alpha) + cap_top_height
column_radius = (mount_width + 2) / sin(beta) + cap_top_height
web_thickness = 3.5

thumb_columns = range(4)
thumb_rows = range(3)
thumb_center_column = 2
thumb_center_row = 1


def plate(size=1, align='horizontal'):
    if size == 2:
        width = key_cap_double_length - 3
    elif size == 1.5:
        width = 27 - 3
    else:
        width = keyswitch_width

    outer_wall = cube([width + 3, keyswitch_height + 3, plate_thickness], center=True)

    if align == 'vertical':
        outer_wall = rotate(90, Z)(outer_wall)

    inner_wall = cube([keyswitch_width, keyswitch_height, plate_thickness + 0.1], center=True)
    wall = difference()(outer_wall - inner_wall)

    nibble = hull()(
        translate([keyswitch_width / 2 + 1.5 / 2, 0, 0])(
            cube([1.5, 2.75, plate_thickness], center=True)
        ),
        translate([keyswitch_width / 2, 2.75 / 2, -1])(
            rotate(90, X)(
                cylinder(r=1, h=2.75)
            )
        )
    )

    return wall + nibble + mirror(X)(nibble)


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
        rotate(15 * (center_row - row), X)(
            translate([0, 0, -row_radius])(
                shape(size, align)
            )
        )
    )

    if column == center_column - 3:
        column_row_offset = [0, 0, 1]
    elif column == center_column:
        column_row_offset = [0, 2.82, -3.0]
    elif column == center_column + 2:
        column_row_offset = [0, -5.8, 5.64]
    elif column >= center_column + 3:
        column_row_offset = [0.2, -5.8, 6.14]
    else:
        column_row_offset = [0, 0, 0]

    column_angle = 5 * (center_column - column)

    placed_shape = translate(column_row_offset)(
        translate([0, 0, column_radius])(
            rotate(column_angle, Y)(
                translate([0, 0, -column_radius])(
                    row_placed_shaped
                )
            )
        )
    )

    return translate([0, 0, 14.5])(
        rotate(15, Y)(
            placed_shape
        )
    )


def thumb_place(column, row, shape, size=1, align='horizontal'):
    row_radius = (mount_height + 1) / sin(alpha) + cap_top_height
    column_radius = (mount_width + 2) / sin(beta) + cap_top_height

    if align == 'vertical':
        if size == 2:
            row -= 1 / 2
        elif size == 1.5:
            row -= 1 / 4
    else:
        if size == 2:
            column -= 1 / 2
        elif size == 1.5:
            column -= 1 / 4

    row_placed_shaped = translate([0, 0, row_radius])(
        rotate(15 * (thumb_center_row - row), X)(
            translate([0, 0, -row_radius])(
                shape(size, align)
            )
        )
    )

    if column == thumb_center_column + 1:
        column_row_offset = [mount_width, 0, -1.1]
    else:
        column_row_offset = [mount_width, 0, 0]

    column_angle = 5 * (thumb_center_column - column)

    placed_shape = rotate(11.25, Z)(
        translate(column_row_offset)(
            translate([0, 0, column_radius])(
                rotate(column_angle, Y)(
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


def key_layout(shape):
    placed_shape = []

    for row in rows:
        for column in columns:
            if column == center_column + 3 and not row >= center_row + 2:
                placed_shape.append(key_place(column, row, shape, 1.5))
            elif column == center_column - 3 and row >= center_row + 1:
                pass
            elif column >= center_column or not row >= center_row + 2:
                placed_shape.append(key_place(column, row, shape))

    return union()(placed_shape)


def thumb_layout(shape):
    placed_shape = []

    for row in thumb_rows:
        for column in thumb_columns:
            if column >= thumb_center_column and row <= thumb_center_row:
                pass
            elif column == thumb_center_column - 1 and row == thumb_center_row:
                pass
            elif column == thumb_center_column + 1:
                placed_shape.append(thumb_place(column, row, shape, 1.5, 'vertical'))
            elif (column == thumb_center_column or column == thumb_center_column - 1) and row == thumb_center_row + 1:
                placed_shape.append(thumb_place(column, row, shape, 2, 'vertical'))
            else:
                placed_shape.append(thumb_place(column, row, shape))

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
        shape = rotate(90, Z)(shape)

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
        return rotate(90, Z)(web_post(size, 'br'))

    return web_post(size, 'tr')


def web_post_tl(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, Z)(web_post(size, 'tr'))

    return web_post(size, 'tl')


def web_post_br(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, Z)(web_post(size, 'bl'))

    return web_post(size, 'br')


def web_post_bl(size=1, align='horizontal'):
    if align == 'vertical':
        return rotate(90, Z)(web_post(size, 'tl'))

    return web_post(size, 'bl')


def key_connectors():
    shape = []
    tmp = []

    # row connections
    for row in rows:
        for column in columns[:-1]:
            if column == center_column - 3 and row >= center_row + 1:
                pass
            elif column <= center_column -1 and row >= center_row + 2:
                pass
            elif column == center_column + 2 and not row >= center_row + 2:
                tmp.append(key_place(column + 1, row, web_post_tl, 1.5))
                tmp.append(key_place(column, row, web_post_tr))
                tmp.append(key_place(column + 1, row, web_post_bl, 1.5))
                tmp.append(key_place(column, row, web_post_br))
            else:
                tmp.append(key_place(column + 1, row, web_post_tl))
                tmp.append(key_place(column, row, web_post_tr))
                tmp.append(key_place(column + 1, row, web_post_bl))
                tmp.append(key_place(column, row, web_post_br))

            shape.append(triangle_hulls(tmp))
            tmp = []

    # column connectors
    for row in rows[:-1]:
        for column in columns:
            if column == center_column - 3 and row >= center_row:
                pass
            elif column <= center_column - 1 and row >= center_row + 1:
                pass
            elif column == center_column + 3 and row >= center_row + 1:
                pass
            elif column == center_column + 3:
                tmp.append(key_place(column, row + 1, web_post_tl, 1.5))
                tmp.append(key_place(column, row + 1, web_post_tr, 1.5))
                tmp.append(key_place(column, row, web_post_bl, 1.5))
                tmp.append(key_place(column, row, web_post_br, 1.5))
            else:
                tmp.append(key_place(column, row + 1, web_post_tl))
                tmp.append(key_place(column, row + 1, web_post_tr))
                tmp.append(key_place(column, row, web_post_bl))
                tmp.append(key_place(column, row, web_post_br))
            shape.append(triangle_hulls(tmp))
            tmp = []

    # diagonal connectors
    for row in rows[:-1]:
        for column in columns[:-1]:
            if column == center_column - 3 and row >= center_row:
                pass
            elif column <= center_column - 1 and row >= center_row + 1:
                pass
            elif column == center_column + 2 and row >= center_row + 1:
                pass
            elif column == center_column + 2:
                tmp.append(key_place(column + 1, row + 1, web_post_tl, 1.5))
                tmp.append(key_place(column, row + 1, web_post_tr))
                tmp.append(key_place(column + 1, row, web_post_bl, 1.5))
                tmp.append(key_place(column, row, web_post_br))
            else:
                tmp.append(key_place(column + 1, row + 1, web_post_tl))
                tmp.append(key_place(column, row + 1, web_post_tr))
                tmp.append(key_place(column + 1, row, web_post_bl))
                tmp.append(key_place(column, row, web_post_br))

            shape.append(triangle_hulls(tmp))
            tmp = []

    # connect right 1u
    # diagonal connection
    tmp.append(key_place(5, 3, web_post_br))
    tmp.append(key_place(6, 3, web_post_bl, 1.5))
    tmp.append(key_place(5, 4, web_post_tr))
    tmp.append(key_place(6, 4, web_post_tl))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(key_place(6, 3, web_post_br, 1.5))
    tmp.append(key_place(6, 3, web_post_bl, 1.5))
    tmp.append(key_place(6, 4, web_post_tr))
    tmp.append(key_place(6, 4, web_post_tl))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(key_place(6, 3, web_post_br, 1.5))
    tmp.append(key_place(6, 4, web_post_tr))
    tmp.append(key_place(6, 4, web_post_tr, 1.5))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(key_place(6, 4, web_post_tr, 1.5))
    tmp.append(key_place(6, 4, web_post_tr))
    tmp.append(key_place(6, 4, web_post_br, 1.5))
    tmp.append(key_place(6, 4, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    return union()(shape)


def thumb_connectors():
    shape = []
    tmp = []

    for row in thumb_rows[:-2]:
        for column in thumb_columns[:-3]:
            tmp.append(thumb_place(column + 1, row, web_post_tl))
            tmp.append(thumb_place(column, row, web_post_tr))
            tmp.append(thumb_place(column + 1, row, web_post_bl))
            tmp.append(thumb_place(column, row, web_post_br))
            shape.append(triangle_hulls(tmp))
            tmp = []

    for row in thumb_rows[:-1]:
        for column in thumb_columns[:-3]:
            tmp.append(thumb_place(column, row + 1, web_post_tl))
            tmp.append(thumb_place(column, row + 1, web_post_tr))
            tmp.append(thumb_place(column, row, web_post_bl))
            tmp.append(thumb_place(column, row, web_post_br))
            shape.append(triangle_hulls(tmp))
            tmp = []

    # connecting the two doubles
    tmp.append(thumb_place(1, 2, web_post_tr, 2, 'vertical'))
    tmp.append(thumb_place(1, 2, web_post_br, 2, 'vertical'))
    tmp.append(thumb_place(2, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(2, 2, web_post_bl, 2, 'vertical'))
    shape.append(triangle_hulls(tmp))
    tmp = []

    # connecting the double to the one above it
    tmp.append(thumb_place(1, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(1, 0, web_post_bl))
    tmp.append(thumb_place(1, 2, web_post_tr, 2, 'vertical'))
    tmp.append(thumb_place(1, 0, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    # connecting the 4 with the double in the bottom left
    tmp.append(thumb_place(1, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(1, 0, web_post_bl))
    tmp.append(thumb_place(0, 1, web_post_tr))
    tmp.append(thumb_place(0, 0, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    # connecting the two singles with middle double
    tmp.append(thumb_place(1, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(1, 2, web_post_bl, 2, 'vertical'))
    tmp.append(thumb_place(0, 1, web_post_br))
    tmp.append(thumb_place(0, 2, web_post_tr))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(1, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(0, 1, web_post_tr))
    tmp.append(thumb_place(0, 1, web_post_br))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(thumb_place(1, 2, web_post_bl, 2, 'vertical'))
    tmp.append(thumb_place(0, 2, web_post_tr))
    tmp.append(thumb_place(0, 2, web_post_br))
    shape.append(hull()(tmp))
    tmp = []


    # connecting the 1.5 with the doubles
    tmp.append(thumb_place(2, 2, web_post_tr, 2, 'vertical'))
    tmp.append(thumb_place(2, 2, web_post_br, 2, 'vertical'))
    tmp.append(thumb_place(3, 2, web_post_tl, 1.5, 'vertical'))
    tmp.append(thumb_place(3, 2, web_post_bl, 1.5, 'vertical'))
    shape.append(triangle_hulls(tmp))
    tmp = []

    # connecting the thumb to everything
    tmp.append(key_place(3, 4, web_post_bl))
    tmp.append(thumb_place(3, 2, web_post_tr, 1.5, 'vertical'))
    tmp.append(thumb_place(3, 2, web_post_br, 1.5, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(key_place(3, 4, web_post_tl))
    tmp.append(key_place(3, 4, web_post_bl))
    tmp.append(thumb_place(3, 2, web_post_tr, 1.5, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(thumb_place(3, 2, web_post_tr, 1.5, 'vertical'))
    tmp.append(key_place(3, 4, web_post_tl))
    tmp.append(key_place(2, 3, web_post_br))
    tmp.append(key_place(3, 3, web_post_bl))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(3, 2, web_post_tl, 1.5, 'vertical'))
    tmp.append(thumb_place(3, 2, web_post_tr, 1.5, 'vertical'))
    tmp.append(key_place(2, 3, web_post_bl))
    tmp.append(key_place(2, 3, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(2, 2, web_post_tr, 2, 'vertical'))
    tmp.append(thumb_place(3, 2, web_post_tl, 1.5, 'vertical'))
    tmp.append(key_place(1, 3, web_post_br))
    tmp.append(key_place(2, 3, web_post_bl))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(2, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(2, 2, web_post_tr, 2, 'vertical'))
    tmp.append(key_place(1, 3, web_post_bl))
    tmp.append(key_place(1, 3, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(2, 2, web_post_tl, 2, 'vertical'))
    tmp.append(thumb_place(1, 2, web_post_tr, 2, 'vertical'))
    tmp.append(key_place(1, 3, web_post_bl))
    tmp.append(thumb_place(1, 0, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(1, 0, web_post_br))
    tmp.append(thumb_place(1, 0, web_post_tr))
    tmp.append(key_place(1, 3, web_post_bl))
    tmp.append(key_place(1, 3, web_post_tl))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(1, 0, web_post_tr))
    tmp.append(key_place(1, 3, web_post_tl))
    tmp.append(key_place(0, 2, web_post_br))
    tmp.append(key_place(1, 2, web_post_bl))
    shape.append(triangle_hulls(tmp))
    tmp = []

    tmp.append(thumb_place(1, 0, web_post_tl))
    tmp.append(thumb_place(1, 0, web_post_tr))
    tmp.append(key_place(0, 2, web_post_bl))
    tmp.append(key_place(0, 2, web_post_br))
    shape.append(triangle_hulls(tmp))
    tmp = []

    return union()(shape)


# case
right_column = list(columns)[-1]
left_column = list(columns)[0]
front_row = list(rows)[-1]
back_row = list(rows)[0]

right_wall_column = right_column + 0.85
right_wall_offset = [0, -3, 0]
left_wall_offset = [0, 1, 0]
front_wall_offset = [0, 0, 0]
back_wall_offset = [0, -4, 1]


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
        rotate(15 * (center_row - row), X)(
            translate([0, 0, -row_radius])(
                shape
            )
        )
    )

    if column == right_column:
        column_offset = [-7.25, -5.8, 0]
    else:
        column_offset = [0, -3.35, 4.9]

    if row == back_row:
        row_offset = [0, 2.25, 0]
    else:
        row_offset = [0, 0, 0]

    if column == right_column and row == back_row:
        column_row_offset = [0, 2.25, 0]
    else:
        column_row_offset = [0, 0, 0]

    column_angle = 5 * (center_column - column)

    placed_shape = translate(row_offset)(
        translate(column_offset)(
            translate(column_row_offset)(
                translate([0, 0, column_radius])(
                    rotate(column_angle, Y)(
                        translate([0, 0, - column_radius])(
                            row_placed_shaped
                        )
                    )
                )
            )
        )
    )

    return translate([0, 0, 14.5])(
        rotate(15, Y)(
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
        rotate(15 * (thumb_center_row - row), X)(
            translate([0, 0, -row_radius])(
                shape
            )
        )
    )

    placed_shape = rotate(11.25, Z)(
        translate([mount_width, 0, 0])(
            translate([0, 0, column_radius])(
                rotate(5 * (thumb_center_column - column), Y)(
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


def wall_sphere_at(v, size):
    return translate(v)(
        sphere(d=size)
    )


def scale_to_range(start, end, x):
    return start + (end - start) * x


def wall_cube(front_to_back_scale, height):
    return wall_cube_at([0, scale_to_range(mount_height / -2 + -3.5, mount_height / 2 + 5, front_to_back_scale), height])


def wall_sphere(front_to_back_scale, height):
    return wall_sphere_at([0, scale_to_range(mount_height / -2 + -3.5, mount_height / 2 + 5, front_to_back_scale), height], 2.5)


wall_bottom_front = wall_sphere(0, -6)
wall_bottom_center = wall_sphere(1 / 2, -6)
wall_bottom_back = wall_sphere(1, -6)


def front_wall():
    shape = []
    tmp = []

    for column in columns[4:]:
        if column == center_column + 3:
            tmp.append(case_place(column - 1 / 2, front_row, translate(front_wall_offset)(wall_bottom_front)))
            tmp.append(case_place(right_wall_column, front_row, translate(front_wall_offset)(wall_bottom_front), 1.5))
            tmp.append(key_place(column, front_row, web_post_bl))
            tmp.append(key_place(column, front_row, web_post_br, 1.5))
        else:
            tmp.append(case_place(column - 1 / 2, front_row, translate(front_wall_offset)(wall_bottom_front)))
            tmp.append(case_place(column + 1 / 2, front_row, translate(front_wall_offset)(wall_bottom_front)))
            tmp.append(key_place(column, front_row, web_post_bl))
            tmp.append(key_place(column, front_row, web_post_br))
        shape.append(hull()(tmp))
        tmp = []

        tmp.append(case_place(column - 1 / 2, front_row, translate(front_wall_offset)(wall_bottom_front)))
        tmp.append(key_place(column, front_row, web_post_bl))
        tmp.append(key_place(column - 1, front_row, web_post_br))
        shape.append(hull()(tmp))
        tmp = []

    # left corner
    tmp.append(case_place(center_column, front_row, translate(front_wall_offset)(wall_bottom_front)))
    tmp.append(case_place(center_column + 1 / 2, front_row, translate(front_wall_offset)(wall_bottom_front)))
    tmp.append(key_place(center_column, front_row, web_post_bl))
    tmp.append(key_place(center_column, front_row, web_post_br))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def back_wall():
    shape = []
    tmp = []

    for column in columns:
        if column == center_column + 3:
            tmp.append(key_place(column, back_row, web_post_tr, 1.5))
            tmp.append(case_place(right_wall_column + 1 / 4, back_row, translate(back_wall_offset)(wall_bottom_back)))
        else:
            tmp.append(key_place(column, back_row, web_post_tr))
            tmp.append(case_place(column + 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)))
        tmp.append(case_place(column - 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)))
        tmp.append(key_place(column, back_row, web_post_tl))
        shape.append(hull()(tmp))
        tmp = []

    for column in columns[1:]:
        tmp.append(case_place(column - 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)))
        tmp.append(key_place(column, back_row, web_post_tl))
        tmp.append(key_place(column - 1, back_row, web_post_tr))
        shape.append(hull()(tmp))
        tmp = []

    return union()(shape)


def right_wall():
    shape = []
    tmp = []

    for row in rows[1:-1]:
        tmp.append(case_place(right_wall_column, row - 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5))
        tmp.append(case_place(right_wall_column, row + 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5))
        tmp.append(key_place(right_column, row, web_post_br, 1.5))
        tmp.append(key_place(right_column, row, web_post_tr, 1.5))
        shape.append(hull()(tmp))
        tmp = []

    for row in rows[:-1]:
        tmp.append(case_place(right_wall_column, row + 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5))
        tmp.append(key_place(right_column, row, web_post_br, 1.5))
        tmp.append(key_place(right_column, row + 1, web_post_tr, 1.5))
        shape.append(hull()(tmp))
        tmp = []

    # top corner
    tmp.append(case_place(right_wall_column, back_row + 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5))
    tmp.append(case_place(right_wall_column + 1 / 4, back_row, translate(back_wall_offset)(wall_bottom_back)))
    tmp.append(key_place(right_column, back_row, web_post_tr, 1.5))
    tmp.append(key_place(right_column, back_row, web_post_br, 1.5))
    shape.append(hull()(tmp))
    tmp = []

    # bottom corner
    tmp.append(case_place(right_wall_column, front_row - 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5))
    tmp.append(case_place(right_wall_column, front_row, translate(front_wall_offset)(wall_bottom_front), 1.5))
    tmp.append(key_place(right_column, front_row, web_post_tr, 1.5))
    tmp.append(key_place(right_column, front_row, web_post_br, 1.5))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def left_wall():
    shape = []
    tmp = []

    for row in rows[:-3]:
        tmp.append(case_place(left_column - 1 / 2, row + 1 / 2, translate(left_wall_offset)(wall_bottom_center)))
        tmp.append(key_place(left_column, row, web_post_bl))
        tmp.append(key_place(left_column, row + 1, web_post_tl))
        shape.append(hull()(tmp))
        tmp = []

    tmp.append(case_place(left_column - 1 / 2, center_row - 3 / 2, translate(left_wall_offset)(wall_bottom_center)))
    tmp.append(case_place(left_column - 1 / 2, center_row - 1 / 2, translate(left_wall_offset)(wall_bottom_center)))
    tmp.append(key_place(left_column, center_row - 1, web_post_tl))
    tmp.append(key_place(left_column, center_row - 1, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    # top corner
    tmp.append(case_place(left_column - 1 / 2, back_row + 1 / 2, translate(left_wall_offset)(wall_bottom_center)))
    tmp.append(case_place(left_column - 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)))
    tmp.append(key_place(left_column, back_row, web_post_tl))
    tmp.append(key_place(left_column, back_row, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    # bottom corner
    tmp.append(case_place(left_column - 1 / 2, center_row - 1 / 2, translate(left_wall_offset)(wall_bottom_center)))
    tmp.append(case_place(left_column - 1 / 2, center_row + 1 / 4, translate(left_wall_offset)(wall_bottom_center)))
    tmp.append(key_place(left_column, center_row, web_post_tl))
    tmp.append(key_place(left_column, center_row, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


thumb_right_column = list(thumb_columns)[-1]
thumb_left_column = list(thumb_columns)[0]
thumb_front_row = list(thumb_rows)[-1]
thumb_back_row = list(thumb_rows)[0]
thumb_right_wall_offset = [0, -3, 0]
thumb_left_wall_offset = [0, 0, 0]
thumb_front_wall_offset = [0, 2, 0]
thumb_back_wall_offset = [0, -2, 0]


def thumb_front_wall():
    shape = []
    tmp = []

    for column in thumb_columns:
        if column == 3:
            tmp.append(thumb_place(column, thumb_front_row, web_post_bl, 1.5, 'vertical'))
            tmp.append(thumb_place(column, thumb_front_row, web_post_br, 1.5, 'vertical'))
        elif column >= 1:
            tmp.append(thumb_place(column, thumb_front_row, web_post_bl, 2, 'vertical'))
            tmp.append(thumb_place(column, thumb_front_row, web_post_br, 2, 'vertical'))
        else:
            tmp.append(thumb_place(column, thumb_front_row, web_post_bl))
            tmp.append(thumb_place(column, thumb_front_row, web_post_br))

        tmp.append(thumb_case_place(column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))
        tmp.append(thumb_case_place(column - 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))
        shape.append(hull()(tmp))
        tmp = []


        if column == 2:
            tmp.append(thumb_place(column + 1, thumb_front_row, web_post_bl, 1.5, 'vertical'))
            tmp.append(thumb_place(column, thumb_front_row, web_post_br, 2, 'vertical'))
            tmp.append(thumb_case_place(column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))
        elif column == 1:
            tmp.append(thumb_place(column + 1, thumb_front_row, web_post_bl, 2, 'vertical'))
            tmp.append(thumb_place(column, thumb_front_row, web_post_br, 2, 'vertical'))
            tmp.append(thumb_case_place(column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))
        elif column == 0:
            tmp.append(thumb_place(column + 1, thumb_front_row, web_post_bl, 2, 'vertical'))
            tmp.append(thumb_place(column, thumb_front_row, web_post_br))
            tmp.append(thumb_case_place(column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))

        shape.append(hull()(tmp))
        tmp = []

    return union()(shape)


def thumb_back_wall():
    shape = []
    tmp = []

    # right corner
    tmp.append(thumb_case_place(1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back)))
    tmp.append(thumb_place(1, thumb_back_row, web_post_tl))
    tmp.append(key_place(left_column, center_row, web_post_bl))
    tmp.append(case_place(left_column - 1 / 2, center_row + 1 / 4, translate(left_wall_offset)(wall_bottom_center)))
    shape.append(hull()(tmp))
    tmp = []

    # center
    tmp.append(thumb_case_place(1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back)))
    tmp.append(thumb_place(thumb_left_column, thumb_back_row, web_post_tr))
    tmp.append(thumb_place(thumb_left_column + 1, thumb_back_row, web_post_tl))
    shape.append(hull()(tmp))
    tmp = []

    # left corner
    tmp.append(thumb_case_place(1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back)))
    tmp.append(thumb_case_place(-1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back)))
    tmp.append(thumb_place(thumb_left_column, thumb_back_row, web_post_tr))
    tmp.append(thumb_place(thumb_left_column, thumb_back_row, web_post_tl))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def thumb_inside_wall():
    shape = []
    tmp = []

    # front corner
    tmp.append(case_place(center_column, front_row, translate(front_wall_offset)(wall_bottom_front)))
    tmp.append(thumb_case_place(thumb_right_column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))
    tmp.append(key_place(center_column, front_row, web_post_bl))
    tmp.append(thumb_place(thumb_right_column, thumb_front_row, web_post_br, 1.5, 'vertical'))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def thumb_left_wall():
    shape = []
    tmp = []

    for row in thumb_rows[:-1]:
        tmp.append(thumb_case_place(thumb_left_column - 1 / 2, row + 1 / 2, wall_bottom_center))
        tmp.append(thumb_place(thumb_left_column, row, web_post_bl))
        tmp.append(thumb_place(thumb_left_column, row + 1, web_post_tl))
        shape.append(hull()(tmp))
        tmp = []

    tmp.append(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row - 1 / 2, wall_bottom_center))
    tmp.append(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row + 1 / 2, wall_bottom_center))
    tmp.append(thumb_place(thumb_left_column, thumb_center_row, web_post_bl))
    tmp.append(thumb_place(thumb_left_column, thumb_center_row, web_post_tl))
    shape.append(hull()(tmp))
    tmp = []

    # front corner
    tmp.append(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row + 1 / 2, wall_bottom_center))
    tmp.append(thumb_case_place(thumb_left_column - 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)))
    tmp.append(thumb_place(thumb_left_column, thumb_front_row, web_post_tl))
    tmp.append(thumb_place(thumb_left_column, thumb_front_row, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    # back corner
    tmp.append(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row - 1 / 2, wall_bottom_center))
    tmp.append(thumb_case_place(thumb_left_column - 1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back)))
    tmp.append(thumb_place(thumb_left_column, thumb_back_row, web_post_tl))
    tmp.append(thumb_place(thumb_left_column, thumb_back_row, web_post_bl))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


def top_case():
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


def bottom_key_guard(size=1, align='horizontal'):
    return translate([0, 0, -web_thickness - 5])(
        cube([mount_width, mount_height, web_thickness], center=True)
    )


def bottom_front_key_guard(size=1, align='horizontal'):
    return translate([0, mount_height / 4, -web_thickness - 5])(
        cube([mount_width, mount_height / 2, web_thickness], center=True)
    )


def shift_web_post_tl(size=1, align='horizontal'):
    return translate([0, 0, -web_thickness - 5])(web_post_tl(size=size, align=align))


def shift_web_post_tr(size=1, align='horizontal'):
    return translate([0, 0, -web_thickness - 5])(web_post_tr(size=size, align=align))


def shift_web_post_bl(size=1, align='horizontal'):
    return translate([0, 0, -web_thickness - 5])(web_post_bl(size=size, align=align))


def shift_web_post_br(size=1, align='horizontal'):
    return translate([0, 0, -web_thickness - 5])(web_post_br(size=size, align=align))


def half_post_tl(size=1, align='horizontal'):
    return translate([0, mount_height / 2, -web_thickness - 5])(web_post_tl(size=size, align=align))


def half_post_tr(size=1, align='horizontal'):
    return translate([0, mount_height / 2, -web_thickness - 5])(web_post_tr(size=size, align=align))


def half_post_bl(size=1, align='horizontal'):
    return translate([0, mount_height / 2, -web_thickness - 5])(web_post_bl(size=size, align=align))


def half_post_br(size=1, align='horizontal'):
    return translate([0, mount_height / 2, -web_thickness - 5])(web_post_br(size=size, align=align))


def bla(p, v=[0, 0, 0]):
    tmp = []
    tmp.append(p)
    tmp.append(translate(v)(linear_extrude(height=1)(projection()(p))))
    return tmp


def bottom_plate():
    shape = []
    tmp = []

    # front_wall
    for column in columns[4:]:
        if column == right_column:
            tmp.append(bla(case_place(column - 1 / 2, front_row, wall_bottom_front), [0, 2, 0]))
            tmp.append(bla(case_place(right_wall_column, front_row, wall_bottom_front, 1.5), [0, 2, 0]))
        else:
            tmp.append(bla(case_place(column - 1 / 2, front_row, wall_bottom_front), [0, 2, 0]))
            tmp.append(bla(case_place(column + 1 / 2, front_row, wall_bottom_front), [0, 2, 0]))
        shape.append(hull()(tmp))
        tmp = []

    # right wall
    for row in rows[1:-1]:
        tmp.append(bla(case_place(right_wall_column, row - 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5), [0, 0, 0]))
        tmp.append(bla(case_place(right_wall_column, row + 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5), [0, 0, 0]))
        shape.append(hull()(tmp))
        tmp = []

    # right front corner
    tmp.append(bla(case_place(right_wall_column, front_row - 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5), [0, 0, 0]))
    tmp.append(bla(case_place(right_wall_column, front_row, wall_bottom_front, 1.5), [0, 2, 0]))
    shape.append(hull()(tmp))
    tmp = []

    # right back corner
    tmp.append(bla(case_place(right_wall_column, back_row + 1 / 2, translate(right_wall_offset)(wall_bottom_center), 1.5), [0, 0, 0]))
    tmp.append(bla(case_place(right_wall_column, back_row, translate(back_wall_offset)(wall_bottom_back), 1.5), [0, -3, 0]))
    shape.append(hull()(tmp))
    tmp = []

    # back wall
    for column in columns:
        if column == right_column:
            tmp.append(bla(case_place(column - 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)), [0, -7 + column - 1 / 2, 0]))
            tmp.append(bla(case_place(right_wall_column, back_row, translate(back_wall_offset)(wall_bottom_back), 1.5), [0, -3, 0]))
        else:
            tmp.append(bla(case_place(column - 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)), [0, -7 + column - 1 / 2, 0]))
            tmp.append(bla(case_place(column + 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)), [0, -7 + column + 1 / 2, 0]))
        shape.append(hull()(tmp))
        tmp = []

    # left wall
    for row in rows[1:-3]:
        tmp.append(bla(case_place(left_column - 1 / 2, row - 1 / 2, translate(left_wall_offset)(wall_bottom_center)), [2, 0, 0]))
        tmp.append(bla(case_place(left_column - 1 / 2, row + 1 / 2, translate(left_wall_offset)(wall_bottom_center)), [2, 0, 0]))
        shape.append(hull()(tmp))
        tmp = []

    tmp.append(bla(case_place(left_column - 1 / 2, back_row, translate(back_wall_offset)(wall_bottom_back)), [0, -7 - 1 / 2, 0]))
    tmp.append(bla(case_place(left_column - 1 / 2, back_row + 1 / 2, translate(left_wall_offset)(wall_bottom_center)), [2, 0, 0]))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(bla(case_place(left_column - 1 / 2, center_row - 1 / 2, translate(left_wall_offset)(wall_bottom_center)), [2, 0, 0]))
    tmp.append(bla(case_place(left_column - 1 / 2, center_row + 1 / 4, translate(left_wall_offset)(wall_bottom_center)), [2, 0, 0]))
    shape.append(hull()(tmp))
    tmp = []

    # left thumb wall
    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row - 1 / 2, wall_bottom_center), [2, 0, 0]))
    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row + 1 / 2, wall_bottom_center), [2, 0, 0]))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back), [2, 0, 0])))
    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row - 1 / 2, wall_bottom_center), [2, 0, 0]))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_center_row + 1 / 2, wall_bottom_center), [2, 0, 0]))
    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front), [2, 0, 0])))
    shape.append(hull()(tmp))
    tmp = []

    # thumb front wall
    for column in thumb_columns:
        tmp.append(bla(thumb_case_place(column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)), [0, 0, 0]))
        tmp.append(bla(thumb_case_place(column - 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)), [0, 0, 0]))
        shape.append(hull()(tmp))
        tmp = []

    # thumb back wall
    tmp.append(bla(thumb_case_place(thumb_left_column - 1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back), [2, 0, 0])))
    tmp.append(bla(thumb_case_place(thumb_left_column + 1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back), [2, 0, 0])))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(bla(case_place(left_column - 1 / 2, center_row + 1 / 4, translate(left_wall_offset)(wall_bottom_center)), [2, 0, 0]))
    tmp.append(bla(thumb_case_place(thumb_left_column + 1 / 2, thumb_back_row, translate(thumb_back_wall_offset)(wall_bottom_back), [2, 0, 0])))
    shape.append(hull()(tmp))
    tmp = []

    # thumb inner wall
    tmp.append(bla(thumb_case_place(thumb_right_column + 1 / 2, thumb_front_row, translate(thumb_front_wall_offset)(wall_bottom_front)), [0, 0, 0]))
    tmp.append(bla(case_place(center_column, front_row, translate(front_wall_offset)(wall_bottom_front)), [0, 2, 0]))
    shape.append(hull()(tmp))
    tmp = []

    tmp.append(bla(case_place(center_column + 1 / 2, front_row, translate(front_wall_offset)(wall_bottom_front)), [0, 2, 0]))
    tmp.append(bla(case_place(center_column, front_row, translate(front_wall_offset)(wall_bottom_front)), [0, 2, 0]))
    shape.append(hull()(tmp))
    tmp = []

    return union()(shape)


if __name__ == '__main__':
    a = key_layout(plate)
    a.add(thumb_layout(plate))
    a.add(key_connectors())
    a.add(thumb_connectors())
    a.add(key_layout(dsa_key_cap))
    a.add(thumb_layout(dsa_key_cap))
    a.add(top_case())
    a.add(bottom_plate())

    scad_render_to_file(a, '../things/dactyl.scad', file_header='$fn = %s;' % SEGMENTS, include_orig_code=False)
