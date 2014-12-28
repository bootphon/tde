"""Evaluate token/type score"""

from __future__ import division

from pprint import pformat

import numpy as np
from joblib import Parallel, delayed

from tde.util.printing import verb_print, banner, pretty_score_f
from tde.util.functions import fscore
from tde.util.reader import load_corpus_txt, load_classes_txt, load_split
from tde.measures.token_type import evaluate_token_type


def load_corpus(fname, verbose, debug):
    with verb_print('loading corpus file', verbose, True, True):
        corpus = load_corpus_txt(fname)

    if debug:
        print banner('CORPUS')
        print repr(corpus)
        print
    return corpus

def load_disc_clsdict(fname, corpus, verbose, debug):
    with verb_print('loading discovered class file', verbose, True, True):
        clsdict = load_classes_txt(fname, corpus)

    if debug:
        print banner('DISC CLSDICT')
        print clsdict.pretty()
        print
    return clsdict

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

def calculate_scores(disc_clsdict, wrd_corpus, interval_dbs,
                     verbose, debug, n_jobs):
    et = evaluate_token_type
    if verbose:
        print 'subsampled {0} files in {1} sets'.format(sum(map(len, interval_dbs)),
                                                        len(interval_dbs))
    with verb_print('calculating scores', verbose, False, True, False):
        pto, rto, pty, rty = zip(*Parallel(n_jobs=n_jobs,
                                           verbose=5 if verbose else 0)
                                 (delayed(et)(disc_clsdict.restrict(ns, False),
                                              wrd_corpus.restrict(ns))
                                  for ns in interval_dbs))
    pto, rto, pty, rty = np.array(pto), np.array(rto), np.array(pty), np.array(rty)
    if debug:
        print banner('pto')
        print pformat(pto)
        print banner('rto')
        print pformat(rto)
        print banner('pty')
        print pformat(pty)
        print banner('rty')
        print pformat(rty)
        print
    return pto, rto, pty, rty

if __name__ == '__main__':
    import argparse
    def parse_args():
        parser = argparse.ArgumentParser(
            prog='group.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Perform grouping evaluation',
            epilog="""Example usage:

$ python group.py disc.classes corpus.phnfile

evaluates the grouping score on the discovered classfile with the annotation
from the corpus file.

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
        parser.add_argument('word_corpus', metavar='WORDCORPUSFILE',
                            nargs=1,
                            help='.wrd file containing the corpus annotation')
        parser.add_argument('phone_corpus', metavar='PHONECORPUSFILE',
                            nargs=1,
                            help='.phn file containing the phone annotation')
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
    word_corpus_file = args['word_corpus'][0]
    phone_corpus_file = args['phone_corpus'][0]

    wrd_corpus = load_corpus(word_corpus_file, verbose, debug)
    phn_corpus = load_corpus(phone_corpus_file, verbose, debug)
    disc_clsdict = load_disc_clsdict(disc_clsfile, phn_corpus, verbose, debug)

    fragments_cross_file = args['cross']
    fragments_within_file = args['within']

    fragments_cross = get_fragments_cross(fragments_cross_file, verbose, debug)
    fragments_within = get_fragments_within(fragments_within_file, verbose, debug)

    ptoc, rtoc, ptyc, rtyc = calculate_scores(disc_clsdict, wrd_corpus,
                                              fragments_cross,
                                              verbose, debug, n_jobs)
    ftoc = np.vectorize(fscore)(ptoc, rtoc)
    ftyc = np.vectorize(fscore)(ptyc, rtyc)

    ptow, rtow, ptyw, rtyw = calculate_scores(disc_clsdict, wrd_corpus,
                                              fragments_within,
                                              verbose, debug, n_jobs)
    ftow = np.vectorize(fscore)(ptow, rtow)
    ftyw = np.vectorize(fscore)(ptyw, rtyw)

    print pretty_score_f(ptow, rtow, ftow, 'token within-speaker',
                          ptow.shape[0], sum(map(len, fragments_within)))
    print pretty_score_f(ptyw, rtyw, ftyw, 'type within-speaker',
                          ptyw.shape[0], sum(map(len, fragments_within)))
    print pretty_score_f(ptoc, rtoc, ftoc, 'token cross-speaker',
                          ptoc.shape[0], sum(map(len, fragments_cross)))
    print pretty_score_f(ptyc, rtyc, ftyc, 'type cross-speaker',
                          ptyc.shape[0], sum(map(len, fragments_cross)))
