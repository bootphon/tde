import pytest

from tde.data.corpus import Corpus
from tde.data.segment_annotation import SegmentAnnotation
from tde.data.interval import Interval, IntervalDB
from tde.data.fragment import FragmentToken

class TestCorpus(object):
    segment_annotations = [SegmentAnnotation('a', [
        FragmentToken('a', Interval(0.0, 0.1), 'a'),
        FragmentToken('a', Interval(0.1, 0.2), 'r'),
        FragmentToken('a', Interval(0.2, 0.3), 'm'),
        FragmentToken('a', Interval(0.3, 0.4), 's'),
        FragmentToken('a', Interval(0.4, 0.5), 'a')]),
                        SegmentAnnotation('a', [
        FragmentToken('a', Interval(0.7, 0.8), 'w'),
        FragmentToken('a', Interval(0.8, 0.9), 'o'),
        FragmentToken('a', Interval(0.9, 1.0), 'r'),
        FragmentToken('a', Interval(1.0, 1.1), 'm'),
        FragmentToken('a', Interval(1.1, 1.2), 's'),
        FragmentToken('a', Interval(1.2, 1.3), 'a')]),
                        SegmentAnnotation('b', [
        FragmentToken('b', Interval(0.1, 0.2), 'w'),
        FragmentToken('b', Interval(0.2, 0.3), 'o'),
        FragmentToken('b', Interval(0.3, 0.4), 'r'),
        FragmentToken('b', Interval(0.4, 0.5), 'd'),
        FragmentToken('b', Interval(0.5, 0.6), 's')])]

    ca = Corpus(segment_annotations)

    def test_len(self):
        assert(len(self.ca) == 2)  #only 2 distinct fname keys

    def test_getitem(self):
        for i in range(len(self.ca)):
            assert(self.ca['b'] == self.ca.segment_annotations['b'])

    def test_ca_intervals(self):
        exp_intervals = {'a': [Interval(0.0, 0.5), Interval(0.7, 1.3)],
                         'b': [Interval(0.1, 0.6)]}
        pred_intervals = {}
        for fname in self.ca.keys():
            intervals = [fa.interval for fa in self.ca.segment_annotations[fname]]
            pred_intervals[fname] = intervals
        assert(exp_intervals == pred_intervals)

    def test_annotation_simple(self):
        assert(self.ca.annotation('b', Interval(0.2, 0.5)) == ('o', 'r', 'd'))

    def test_annotation_complex(self):
        assert(self.ca.annotation('a', Interval(0.7, 1.2)) == ('w', 'o', 'r', 'm', 's'))

    def test_badtoken_fname(self):
        with pytest.raises(KeyError):
            self.ca.tokens('badfilename', 1)

    def test_badtoken_interval(self):
        with pytest.raises(ValueError):
            self.ca.tokens('a', Interval(-10, -5))
        with pytest.raises(ValueError):
            self.ca.tokens('a', Interval(10, 20))

    def test_restrict(self):
        s1 = IntervalDB({'a': [(0.0, 0.5)]})
        s2 = IntervalDB({'a': [(0.0, 1.3)]})
        s3 = IntervalDB({'a': [(0.0, 1.0)]})
        assert(self.ca.restrict(s1) == Corpus(self.segment_annotations[:1]))
        assert(self.ca.restrict(s2) == Corpus(self.segment_annotations[:2]))
        assert(self.ca.restrict(s3) ==
               Corpus([self.segment_annotations[0],
                       SegmentAnnotation('a',
                                         self.segment_annotations[1][:3])]))
