"""Find common substrings.

"""

import numpy as np
import ccss

def allcommonsubstrings(s1, s2=None, minlength=3, same=False):
    """Find all common substrings.

    The algorithm used is a simple dp. This could be sped up by using
    suffix trees.

    Parameters
    ----------
    s1 : iterable
    s2 : iterable, optional
    minlength : int, optional
        minimum length of substrings

    Returns
    -------
    r : list of (Slice, Slice)
        Indices into `s1` and `s2`

    """
    if s2 is None or same:
        symbols = sorted(list(set(s1)))
    else:
        symbols = sorted(list(set(s1 + s2)))

    if s2 is None or same:
        s2 = s1
        same = 1
    else:
        same = 0

    if s1 == [] or s2 == []:
        return []

    sym2idx = {v: k for k, v in enumerate(symbols)}

    s1_arr = np.fromiter((sym2idx[s] for s in s1), dtype=np.long)
    s2_arr = np.fromiter((sym2idx[s] for s in s2), dtype=np.long)

    css = ccss.allcommonsubstrings(s1_arr, s2_arr, minlength, same)
    if css is None:
        return []

    r = []
    for row in css:
        r.append((slice(row[0], row[0]+row[2]),
                  slice(row[1], row[1]+row[2])))
    return r
