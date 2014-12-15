from __future__ import division

from itertools import chain
from collections import defaultdict

import numpy as np

_flatten = chain.from_iterable

class Boundaries(object):
    def __init__(self, container):
        if hasattr(container, 'iter_fragments'):
            iterator = container.iter_fragments()
        else:
            iterator = (f for f in container)

        bounds = defaultdict(list)
        for fragment in iterator:
            bounds[fragment.name].append(fragment.interval)
        self.bounds = {}
        for name, intervals in bounds.iteritems():
            points = set(_flatten((interval.start, interval.end)
                                  for interval in intervals))
            self.bounds[name] = np.sort(np.array(list(points)))

    def has_close(self, name, query_point):
        if not name in self.bounds:
            b = False
        else:
            points = self.bounds[name]
            ix = np.searchsorted(points, query_point, side='left')
            if ix == 0 or ix == points.shape[0] - 1:
                found_point = points[ix]
            elif ix == points.shape[0]:
                found_point = points[ix-1]
            elif query_point - points[ix-1] < points[ix] - query_point:
                found_point = points[ix-1]
            else:
                found_point = points[ix]
            b = np.abs(found_point - query_point) < 0.03
        return b

    def __iter__(self):
        for name, points in self.bounds.iteritems():
            for point in points:
                yield name, point

def eval_from_bounds(disc, gold):
    prec = np.fromiter((gold.has_close(n, p)
                        for n, p in disc),
                       dtype=np.bool).mean()
    rec = np.fromiter((disc.has_close(n, p)
                       for n, p in gold),
                      dtype=np.bool).mean()
    return prec, rec


def evaluate_boundaries(disc_clsdict, corpus):
    disc = Boundaries(disc_clsdict)
    gold = Boundaries(corpus)
    return eval_from_bounds(disc, gold)
