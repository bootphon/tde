import pytest
from pytest import list_of
from tde.acss import allcommonsubstrings


def test_empty():
    l1 = 'abcde'
    l2 = 'fghij'
    assert(allcommonsubstrings(l1, l2) == [])

    l1 = []
    l2 = []
    assert(allcommonsubstrings(l1, l2) == [])


def test_simple():
    l1 = 'abcde'
    l2 = 'fghijabc'
    m1, m2 = allcommonsubstrings(l1, l2, minlength=3)[0]
    assert(l1[m1] == l2[m2])


@pytest.mark.randomize(l1=list_of(int, min_items=100, max_items=100),
                       l2=list_of(int, min_items=100, max_items=100),
                       choices=[0,1])
def test_length(l1, l2):
    n = 4
    for slice1, slice2 in allcommonsubstrings(l1, l2, minlength=n):
        assert(slice1.stop - slice1.start >= n)
        assert(slice2.stop - slice2.start >= n)


@pytest.mark.randomize(l1=list_of(int, min_items=100, max_items=100),
                       l2=list_of(int, min_items=100, max_items=100),
                       choices=[0,1])
def test_equality(l1, l2):
    for slice1, slice2 in allcommonsubstrings(l1, l2, minlength=4):
        assert(l1[slice1] == l2[slice2])


@pytest.mark.randomize(l1=list_of(int, min_items=100, max_items=100),
                       l2=list_of(int, min_items=100, max_items=100),
                       choices=[0,1])
def test_uniqueness(l1, l2):
    results = set()
    ss = allcommonsubstrings(l1, l2, minlength=4)
    for slice1, slice2 in ss:
        results.add((slice1.start, slice1.stop, slice2.start, slice2.stop))
    assert(len(results) == len(ss))
