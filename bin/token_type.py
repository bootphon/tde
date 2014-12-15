"""Evaluate token/type score"""

from __future__ import division

from pprint import pformat
from collections import defaultdict

import numpy as np
from joblib import Parallel, delayed

import tde.reader
import tde.util
import tde.token_type
import tde.corpus

def load_corpus(fname, verbose, debug):
    with tde.util.verb_print('loading corpus file', verbose, True, True):
        corpus = tde.reader.load_corpus_txt(fname)

    if debug:
        print tde.util.dbg_banner('CORPUS')
        print repr(corpus)
        print
    return corpus

def load_disc_clsdict(fname, corpus, verbose, debug):
    with tde.util.verb_print('loading discovered class file', verbose, True, True):
        clsdict = tde.reader.load_classes_txt(fname, corpus)

    if debug:
        print tde.util.dbg_banner('DISC CLSDICT')
        print clsdict.pretty()
        print
    return clsdict

def check_names(names_cross_file, names_within_file, do_exact):
    if names_cross_file is None and names_within_file is None and not do_exact:
        print 'no names files supplied for subsampling. use option ' \
            '--force-exact to force an exact evaluation.'
        exit()
    if do_exact:
        print 'calculating exact matching measures. this is slow, memory-inten'\
        'sive and generally not recommended.'


def load_names_file(names_file):
    names = [[]]
    for line in open(names_file):
        if line == '\n':
            names.append([])
        else:
            names[-1].append(line.strip())
    return names

def get_names_cross(names_file, corpus, verbose, debug):
    if names_file is None:
        if verbose:
            print 'no names file supplied for cross, using corpus'
        names = corpus.keys()
    else:
        if verbose:
            print 'loading names file "{0}"'.format(names_file)
        names = load_names_file(names_file)
    if debug:
        print tde.util.dbg_banner('names cross ({0})'.format(len(names)))
        print pformat(names)
        print
    return names


def get_names_within(names_file, corpus, verbose, debug):
    if names_file is None:
        # construct from corpus
        if verbose:
            print 'no names file supplied for within, using corpus'
        names_per_speaker = defaultdict(list)
        for name in corpus.keys():
            names_per_speaker[name[:3]].append(name)
        names = names_per_speaker.values()
    else:
        if verbose:
            print 'loading names file "{0}"'.format(names_file)
        names = load_names_file(names_file)
    if debug:
        print tde.util.dbg_banner('names within ({0})'.format(len(names)))
        print pformat(names)
        print
    return names

def calculate_scores(clsdict, lex, names, verbose, debug, n_jobs):
    et = tde.token_type.evaluate_token_type
    if verbose:
        print 'subsampled {0} files in {1} sets'.format(sum(map(len, names)),
                                                        len(names))
    with tde.util.verb_print('calculating scores', verbose, False, True, False):
        pto, rto, pty, rty = zip(*Parallel(n_jobs=n_jobs,
                                           verbose=5 if verbose else 0)
                                 (delayed(et)(clsdict.restrict(ns, False), lex)
                                  for ns in names))
    pto, rto, pty, rty = np.array(pto), np.array(rto), np.array(pty), np.array(rty)
    if debug:
        print tde.util.dbg_banner('pto')
        print pformat(pto)
        print tde.util.dbg_banner('rto')
        print pformat(rto)
        print tde.util.dbg_banner('pty')
        print pformat(pty)
        print tde.util.dbg_banner('rty')
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
    word_corpus_file = args['word_corpus'][0]
    phone_corpus_file = args['phone_corpus'][0]

    names_cross_file = args['cross']
    names_within_file = args['within']
    do_exact = args['exact']
    check_names(names_cross_file, names_within_file, do_exact)
    if do_exact:
        names_cross_file = None
        names_within_file = None

    wrd_corpus = load_corpus(word_corpus_file, verbose, debug)
    phn_corpus = load_corpus(phone_corpus_file, verbose, debug)
    disc_clsdict = load_disc_clsdict(disc_clsfile, phn_corpus, verbose, debug)

    names_cross = get_names_cross(names_cross_file, phn_corpus, verbose, debug)
    names_within = get_names_within(names_within_file, phn_corpus, verbose, debug)

    lex = tde.corpus.lexicon(wrd_corpus, phn_corpus)

    ptoc, rtoc, ptyc, rtyc = calculate_scores(disc_clsdict, lex, names_cross,
                                              verbose, debug, n_jobs)
    ftoc = np.vectorize(tde.util.fscore)(ptoc, rtoc)
    ftyc = np.vectorize(tde.util.fscore)(ptyc, rtyc)

    ptow, rtow, ptyw, rtyw = calculate_scores(disc_clsdict, lex, names_within,
                                              verbose, debug, n_jobs)
    ftow = np.vectorize(tde.util.fscore)(ptow, rtow)
    ftyw = np.vectorize(tde.util.fscore)(ptyw, rtyw)

    print tde.util.pretty_scores(ptow, rtow, ftow, 'token within-speaker',
                                 ptow.shape[0], sum(map(len, names_within)))
    print tde.util.pretty_scores(ptyw, rtyw, ftyw, 'type within-speaker',
                                 ptyw.shape[0], sum(map(len, names_within)))
    print tde.util.pretty_scores(ptoc, rtoc, ftoc, 'token cross-speaker',
                                 ptoc.shape[0], sum(map(len, names_cross)))
    print tde.util.pretty_scores(ptyc, rtyc, ftyc, 'type cross-speaker',
                                 ptyc.shape[0], sum(map(len, names_cross)))
