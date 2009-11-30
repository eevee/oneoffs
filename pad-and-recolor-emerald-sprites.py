#!/usr/bin/env python
"""The Emerald animations floating around the Web as of today have two major
problems.

One: They are all autocropped.
Two: There are no shiny animations.

This script fixes both of those problems.  It requires uncropped static sprites
to figure out how to pad the animated sprite, and a shiny static sprite to
figure out the colors for a shiny animated sprite.

Requires PIL for obvious reasons.  Also requires gifsicle.

Relies on the file arrangement I'm already using:
- Current directory contains regular 64x64 sprites.
- A directory called `shiny` contains shiny versions of the above.
- A directory called `orig-animated` contains cropped animations.
- `animated/` and `shiny/animated/` exist.  These will be populated.
"""

from __future__ import division
import glob
import os
import subprocess

from PIL import Image

def first_pixel(image):
    """Returns (x, y) of the first non-transparent pixel found by scanning from
    the top-left of the image, across then down.
    """

    (w, h) = image.size
    data = image.convert('RGBA').load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]
            if a != 0:
                return x, y


for n in range(328, 387):
    # Keep us posted on status here
    print n

    static_normal = Image.open('%d.png' % n)
    static_shiny = Image.open('shiny/%d.png' % n)

    anim_original = Image.open('orig-animated/%d.gif' % n)

    static_x, static_y = first_pixel(static_normal)
    anim_x, anim_y = first_pixel(anim_original)

    left_margin = static_x - anim_x
    top_margin = static_y - anim_y

    subprocess.call([
        'gifsicle',
        # Expand canvas to 96x96
        '--screen', '96x96',
        # Reposition the entire image appropriately
        '--position', "{0},{1}".format(16 + left_margin,
                                       16 + top_margin),
        # Crush the hell out of it
        '--optimize',

        "orig-animated/{0}.gif".format(n),
        '--output', "animated/{0}.gif".format(n),
    ])

    # Time for stage 2: creating the shiny version.
    anim_original = None
    anim_normal = Image.open('animated/%d.gif' % n)

    shiny_colors = {}
    normal_data = static_normal.load()
    shiny_data = static_shiny.load()
    try:
        for x in range(64):
            for y in range(64):
                normal_px = normal_data[x, y]
                shiny_px = shiny_data[x, y]
                if normal_px in shiny_colors and shiny_colors[normal_px] != shiny_px:
                    print """  BAILING: {normal} maps to {shiny} at ({x}, {y}) but was already {previous_shiny}""" \
                        .format(x=x, y=y,
                                normal=normal_px,
                                shiny=shiny_px,
                                previous_shiny=shiny_colors[normal_px])
                    raise ValueError
                shiny_colors[normal_px] = shiny_px
    except ValueError:
        continue

    # Now we have a dictionary of old colors => new colors.  Lucky for me,
    # gifsicle can also swap colors!
    color_swap_args = []
    for normal, shiny in shiny_colors.items():
        if normal[3] == 0:
            continue
        color_swap_args.append('--change-color')
        color_swap_args.append("#{0:02x}{1:02x}{2:02x}".format(*normal))
        color_swap_args.append("#{0:02x}{1:02x}{2:02x}".format(*shiny))

    subprocess.call(
        [ 'gifsicle' ]
        + color_swap_args +
        [
            "animated/{0}.gif".format(n),
            '--output', "shiny/animated/{0}.gif".format(n),
        ]
    )
