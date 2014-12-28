"""Evaluate grouping score

"""

from __future__ import division

from pprint import pformat

import numpy as np
from joblib import Parallel, delayed

from tde.util.printing import verb_print, banner, pretty_score_f
from tde.util.functions import fscore
from tde.util.reader import load_corpus_txt, load_classes_txt, load_split
from tde.measures.group import evaluate_group

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

def check_names(fragments_cross_file, fragments_within_file, do_exact):
    if fragments_cross_file is None and fragments_within_file is None and not do_exact:
        print 'no fragments files supplied for subsampling. use option ' \
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

def calculate_scores(disc_clsdict, names, verbose, debug, n_jobs):
    eg = evaluate_group
    if verbose:
        print 'subsampled {0} files in {1} sets'.format(sum(map(len, names)),
                                                        len(names))
    with verb_print('calculating scores', verbose, False, True, False):
        tp, tr = zip(*Parallel(n_jobs=n_jobs,
                               verbose=5 if verbose else 0,
                               pre_dispatch='n_jobs')
                     (delayed(eg)(disc_clsdict.restrict(ns, True))
                      for ns in names))
        # tp, tr = izip(*[eg(disc_clsdict.restrict(ns, True),
        #                    verbose=verbose, debug=debug)
        #                 for ns in names])
    tp = np.array(tp)
    tr = np.array(tr)
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
    corpus_file = args['corpusfile'][0]

    fragments_cross_file = args['cross']
    fragments_within_file = args['within']

    corpus = load_corpus(corpus_file, verbose, debug)
    disc_clsdict = load_disc_clsdict(disc_clsfile, corpus, verbose, debug)

    fragments_cross = get_fragments_cross(fragments_cross_file, verbose, debug)
    fragments_within = get_fragments_within(fragments_within_file, verbose, debug)

    pc, rc = calculate_scores(disc_clsdict, fragments_cross,
                              verbose=verbose, debug=debug, n_jobs=n_jobs)

    pw, rw = calculate_scores(disc_clsdict, fragments_within,
                              verbose=verbose, debug=debug, n_jobs=n_jobs)

    fw = np.vectorize(fscore)(pw, rw)
    fc = np.vectorize(fscore)(pc, rc)

    print pretty_score_f(pw, rw, fw, 'group within-speaker',
                         pw.shape[0], sum(map(len, fragments_within)))
    print pretty_score_f(pc, rc, fc, 'group cross-speaker',
                         pc.shape[0], sum(map(len, fragments_cross)))
