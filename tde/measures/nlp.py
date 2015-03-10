from __future__ import division

from collections import defaultdict

import numpy as np

from tde.substrings.levenshtein import distance
from tde.data.interval import Interval

def NED(clsdict):
    neds = np.fromiter((ned(f1.mark, f2.mark)
                        for f1, f2 in clsdict.iter_pairs(within=True,
                                                         order=False)),
                       dtype=np.double)
    if len(neds) == 0:
        r = np.nan
    else:
        r = neds.mean()
    return r

class Node(object):
    def __init__(self, value):
        self.value = value
        self.links = set()

    def add_link(self, other):
        self.links.add(other)
        other.links.add(self)

def connected(nodes):
    """
    Yield connected groups in a set of nodes.

    Simple linked-list implementation of Connected-Components (CLSR p.564)

    Parameters
    ----------
    nodes : list of Nodes

    Returns
    -------
    Iterator over lists of Nodes
    """
    nodes = set(nodes)
    while nodes:
        n = nodes.pop()
        group = {n}
        queue = [n]
        while queue:
            n = queue.pop(0)
            neighbors = n.links
            neighbors -= group
            nodes -= neighbors
            group.update(neighbors)
            queue.extend(neighbors)
        yield group

def collapse(intervals):
    """
    Compute the union of a list of intervals.

    The union of intervals is defined as the set-theoretic union
    for intervals that overlap and concatenation for intervals that don't.

    Parameters
    ----------
    intervals : list of Intervals

    Returns
    -------
    list of Intervals

    """
    intervals = sorted(intervals, key=lambda x: x.start)
    nodes = [Node(i) for i in intervals]
    for i in xrange(len(intervals)):
        for j in xrange(i+1, len(intervals)):
            i1 = intervals[i]
            i2 = intervals[j]
            if not i2.is_right_adjacent_to(i1) and i2.start > i1.end:
                break
            if i1.overlap(i2) > 0 or i1.is_adjacent(i2):
                nodes[i].add_link(nodes[j])
    r = []
    for c in connected(nodes):
        starts, ends = zip(*(node.value for node in c))
        r.append(Interval(min(starts), max(ends)))
    return sorted(r, key=lambda x: x.start)


def cover(clsdict):
    """Compute the cover.

    Parameters
    ----------
    clsdict : ClassDict

    Returns
    -------
    float
        Absolute coverage
    """
    c = defaultdict(list)
    for f in clsdict.iter_fragments():
        c[f.name].append(f.interval)
    c = {k: collapse(v) for k, v in c.iteritems()}
    return sum(interval.length() for v in c.itervalues() for interval in v)


def coverage(disc_clsdict, gold_clsdict):
    """Compute the coverage of disc_clsdict relative to gold_clsdict

    Parameters
    ----------
    disc_clsdict, gold_clsdict : ClassDict

    Returns
    -------
    float
        Relative coverage
    """
    num = cover(disc_clsdict)
    den = cover(gold_clsdict)
    if np.isclose(den, 0.) or np.isclose(num, 0):
        c = np.nan
    else:
        c = num  / den
    return c


def ued(s1, s2):
    """Unnormalized edit distance.

    Calculate the levenshtein distance between s1 and s2.

    Parameters
    ----------
    s1, s2 : iterable

    Returns
    -------
    r : np.uint32
        edit distance
    """
    symbols = list(set(s1+s2))
    symbol2ix = {v: k for k, v in enumerate(symbols)}

    s1_arr = np.fromiter((symbol2ix[s] for s in s1), dtype=np.uint32)
    s2_arr = np.fromiter((symbol2ix[s] for s in s2), dtype=np.uint32)

    return distance(s1_arr, s2_arr)

def ned(s1, s2):
    """Normalized edit distance.

    Calculate the levenshtein distance between s1 and s2 divided by the maximum
    of the lengths of s1 and s2.

    Parameters
    ----------
    s1, s2 : iterable


    Returns
    -------
    r : double
        edit distance
    """
    return ued(s1, s2) / max(len(s1), len(s2))
