"""Evaluate matching score

"""

from __future__ import division

from pprint import pformat

import numpy as np

from tde.data.sets import Pclus, Psubs, nmatch, typeset, weights
from tde.util.printing import banner, verb_print, pretty_pairs
from tde.util.functions import intersection


def make_pgold(gold_clsdict, verbose, debug):
    with verb_print('constructing pgold set', verbose, True, True):
        pgold = list(Pclus(gold_clsdict))
    if debug:
        print banner('PGOLD ({0})'.format(len(pgold)))
        print pretty_pairs(pgold)
        print
    return pgold


def make_pdisc(disc_clsdict, verbose, debug):
    with verb_print('constructing pdisc set', verbose, True, True):
        pdisc = list(Pclus(disc_clsdict))
    if debug:
        print banner('PDISC ({0})'.format(len(pdisc)))
        print pretty_pairs(pdisc)
        print
    return pdisc


def make_psubs(disc_clsdict, corpus, minlength, maxlength,
               verbose, debug):
    with verb_print('constructing psubs set', verbose, True, True):
        psubs = list(Psubs(disc_clsdict, corpus, minlength=minlength,
                           maxlength=maxlength))
    if debug:
        print banner('PSUBS ({0})'.format(len(psubs)))
        print pretty_pairs(psubs)
        print
    return psubs


def make_typeset(psubs, verbose, debug):
    with verb_print('making typeset', verbose, True, True):
        ts = list(typeset(psubs))
    if debug:
        print banner('TYPES(PSUBS) ({0})'.format(len(ts)))
        print pformat(ts)
        print
    return ts


def make_weights(psubs, verbose, debug):
    with verb_print('making weights', verbose, True, True):
        ws = weights(psubs)
    if debug:
        print banner('WEIGHTS(PSUBS) ({0})'.format(len(ws)))
        print pformat(ws)
        print
    return ws


def make_psubs_pgold_nmatch(pgold, psubs, verbose, debug):
    with verb_print('making psubs/pgold nmatch', verbose, True, True):
        psubs_pgold_intersect = intersection(pgold, psubs)
        psubs_pgold_nmatch = nmatch(psubs_pgold_intersect)
    if debug:
        print banner('NMATCH(PSUBS/PGOLD)')
        print pformat(psubs_pgold_nmatch)
        print
    return psubs_pgold_nmatch


def make_psubs_nmatch(psubs, verbose, debug):
    with verb_print('making psubs nmatch', verbose, True, True):
        psubs_nmatch = nmatch(psubs)
    if debug:
        print banner('NMATCH(PSUBS)')
        print pformat(psubs_nmatch)
        print
    return psubs_nmatch


def make_pgold_nmatch(pgold, verbose, debug):
    with verb_print('constructing nmatch_gold', verbose, True, True):
        nmatch_gold = nmatch(pgold)

    if debug:
        print banner('nmatch_gold')
        for k, v in nmatch_gold.iteritems():
            print k, v
    return nmatch_gold

def eval_from_psets(pdisc, pgold, psubs, verbose=False, debug=False):
    ts_disc = make_typeset(psubs, verbose, debug)
    ts_gold = make_typeset(pgold, verbose, debug)

    psubs_pgold_nmatch = make_psubs_pgold_nmatch(pgold, psubs,
                                                 verbose, debug)

    psubs_nmatch = make_psubs_nmatch(psubs, verbose, debug)
    pgold_nmatch = make_pgold_nmatch(pgold, verbose, debug)

    ws_disc = make_weights(psubs, verbose, debug)
    ws_gold = make_weights(pgold, verbose, debug)

    if len(psubs_nmatch) == 0:
        prec = 0.
    else:
        prec = sum(ws_disc[t] * psubs_pgold_nmatch[t] / psubs_nmatch[t]
                   for t in ts_disc if psubs_nmatch[t] > 0)
        if not np.isfinite(prec):
            prec = 0.

    if len(pgold_nmatch) == 0:
        rec = 0.
    else:
        rec = sum(ws_gold[t] * psubs_pgold_nmatch[t] / pgold_nmatch[t]
                  for t in ts_gold if pgold_nmatch[t] > 0)
        if not np.isfinite(rec):
            rec = 0.
    return prec, rec

def evaluate_matching(disc_clsdict, gold_clsdict, corpus, minlength=3,
                      maxlength=3, verbose=False, debug=False):
    pgold = make_pgold(gold_clsdict, verbose, debug)
    pdisc = make_pdisc(disc_clsdict, verbose, debug)
    psubs = make_psubs(disc_clsdict, corpus, minlength, maxlength,
                       verbose, debug)
    return eval_from_psets(pdisc, pgold, psubs, verbose, debug)
