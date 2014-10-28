import pytest

from tde.sortedlist import SortedList

def test_simplelist():
    sl = SortedList([3, 6, 1, 7, 0])

    assert(sl._k == [0, 1, 3, 6, 7])
    assert(sl._v == [0, 1, 3, 6, 7])

    assert(sl.index_le(3) == 2)
    assert(sl.index_lt(3) == 1)
    assert(sl.index_ge(3) == 2)
    assert(sl.index_gt(3) == 3)

    assert(sl.find_lt(3) == 1)
    assert(sl.find_le(4) == 3)
    assert(sl.find_gt(3) == 6)
    assert(sl.find_ge(4) == 6)

    with pytest.raises(ValueError):
        sl.index(4)

    with pytest.raises(ValueError):
        sl.remove(4)

    assert(repr(sl) == '[0, 1, 3, 6, 7]')
    assert(len(sl) == 5)
    for item in sl:
        assert(item in sl)
    for ix, item in enumerate(sl):
        assert(item == sl[ix])
    sl.insert(4)
    assert(sl._k == [0, 1, 3, 4, 6, 7])
    assert(sl._v == [0, 1, 3, 4, 6, 7])

def test_tuplelist():
    data = [(3, 'a'), (4, 'v'), (1, 'z'), (5, 'b')]

    sl = SortedList(data, key=lambda x: x[1])
    assert(sl._k == ['a', 'b', 'v', 'z'])
    assert(sl._v == [(3, 'a'), (5, 'b'), (4, 'v'), (1, 'z')])

    assert(sl.index_lt((10, 'e')) == 1)
    assert(sl.index_le((10, 'e')) == 1)
    assert(sl.index_lt((5, 'b')) == 0)

    with pytest.raises(ValueError):
        sl.index((10, 'b'))

    with pytest.raises(ValueError):
        sl.index((3, 'b'))

from pytest import list_of
@pytest.mark.randomize(l=list_of(int))
def test_intlist1(l):
    sl = SortedList(l)
    assert(sorted(l) == sl._v)
    assert(sorted(l) == sl._k)

@pytest.mark.randomize(l=list_of(int, min_items=1))
def test_intlist2(l):
    el = l[:-1]
    e = l[-1]
    sl = SortedList(el)
    assert(sorted(el) == sl._v)
    assert(sorted(el) == sl._k)

    sl.insert(e)
    assert(sorted(l) == sl._v)
    assert(sorted(l) == sl._k)

    sl.remove(e)
    assert(sorted(el) == sl._v)
    assert(sorted(el) == sl._k)

@pytest.mark.randomize(l=list_of(float))
def test_floatlist1(l):
    sl = SortedList(l)
    assert(sorted(l) == sl._v)
    assert(sorted(l) == sl._k)

@pytest.mark.randomize(l=list_of(float, min_items=1))
def test_floatlist2(l):
    el = l[:-1]
    e = l[-1]
    sl = SortedList(el)
    assert(sorted(el) == sl._v)
    assert(sorted(el) == sl._k)

    sl.insert(e)
    assert(sorted(l) == sl._v)
    assert(sorted(l) == sl._k)

    sl.remove(e)
    assert(sorted(el) == sl._v)
    assert(sorted(el) == sl._k)

@pytest.mark.randomize(l=list_of(str))
def test_stringlist1(l):
    sl = SortedList(l)
    assert(sorted(l) == sl._v)
    assert(sorted(l) == sl._k)

@pytest.mark.randomize(l=list_of(str, min_items=1))
def test_stringlist2(l):
    el = l[:-1]
    e = l[-1]
    sl = SortedList(el)
    assert(sorted(el) == sl._v)
    assert(sorted(el) == sl._k)

    sl.insert(e)
    assert(sorted(l) == sl._v)
    assert(sorted(l) == sl._k)

    sl.remove(e)
    assert(sorted(el) == sl._v)
    assert(sorted(el) == sl._k)

@pytest.mark.randomize(l1=list_of(str),
                       l2=list_of(int))
def test_tuplelist_random(l1, l2):
    zip1 = zip(l1, l2)
    l1 = l1[:len(zip1)]
    l2 = l2[:len(zip1)]
    sl = SortedList(zip1, key=lambda x: x[0])
    assert(sorted(l1) == sl._k)
    assert(sorted(zip1, key=lambda x: x[0]) == sl._v)

    sl = SortedList(zip1, key=lambda x: x[1])
    assert(sorted(l2) == sl._k)
    assert(sorted(zip1, key=lambda x: x[1]) == sl._v)

    zip2 = zip(l2, l1)
    sl = SortedList(zip2, key=lambda x: x[0])
    assert(sorted(l2) == sl._k)
    assert(sorted(zip2, key=lambda x: x[0]) == sl._v)

    sl = SortedList(zip2, key=lambda x: x[1])
    assert(sorted(l1) == sl._k)
    assert(sorted(zip2, key=lambda x: x[1]) == sl._v)
