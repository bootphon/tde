"""
Objects for handling temporal intervals.

Classes
-------
Interval
    Defines temporal interval.
IntervalDB
    Collection of intervals.

Functions
---------
interval_cmp
    Comparison function for Interval objects.

"""

import bisect
from pprint import pformat

import numpy as np


class Interval(object):
    """
    Time interval.

    This class represents a temporal interval. It contains methods for
    determining whether two intervals overlap and for calculating that overlap.

    The default values for the keyword arguments assume that time is measured
    in seconds and set the minimum overlap to 30 milliseconds and the minimum
    overlap fraction to 0.5.

    Parameters
    ----------
    start : float
        Start of the interval.
    end : float
        End  of the interval.
    minimum_overlap : float, optional
        Minimum time for two intervals to be considered to overlap.
    minimum_overlap_fraction : float, optional
        Minimum fraction of either interval to be considered an overlap.


    Methods
    -------
    length()
        The length of the interval.
    overlap(interval)
        Calculate overlap with another interval.
    overlaps_with(interval)
        Determine whether there is an overlap.
    contains(interval)
        Determine whether another interval is contained in this one.
    is_adjacent(interval)
        Determine whether another interval is adjacent to this one.
    is_left_adjacent_to(interval)
        Determine whether this interval is immediately to the left of another.
    is_right_adjacent_to(interval)
        Determine whether this interval is immediately to the right of another.

    Raises
    ------
    ValueError
        If start > end or start < 0 or end < 0

    """
    def __init__(self, start, end,
                 minimum_overlap=0.03, minimum_overlap_fraction=0.5):
        if end < start:
            raise ValueError('end must be greater than start')
        if start < 0 or end < 0:
            raise ValueError('start and end must be non-negative')
        self.start = start
        self.end = end
        self.minimum_overlap = minimum_overlap
        self.minimum_overlap_fraction = minimum_overlap_fraction
        self._length = self.end - self.start

    def __repr__(self):
        return '[{0},{1}]'.format(self.start, self.end)

    def __str__(self):
        return '[{0},{1}]'.format(self.start, self.end)

    def __eq__(self, other):
        if isinstance(other, Interval):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def __hash__(self):
        return (hash(self.start) << 1) ^ hash(self.end)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        yield self.start
        yield self.end

    def length(self):
        """
        Calculate the length of the interval.

        Returns
        -------
        float

        """
        return self._length

    def overlap(self, other):
        """
        Calculate overlap with another interval.

        Parameters
        ----------
        other : Interval

        Returns
        -------
        float

        """
        if self.end < other.start:
            return 0.
        if self.start > other.end:
            return 0.
        return min(self.end, other.end) - max(self.start, other.start)

    def overlaps_with(self, other):
        """
        Determine whether there is an overlap.

        Overlap is calculated in accordance with the minimum
        and maximum overlap parameters. An overlap is confirmed if the
        overlapping time is at least `minimum_overlap` or at least
        `minimum_overlap_fraction` of either interval.


        Parameters
        ----------
        other : Interval

        Returns
        -------
        bool

        Examples
        --------
        >>> i1 = Interval(0, 2)
        >>> i2 = Interval(1, 3)
        >>> i1.overlaps_with(i2)
        True
        >>> i1 = Interval(0.0, 1.0, minimum_overlap=0.5, minimum_overlap_fraction=0.5)
        >>> i2 = Interval(0.9, 3.0, minimum_overlap=0.5, minimum_overlap_fraction=0.5)
        >>> i1.overlaps_with(i2)
        False

        """
        if self.minimum_overlap != other.minimum_overlap:
            raise ValueError('Attempting to calculate overlap on incomparable '
                             'intervals. Make sure that `minimum_overlap` on '
                             'both intervals is the same.')
        if self.minimum_overlap_fraction != other.minimum_overlap_fraction:
            raise ValueError('Attempting to calculate overlap on incomparable '
                             'intervals. Make sure that `minimum_overlap_fraction`'
                             ' on both intervals is the same.')

        over = self.overlap(other)
        if over < 0.00000001: #np.isclose(over, 0.0):
            return False
        if over > self.minimum_overlap:
            return True
        if over > self.minimum_overlap_fraction * other.length():
            return True
        if over > self.minimum_overlap_fraction * self.length():
            return True
        return False

    def contains(self, other):
        """
        Determine whether another interval is contained in this one.

        Parameters
        ----------
        other : Interval

        Returns
        -------
        bool

        """
        return self.start <= other.start and self.end >= other.end

    def is_adjacent(self, other):
        """
        Determine whether another interval is adjacent to this one.

        Parameters
        ----------
        other : Interval

        Returns
        -------
        bool

        """
        return self.is_left_adjacent_to(other) or \
            self.is_right_adjacent_to(other)


    def is_left_adjacent_to(self, other):
        """
        Determine whether this interval is immediately to the left of another.

        Parameters
        ----------
        other : Interval

        Returns
        -------
        bool

        """
        return  abs(self.end - other.start) < 1e-05  #  np.isclose(self.end, other.start)

    def is_right_adjacent_to(self, other):
        """
        Determine whether this interval is immediately to the right of another.

        Parameters
        ----------
        other : Interval

        Returns
        -------
        bool

        """
        return abs(other.end - self.start) < 1e-05  # np.isclose(other.end, self.start)



