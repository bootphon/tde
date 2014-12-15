"""Evaluate NLP measures: NED and Coverage"""

from __future__ import division
from pprint import pformat
from collections import defaultdict

import numpy as np
from joblib import Parallel, delayed

import tde.nlp
import tde.util
import tde.reader

def calculate_ned_score(disc_clsdict, names, verbose, debug, n_jobs):
    ned = tde.nlp.NED
    with tde.util.verb_print('calculating NED score',
                             verbose, False, True, False):
        s = Parallel(n_jobs=n_jobs)(delayed(ned)(disc_clsdict.restrict(ns, True))
                                    for ns in names)
    return np.array(s)
    #     scores = np.fromiter((tde.nlp.NED(disc_clsdict.restrict(ns, True))
    #                           for ns in names),
    #                          dtype=np.double)
    # return scores

def calculate_coverage_score(disc_clsdict, gold_clsdict, names,
                             verbose, debug, n_jobs):
    cov = tde.nlp.coverage
    with tde.util.verb_print('calculating coverage score',
                             verbose, False, True, False):
        s = Parallel(n_jobs=n_jobs)(delayed(cov)(disc_clsdict.restrict(ns, False),
                                                 gold_clsdict.restrict(ns, False))
                                    for ns in names)
    return np.array(s)
        # scores = np.fromiter((tde.nlp.coverage(disc_clsdict.restrict(ns, False),
        #                                        gold_clsdict.restrict(ns, False))
        #                       for ns in names),
        #                      dtype=np.double)


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
        names = [corpus.keys()]
    else:
        if verbose:
            print 'loading names file "{0}"'.format(names_file)
        names = load_names_file(names_file)
    if debug:
        print tde.util.dbg_banner('names cross ({0})'.format(len(names)))
        print pformat(names)
        print
    return names


def get_names_within(names_file, corpus, verbose, debug, fname2speaker=None):
    if fname2speaker is None:
        fname2speaker = lambda x: x
    if names_file is None:
        # construct from corpus
        if verbose:
            print 'no names file supplied for within, using corpus'
        names_per_speaker = defaultdict(list)
        for name in corpus.keys():
            names_per_speaker[fname2speaker(name)].append(name)
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

def load_disc_clsdict(fname, corpus, verbose, debug):
    with tde.util.verb_print('loading discovered class file', verbose, True, True):
        clsdict = tde.reader.load_classes_txt(fname, corpus)

    if debug:
        print tde.util.dbg_banner('DISC CLSDICT')
        print pformat(clsdict)
        print
    return clsdict

def load_gold_clsdict(fname, corpus, verbose, debug):
    with tde.util.verb_print('loading gold class file', verbose, True, True):
        gold_clsdict = tde.reader.load_classes_txt(gold_clsfile, corpus)

    if debug:
        print tde.util.dbg_banner('GOLD CLSDICT')
        print pformat(gold_clsdict)
        print
    return gold_clsdict

def load_corpus(fname, verbose, debug):
    with tde.util.verb_print('loading corpus file', verbose, True, True):
        corpus = tde.reader.load_corpus_txt(fname)

    if debug:
        print tde.util.dbg_banner('CORPUS')
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
    gold_clsfile = args['gold_clsfile'][0]
    corpus_file = args['corpusfile'][0]

    corpus = load_corpus(corpus_file, verbose, debug)

    disc_clsdict = load_disc_clsdict(disc_clsfile, corpus, verbose, debug)
    gold_clsdict = load_gold_clsdict(disc_clsfile, corpus, verbose, debug)

    names_cross_file = args['cross']
    names_within_file = args['within']
    do_exact = args['exact']
    check_names(names_cross_file, names_within_file, do_exact)
    if do_exact:
        names_cross_file = None
        names_within_file = None

    names_cross = get_names_cross(names_cross_file, corpus, verbose, debug)
    names_within = get_names_within(names_within_file, corpus, verbose, debug)

    ned_score_cross = calculate_ned_score(disc_clsdict, names_cross,
                                          verbose, debug, n_jobs)
    ned_score_within = calculate_ned_score(disc_clsdict, names_within,
                                           verbose, debug, n_jobs)
    coverage_score_cross = calculate_coverage_score(disc_clsdict, gold_clsdict,
                                                    names_cross,
                                                    verbose, debug, n_jobs)
    coverage_score_within = calculate_coverage_score(disc_clsdict, gold_clsdict,
                                                     names_within,
                                                     verbose, debug, n_jobs)
    print tde.nlp.pretty_score(ned_score_within, coverage_score_within,
                               'NLP within speaker', len(names_within),
                               sum([len(ns) for ns in names_within]))
    print tde.nlp.pretty_score(ned_score_cross, coverage_score_cross,
                               'NLP cross speaker', len(names_cross),
                               sum([len(ns) for ns in names_cross]))
