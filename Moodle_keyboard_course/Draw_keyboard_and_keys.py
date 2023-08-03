#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# pip install drawsvg
# pip install "drawsvg[all]" # for all raster images
# pip install scour

import drawsvg as draw
from scour import scour
from scour.scour import parse_args as parse_args


def optimize_svg(svg):
    scouroptions = parse_args([
        "--shorten-ids",
        "--indent=none",
        "--no-line-breaks"])

    scour_options = scour.sanitizeOptions(scouroptions)
    scour_options.remove_metadata = True
    return scour.scourString(svg, options=scour_options)


def draw_key(key):
    d = draw.Drawing(50, 50, origin=(0, 0))
    d.append(draw.Rectangle(0, 0, 50, 50, rx='7', ry='7', stroke='black', fill='white'))
    d.append(draw.Text(key, font_size=40, x=25, y=40, text_anchor='middle', font_family='Times New Roman'))
    return d.as_svg()


def draw_keyboard():
    d = draw.Drawing(840, 210, origin=(0, 0))

    # Draw empty keys
    for j in range(0, 3):
        z = {0: 12, 1: 11, 2: 9}
        for i in range(0, z[j]):
            d.append(draw.Rectangle(j*35+10+70*i, 10+j*70, 50, 50, rx='7', ry='7', stroke='black', fill='white'))

    # Add relief for F and J
    d.append(draw.Line(275, 115, 285, 115, stroke='black',  stroke_width=2))
    d.append(draw.Line(485, 115, 495, 115, stroke='black', stroke_width=2))
    return d.as_svg()


def save_svg(svg_filename, svg_text):
    # Make dir if not exist
    if not os.path.exists(os.path.split(svg_filename)[0]):
        os.makedirs(os.path.split(svg_filename)[0])

    with open(svg_filename, 'w') as o:
        o.write(svg_text)


keyboard_dir = 'data/keyboard'

for k in range(ord('A'), ord('Z')+1):
    save_svg('{0}/{1}/key_{1}_{2}.svg'.format(keyboard_dir, 'en', chr(k)), optimize_svg(draw_key(chr(k))))

for k in range(ord('А'), ord('Я')+1):
    save_svg('{0}/{1}/key_{1}_{2}.svg'.format(keyboard_dir, 'ru', chr(k)), optimize_svg(draw_key(chr(k))))


save_svg('{}/keyboard.svg'.format(keyboard_dir), optimize_svg(draw_keyboard()))
