import pytest

from tde.util.functions import unique, intersection, fname2speaker

@pytest.mark.randomize(it=pytest.list_of(str))
def test_unique(it):
    assert (sorted(list(unique(it))) == sorted(list(set(it))))

def test_intersection():
    it1 = range(20)
    it2 = range(10, 30)
    assert (sorted(list(intersection(it1, it2))) ==
            sorted(list(set(it1) & set(it2))))

def test_fname2speaker():
    t = 'buckeye'
    assert (fname2speaker(t)('s2801a_1923810923') == 's28')
    with pytest.raises(NotImplementedError):
        fname2speaker('somethingelse')
