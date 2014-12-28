from tde.util.splits import check_intervals, truncate_intervals
from tde.data.corpus import Corpus
from tde.data.interval import Interval, IntervalDB
from tde.data.classes import ClassDict, ClassID
from tde.data.fragment import FragmentToken
from tde.data.segment_annotation import SegmentAnnotation


class TestCheckIntervals(object):
    m1 = IntervalDB({'a': [(0.0, 1.0), (2.0, 3.0)]})
    d1 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.0, 1.0), 'm1'),)})
    d2 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.5, 1.5), 'm1'),)})
    d3 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('b', Interval(0.0, 1.0), 'm1'),)})
    d4 = ClassDict({ClassID(0, 'm1'):
                    (FragmentToken('a', Interval(0.5, 2.5), 'm1'),)})

    def test_good_interval(self):
        assert(check_intervals(self.d1, self.m1) == ([], []))

    def test_interval_errors(self):
        assert(check_intervals(self.d2, self.m1) ==
               ([FragmentToken('a', Interval(0.5, 1.5), 'm1')],
               []))
        assert(check_intervals(self.d4, self.m1) ==
               ([FragmentToken('a', Interval(0.5, 2.5), 'm1')],
               []))

    def test_bad_filename(self):
        assert(check_intervals(self.d3, self.m1) == ([], ['b']))

class TestCheckTruncateIntervals(object):
    m1 = IntervalDB({'a': [(0.0, 1.0), (2.0, 3.0)]})
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
               (self.d1, [], []))

    def test_truncate_interval(self):
        assert(truncate_intervals(self.d2, self.ca, self.m1) ==
           (ClassDict({ClassID(0, 'm1'): (FragmentToken('a', Interval(0.5, 1.0),
                                                        ('c', 'd')),)}),
            [], []))
        assert(truncate_intervals(self.d4, self.ca, self.m1) ==
           (ClassDict({ClassID(0, 'm1'): (FragmentToken('a', Interval(0.5, 1.0),
                                                        ('c', 'd')),)}),
            [], []))
