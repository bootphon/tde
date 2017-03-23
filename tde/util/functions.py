"""
Assorted helper functions
"""

from __future__ import division

import os.path as path
import math


from itertools import izip, chain, repeat, imap

flatten = chain.from_iterable


def nCr(n,r):
    '''Compute the number of combinations nCr(n,r)
    
    Parameters:
    -----------
    n : number of elements, integer
    r : size of the group, integer

    Returns:
    val : number of combinations 

    >> nCr(4,2)
    6
    
    >> nCr(50,2)
    1225L
    
    '''
    f = math.factorial
    return f(n) / f(r) / f(n-r)

def iterator_length(iterable):
    return sum(1 for _ in iterable)

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


def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return izip(*[chain(iterable, repeat(padvalue, n-1))]*n)

def fname2speaker(corpus_type):
    if corpus_type == 'buckeye':
        return lambda x: path.splitext(path.basename(x))[0][:3]
    elif corpus_type == 'mandarin':
        return lambda x: path.splitext(path.basename(x))[0][:3]
    elif corpus_type == 'english':
        return lambda x: path.splitext(path.basename(x))[0]
    elif corpus_type == 'french':
        return lambda x: path.splitext(path.basename(x))[0][:5]
    elif corpus_type == 'xitsonga':
        return lambda x: path.splitext(path.basename(x))[0].split('_')[2]
    else:
        raise NotImplementedError('no implementation of fname2speaker for {0}'
                                  .format(corpus_type))

def fscore(p, r):
    if p == 0 and r == 0:
        f = 0
    else:
        f = 2 * p * r / (p + r)
    return f
