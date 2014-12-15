"""Set primitives.

"""
from __future__ import division

from collections import Counter
from itertools import chain

from .util import unique
from .acss import pairwise_substring_completion

_flatten = chain.from_iterable


def typeset(pairs):
    return unique(f.mark for f in flatten(pairs))


def freqs(pairs):
    return dict(Counter(f.mark for f in flatten(pairs)))


def weights(pairs):
    total = len(list(flatten(pairs)))
    fs = freqs(pairs)
    return {t: fs[t] / total for t in typeset(pairs)}


def flatten(pairs):
    r"""Flatten a sequence of ((c1, p1), (c2, p2)) pairs into a set of (c, p).

    .. math::

       \mathrm{flat}(P) = \{(i, j) | \exists q(((i, j), q) \in P)\}

    Parameters
    ----------
    pairs : iterable over (FragmentToken, FragmentToken) pairs
        pairs

    Returns
    -------
    p : iterator over FragmentTokens

    """
    return unique(_flatten(pairs))


def Pgoldclus(clsdict):
    r"""Generate Pgoldclus - all the non-overlapping fragment pairs that have
    the same annotation.

    .. math::

       P_{\mathrm{goldclus}} = \{((i, j), (k,l)) | \exists c_1, c_2\in C_{\mathrm{disc}} ((i,j)\in c_1 \land (k, l)\in c_2 \land T_{i,j} = T_{k,l} \land \{i\ldots j\}\cap\{k\ldots l\}=\emptyset)\}

    Parameters
    ----------
    clsdict : ClassDict

    Returns
    -------
    iter : iterator (FragmentToken, FragmentToken) pairs

    """
    return ((f1, f2)
            for f1, f2 in clsdict.iter_pairs(within=False, order=False)
            if f1.mark == f2.mark and
            not (f1.name == f2.name and
                 f1.interval.overlap(f2.interval) > 0))


def Pgoldlex(clsdict, lexicon):
    words = set(r for v in lexicon.itervalues() for r in v)

    return ((f1, f2)
            for f1, f2 in clsdict.iter_pairs(within=False, order=False)
            if f1.mark == f2.mark
            and not (f1.name == f2.name and f1.interval.overlap(f2.interval) > 0)
            and f1.mark in words)


def Pclus_single(clsdict):
    r"""Generate Pclus - all the pairs of FragmentTokens per cluster, each
    pair only occurring once, regardless of order. Contrast with Pclus

    .. math::

       P_{\mathrm{clus_single}} = \{((i, j), (k, l)) | \exists c \in C_{\mathrm{disc}} \land (i,j)\in c \land (j,k) \in c\}

    where :math:`C_{\mathrm{disc}}` is the set of discovered clusters, each set being a set of fragments.

    Parameters
    ----------
    classdict : ClassDict

    Returns
    -------
    iter : iterator over FragmentToken pairs

    """
    return clsdict.iter_pairs(within=True, order=False)


def Pclus(clsdict):
    r"""Generate Pclus - all the pairs of FragmentTokens per cluster

    .. math::

       P_{\mathrm{clus}} = \{((i, j), (k, l)) | \exists c \in C_{\mathrm{disc}} \land (i,j)\in c \land (j,k) \in c\}

    where :math:`C_{\mathrm{disc}}` is the set of discovered clusters, each set being a set of fragments.

    Parameters
    ----------
    clsdict : ClassDict

    Returns
    -------
    iter : iterator (FragmentToken, FragmentToken) pairs

    """
    return clsdict.iter_pairs(within=True, order=True)


def Fclus(clsdict):
    """Generate Fclus all the fragments in a classdict

    Parameters
    ----------
    clsdict : ClassDict

    Returns
    -------
    iter : iterator over FragmentTokens

    """
    return clsdict.iter_fragments()


def Pdisc(clsdict):
    r"""Generate Pdisc - the discovered fragment pairs.

    Delegates to Pclus

    Parameters
    ----------
    clsdict : ClassDict

    Returns
    -------
    iter : iterator (FragmentToken, FragmentToken) pairs

    """
    return Pclus(clsdict)


def nmatch(pairs):
    """Count the number of pairs of fragments per annotation string.

    .. math::
       \mathrm{nmatch}(t, P) = |\{(x, (i, j))\in P | T_{i,j} = t\}|

    Parameters
    ----------
    pairs : iterable over (FragmentToken, FragmentToken) pairs
    corpus : Corpus

    Returns
    -------
    d : dict from string tuple to int
        Annotation counts.

    """
    return Counter(f.mark
                   for _, f in pairs)



def Psubs(clsdict, corpus, minlength=3, maxlength=20):
    """Generate Psubs - the substring completion of a set of pairs.

    Psubs is the association between all substrings of the pairs in classdict.

    Parameters
    ----------
    clsdict : ClassDict
    corpus : Corpus
    minlength : int, optional
        minimum number of phones for the substrings
    maxlength : int, optional
        maximum number of phones for the substrings

    Returns
    -------
    i : iterator over (FragmentToken, FragmentToken) pairs

    """
    sub_pairs = (pairwise_substring_completion(f1, f2, corpus,
                                               minlength,
                                               maxlength)
                 for f1, f2 in clsdict.iter_pairs(within=True, order=True))
    return flatten(sub_pairs)