def interval_cmp(i1, i2):
    """Interval comparison function.

    Compares two intervals as temporal objects on a timeline Interval i1 == i2
    iff i1.start == i2.start and i1.end == i2.end. If i1 overlaps with i2, the
    interval with the earliest start is considered the lesser. If i1 does not
    overlap with i2, the interval with the earliest end is the lesser.

    The function returns -1 if i1 < i2, 0 if i1 == i2 and 1 if i1 > i2.

    Parameters
    ----------
    i1, i2 : Interval

    Returns
    -------
    int
        Comparison result.

    Examples
    --------
    >>> i1 = Interval(0, 1)
    >>> i2 = Interval(2, 3)
    >>> interval_cmp(i1, i2)
    -1
    >>> i2 = Interval(0.5, 1)
    >>> interval_cmp(i1, i2)
    0
    >>> i2 = Interval(0.99, 3)
    >>> interval_cmp(i1, i2)
    -1
    >>> i1 = Interval(4, 5)
    >>> interval_cmp(i1, i2)
    1

    """
    if i1.overlaps_with(i2):
        return 0
    overlap = i1.overlap(i2)
    if overlap > 0.:
        if i1.start < i2.start:
            return -1
        else:
            return 1
    else:
        if i1.end <= i2.start:  # i1 to the left of i2
            return -1
        else:  # i1 to the right of i2
            return 1


class IntervalDB(object):
    """Holds collection of fragments and makes them easily searchable.

    Parameters
    ----------
    mapping : dict from string to sorted list of Intervals

    Attributes
    ----------
    starts, ends : list of floats

    Methods
    -------
    find(filename, interval)
        Find all the intervals that overlap with the query interval.
    is_covered(filename, interval)
        Determine if an interval is covered.
    largest_overlap(filename, interval)
        Find the interval with the largest overlap.

    """
    def __init__(self, mapping):
        starts = {}
        ends = {}
        for fname in mapping:
            starts[fname], ends[fname] = zip(*mapping[fname])
        self.starts = starts
        self.ends = ends

    def __eq__(self, other):
        if isinstance(other, IntervalDB):
            return self.starts == other.starts and self.ends == other.ends
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<IntervalDB {0} entries>'.format(
            sum(map(len, self.starts.itervalues())))

    def __str__(self):
        return 'IntervalDB\n- starts: {0}\n- ends: {1}'.format(
            pformat(self.starts), pformat(self.ends))

    def __len__(self):
        return sum(map(len, self.starts.itervalues()))

    def find(self, fname, interval):
        """
        Find all the intervals that overlap with the query interval.

        Parameters
        ----------
        fname : string
        interval : Interval

        Returns
        -------
        r : iterator over Intervals
            intervals with overlap

        Raises
        ------
        KeyError
            if fname is not a known key
        """
        starts = self.starts[fname]
        ends = self.ends[fname]
        qstart, qend = interval.start, interval.end
        left = max(bisect.bisect_left(starts, qstart) - 1, 0)
        right = bisect.bisect_right(starts, qend)
        return (Interval(start, end)
                for start, end in zip(starts[left:right],
                                      ends[left:right])
                if Interval(start, end).overlap(interval) > 0)

    def is_covered(self, fname, interval):
        """
        Determine if an interval is covered.

        Parameters
        ----------
        fname : string
        interval : Interval

        Returns
        -------
        bool

        """
        try:
            b = any(interval.start >= start and interval.end <= end
                    for start, end in self.find(fname, interval))
        except KeyError:
            b = False
        return b

    def largest_overlap(self, fname, interval):
        """Return the interval that has the largest overlap with the query
        interval.

        Parameters
        ----------
        fname : string
        interval : Interval

        Returns
        -------
        start, end : float
            start and end points of interval with the largest overlap

        Raises
        ------
        KeyError
            if fname is not a known key
        ValueError
            if no interval is found
        """
        return max(self.find(fname, interval),
                   key=lambda x: interval.overlap(x))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
