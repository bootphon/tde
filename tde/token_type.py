"""Evaluate token and type measures"""

from __future__ import division

from pprint import pformat

from .util import verb_print, dbg_banner, pretty_pairs, intersection
from .sets import Pclus_single, Pgoldlex, typeset, nmatch, weights


def make_pclus(disc_clsdict, verbose, debug):
    with verb_print('constructing pclus', verbose, True, True):
        pclus = list(Pclus_single(disc_clsdict))
    if debug:
        print dbg_banner('PCLUS ({0})'.format(len(pclus)))
        print pretty_pairs(pclus)
        print
    return pclus


def make_pgoldlex(disc_clsdict, lexicon, verbose, debug):
    with verb_print('constructing pgoldclus', verbose, True, True):
        pgoldclus = list(Pgoldlex(disc_clsdict, lexicon))
    if debug:
        print dbg_banner('PGOLDCLUS ({0})'.format(len(pgoldclus)))
        print pretty_pairs(pgoldclus)
        print
    return pgoldclus


def make_typeset(pclus_set, verbose, debug):
    with verb_print('constructing typeset', verbose, True, True):
        ts = list(typeset(pclus_set))
    if debug:
        print dbg_banner('TYPESET ({0})'.format(len(ts)))
        print pformat(ts)
        print
    return ts


def make_weights(pclus_set, verbose, debug):
    with verb_print('constructing weights', verbose, True, True):
        ws = weights(pclus_set)
    if debug:
        print dbg_banner('WEIGHTS')
        print pformat(ws)
        print
    return ws

def make_pdisc_pgoldlex_nmatch(pdisc, pgoldlex, verbose, debug):
    with verb_print('making pdisc/pgoldlex nmatch', verbose, True, True):
        pdisc_pgoldlex_intersect = list(intersection(pgoldlex, pdisc))
        pdisc_pgoldlex_nmatch = nmatch(pdisc_pgoldlex_intersect)
    if debug:
        print dbg_banner('NMATCH(PDISC/PGOLDLEX)')
        print pformat(pdisc_pgoldlex_nmatch)
        print
    return pdisc_pgoldlex_nmatch

def make_pdisc_nmatch(pdisc, verbose, debug):
    with verb_print('making pdisc nmatch', verbose, True, True):
        pdisc_nmatch = nmatch(pdisc)
    if debug:
        print dbg_banner('NMATCH(PDISC)')
        print pformat(pdisc_nmatch)
        print
    return pdisc_nmatch


def make_pgoldlex_nmatch(pgoldlex, verbose, debug):
    with verb_print('making pgoldlex nmatch', verbose, True, True):
        pgoldlex_nmatch = nmatch(pgoldlex)
    if debug:
        print dbg_banner('NMATCH(PGOLDLEX)')
        print pformat(pgoldlex_nmatch)
        print
    return pgoldlex_nmatch

def evaluate_token_type(disc_clsdict, lexicon, verbose=False, debug=False):
    pdisc = make_pclus(disc_clsdict, verbose, debug)
    pgoldlex = make_pgoldlex(disc_clsdict, lexicon, verbose, debug)

    ts = make_typeset(pdisc, verbose, debug)
    one_over_ntypes = 1./len(ts)
    ws = make_weights(pdisc, verbose, debug)

    pdisc_pgoldlex_nmatch = make_pdisc_pgoldlex_nmatch(pdisc, pgoldlex,
                                                       verbose, debug)
    pdisc_nmatch = make_pdisc_nmatch(pdisc, verbose, debug)
    pgoldlex_nmatch = make_pgoldlex_nmatch(pgoldlex, verbose, debug)

    prec_token = sum(ws[t] * pdisc_pgoldlex_nmatch[t] / pdisc_nmatch[t]
                     for t in ts if pdisc_nmatch[t] > 0)
    rec_token = sum(ws[t] * pdisc_pgoldlex_nmatch[t] / pgoldlex_nmatch[t]
                     for t in ts if pgoldlex_nmatch[t] > 0)
    prec_type = sum(one_over_ntypes * pdisc_pgoldlex_nmatch[t] / pdisc_nmatch[t]
                    for t in ts if pdisc_nmatch[t] > 0)
    rec_type = sum(one_over_ntypes * pdisc_pgoldlex_nmatch[t] / pgoldlex_nmatch[t]
                   for t in ts if pgoldlex_nmatch[t] > 0)
    return prec_token, rec_token, prec_type, rec_type
