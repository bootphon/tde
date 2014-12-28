"""goldset: extract gold fragment pairs

"""

from itertools import combinations, chain, izip, izip_longest
import sys

import time

from joblib import Parallel, delayed

from corpus import Interval, FragmentToken
from acss import allcommonsubstrings

def extract_batch(tokens, ixs, minlength, maxlength):
    """Extract gold alignments between two lists.

    This is just a wrapper around `extract_single` to send larger batches into
    separate processes.

    Parameters
    ----------
    tokens : list of list of FragmentTokens
        All input tokens
    ixs : iterable of (int, int) pairs
        Batch to be processed.
    minlength : int
        Minimum number of symbols in a fragment.

    Returns
    -------
    r : list of (FragmentToken, FragmentToken)
        List of token pairs containing the cooccurring fragments.

    """
    r = []
    if ixs is None:
        return r

    for ix in ixs:
        if ix is None:
            continue
        ix1, ix2 = ix
        r_ = extract_single(tokens[ix1], tokens[ix2], minlength, maxlength,
                            ix1==ix2)
        if r_:
            r.extend(r_)
    return r


def extract_single(tokens1, tokens2, minlength, maxlength, same):
    """Extract gold alignments between two phone lists.

    Parameters
    ----------
    tokens1, tokens2 : list of FragmentTokens
    minlength : int
        Minimum number of symbols in a fragment
    same : boolean
        Whether `tokens1` and `tokens2` are identical.

    Returns
    -------
    l : list of (FragmentToken, FragmentToken)
        List of token pairs containing the cooccurring fragments

    """
    ids1, intervals1, phones1 = zip(*tokens1)
    ids2, intervals2, phones2 = zip(*tokens2)
    id1 = ids1[0]  # ids are all the same
    id2 = ids2[0]
    css = allcommonsubstrings(phones1, phones2,
                              minlength=minlength, maxlength=maxlength,
                              same=same)
    if css is None:
        return []
    r = []
    for slice1, slice2 in css:
        r.append((FragmentToken(id1,
                                Interval(intervals1[slice1.start].start,
                                         intervals1[slice1.stop - 1].end),
                                phones1[slice1]),
                  FragmentToken(id2,
                                Interval(intervals2[slice2.start].start,
                                         intervals2[slice2.stop - 1].end),
                                phones2[slice2])))
    return r


def extract_gold_fragments(tokenlists, minlength=3, maxlength=20,
                           verbose=False, n_jobs=1, batch_size=10000):
    """Extract the gold fragments.

    Parameters
    ----------
    tokenlists : list of lists of FragmentTokens
    minlength : int, optional
        Minimum length of fragments
    verbose : boolean
        Print information during processing.

    Returns
    -------
    l : list of (string, string, list of (list of string, Interval, Interval))
        A list consisting of tuples of two filename identifiers and a list of
        a phonesequence and the intervals in the two filenames

    l : list of FragmentTokens

    returns a list of (id1, id2, list of (phonseq, interval1, interval2)) tuples
    where id1, id2 are wavfile identifiers, phonseq is the fragment as a list
    of phones and interval1, interval2 are the time intervals in wavfile1 and
    wavfile2 respectively

    """
    # combinations of all tokens in fragment_type plus each token with itself
    combos = chain(combinations(xrange(len(tokenlists)), r=2),
                   izip(xrange(len(tokenlists)), xrange(len(tokenlists))))
    if verbose:
        total = sum(xrange(len(tokenlists)+1))
        print 'Found {0} sequences. Extracting fragments from {1} combinations'.format(
            len(tokenlists), total)
        if verbose:
            t0 = time.time()
        sys.stdout.flush()

    r = list(chain.from_iterable(Parallel(n_jobs=n_jobs,
                                          pre_dispatch='2*n_jobs',
                                          verbose=5 if verbose else 0)
                                 (delayed(extract_batch)(tokenlists,
                                                         ixs,
                                                         minlength,
                                                         maxlength)
                                  for ixs in izip_longest(*([iter(combos)]
                                                            * batch_size)))))
    if verbose:
        print '\rDone. Took {0:.3f} seconds.                           '.format(
            time.time() - t0)
    r = [t for t in r if not t == []]
    return r
