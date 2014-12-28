"""
Objects for holding fragments of annotation.

Classes
-------
FragmentToken
    Hold single pieces of annotation (a word, a phone), and associate a
    filename and interval with a symbol (`mark`).

FragmentType
    Hold multiple tokens together and collectively associate them with a
    symbol (`mark`).

Functions
---------
token_cmp
    Comparison function for FragmentToken objects.

"""

import collections

from tde.data.interval import interval_cmp

FragmentType = collections.namedtuple('FragmentType', ['tokens', 'mark'])
FragmentType.__repr__ = \
    lambda self: '%s(%r, %r, %r)' % (self.__class__.__name__,
                                     self.tokens, self.mark)


FragmentToken = collections.namedtuple('FragmentToken',
                                       ['name', 'interval', 'mark'])
FragmentToken.__repr__ = \
    lambda self: '%s(%r, %r, %r)' % (self.__class__.__name__,
                                     self.name, self.interval,
                                     self.mark)

def token_cmp(token1, token2):
    """Comparison function for FragmentToken objects.

    Compares tokens on their interval. Returns -1 if `token1` < `token2`,
    0 if `token1` == `token2` (that is, they overlap) and
    1 if `token1` > `token2`.

    Parameters
    ----------
    token1, token2 : FragmentToken

    Returns
    -------
    int
        Comparison result.

    Raises
    ------
    ValueError
        If the names of the FragmentTokens don't match.
    """
    if token1.name != token2.name:
        raise ValueError('fragments with different `name` values cannot be '
                         'compared')
    return interval_cmp(token1.interval, token2.interval)
