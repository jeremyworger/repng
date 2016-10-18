# repng

Creates a PNG image with the same pixels as the input, but in a different order. By default, sorts same-pixel clusters by frequency.

    Usage: python repng.py [-d 1-8] [-r RESHAPE_MODE] [-o ORDERING] INFILE OUTFILE

## Options:

  - `-d`: Downsample colors by n bits where 0 <= n <= 8 (default: 0)
  - `-r`: Reshape the output image (default: none)
  - `-o`: Order the output in a different way (default: freq)

## Orderings:

  - `freq`: (default) Most common pixels first
  - `rfreq`: Least common pixels first
  - `shuf`: Like freq, but shuffle the color clusters
  - `light`: Lightest pixels first
  - `dark`: Darkest pixels first

## Reshape modes:

  - `none`: (default) Output is the same dimensions as the input
  - `square`: Output is a square of (approximately) equal-area to the input
  - `tall`: Output height is the taller of the input dimensions
  - `wide`: Output width is the taller of the input dimensions

---

Copyright (c) 2016 Quint Guvernator by the GNU GPL v3, see the file `LICENSE` for details.
