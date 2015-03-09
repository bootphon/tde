#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------
# file: group.py
# author:
# Maarten Versteegh
# github.com/mwv
# maartenversteegh AT gmail DOT com
#
# Licensed under GPLv3
# ------------------------------------
"""group: evaluate grouping score

"""

from __future__ import division
from pprint import pformat

import numpy as np

from tde.data.sets import Pclus_single, Pgoldclus, typeset, weights, nmatch
from tde.util.printing import verb_print, banner, pretty_pairs
from tde.util.functions import intersection

def make_pclus(disc_clsdict, verbose, debug):
    with verb_print('constructing pclus', verbose, True, True):
        pclus = list(tuple(sorted((f1, f2),
                             key=lambda f: (f.name, f.interval.start)))
                     for f1, f2 in Pclus_single(disc_clsdict))
    if debug:
        print banner('PCLUS ({0})'.format(len(pclus)))
        print pretty_pairs(pclus)
        print
    return pclus

def make_pgoldclus(disc_clsdict, verbose, debug):
    with verb_print('constructing pgoldclus', verbose, True, True):
        pgoldclus = list(tuple(sorted((f1, f2),
                                      key=lambda f: (f.name, f.interval.start)))
                         for f1, f2 in Pgoldclus(disc_clsdict))
    if debug:
        pgoldclus = list(pgoldclus)
        print banner('PGOLDCLUS ({0})'.format(len(pgoldclus)))
        print pretty_pairs(pgoldclus)
        print
    return pgoldclus

def make_typeset(pclus, verbose, debug):
    with verb_print('constructing typeset', verbose, True, True):
        ts = list(typeset(pclus))
    if debug:
        print banner('TYPESET ({0})'.format(len(ts)))
        print pformat(ts)
        print
    return ts

def make_weights(pclus, verbose, debug):
    with verb_print('constructing weights', verbose, True, True):
        ws = weights(pclus)
    if debug:
        print banner('WEIGHTS')
        print pformat(ws)
        print
    return ws

def make_pclus_pgoldclus_nmatch(pclus, pgoldclus, verbose, debug):
    with verb_print('making pclus/pgoldclus nmatch', verbose, True, True):
        pclus_pgoldclus_intersect = list(intersection(pclus, pgoldclus))
        pclus_pgoldclus_nmatch = nmatch(pclus_pgoldclus_intersect)
    if debug:
        print banner('NMATCH(PCLUS/PGOLDCLUS)')
        print pformat(pclus_pgoldclus_nmatch)
        print
    return pclus_pgoldclus_nmatch

def make_pclus_nmatch(pclus, verbose, debug):
    with verb_print('constructing pclus nmatch', verbose, True, True):
        pclus_nmatch = nmatch(pclus)
    if debug:
        print banner('NMATCH(PCLUS)')
        print pformat(pclus_nmatch)
        print
    return pclus_nmatch

def make_pgoldclus_nmatch(pgoldclus, verbose, debug):
    with verb_print('constructing pgoldclus_nmatch', verbose, True, True):
        pgoldclus_nmatch = nmatch(pgoldclus)
    if debug:
        print banner('NMATCH(PGOLDCLUS)')
        print pformat(pgoldclus_nmatch)
        print
    return pgoldclus_nmatch

def evaluate_group(disc_clsdict, verbose=False, debug=False):
    pclus = make_pclus(disc_clsdict, verbose, debug)
    pgoldclus = make_pgoldclus(disc_clsdict, verbose, debug)

    ts_disc = make_typeset(pclus, verbose, debug)
    ts_gold = make_typeset(pgoldclus, verbose, debug)

    pclus_pgoldclus_nmatch = make_pclus_pgoldclus_nmatch(pclus,
                                                         pgoldclus,
                                                         verbose, debug)
    pclus_nmatch = make_pclus_nmatch(pclus, verbose, debug)
    pgoldclus_nmatch = make_pgoldclus_nmatch(pgoldclus,
                                             verbose, debug)

    ws_disc = make_weights(pclus, verbose, debug)
    ws_gold = make_weights(pgoldclus, verbose, debug)

    if len(pclus_nmatch) == 0:
        prec = 0.
    else:
        prec = sum(ws_disc[t] * pclus_pgoldclus_nmatch[t] / pclus_nmatch[t]
                   for t in ts_disc if pclus_nmatch[t] > 0)
        if not np.isfinite(prec):
            prec = 0.

    if len(pgoldclus_nmatch) == 0:
        rec = 0.
    else:
        rec = sum(ws_gold[t] * pclus_pgoldclus_nmatch[t] / pgoldclus_nmatch[t]
                  for t in ts_gold if pgoldclus_nmatch[t] > 0)
        if not np.isfinite(rec):
            rec = 0.
    return prec, rec
