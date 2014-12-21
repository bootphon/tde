import pytest

from tde.split_utils import FileNameError, largest_overlap, check_intervals, \
    truncate_intervals
from tde.corpus import Interval, ClassID, ClassDict, FragmentToken, \
    SegmentAnnotation, Corpus

class TestLargestOverlap(object):
    mapping = {'a': [(0.0, 1.0), (2.0, 3.0)]}

    def test_fname_not_found(self):
        with pytest.raises(FileNameError):
            largest_overlap(self.mapping, 'b', 0.0, 0.0)
        try:
            largest_overlap(self.mapping, 'b', 0.0, 0.0)
        except FileNameError as e:
            assert(e.message == 'b')

    def test_bad_interval(self):
        with pytest.raises(ValueError):
            largest_overlap(self.mapping, 'a', 1.0, 0.0)
        with pytest.raises(ValueError):
            largest_overlap(self.mapping, 'a', -1.0, 0.0)
        with pytest.raises(ValueError):
            largest_overlap(self.mapping, 'a', 0.0, -1.0)

    def test_no_overlap(self):
        with pytest.raises(KeyError):
            largest_overlap(self.mapping, 'a', 1.1, 1.9)
        with pytest.raises(KeyError):
            largest_overlap(self.mapping, 'a', 1.0, 2.0)

    def test_within(self):
        assert(largest_overlap(self.mapping, 'a', 0.1, 0.9)
               == (0.1, 0.9))
        assert(largest_overlap(self.mapping, 'a', 2.1, 2.9)
               == (2.1, 2.9))

    def test_overlap_1(self):
        assert(largest_overlap(self.mapping, 'a', 0.5, 1.5)
               == (0.5, 1.0))
        assert(largest_overlap(self.mapping, 'a', 1.5, 2.5)
               == (2.0, 2.5))
        assert(largest_overlap(self.mapping, 'a', 2.5, 3.5)
               == (2.5, 3.0))

    def test_overlap_2(self):
        assert(largest_overlap(self.mapping, 'a', 0.6, 2.5)
               == (2.0, 2.5))
        assert(largest_overlap(self.mapping, 'a', 0.5, 2.5)
               == (0.5, 1.0))
        assert(largest_overlap(self.mapping, 'a', 0.0, 3.0)
               == (0.0, 1.0))

class TestCheckIntervals(object):
    m1 = {'a': [(0.0, 1.0), (2.0, 3.0)]}
    d1 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.0, 1.0), 'm1'),)})
    d2 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.5, 1.5), 'm1'),)})
    d3 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('b', Interval(0.0, 1.0), 'm1'),)})
    d4 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.5, 2.5), 'm1'),)})

    def test_good_interval(self):
        assert(check_intervals(self.d1, self.m1) == ([], [], []))

    def test_interval_errors(self):
        assert(check_intervals(self.d2, self.m1) ==
               ([(FragmentToken('a', Interval(0.5, 1.5), 'm1'), 0.5, 1.0)],
               [], []))
        assert(check_intervals(self.d4, self.m1) ==
               ([(FragmentToken('a', Interval(0.5, 2.5), 'm1'), 0.5, 1.0)],
               [], []))

    def test_bad_filename(self):
        assert(check_intervals(self.d3, self.m1) == ([], ['b'], []))

class TestCheckTruncateIntervals(object):
    m1 = {'a': [(0.0, 1.0), (2.0, 3.0)]}
    d1 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.0, 1.0), 'm1'),)})
    d2 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.5, 1.5), 'm1'),)})
    d3 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('b', Interval(0.0, 1.0), 'm1'),)})
    d4 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.5, 2.5), 'm1'),)})
    sa = [SegmentAnnotation('a', [FragmentToken('a', Interval(0.0, 0.25), 'a'),
                                  FragmentToken('a', Interval(0.25, 0.5), 'b'),
                                  FragmentToken('a', Interval(0.5, 0.75), 'c'),
                                  FragmentToken('a', Interval(0.75, 1.0), 'd')])]
    ca = Corpus(sa)

    def test_good_interval(self):
        assert(truncate_intervals(self.d1, self.ca, self.m1) ==
               (self.d1, [], [], []))

    def test_truncate_interval(self):
        assert(truncate_intervals(self.d2, self.ca, self.m1) ==
           (ClassDict({ClassID(0, 'm1'): (FragmentToken('a', Interval(0.5, 1.0),
                                                        ('c', 'd')),)}),
            [], [], []))
        assert(truncate_intervals(self.d4, self.ca, self.m1) ==
           (ClassDict({ClassID(0, 'm1'): (FragmentToken('a', Interval(0.5, 1.0),
                                                        ('c', 'd')),)}),
            [], [], []))
