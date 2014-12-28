import pytest

import numpy as np
from tde.data.interval import Interval, interval_cmp, IntervalDB

class TestInterval(object):
    # This looks stupid, but it's good to test the wonky (in-)equalities that
    # hold for Intervals
    i1 = Interval(0., 0.5)
    i2 = Interval(0.5, 1.5)
    i3 = Interval(1.3, 1.4)

    def test_len(self):
        # regression test. len() casts the call to object.__len__() to int.
        # this is the wrong behavior for Interval
        # as a solution, len(Interval) and Interval().__len__() should now
        # raise and AttributeError
        with pytest.raises(TypeError):
            len(self.i1)
        with pytest.raises(AttributeError):
            self.i1.__len__()

    def test_adjacent(self):
        assert (self.i1.is_adjacent(self.i2))
        assert (self.i2.is_adjacent(self.i1))

        assert (not self.i1.is_adjacent(self.i3))
        assert (not self.i3.is_adjacent(self.i1))

        assert (not self.i3.is_adjacent(self.i2))
        assert (not self.i2.is_adjacent(self.i3))

    def test_adjacent_left(self):
        assert (self.i1.is_left_adjacent_to(self.i2))
        assert (not self.i2.is_left_adjacent_to(self.i1))
        assert (not self.i3.is_left_adjacent_to(self.i1))
        assert (not self.i1.is_left_adjacent_to(self.i3))

    def test_adjacent_right(self):
        assert (self.i2.is_right_adjacent_to(self.i1))
        assert (not self.i2.is_right_adjacent_to(self.i3))
        assert (not self.i3.is_right_adjacent_to(self.i2))

    def test_strrepr(self):
        assert(str(self.i1) == '[0.0,0.5]')
        assert(repr(self.i1) == '[0.0,0.5]')

    def test_overlap(self):
        assert(self.i1.overlap(self.i2) == 0.0)
        assert(self.i1.overlap(self.i3) == 0.0)
        assert(np.isclose(self.i2.overlap(self.i3), 0.1))

    def test_overlaps_with(self):
        assert(not self.i1.overlaps_with(self.i2))
        assert(not self.i1.overlaps_with(self.i3))
        assert(self.i2.overlaps_with(self.i3))

    def test_interval_cmp(self):
        assert(interval_cmp(self.i1, self.i2) == -1)
        assert(interval_cmp(self.i1, self.i3) == -1)
        assert(interval_cmp(self.i2, self.i1) == 1)
        assert(interval_cmp(self.i3, self.i1) == 1)
        assert(interval_cmp(self.i1, self.i1) == 0)
        assert(interval_cmp(self.i2, self.i2) == 0)
        assert(interval_cmp(self.i3, self.i3) == 0)
        assert(interval_cmp(self.i1, self.i2) != 0)
        assert(interval_cmp(self.i2, self.i3) == 0)
        assert(interval_cmp(self.i3, self.i1) != 0)

    def test_not_enough_overlap(self):
        i1 = Interval(0, 1)
        i2 = Interval(0.98, 2)
        assert (not i1.overlaps_with(i2))
        assert (not i2.overlaps_with(i1))
        assert (interval_cmp(i1, i2) == -1)
        assert (interval_cmp(i2, i1) == 1)

    def test_badinterval(self):
        with pytest.raises(ValueError):
            Interval(1, 0)
        with pytest.raises(ValueError):
            Interval(-1, -0.5)
        with pytest.raises(ValueError):
            Interval(-2, -3)

    def test_eq(self):
        assert (Interval(0, 1) != (0, 1))
        assert (Interval(0, 1) == Interval(0, 1))
        assert (Interval(0, 1, 3, 4) == Interval(0, 1, 5, 6))

    def test_neq(self):
        assert (Interval(0, 1) != Interval(2, 3))
        assert (Interval(0, 1, 2, 3) != Interval(5, 6, 2, 3))

    def test_hash(self):
        assert (hash(Interval(0, 1)) == hash(Interval(0, 1)))
        assert (hash(Interval(0, 1)) != hash(Interval(2, 3)))
        assert (hash(Interval(0, 1, 2, 3)) == hash(Interval(0, 1, 5, 6)))

    def test_iter(self):
        assert (tuple(iter(Interval(0, 1))) == (0, 1))

    def test_contains(self):
        assert (Interval(0, 1).contains(Interval(0.1, 0.9)))
        assert (not Interval(0.1, 0.9).contains(Interval(0, 1)))
        assert (not Interval(0, 1).contains(Interval(0, 2)))
        assert (not Interval(0, 1).contains(Interval(4, 5)))

