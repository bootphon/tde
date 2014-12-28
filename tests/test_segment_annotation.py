import pytest

from tde.data.interval import Interval, IntervalDB
from tde.data.fragment import FragmentToken
from tde.data.segment_annotation import SegmentAnnotation, annotation_cmp

class TestSegmentAnnotation(object):
    tokenlist = (FragmentToken('a', Interval(0.0,0.1), 'a'),
                 FragmentToken('a', Interval(0.1,0.2), 'r'),
                 FragmentToken('a', Interval(0.2,0.3), 'm'),
                 FragmentToken('a', Interval(0.3,0.4), 's'),
                 FragmentToken('a', Interval(0.4,0.5), 'a'))
    sa = SegmentAnnotation('name1', tokenlist)

    def test_restrict(self):
        db1 = IntervalDB({'a': [Interval(0, 0.5)]})
        db2 = IntervalDB({'a': [Interval(0, 0.3)]})
        assert (self.sa.restrict(db1) == self.sa)
        assert (self.sa.restrict(db2) ==
                SegmentAnnotation('name1', self.tokenlist[:3]))

    def test_len(self):
        assert (len(self.sa) == 5)

    def test_iter(self):
        assert (list(iter(self.sa)) == list(self.tokenlist))

    def test_get_item(self):
        for i in xrange(len(self.tokenlist)):
            assert (self.sa[i] == self.tokenlist[i])

    def test_eq(self):
        assert (self.sa == self.sa)

    def test_eq_wrong_name(self):
        sa1 = SegmentAnnotation('name1', [])
        sa2 = SegmentAnnotation('name2', [])
        assert (sa1 != sa2)

    def test_eq_wrong_interval(self):
        sa1 = SegmentAnnotation('name1',
                                [FragmentToken('', Interval(0, 1), None)])
        sa2 = SegmentAnnotation('name1',
                                [FragmentToken('', Interval(0, 3), None)])
        assert (sa1 != sa2)

    def test_eq_wrong_ntokens(self):
        sa1 = SegmentAnnotation('name1',
                                [FragmentToken('', Interval(0, 2), None)])
        sa2 = SegmentAnnotation('name1',
                                [FragmentToken('', Interval(0, 1), None),
                                 FragmentToken('', Interval(1, 2), None)])
        assert (sa1 != sa2)

    def test_tokens_at_interval(self):
        assert(self.sa.tokens_at_interval(Interval(0.0, 0.5))
               == tuple(self.tokenlist))
        assert(self.sa.tokens_at_interval(Interval(0.1, 0.4))
               == tuple(self.tokenlist[1:4]))
        assert(self.sa.tokens_at_interval(Interval(0.0, 0.05))
               == (self.tokenlist[0],))
        assert(self.sa.tokens_at_interval(Interval(10, 11))
               == tuple())
        assert (SegmentAnnotation('', []).tokens_at_interval(Interval(0,1))
                == tuple())

    def test_annotation_at_interval(self):
        assert(self.sa.annotation_at_interval(Interval(0.0, 0.5))
               == tuple(['a', 'r', 'm', 's', 'a']))
        assert(self.sa.annotation_at_interval(Interval(0.1, 0.4))
               == tuple(['r', 'm', 's']))
        assert(self.sa.annotation_at_interval(Interval(0.0, 0.05))
               == tuple(['a']))
        assert(self.sa.annotation_at_interval(Interval(10, 11))
               == tuple())

    def test_empty(self):
        e = SegmentAnnotation('', [])
        assert (e.name == '')
        assert (e.interval is None)

    def test_non_contiguous(self):
        with pytest.raises(ValueError):
            SegmentAnnotation('',
                              [FragmentToken('a', Interval(0, 1), None),
                               FragmentToken('a', Interval(2, 3), None)])

    def test_different_names(self):
        with pytest.raises(ValueError):
            SegmentAnnotation('',
                              [FragmentToken('a', Interval(0, 1), None),
                               FragmentToken('b', Interval(1, 2), None)])


class TestSegmentAnnotationCmp(object):
    sa1 = SegmentAnnotation('n1', [FragmentToken('n1', Interval(0, 0.5), None)])
    sa2 = SegmentAnnotation('n1', [FragmentToken('n1', Interval(0.5, 1.5), None)])
    sa3 = SegmentAnnotation('n1', [FragmentToken('n1', Interval(1.3, 1.4), None)])
    sa4 = SegmentAnnotation('n2', [FragmentToken('n2', Interval(0, 1), None)])

    def test_invalid_comparison(self):
        with pytest.raises(ValueError):
            annotation_cmp(self.sa1, self.sa4)

    def test_annotation_eq(self):
        assert (annotation_cmp(self.sa1, self.sa1) == 0)
        assert (annotation_cmp(self.sa2, self.sa2) == 0)
        assert (annotation_cmp(self.sa3, self.sa3) == 0)

    def test_annotation_cmp(self):
        assert (annotation_cmp(self.sa1, self.sa2) == -1)
        assert (annotation_cmp(self.sa1, self.sa3) == -1)
        assert (annotation_cmp(self.sa2, self.sa1) == 1)
        assert (annotation_cmp(self.sa3, self.sa1) == 1)

        assert (annotation_cmp(self.sa2, self.sa3) == 0)
        assert (annotation_cmp(self.sa3, self.sa2) == 0)


if __name__ == '__main__':
    pytest.main('-s')
