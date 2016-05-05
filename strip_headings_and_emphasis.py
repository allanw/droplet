#!/usr/bin/env python

from pandocfilters import walk, toJSONFilter, Str, Emph, Para, stringify
from caps import caps

def strip_headings_and_emphasis(key, val, fmt, meta):
    if key == 'Strong' or key == 'Emph':
        return walk(val, caps, fmt, meta)
    if key == 'Header' and len(val[2]):
        return Para([Emph(val[2])] + [Str('\n')] + [Str('=')]*len(stringify(val)))

if __name__ == "__main__":
    toJSONFilter(strip_headings_and_emphasis)
