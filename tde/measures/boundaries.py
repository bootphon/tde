from __future__ import division

from collections import defaultdict

import numpy as np

from tde.util.functions import flatten

class Boundaries(object):
    def __init__(self, container, threshold=0.03):
        self.threshold = threshold
        if hasattr(container, 'iter_fragments'):
            iterator = container.iter_fragments()
        else:
            iterator = (f for f in container)

        bounds = defaultdict(list)
        length = 0
        for fragment in iterator:
            bounds[fragment.name].append(fragment.interval)
            length += 1
        self.length = length
        self.bounds = {}
        for name, intervals in bounds.iteritems():
            points = set(flatten((interval.start, interval.end)
                                  for interval in intervals))
            self.bounds[name] = np.sort(np.array(list(points)))

    def __len__(self):
        return self.length

    def has_close(self, name, query_point):
        if not name in self.bounds:
            b = False
        else:
            points = self.bounds[name]
            ix = np.searchsorted(points, query_point, side='left')
            if ix == 0:
                found_point = points[0]
            elif ix == points.shape[0]:
                found_point = points[-1]
            elif query_point - points[ix-1] < points[ix] - query_point:
                found_point = points[ix-1]
            else:
                found_point = points[ix]
            b = np.abs(found_point - query_point) < self.threshold
        return b

    def __iter__(self):
        for name, points in self.bounds.iteritems():
            for point in points:
                yield name, point

def eval_from_bounds(disc, gold):
    gold_close = np.fromiter((gold.has_close(n, p)
                              for n, p in disc),
                             dtype=np.bool)
    if gold_close.shape[0] > 0:
        prec = gold_close.mean()
        if not np.isfinite(prec):
            prec = 0.
    else:
        prec = 0.

    disc_close = np.fromiter((disc.has_close(n, p)
                              for n, p in gold),
                             dtype=np.bool)
    if disc_close.shape[0] > 0:
        rec = disc_close.mean()
        if not np.isfinite(rec):
            rec = 0.
    else:
        rec = 0.
    return prec, rec


def evaluate_boundaries(disc_clsdict, corpus):
    disc = Boundaries(disc_clsdict)
    gold = Boundaries(corpus)
    return eval_from_bounds(disc, gold)
