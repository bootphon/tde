import pytest

from pytest import list_of

from tde.data.sets import typeset, freqs, weights
from tde.data.fragment import FragmentToken
from tde.data.interval import Interval

def test_typeset():
    pairs = [(FragmentToken(None, Interval(0,1), 'm{0}'.format(n1)),
              FragmentToken(None, Interval(0,1), 'n{0}'.format(n2)))
              for n1, n2 in zip(xrange(10), xrange(10,20))]
    assert (set(list(typeset(pairs))) ==
            set(['m{0}'.format(n) for n in xrange(10)] +
                ['n{0}'.format(n) for n in xrange(10,20)]))
    pairs = []
    assert (set(list(typeset(pairs))) == set())

    pairs = [(FragmentToken(None, Interval(0,1), 'm{0}'.format(n)),
              FragmentToken(None, Interval(0,1), 'm{0}'.format(n)))
             for n in xrange(10)]
    assert (set(typeset(pairs)) == set('m{0}'.format(n) for n in xrange(10)))

def test_freqs():
    pairs = [(FragmentToken(None, Interval(0,1), 'm{0}'.format(n1)),
              FragmentToken(None, Interval(0,1), 'n{0}'.format(n2)))
              for n1, n2 in zip(xrange(10), xrange(10,20))]
    assert (freqs(pairs) == dict({'m{0}'.format(n): 1
                                  for n in xrange(10)}.items() +
                                 {'n{0}'.format(n): 1
                                  for n in xrange(10,20)}.items()))
    pairs = []
    assert (freqs(pairs) == dict())

    pairs = [(FragmentToken(None, Interval(0,1), 'm{0}'.format(n)),
              FragmentToken(None, Interval(0,1), 'm{0}'.format(n)))
             for n in xrange(10)]
    assert (freqs(pairs) == {'m{0}'.format(n): 1 for n in xrange(10)})

# def test_weights():
