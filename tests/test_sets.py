import pytest

from pytest import list_of

import tde.sets
import tde.corpus

class TestUnique(object):
    @pytest.mark.randomize(l=list_of(int), choices=range(5))
    def test_unique(self, l):
        u = list(tde.sets.unique(l))
        assert(len(u) == len(set(u)))

    @pytest.mark.randomize(l=list_of(int), choices=range(5))
    def test_conservation(self, l):
        u = list(tde.sets.unique(l))
        assert(all(x in u for x in l))

# class TestFlatten(object):
#     @pytest.mark.randomize(l1=list_of(int), l2=list_of(int), choices=range(5))
#     def test_flat(self, l1, l2):
#         f = list(tde.sets.flatten(zip(l1, l2)))
#         assert(all(len(x) == 1) for x in f)
