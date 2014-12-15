from __future__ import division

import numpy as np
from .levenshtein import distance

def NED(clsdict):
    neds = np.fromiter((ned(f1.mark, f2.mark)
                        for f1, f2 in clsdict.iter_pairs(within=True,
                                                         order=False)),
                       dtype=np.double)
    return neds.mean()

def cover(clsdict):
    """Compute the cover

    Parameters
    ----------


    """
    return sum(f.interval.length()
               for f in clsdict.iter_fragments())

def coverage(disc_clsdict, gold_clsdict):
    """Compute the coverage of disc_clsdict relative to gold_clsdict

    Parameters
    ----------
    disc_clsdict, gold_clsdict : ClassDict

    Returns
    -------
    d : double
        relative coverage
    """
    return cover(disc_clsdict) / cover(gold_clsdict)

def ued(s1, s2):
    """Unnormalized edit distance.

    Calculate the levenshtein distance between s1 and s2.

    Parameters
    ----------
    s1, s2 : iterable

    Returns
    -------
    r : np.uint32
        edit distance
    """
    symbols = list(set(s1+s2))
    symbol2ix = {v: k for k, v in enumerate(symbols)}

    s1_arr = np.fromiter((symbol2ix[s] for s in s1), dtype=np.uint32)
    s2_arr = np.fromiter((symbol2ix[s] for s in s2), dtype=np.uint32)

    return distance(s1_arr, s2_arr)

def ned(s1, s2):
    """Normalized edit distance.

    Calculate the levenshtein distance between s1 and s2 divided by the maximum
    of the lengths of s1 and s2.

    Parameters
    ----------
    s1, s2 : iterable


    Returns
    -------
    r : double
        edit distance
    """
    return ued(s1, s2) / max(len(s1), len(s2))


def pretty_score(ned_score, coverage_score, label, nfolds, nsamples):
    r = '{sep}\n'.format(sep=37*'-')
    r += '{label}\n#folds:    {nfolds}\n#samples:  {nsamples}\n'.format(
        label=label, nfolds=nfolds, nsamples=nsamples)
    r += '{sep}\n'.format(sep=37*'-')
    r += '{score:9s}  {mean:5s}  {std:5s}  {min:5s}  {max:5s}\n'.format(
        score="measure", mean="mean", std="std", min="min", max="max")
    r += '---------  -----  -----  -----  -----\n'
    r += '{score:9s}  {mean:.3f}  {std:.3f}  {min:.3f}  {max:.3f}\n'.format(
        score="NED", mean=ned_score.mean(), std=ned_score.std(),
        min=ned_score.min(), max=ned_score.max())
    r += '{score:9s}  {mean:.3f}  {std:.3f}  {min:.3f}  {max:.3f}\n'.format(
        score="coverage", mean=coverage_score.mean(), std=coverage_score.std(),
        min=coverage_score.min(), max=coverage_score.max())
    r += '{sep}\n'.format(sep=37*'-')
    return r
