#!/usr/bin/env python
import math

def large_number(n, short=False):
    """ Return human readable large numbers. """
    millnames = ['','k','m','bn','tn']
    try:
        n = float(n)
        millidx = max(0, min(len(millnames)-1,
        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    except TypeError:
        return '?'