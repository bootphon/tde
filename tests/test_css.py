import pytest
from pytest import list_of
from tde.acss import allcommonsubstrings, substrings

class TestPairwiseSubstringCompletion(object):
    pass

class TestSubstrings(object):
    def test_triv(self):
        assert (list(substrings('abc', 3, 20)) == ['abc'])

    def test_null(self):
        assert (list(substrings('abc', 4, 20)) == [])

    def test_string(self):
        assert (set(list(substrings('abcde', 3, 20))) ==
                set(['abc', 'abcd', 'abcde', 'bcd', 'bcde', 'cde']))

    @pytest.mark.randomize(s1=str, minlength=int, maxlength=int)
    def length_invariant(s1, minlength, maxlength):
        l1 = len(s1)
        for sub in substrings(s1, minlength):
            assert (minlength <= len(sub) <= min(l1, maxlength))

def test_empty():
    l1 = 'abcde'
    l2 = 'fghij'
    assert(allcommonsubstrings(l1, l2) == [])

    l1 = []
    l2 = []
    assert(allcommonsubstrings(l1, l2) == [])

def test_single_empty():
    l1 = 'abcde'
    assert(allcommonsubstrings(l1, same=True) == [])

def test_single_nonempty():
    l1 = 'abcdeabc'
    expected = [(slice(0, 3, None), slice(5, 8, None)),
                (slice(5, 8, None), slice(0, 3, None))]
    assert(allcommonsubstrings(l1, minlength=3, same=True) == expected)

def test_simple():
    l1 = 'abcde'
    l2 = 'fghijabc'
    m1, m2 = allcommonsubstrings(l1, l2, minlength=3)[0]
    assert(l1[m1] == l2[m2])


@pytest.mark.randomize(l1=list_of(int, min_items=10, max_items=100),
                       l2=list_of(int, min_items=10, max_items=100),
                       choices=[0,1])
def test_length(l1, l2):
    n = 4
    for slice1, slice2 in allcommonsubstrings(l1, l2, minlength=n):
        assert(slice1.stop - slice1.start >= n)
        assert(slice2.stop - slice2.start >= n)


@pytest.mark.randomize(l1=list_of(int, min_items=10, max_items=100),
                       l2=list_of(int, min_items=10, max_items=100),
                       choices=[0,1])
def test_equality(l1, l2):
    for slice1, slice2 in allcommonsubstrings(l1, l2, minlength=4):
        assert(l1[slice1] == l2[slice2])


@pytest.mark.randomize(l1=list_of(int, min_items=10, max_items=100),
                       l2=list_of(int, min_items=10, max_items=100),
                       choices=[0,1])
def test_uniqueness(l1, l2):
    results = set()
    ss = allcommonsubstrings(l1, l2, minlength=4)
    for slice1, slice2 in ss:
        results.add((slice1.start, slice1.stop, slice2.start, slice2.stop))
    assert(len(results) == len(ss))
