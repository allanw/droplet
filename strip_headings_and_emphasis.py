#!/usr/bin/env python

from pandocfilters import walk, toJSONFilter, Str, Emph, Para
from caps import caps

def strip_headings_and_emphasis(key, val, fmt, meta):
    if key == 'Strong' or key == 'Emph':
        return walk(val, caps, fmt, meta)

if __name__ == "__main__":
    toJSONFilter(strip_headings_and_emphasis)
