"""Evaluate matching score

"""
from __future__ import division

from pprint import pformat
from collections import defaultdict

import numpy as np
from joblib import Parallel, delayed

from tde.util.printing import verb_print, banner, pretty_score_f, pretty_pairs
from tde.util.reader import load_corpus_txt, load_classes_txt, load_split
from tde.util.functions import fscore
from tde.measures.match import eval_from_psets, make_pdisc, make_pgold, make_psubs

def load_corpus(fname, verbose, debug):
    with verb_print('loading corpus file', verbose, True, True, True):
        corpus = load_corpus_txt(fname)

    if debug:
        print banner('CORPUS')
        print repr(corpus)
        print
    return corpus

def load_disc_clsdict(fname, corpus, verbose, debug):
    with verb_print('loading discovered class file',
                             verbose, True, True, True):
        clsdict = load_classes_txt(fname, corpus)

    if debug:
        print banner('DISC CLSDICT')
        print clsdict.pretty()
        print
    return clsdict

def load_gold_clsdict(fname, corpus, verbose, debug):
    with verb_print('loading gold class file', verbose, True, True):
        goldset = load_classes_txt(gold_clsfile, corpus)

    if debug:
        print banner('GOLD CLSDICT')
        print goldset.pretty()
        print
    return goldset

def get_fragments_cross(fragments_file, verbose, debug):
    if verbose:
        print 'loading cross file "{0}"'.format(fragments_file)
    fragments = load_split(fragments_file, multiple=True)
    if debug:
        print banner('fragments cross ({0})'.format(len(fragments)))
        print str(fragments)
        print
    return fragments

def get_fragments_within(fragments_file, verbose, debug):
    if verbose:
        print 'loading within file "{0}"'.format(fragments_file)
    fragments = load_split(fragments_file, multiple=True)
    if debug:
        print banner('fragments within ({0})'.format(len(fragments)))
        print str(fragments)
        print
    return fragments


def calculate_scores(disc_clsdict, gold_clsdict, corpus, names,
                     verbose, debug, n_jobs):
    em = eval_from_psets
    if verbose:
        print 'subsampled {0} files in {1} sets'.format(sum(map(len, names)),
                                                        len(names))
    with verb_print('prepping psets', verbose, False, True, False):
        pdiscs = [make_pdisc(disc_clsdict.restrict(ns, True), False, False)
                  for ns in names]
        pgolds = [make_pgold(gold_clsdict.restrict(ns, True), False, False)
                  for ns in names]
        psubs = [make_psubs(disc_clsdict.restrict(ns, True), corpus, 3, 20,
                            False, False)
                 for ns in names]

    if debug:
        print banner('PDISCS')
        for pairs in pdiscs:
            print pretty_pairs(pairs)
            print
        print banner('PGOLDS')
        for pairs in pgolds:
            print pretty_pairs(pairs)
            print
        print banner('PSUBS')
        for pairs in psubs:
            print pretty_pairs(pairs)
            print


    with verb_print('calculating scores', verbose, False, True, False):
        tp, tr = zip(*(Parallel(n_jobs=n_jobs,
                                verbose=5 if verbose else 0,
                                pre_dispatch='n_jobs')
                       (delayed(em)(pdisc, pgold, psub)
                       for pdisc, pgold, psub in zip(pdiscs, pgolds, psubs))))
        # tp, tr = izip(*[em(disc_clsdict.restrict(ns, True),
        #                    gold_clsdict.restrict(ns, True),
        #                    corpus.restrict(ns),
        #                    verbose=verbose, debug=debug)
        #                 for ns in names])
    tp = np.array(tp)
    tr = np.array(tr)
    # tp = np.fromiter(tp, dtype=np.double)
    # tr = np.fromiter(tr, dtype=np.double)
    if debug:
        print banner('calculate_scores tp')
        print pformat(tp)
        print banner('calculate_scores tr')
        print pformat(tr)
        print
    return tp, tr

if __name__ == '__main__':
    import argparse
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='match.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Perform matching evaluation',
            epilog="""Example usage:

$ python match.py disc.classes gold.classes corpus.phn

evaluates the matching score on the classfile with the annotation from the
corpus file and the gold classes generated.

Classfiles must be formatted like this:

Class 1 (optional_name)
fileID starttime endtime
fileID starttime endtime
...

Class 2 (optional_name)
fileID starttime endtime
...

The corpusfile must be formatted like this:

fileID starttime endtime phone
...
""")
        parser.add_argument('disc_clsfile', metavar='DISCCLSFILE',
                            nargs=1,
                            help='classfile output from STD system')
        parser.add_argument('gold_clsfile', metavar='GOLDCLSFILE',
                            nargs=1,
                            help='gold classfile')
        parser.add_argument('corpusfile', metavar='CORPUSFILE',
                            nargs=1,
                            help='phonefile containing the corpus annotation')
        parser.add_argument('--cross-file',
                            action='store',
                            dest='cross',
                            default=None,
                            help='file containing the names to be used for '
                            'cross-speaker validation')
        parser.add_argument('--within-file',
                            action='store',
                            dest='within',
                            default=None,
                            help='file containing the names to be used for '
                            'within-speaker validation')
        parser.add_argument('--force-exact',
                            action='store_true',
                            dest='exact',
                            default=False,
                            help='force an exact evaluation, not recommended')
        parser.add_argument('-v', '--verbose',
                            action='store_true',
                            dest='verbose',
                            default=False,
                            help='display progress')
        parser.add_argument('-d', '--debug',
                            action='store_true',
                            dest='debug',
                            default=False,
                            help='display debug information')
        parser.add_argument('-j', '--n-jobs',
                            action='store',
                            dest='n_jobs',
                            default=1,
                            help='number of cores to use')
        return vars(parser.parse_args())
    args = parse_args()

    verbose = args['verbose']
    debug = args['debug']
    n_jobs = int(args['n_jobs'])

    disc_clsfile = args['disc_clsfile'][0]
    corpus_file = args['corpusfile'][0]
    gold_clsfile = args['gold_clsfile'][0]

    corpus = load_corpus(corpus_file, verbose, debug)
    disc_clsdict = load_disc_clsdict(disc_clsfile, corpus, verbose, debug)
    gold_clsdict = load_gold_clsdict(gold_clsfile, corpus, verbose, debug)

    fragments_cross_file = args['cross']
    fragments_within_file = args['within']

    fragments_cross = get_fragments_cross(fragments_cross_file, verbose, debug)
    fragments_within = get_fragments_within(fragments_within_file, verbose, debug)

    pc, rc = calculate_scores(disc_clsdict, gold_clsdict,
                              corpus, fragments_cross,
                              verbose=verbose, debug=debug, n_jobs=n_jobs)

    pw, rw = calculate_scores(disc_clsdict, gold_clsdict,
                              corpus, fragments_within,
                              verbose=verbose, debug=debug, n_jobs=n_jobs)

    fw = np.vectorize(fscore)(pw, rw)
    fc = np.vectorize(fscore)(pc, rc)

    print pretty_score_f(pw, rw, fw, 'within-speaker',
                         pw.shape[0], sum(map(len, fragments_within)))
    print pretty_score_f(pc, rc, fc, 'cross-speaker',
                         pc.shape[0], sum(map(len, fragments_cross)))
