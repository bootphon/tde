"""Evaluate NLP measures: NED and Coverage"""

from __future__ import division
from pprint import pformat
from collections import defaultdict

import numpy as np
from joblib import Parallel, delayed

from tde.measures.nlp import NED, coverage
from tde.util.printing import verb_print, banner, pretty_score_nlp
from tde.util.reader import load_classes_txt, load_corpus_txt, load_split


def calculate_ned_score(disc_clsdict, names, verbose, debug, n_jobs):
    ned = NED
    with verb_print('calculating NED score',
                    verbose, False, True, False):
        s = Parallel(n_jobs=n_jobs)(delayed(ned)(disc_clsdict.restrict(ns, True))
                                    for ns in names)
    return np.array(s)


def calculate_coverage_score(disc_clsdict, gold_clsdict, names,
                             verbose, debug, n_jobs):
    cov = coverage
    with verb_print('calculating coverage score',
                    verbose, False, True, False):
        s = Parallel(n_jobs=n_jobs)(delayed(cov)(disc_clsdict.restrict(ns, False),
                                                 gold_clsdict.restrict(ns, False))
                                    for ns in names)
    return np.array(s)


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


def load_disc_clsdict(fname, corpus, verbose, debug):
    with verb_print('loading discovered class file', verbose, True, True):
        clsdict = load_classes_txt(fname, corpus)

    if debug:
        print banner('DISC CLSDICT')
        print pformat(clsdict)
        print
    return clsdict

def load_gold_clsdict(fname, corpus, verbose, debug):
    with verb_print('loading gold class file', verbose, True, True):
        gold_clsdict = load_classes_txt(gold_clsfile, corpus)

    if debug:
        print banner('GOLD CLSDICT')
        print pformat(gold_clsdict)
        print
    return gold_clsdict

def load_corpus(fname, verbose, debug):
    with verb_print('loading corpus file', verbose, True, True):
        corpus = load_corpus_txt(fname)

    if debug:
        print banner('CORPUS')
        print repr(corpus)
        print
    return corpus


if __name__ == '__main__':
    import argparse
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='nlp.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Perform matching evaluation',
            epilog="""Example usage:

$ python nlp.py disc.classes gold.classes corpus.phn

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
    gold_clsfile = args['gold_clsfile'][0]
    corpus_file = args['corpusfile'][0]

    corpus = load_corpus(corpus_file, verbose, debug)

    disc_clsdict = load_disc_clsdict(disc_clsfile, corpus, verbose, debug)
    gold_clsdict = load_gold_clsdict(disc_clsfile, corpus, verbose, debug)

    fragments_cross_file = args['cross']
    fragments_within_file = args['within']

    fragments_cross = get_fragments_cross(fragments_cross_file, verbose, debug)
    fragments_within = get_fragments_within(fragments_within_file, verbose, debug)

    ned_score_cross = calculate_ned_score(disc_clsdict, fragments_cross,
                                          verbose, debug, n_jobs)
    ned_score_within = calculate_ned_score(disc_clsdict, fragments_within,
                                           verbose, debug, n_jobs)
    coverage_score_cross = calculate_coverage_score(disc_clsdict, gold_clsdict,
                                                    fragments_cross,
                                                    verbose, debug, n_jobs)
    coverage_score_within = calculate_coverage_score(disc_clsdict, gold_clsdict,
                                                     fragments_within,
                                                     verbose, debug, n_jobs)
    print pretty_score_nlp(ned_score_within, coverage_score_within,
                           'NLP within speaker', len(fragments_within),
                           sum([len(ns) for ns in fragments_within]))
    print pretty_score_nlp(ned_score_cross, coverage_score_cross,
                           'NLP cross speaker', len(fragments_cross),
                           sum([len(ns) for ns in fragments_cross]))
