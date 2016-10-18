#!/usr/bin/env python3

import math
import png
import sys

from collections import Counter
from itertools import islice
from random import shuffle

# generates n-sized subtuples of an iterator
def groups(iterable, group_size):
    gen = (x for x in iterable)
    while True:
        try:
            group = tuple(islice(gen, group_size))
            if not group:
                break
            yield group
        except StopIteration:
            break

def get_rgba_pixels(rows) -> (('r', 'g', 'b', 'a')):
    for row in rows:
        for pixel in groups(row, 4):
            yield pixel

def n_downsample(byte, amount, minimum, maximum):
    if amount < 1:
        return byte

    # since we round down, add half of the quantization for a fair round
    byte += 1 << (amount - 1)
    byte = (byte >> amount) << amount

    if byte > maximum:
        return maximum
    elif byte < minimum:
        return minimum
    else:
        return byte

def n_downsample_pixels(pixels, amount):
    for pixel in pixels:
        yield tuple([ n_downsample(v, amount, 0, 0xff) for v in pixel ])

def sorted_png(infile: 'file', outfile: 'file', downsample=0, reshape=None, ordering="freq"):
    r = png.Reader(infile)
    width, height, rows = r.read()[:3]

    # if we want to create a square image, calculate equal-area dimensions,
    # though we may end up with less area. this means our pixel list may be too
    # long, but this is safe; Writer.write_array will just silently discard
    # those bytes.
    if reshape == "square":
        width = height = math.floor(math.sqrt(width * height))

    elif reshape == "tall":
        width, height = min(width, height), max(width, height)

    elif reshape == "wide":
        width, height = max(width, height), min(width, height)

    # sort pixels by frequency in image
    c = Counter(n_downsample_pixels(get_rgba_pixels(rows), downsample))

    bitmap = []
    frequencies = c.most_common()

    # if we want, put down the pixel clusters in a random order
    if ordering == "shuf":
        shuffle(frequencies)

    elif ordering in ("light", "dark"):
        frequencies.sort(key=lambda x: sum([ v for v in x[0][:3]]),
                         reverse=(ordering == "light"))

    elif ordering == "rfreq":
        frequencies.reverse()

    # write the pixels to the image
    for pixel, n in frequencies:
        for _ in range(n):
            bitmap.extend(pixel)

    png.Writer(width, height, alpha=True).write_array(outfile, bitmap)

def poparg(flag, default=None, boolean=False):
    try:
        i = sys.argv.index(flag, 1)
        del sys.argv[i]
        return sys.argv.pop(i)
    except ValueError:
        return default

def popflag(flag):
    try:
        sys.argv.remove(flag)
        return True
    except ValueError:
        return False

def main():

    # how much should we downsample the image?
    downsample = int(poparg("-d", default=0))

    # how should we reshape the image?
    resize = poparg("-r", default=None)

    # how should we order the pixel clusters?
    ordering = poparg("-o", default="freq")

    # input image, or stdin
    infile = sys.argv[1]
    if infile == '-':
        infile = sys.stdin.buffer
    else:
        infile = open(infile, 'rb')

    # output file, or stdout
    outfile = sys.argv[2]
    if outfile == '-':
        outfile = sys.stdout.buffer
    else:
        outfile = open(outfile, 'wb')

    # display the image
    sorted_png(infile, outfile, downsample, resize, ordering)

try:
    main()
except (Exception, KeyboardInterrupt):
    print('''\
Usage: {} [-d 1-8] [-r RESHAPE_MODE] [-o ORDERING] INFILE OUTFILE

Creates a PNG image with the same pixels as the input, but in a different
order. By default, sorts same-pixel clusters by frequency.
    
Options:
    -d      Downsample colors by n bits where 0 <= n <= 8 (default: 0)
    -r      Reshape the output image (default: none)
    -o      Order the output in a different way (default: freq)

Orderings:
    freq    (default) Most common pixels first
    rfreq   Least common pixels first
    shuf    Like freq, but shuffle the color clusters
    light   Lightest pixels first
    dark    Darkest pixels first

Reshape modes:
    none    (default) Output is the same dimensions as the input
    square  Output is a square of (approximately) equal-area to the input
    tall    Output height is the taller of the input dimensions
    wide    Output width is the taller of the input dimensions
    '''.format(sys.argv[0]))
    sys.exit(1)
