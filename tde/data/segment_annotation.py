"""
Object for holding the annotation of a contiguous time segment.

Classes
-------
SegmentAnnotation
    Annotation for contiguous time segment.

Functions
---------
annotation_cmp
    Comparison function for SegmentAnnotation objects.

"""

import collections
from functools import cmp_to_key

from tde.data.sorted_list import SortedList
from tde.data.interval import Interval, interval_cmp
from tde.data.fragment import token_cmp, FragmentToken

class SegmentAnnotation(collections.Sequence):
    """
    Annotation for contiguous time segment.

    This class represents a contiguous sequence of annotations. It contains
    methods for efficiently finding the annotation corresponding to a temporal
    interval.

    Parameters
    ----------
    name : string
        Identifier for the annotation.
    tokens : list of FragmentToken objects
        The sequence of annotations.

    Attributes
    ----------
    interval : Interval
        The temporal interval that is covered.

    Raises
    ------
    ValueError
        If tokens are not contiguous or don't all have the same name.

    """
    def __init__(self, name, tokens):
        self.name = name
        self.tokens = SortedList(tokens, key=cmp_to_key(token_cmp))
        if len(self.tokens) == 0:
            self.interval = None
        else:
            self.interval = Interval(self.tokens[0].interval.start,
                                     self.tokens[-1].interval.end)
        if not all(t1.interval.end == t2.interval.start
                   for t1, t2 in zip(self.tokens[:-1], self.tokens[1:])):
            raise ValueError('Non-contiguous tokens.')

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        return iter(self.tokens)

    def __getitem__(self, i):
        return self.tokens[i]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)

    def __str__(self):
        return '<SegmentAnnotation {0} {1} {2} tokens>'.format(
            self.name, str(self.interval), len(self.tokens))

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.interval != other.interval:
            return False
        if len(self.tokens) != len(other.tokens):
            return False
        return all(t1 == t2 for t1, t2 in zip(self.tokens, other.tokens))

    def __ne__(self, other):
        return not self.__eq__(other)

    def restrict(self, interval_db):
        """
        Restrict the SegmentAnnotation to a set of Intervals.

        Returns a new SegmentAnnotation object with only the FragmentTokens
        that are fully covered in `interval_db`.

        Parameters
        ----------
        interval_db : IntervalDB

        Returns
        -------
        SegmentAnnotation
            New SegmentAnnotation object.

        """
        return SegmentAnnotation(self.name,
                                 [f for f in self.tokens
                                  if interval_db.is_covered(f.name, f.interval)])

    def annotation_at_interval(self, interval):
        """
        Get the annotation corresponding to an interval.

        Parameters
        ----------
        interval : Interval

        Returns
        -------
        s : list of strings
            Annotation symbols covered by the interval.
        """
        return tuple([x.mark for x in self.tokens_at_interval(interval)])

    def tokens_at_interval(self, interval):
        """
        Get the annotation tokens corresponding to an interval.

        Parameters
        ----------
        interval : Interval

        Returns
        -------
        tuple of FragmentTokens
            FragmentTokens covered by the interval.
        """
        if len(self.tokens) > 0:
            name = self.tokens[0].name
        else:
            return tuple()
        dummy_token = FragmentToken(name, interval, None)
        try:
            start = self.tokens.index_ge(dummy_token)
        except ValueError:
            return tuple()
        try:
            stop = self.tokens.index_gt(dummy_token)
        except ValueError:
            stop = len(self.tokens)
        return tuple([x for x in self.tokens[start:stop]])


def annotation_cmp(segment_annotation1, segment_annotation2):
    """
    Comparison function for SegmentAnnotation objects.

    Compares annotations on their interval attributes.

    Parameters
    ----------
    segment_annotation1, segment_annotation2 : SegmentAnnotation

    Returns
    -------
    int
        Comparison result.

    Raises
    ------
    ValueError
        If the names of the SegmentAnnotations don't match.

    """
    if segment_annotation1.name != segment_annotation2.name:
        raise ValueError('SegmentAnnotations with different names cannot be '
                         'compared')
    return interval_cmp(segment_annotation1.interval,
                        segment_annotation2.interval)
