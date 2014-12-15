"""Find common substrings.

"""

import numpy as np
from itertools import product, combinations
from .ccss import allcommonsubstrings as _acss
from .corpus import Interval, FragmentToken

def pairwise_substring_completion(fragment1, fragment2, corpus,
                                  minlength, maxlength):
    name1, name2 = fragment1.name, fragment2.name
    tokenseq1 = [(f.mark, f.interval)
                 for f in corpus.tokens(name1, fragment1.interval)]
    tokenseq2 = [(f.mark, f.interval)
                 for f in corpus.tokens(name2, fragment2.interval)]
    for seq1, seq2 in product(substrings(tokenseq1, minlength, maxlength),
                              substrings(tokenseq2, minlength, maxlength)):
        submark1, intervalseq1 = zip(*seq1)
        submark2, intervalseq2 = zip(*seq2)
        interval1 = Interval(intervalseq1[0].start, intervalseq1[-1].end)
        interval2 = Interval(intervalseq2[0].start, intervalseq2[-1].end)
        yield (FragmentToken(name1, interval1, submark1),
               FragmentToken(name2, interval2, submark2))

# def pairwise_substring_completion(pair, corpus, minlength, maxlength):
#     """Generate the substring completions of a pair.

#     Parameters
#     ----------
#     pair : ((ClassID, FragmentToken), (ClassID, FragmentToken)) tuple
#     corpus : Corpus

#     Returns
#     -------
#     i : iterator over pairs of ((ClassID, FragmentToken), (ClassID, FragmentToken))

#     """
#     (classID1, token1), (classID2, token2) = pair
#     name1 = token1.name
#     name2 = token2.name

#     tokenseq1 = [(x.mark, x.interval)
#                  for x in corpus.tokens(name1, token1.interval)]
#     tokenseq2 = [(x.mark, x.interval)
#                  for x in corpus.tokens(name2, token2.interval)]

#     for seq1, seq2 in product(substrings(tokenseq1, minlength, maxlength),
#                               substrings(tokenseq2, minlength, maxlength)):
#         submark1, intervalseq1 = zip(*seq1)
#         submark2, intervalseq2 = zip(*seq2)
#         interval1 = Interval(intervalseq1[0].start, intervalseq1[-1].end)
#         interval2 = Interval(intervalseq2[0].start, intervalseq2[-1].end)

#         yield ((classID1, FragmentToken(name1, interval1, submark1)),
#                (classID2, FragmentToken(name2, interval2, submark2)))


def substrings(s, minlength, maxlength):
    """Generate all substrings of s.

    Parameters
    ----------
    s : iterable
    minlength : minimum length of substrings

    Returns
    -------
    i : iterator over substrings of s

    """
    for start, end in combinations(xrange(len(s)+1), 2):
        if minlength <= end - start <= maxlength:
            yield s[start: end]



def allcommonsubstrings(s1, s2=None, minlength=3, maxlength=20, same=False):
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

    css = _acss(s1_arr, s2_arr, minlength, maxlength, same)
    if css is None:
        return []

    r = []
    for row in css:
        r.append((slice(row[0], row[0]+row[2]),
                  slice(row[1], row[1]+row[2])))
    return r
