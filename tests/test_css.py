import pytest
from pytest import list_of
from tde.substrings.acss import allcommonsubstrings, substrings, psubstrings, \
    pairwise_substring_completion

from tde.data.corpus import Corpus
from tde.data.fragment import FragmentToken
from tde.data.interval import Interval
from tde.data.segment_annotation import SegmentAnnotation


class TestPairwiseSubstringCompletion(object):
    fragments = [FragmentToken('a', Interval(0.0, 0.25), 'a'),
                 FragmentToken('a', Interval(0.25, 0.5), 'b'),
                 FragmentToken('a', Interval(0.5, 0.75), 'c'),
                 FragmentToken('a', Interval(0.75, 1.0), 'd'),
                 FragmentToken('a', Interval(1.0, 1.25), 'e'),

                 FragmentToken('b', Interval(0.0, 0.25), 'a'),
                 FragmentToken('b', Interval(0.25, 0.5), 'b'),
                 FragmentToken('b', Interval(0.5, 0.75), 'c'),
                 FragmentToken('b', Interval(0.75, 1.0), 'd'),
                 FragmentToken('b', Interval(1.0, 1.25), 'e'),

                 FragmentToken('c', Interval(0.0, 0.25), 'f'),
                 FragmentToken('c', Interval(0.25, 0.5), 'g'),
                 FragmentToken('c', Interval(0.5, 0.75), 'h'),
                 FragmentToken('c', Interval(0.75, 1.0), 'i'),
                 FragmentToken('c', Interval(1.0, 1.25), 'j')]
    sa = [SegmentAnnotation('a', fragments[:5]),
          SegmentAnnotation('b', fragments[5:10]),
          SegmentAnnotation('c', fragments[10:])]
    ca = Corpus(sa)
    fragment1 = FragmentToken('a', Interval(0.0, 1.0), None)
    fragment2 = FragmentToken('b', Interval(0.0, 1.0), None)
    fragment3 = FragmentToken('c', Interval(0.0, 1.0), None)
    fragment4 = FragmentToken('b', Interval(0.0, 1.25), None)

    pfragments = [FragmentToken('a', Interval(0.0, 1.0), ('a', 'b', 'c', 'd')),
                  FragmentToken('a', Interval(0.25, 1.25), ('b', 'c', 'd', 'e')),
                  FragmentToken('a', Interval(0.0, 0.75), ('a', 'b', 'c')),
                  FragmentToken('a', Interval(0.25, 1.0), ('b', 'c', 'd')),
                  FragmentToken('a', Interval(0.5, 1.25), ('c', 'd', 'e')),

                  FragmentToken('b', Interval(0.0, 1.0), ('a', 'b', 'c', 'd')),
                  FragmentToken('b', Interval(0.25, 1.25), ('b', 'c', 'd', 'e')),
                  FragmentToken('b', Interval(0.0, 0.75), ('a', 'b', 'c')),
                  FragmentToken('b', Interval(0.25, 1.0), ('b', 'c', 'd')),
                  FragmentToken('b', Interval(0.5, 1.25), ('c', 'd', 'e')),

                  FragmentToken('c', Interval(0.0, 1.0), ('f', 'g', 'h', 'i')),
                  FragmentToken('c', Interval(0.25, 1.25), ('g', 'h', 'i', 'j')),
                  FragmentToken('c', Interval(0.0, 0.75), ('f', 'g', 'h')),
                  FragmentToken('c', Interval(0.25, 1.0), ('g', 'h', 'i')),
                  FragmentToken('c', Interval(0.5, 1.25), ('h', 'i', 'j'))]


    def test_same(self):
        # fragment1 - fragment2
        # abcd - abcd

        # expected:
        # abcd - abcd
        # abc - abc
        # bcd - bcd
        e = set([(self.pfragments[0], self.pfragments[5]),
                 (self.pfragments[2], self.pfragments[7]),
                 (self.pfragments[3], self.pfragments[8])])
        p = set(pairwise_substring_completion(self.fragment1,
                                              self.fragment2,
                                              self.ca, 3, 20))
        assert(p == e)

    def test_different(self):
        # fragment1 - fragment3
        # abcd - fghi

        # expected:
        # abcd - fghi
        # abc - fgh
        # bcd - ghi
        e = set([(self.pfragments[0], self.pfragments[10]),
                 (self.pfragments[2], self.pfragments[12]),
                 (self.pfragments[3], self.pfragments[13])])
        p = set(pairwise_substring_completion(self.fragment1,
                                              self.fragment3,
                                              self.ca, 3, 20))
        assert(e == p)

    def test_longer(self):
        # fragment1 - fragment4
        # abcd - abcde

        # expected:

        # abcd - abcd
        # abc - abc
        # bcd - bcd

        # abcd - bcde
        # abc - bcd
        # bcd - cde
        e = set([(self.pfragments[0], self.pfragments[5]),
                 (self.pfragments[2], self.pfragments[7]),
                 (self.pfragments[3], self.pfragments[8]),

                 (self.pfragments[0], self.pfragments[6]),
                 (self.pfragments[2], self.pfragments[8]),
                 (self.pfragments[3], self.pfragments[9])])
        p = set(pairwise_substring_completion(self.fragment1,
                                              self.fragment4,
                                              self.ca, 3, 20))
        assert (e == p)

    def test_different_and_longer(self):
        # fragment3 - fragment4
        # fghi - abcde

        # expected:
        # fghi - abcd
        # fgh - abc
        # ghi - bcd

        # fghi - bcde
        # fgh - bcd
        # ghi - cde
        e = set([(self.pfragments[10], self.pfragments[5]),
                 (self.pfragments[12], self.pfragments[7]),
                 (self.pfragments[13], self.pfragments[8]),
                 (self.pfragments[10], self.pfragments[6]),
                 (self.pfragments[12], self.pfragments[8]),
                 (self.pfragments[13], self.pfragments[9])])
        p = set(pairwise_substring_completion(self.fragment3,
                                              self.fragment4,
                                              self.ca, 3, 20))
        assert (e == p)


