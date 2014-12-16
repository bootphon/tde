from itertools import izip, chain, repeat, imap
from contextlib import contextmanager
import time
import sys


def unique(iterable):
    seen = set()
    seen_add = seen.add
    for element in iterable:
        if element in seen:
            continue
        seen_add(element)
        yield element


def unique_by(iterable, key):
    """Iterate over elements that are unique in their key.

    Parameters:
    -----------
    iterable : iterator
    key : function that produces the key to compare by

    Returns:
    --------
    i : iterator over unique elements.
    """
    seen = set()
    seen_add = seen.add
    for element in iterable:
        k = key(element)
        if k in seen:
            continue
        seen_add(k)
        yield element

def intersection(iterable1, iterable2):
    set1 = set(iterable1)
    seen = set()
    seen_add = seen.add
    for element in iterable2:
        if element in seen:
            continue
        seen_add(element)
        if element in set1:
            yield element


def intersection_by(iterable1, iterable2, key):
    set1 = set(imap(key, iterable1))
    seen = set()
    seen_add = seen.add
    for element in iterable2:
        k = key(element)
        if k in seen:
            continue
        seen_add(k)
        if k in set1:
            yield element

def dbg_banner(s):
    l = len(s)
    return '-'*l+'\n'+s+'\n'+'-'*l


def pretty_pairs(pclus_set):
    strings = [('({0} {1} {2})'.format(f1.name, f1.interval, f1.mark),
                '({0} {1} {2})'.format(f2.name, f2.interval, f2.mark))
               for f1, f2 in pclus_set]
    if len(strings) == 0:
        return ''
    longest = max(len(x[0]) for x in strings)
    return '\n'.join('{1:{0}s} - {2:{0}s}'.format(longest, s1, s2)
                     for s1, s2 in strings)


def pretty_scores(ps, rs, fs, label, nfolds, nsamples):
    r = '{sep}\n'.format(sep=37*'-')
    r += '{label}\n#folds:    {nfolds}\n#samples:  {nsamples}\n'.format(
        label=label, nfolds=nfolds, nsamples=nsamples)
    r += '{sep}\n'.format(sep=37*'-')
    r += '{score:9s}  {mean:5s}  {std:5s}  {min:5s}  {max:5s}\n'.format(
        score="measure", mean="mean", std="std",
        min="min", max="max")
    r += '---------  -----  -----  -----  -----\n'
    r += '{score:9s}  {mean:.3f}  {std:.3f}  {min:.3f}  {max:.3f}\n'.format(
        score="precision", mean=ps.mean(), std=ps.std(),
        min=ps.min(), max=ps.max())
    r += '{score:9s}  {mean:.3f}  {std:.3f}  {min:.3f}  {max:.3f}\n'.format(
        score="recall", mean=rs.mean(), std=rs.std(),
        min=rs.min(), max=rs.max())
    r += '{score:9s}  {mean:.3f}  {std:.3f}  {min:.3f}  {max:.3f}\n'.format(
        score="fscore", mean=fs.mean(), std=fs.std(),
        min=fs.min(), max=fs.max())
    r += '{sep}\n'.format(sep=37*'-')
    return r

@contextmanager
def verb_print(label, verbose=False, when_done=False,
               timeit=False, with_dots=False):
    if timeit:
        t0 = time.time()
    if verbose:
        msg = label + ('...' if with_dots else '') + ('' if when_done else '\n')
        print msg,
        sys.stdout.flush()
    try:
        yield
    finally:
        if verbose and when_done:
            if timeit:
                print 'done. Time: {0:.3f}s'.format(time.time() - t0)
            else:
                print 'done.'
            sys.stdout.flush()
        elif verbose and timeit:
            print '{1}: time: {0:.3f}s'.format(time.time() - t0, label)
            sys.stdout.flush()


def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return izip(*[chain(iterable, repeat(padvalue, n-1))]*n)

def fname2speaker(corpus_type):
    if corpus_type == 'buckeye':
        return lambda x: x[:3]
    else:
        raise NotImplementedError('no implementation of fname2speaker for {0}'
                                  .format(corpus_type))

def fscore(p, r):
    if p == 0 and r == 0:
        f = 0
    else:
        f = 2 * p * r / (p + r)
    return f