class TestIntervalDB(object):
    d = {'a': [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)]}
    m = IntervalDB(d)
    q1 = Interval(0.0, 1.0)
    q2 = Interval(0.5, 1.0)
    q3 = Interval(0.5, 1.5)
    q4 = Interval(0.0, 3.0)
    q5 = Interval(1.1, 1.9)
    q6 = Interval(1.0, 2.0)
    q7 = Interval(2.1, 2.9)
    q8 = Interval(1.5, 8.0)
    q9 = Interval(1.5, 5.0)
    q10 = Interval(5.0, 6.0)

    def test_strrepr(self):
        assert (repr(self.m) == '<IntervalDB 3 entries>')
        assert (str(self.m) == "IntervalDB\n- starts: {'a': (0.0, 2.0, 4.0)}\n"
                "- ends: {'a': (1.0, 3.0, 5.0)}")

    def test_eq(self):
        m = IntervalDB({'a': [(0, 1)]})
        assert (m != 1)  # run over isinstance line
        assert (m == m)
        assert (m != self.m)

    def test_largest_overlap(self):
        assert (self.m.largest_overlap('a', self.q1) == Interval(0.0, 1.0))
        assert (self.m.largest_overlap('a', self.q2) == Interval(0.0, 1.0))
        assert (self.m.largest_overlap('a', self.q3) == Interval(0.0, 1.0))
        assert (self.m.largest_overlap('a', self.q4) == Interval(0.0, 1.0))
        with pytest.raises(ValueError):
            self.m.largest_overlap('a', self.q5)
        with pytest.raises(ValueError):
            self.m.largest_overlap('a', self.q6)
        assert (self.m.largest_overlap('a', self.q7) == Interval(2.0, 3.0))
        assert (self.m.largest_overlap('a', self.q8) == Interval(2.0, 3.0))
        assert (self.m.largest_overlap('a', self.q9) == Interval(2.0, 3.0))
        with pytest.raises(ValueError):
            self.m.largest_overlap('a', self.q10)

    def test_find(self):
        assert (list(self.m.find('a', self.q1)) == [Interval(0.0, 1.0)])
        assert (list(self.m.find('a', self.q2)) == [Interval(0.0, 1.0)])
        assert (list(self.m.find('a', self.q3)) == [Interval(0.0, 1.0)])
        assert (list(self.m.find('a', self.q4)) == [Interval(0.0, 1.0),
                                                    Interval(2.0, 3.0)])
        assert (list(self.m.find('a', self.q5)) == [])
        assert (list(self.m.find('a', self.q6)) == [])
        assert (list(self.m.find('a', self.q7)) == [Interval(2.0, 3.0)])
        assert (list(self.m.find('a', self.q8)) == [Interval(2.0, 3.0),
                                                    Interval(4.0, 5.0)])
        assert (list(self.m.find('a', self.q9)) == [Interval(2.0, 3.0),
                                                    Interval(4.0, 5.0)])
        assert (list(self.m.find('a', self.q10)) == [])

    def test_find_bad_fname(self):
        with pytest.raises(KeyError):
            self.m.find('b', None)

    def test_is_covered(self):
        assert (self.m.is_covered('a', self.q1) == True)
        assert (self.m.is_covered('a', self.q2) == True)
        assert (self.m.is_covered('a', self.q3) == False)
        assert (self.m.is_covered('a', self.q4) == False)
        assert (self.m.is_covered('a', self.q5) == False)
        assert (self.m.is_covered('a', self.q6) == False)
        assert (self.m.is_covered('a', self.q7) == True)
        assert (self.m.is_covered('a', self.q8) == False)
        assert (self.m.is_covered('a', self.q9) == False)
        assert (self.m.is_covered('a', self.q10) == False)

        assert (self.m.is_covered('b', None) == False)
