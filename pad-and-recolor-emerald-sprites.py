#!/usr/bin/env python
"""The Emerald animations floating around the Web as of today have two major
problems.

One: They are all autocropped.
Two: There are no shiny animations.

This script fixes both of those problems.  It requires uncropped static sprites
to figure out how to pad the animated sprite, and a shiny static sprite to
figure out the colors for a shiny animated sprite.

Requires PIL for obvious reasons.  Also requires ImageMagick, because PIL
sucks.
"""

from __future__ import division
import glob
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


for n in [133]:
    # Keep us posted on status here
    print n

    static_normal = Image.open('%d.png' % n)
    static_shiny = Image.open('%d-shiny.png' % n)

    anim_original = Image.open('%d.gif' % n)

    static_x, static_y = first_pixel(static_normal)
    anim_x, anim_y = first_pixel(anim_original)

    left_margin = static_x - anim_x
    top_margin = static_y - anim_y

    subprocess.call(['convert', '%d.gif' % n, '-background', 'none', '-extent', "64x64-%d-%d" % (left_margin, top_margin), '%d-fixed.gif' % n])

    # Time for stage 2: creating the shiny version.
    anim_original = None
    anim_normal = Image.open('%d-fixed.gif' % n)

    shiny_colors = {}
    normal_data = static_normal.load()
    shiny_data = static_shiny.load()
    for x in range(64):
        for y in range(64):
            normal_px = normal_data[x, y]
            shiny_px = shiny_data[x, y]
            if normal_px in shiny_colors and shiny_colors[normal_px] != shiny_px:
                print shiny_colors, normal_px, shiny_px
                raise ValueError
            shiny_colors[normal_px] = shiny_px

    # Now we have a dictionary of old colors => new colors.  Okay, now what?
    # Unfortunately, it seems the only way to do a palette swap all at once with
    # either PIL or ImageMagick is to use a lot of ternary expressions with -fx
    # and the ?: operator.
    # So let's just do that.
    fx_chunk = "(abs(r - %f) < 0.0001 && abs(g - %f) < 0.0001 && abs(b - %f) < 0.0001) ? rgb(%d, %d, %d)"
    fx_chunks = ["a == 0 ? p"]
    for normal_px, shiny_px in shiny_colors.items():
        vals = list([_ / 255 for _ in normal_px[0:3]]) + list(shiny_px[0:3])
        fx_chunks.append(fx_chunk % tuple(vals))
    fx_chunks.append("rgb(255, 0, 255)")  # default fallback: magenta
    fx = ' : '.join(fx_chunks)

    # -fx operates on every image at once, which isn't going to work so well for
    # us, alas.  We have to operate on every frame individually, then stitch it
    # together with the same options as the original.  Sigh.
    subprocess.call(['convert', '%d-fixed.gif' % n, '+adjoin', '%d-parts%03d.gif' % n])
    parts = glob.glob('%d-parts*.gif' % n)
    parts.sort()  # keep frames in the right order...
    for part in parts:
        subprocess.call(['convert', part, '-fx', fx, part])

    subprocess.call(['convert'] + parts + ['-loop', '0', '%d-shiny.gif' % n])
