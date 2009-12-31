#!/usr/bin/env python
"""Nobody has animations for all the Emerald Unown variations!

Now we do.

This script is similar to pad-and-..., except it generates the same animation
pattern for a variety of static sprites.  Requires ImageMagick.

Assumes the following:
- orig-animated/201.gif is an autocropped Unown animation.
- 201.png is an uncropped static first frame of the same Unown form.
- 201-*.png are uncropped static first frames of every Unown form.
- shiny/201-*.png are shiny versions of the above.
- animated/ and shiny/animated/ are writeable.
"""

from __future__ import division
import glob
import os
import subprocess

# PIL apparently sucks at animated GIFs for reasons I don't care to
# investigate, so the following list of frame offsets was collected manually.
# Eh.
frame_offsets = [
    (0, 0),
    (-1, -1),
    (-3, -3),
    (-5, -5),
    (-4, -6),
    (0, -6),
    (4, -6),
    (4, -4),
    (0, 0),
    (-4, 4),
    (-4, 6),
    (0, 6),
    (4, 6),
    (4, 4),
    (0, 0),
    (-4, -4),
    (-4, -6),
    (0, -6),
    (4, -6),
    (4, -4),
    (0, 0),
    (-4, 4),
    (-4, 6),
    (0, 6),
    (4, 6),
    (5, 5),
    (3, 3),
    (1, 1),
    (0, 0),
]

for shiny in (True, False):
    # Fair warning: this DOES NOT WORK with ? and may overwrite others.  I had
    # to move 201-?.png to 201-qm.png.
    for letter in "abcdefghijklmnopqrstuvwxyz?!":
        source = "201-{0}.png".format(letter)
        dest = "animated/201-{0}.gif".format(letter)

        if shiny:
            source = "shiny/" + source
            dest = "shiny/" + dest

        # Feedback is nice
        print source

        # Construct a big complicated ImageMagick command for slapping this all
        # together.  gifsicle would probably also work, but I would need to convert the
        # source PNG to GIF first anyway, so whatever.
        command = [
            'convert',
            '-dispose', 'Background',   # frame disposal
            '-loop', '0',               # loop forever

            # First frame.  Needs some special jutsu to force a 96x96 square,
            # as the first frame sets the entire image's size.
            '-delay', '8',
            '-page', '96x96+16+16',
            source,
        ]

        # Add intermediate frames
        for i, (x, y) in enumerate(frame_offsets[1:]):
            page_x = x + 16
            page_y = y + 16

            delay = '2'
            if i == len(frame_offsets) - 2:
                # Last frame hangs around for much longer
                delay = '225'

            command += [
                '-delay', delay,
                '-page', "{0:+d}{1:+d}".format(page_x, page_y),
                source,
            ]

        # Add final filename
        command += [ dest ]

        # Run it!
        subprocess.call(command)
