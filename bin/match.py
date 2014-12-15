"""Evaluate matching score

"""
from __future__ import division

from pprint import pformat
from collections import defaultdict
from itertools import izip

import numpy as np
from joblib import Parallel, delayed

import tde.reader
import tde.util
import tde.match

def load_corpus(fname, verbose, debug):
    with tde.util.verb_print('loading corpus file', verbose, True, True, True):
        corpus = tde.reader.load_corpus_txt(fname)

    if debug:
        print tde.util.dbg_banner('CORPUS')
        print repr(corpus)
        print
    return corpus

def load_disc_clsdict(fname, corpus, verbose, debug):
    with tde.util.verb_print('loading discovered class file',
                             verbose, True, True, True):
        clsdict = tde.reader.load_classes_txt(fname, corpus)

    if debug:
        print tde.util.dbg_banner('DISC CLSDICT')
        print clsdict.pretty()
        print
    return clsdict

def load_gold_clsdict(fname, corpus, verbose, debug):
    with tde.util.verb_print('loading gold class file', verbose, True, True):
        goldset = tde.reader.load_classes_txt(gold_clsfile, corpus)

    if debug:
        print tde.util.dbg_banner('GOLD CLSDICT')
        print goldset.pretty()
        print
    return goldset

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


def calculate_scores(disc_clsdict, gold_clsdict, corpus, names,
                     verbose, debug, n_jobs):
    em = tde.match.eval_from_psets
    if verbose:
        print 'subsampled {0} files in {1} sets'.format(sum(map(len, names)),
                                                        len(names))
    with tde.util.verb_print('prepping psets', verbose, False, True, False):
        pdiscs = [tde.match.make_pdisc(disc_clsdict.restrict(ns, True))
                  for ns in names]
        pgolds = [tde.match.make_pgold(gold_clsdict.restrict(ns, True))
                  for ns in names]
        psubs = [tde.match.make_psubs(disc_clsdict.restrict(ns, True), corpus)
                 for ns in names]

    with tde.util.verb_print('calculating scores', verbose, False, True, False):
        tp, tr = zip(*(Parallel(n_jobs=n_jobs,
                                verbose=5 if verbose else 0,
                                pre_dispatch='n_jobs')
                       (delayed(em)(pdisc, pgold, psub))
                       for pdisc, pgold, psub in zip(pdiscs, pgolds, psubs)))
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
        print tde.util.dbg_banner('calculate_scores tp')
        print pformat(tp)
        print tde.util.dbg_banner('calculate_scores tr')
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

    names_cross_file = args['cross']
    names_within_file = args['within']
    do_exact = args['exact']
    check_names(names_cross_file, names_within_file, do_exact)
    if do_exact:
        names_cross_file = None
        names_within_file = None

    corpus = load_corpus(corpus_file, verbose, debug)
    disc_clsdict = load_disc_clsdict(disc_clsfile, corpus, verbose, debug)
    gold_clsdict = load_gold_clsdict(gold_clsfile, corpus, verbose, debug)

    names_cross = get_names_cross(names_cross_file, corpus, verbose, debug)
    names_within = get_names_within(names_within_file, corpus, verbose, debug)

    pc, rc = calculate_scores(disc_clsdict, gold_clsdict,
                              corpus, names_cross,
                              verbose=verbose, debug=debug, n_jobs=n_jobs)

    pw, rw = calculate_scores(disc_clsdict, gold_clsdict,
                              corpus, names_within,
                              verbose=verbose, debug=debug, n_jobs=n_jobs)

    fw = np.vectorize(tde.util.fscore)(pw, rw)
    fc = np.vectorize(tde.util.fscore)(pc, rc)

    print tde.util.pretty_scores(pw, rw, fw, 'within-speaker',
                                 pw.shape[0], sum(map(len, names_within)))
    print tde.util.pretty_scores(pc, rc, fc, 'cross-speaker',
                                 pc.shape[0], sum(map(len, names_cross)))
