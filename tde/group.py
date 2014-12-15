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

from .sets import Pclus_single, Pgoldclus, typeset, weights, nmatch
from .util import verb_print, dbg_banner, pretty_pairs, intersection

def make_pclus(disc_clsdict, verbose, debug):
    with verb_print('constructing pclus', verbose, True, True):
        pclus = list(Pclus_single(disc_clsdict))
    if debug:
        print dbg_banner('PCLUS ({0})'.format(len(pclus)))
        print pretty_pairs(pclus)
        print
    return pclus

def make_pgoldclus(disc_clsdict, verbose, debug):
    with verb_print('constructing pgoldclus', verbose, True, True):
        pgoldclus = Pgoldclus(disc_clsdict)
    if debug:
        print dbg_banner('PGOLDCLUS ({0})'.format(len(pgoldclus)))
        print pretty_pairs(pgoldclus)
        print
    return pgoldclus

def make_typeset(pclus, verbose, debug):
    with verb_print('constructing typeset', verbose, True, True):
        ts = list(typeset(pclus))
    if debug:
        print dbg_banner('TYPESET ({0})'.format(len(ts)))
        print pformat(ts)
        print
    return ts

def make_weights(pclus, verbose, debug):
    with verb_print('constructing weights', verbose, True, True):
        ws = weights(pclus)
    if debug:
        print dbg_banner('WEIGHTS')
        print pformat(ws)
        print
    return ws

def make_pclus_pgoldclus_nmatch(pclus, pgoldclus, verbose, debug):
    with verb_print('making pclus/pgoldclus nmatch', verbose, True, True):
        pclus_pgoldclus_intersect = list(intersection(pclus, pgoldclus))
        pclus_pgoldclus_nmatch = nmatch(pclus_pgoldclus_intersect)
    if debug:
        print dbg_banner('NMATCH(PCLUS/PGOLDCLUS)')
        print pformat(pclus_pgoldclus_nmatch)
        print
    return pclus_pgoldclus_nmatch

def make_pclus_nmatch(pclus, verbose, debug):
    with verb_print('constructing pclus nmatch', verbose, True, True):
        pclus_nmatch = nmatch(pclus)
    if debug:
        print dbg_banner('NMATCH(PCLUS)')
        print pformat(pclus_nmatch)
        print
    return pclus_nmatch

def make_pgoldclus_nmatch(pgoldclus, verbose, debug):
    with verb_print('constructing pgoldclus_nmatch', verbose, True, True):
        pgoldclus_nmatch = nmatch(pgoldclus)
    if debug:
        print dbg_banner('NMATCH(PGOLDCLUS)')
        print pformat(pgoldclus_nmatch)
        print
    return pgoldclus_nmatch

def evaluate_group(disc_clsdict, verbose=False, debug=False):
    pclus = make_pclus(disc_clsdict, verbose, debug)
    ts = make_typeset(pclus, verbose, debug)
    ws = make_weights(pclus, verbose, debug)

    # pgoldclus = make_pgoldclus(disc_clsdict, verbose, debug)
    pclus_pgoldclus_nmatch = make_pclus_pgoldclus_nmatch(pclus,
                                                         Pgoldclus(disc_clsdict),
                                                         verbose, debug)
    pclus_nmatch = make_pclus_nmatch(pclus, verbose, debug)
    pgoldclus_nmatch = make_pgoldclus_nmatch(Pgoldclus(disc_clsdict),
                                             verbose, debug)

    prec = sum(ws[t] * pclus_pgoldclus_nmatch[t] / pclus_nmatch[t]
               for t in ts if pclus_nmatch[t] > 0)
    rec = sum(ws[t] * pclus_pgoldclus_nmatch[t] / pgoldclus_nmatch[t]
              for t in ts if pgoldclus_nmatch[t] > 0)
    return prec, rec