class TestPSubstrings(object):
    def test_triv(self):
        assert (list(psubstrings('abc', 'abc', 3, 20)) == [('abc', 'abc')])

    def test_null(self):
        assert (list(psubstrings('abc', 'abc', 4, 20)) == [])
        assert (list(psubstrings('abc', 'abcd', 4, 20)) == [])

    def test_equal(self):
        assert (set(list(psubstrings('abcd', 'abcd', 3, 20))) ==
                set([('abcd', 'abcd'), ('abc', 'abc'), ('bcd', 'bcd')]))
        assert (set(list(psubstrings('abcde', 'abcde', 3, 20))) ==
                set([('abcde', 'abcde'), ('abcd', 'abcd'), ('abc', 'abc'),
                     ('bcd', 'bcd'), ('bcde', 'bcde'), ('cde', 'cde')]))

    def test_inequal(self):
        assert (set(list(psubstrings('abc', 'abcd', 3, 20))) ==
                set([('abc', 'abc'), ('abc', 'bcd')]))
        assert (set(list(psubstrings('abcd', 'abcde', 3, 20))) ==
                set([('abcd', 'abcd'), ('abc', 'abc'), ('bcd', 'bcd'),
                     ('abcd', 'bcde'), ('abc', 'bcd'), ('bcd', 'cde')]))
        assert (set(list(psubstrings('abcd', 'abcdef', 3, 20))) ==
                set([('abcd', 'abcd'), ('abc', 'abc'), ('bcd', 'bcd'),
                     ('abcd', 'bcde'), ('abc', 'bcd'), ('bcd', 'cde'),
                     ('abcd', 'cdef'), ('abc', 'cde'), ('bcd', 'def')]))

    def test_reverse(self):
        assert (set(list(psubstrings('abcde', 'abcd', 3, 20))) ==
                set([(b, a) for a, b in psubstrings('abcd', 'abcde', 3, 20)]))

    @pytest.mark.randomize(l1=list_of(int, min_items=10, max_items=100),
                           l2=list_of(int, min_items=10, max_items=100),
                           choices=[0,1])
    def test_length(self, l1, l2):
        for a, b in psubstrings(l1, l2, 3, 40):
            assert (3 <= len(a) <= 40)
            assert (3 <= len(b) <= 40)


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
