"""Defines datatypes used for holding and querying annotations.

"""

import collections
from functools import cmp_to_key
from itertools import chain, combinations
from pprint import pformat

import numpy as np

from .sortedlist import SortedList
from .util import unique

_flatten = chain.from_iterable
class ClassDict(collections.Mapping):
    def __init__(self, clsdict):
        self.clsdict = clsdict

    def __contains__(self, key):
        return key in self.clsdict

    def __getitem__(self, key):
        return self.clsdict[key]

    def __iter__(self):
        return iter(self.clsdict)

    def __len__(self):
        return len(self.clsdict)

    def __str__(self):
        return str(self.clsdict)

    def pretty(self):
        return pformat(self.clsdict)

    def iter_fragments(self):
        return unique(_flatten(self.clsdict.itervalues()))

    def iter_pairs(self, within, order):
        vals = self.clsdict.itervalues()
        if within:
            if order:
                pairs = _flatten(((f1, f2), (f2, f1))
                                 for fragments in vals
                                 for f1, f2 in combinations(fragments, 2))
            else:
                pairs = ((f1, f2)
                         for fragments in vals
                         for f1, f2 in combinations(fragments, 2))
        else: # across classes
            if order:
                pairs = (((f1, f2), (f2, f1))
                         for f1, f2 in combinations(_flatten(vals), 2))
                pairs = _flatten(pairs)
            else:
                pairs = ((f1, f2)
                         for f1, f2 in combinations(_flatten(vals), 2))
        return unique(pairs)

    def restrict(self, names, remove_singletons=False):
        """Return a new ClassDict object restricted to only the identifiers in
        names.

        Parameters
        ----------
        names : list of strings
          Identifiers to restrict the mapping to.
        remove_singletons : bool
          Remove classes with a single element

        Returns
        -------
        d : ClassDict object
          Restricted class map
        """
        names = set(names)
        r = {}
        for classID, fragments in self.clsdict.iteritems():
            fs = [f for f in fragments if f.name in names]
            if len(fs) > 1:
                r[classID] = fs
        return ClassDict(r)


class Corpus(object):
    """Corpus annotation.

    Holds full segmental annotation of a corpus with fast search on annotation
    for intervals.

    Parameters
    ----------
    segment_annotations : list of SegmentAnnotations

    """
    def __init__(self, segment_annotations=None):
        self.segment_annotations = {}
        if segment_annotations is None:
            segment_annotations = []
        for fa in segment_annotations:
            try:
                self.segment_annotations[fa.name].insert(fa)
            except KeyError:
                sc = SortedList([fa], key=cmp_to_key(annotation_cmp))
                self.segment_annotations[fa.name] = sc

        self._cache = {}

    def keys(self):
        """Return the names in the index.

        Returns
        -------
        k : list of strings

        """
        return self.segment_annotations.keys()

    def __eq__(self, other):
        if sorted(self.keys()) != sorted(other.keys()):
            return False
        for k in sorted(self.keys()):
            s = self.segment_annotations[k]
            o = other.segment_annotations[k]
            if len(s) != len(o):
                return False
            for i in xrange(len(s)):
                if s[i] != o[i]:
                    return False
        return True

    def __len__(self):
        return len(self.segment_annotations)

    def __getitem__(self, key):
        return self.segment_annotations[key]

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, key):
        return key in self.keys()

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)

    def __str__(self):
        return '<Corpus {0} {1} {2} segments>'.format(
            self.name, str(self.interval), len(self.segment_annotations))

    def annotation(self, name, interval):
        """Find the annotation covering an interval.

        Parameters
        ----------
        name : string
            Identifier.
        interval : Interval
            Time segment.

        Returns
        -------
        a : list of strings
            Symbols covered by the interval.
        """
        return [x.mark for x in self.tokens(name, interval)]

    def tokens(self, name, interval):
        """Find the FragmentTokens covering an interval.

        Parameters
        ----------
        name : string
            Identifier.
        interval : Interval
            Time segment.

        Returns
        -------
        t : list of tokens
            FragmentTokens covered by the interval.
        """
        key = (name, interval)
        if not key in self._cache:
            try:
                fa_for_filename = self.segment_annotations[name]
            except KeyError:
                raise KeyError('no such name: {0}'.format(name))
            dummy_token = FragmentToken(None, interval, None)
            try:
                fa = fa_for_filename.find_le(dummy_token)
            except ValueError:
                raise ValueError('interval not found: {0}'.format(str(interval)))
            if (fa.interval.overlap(interval)) > 0:
                self._cache[key] = fa.tokens_at_interval(interval)
            else:
                raise ValueError('interval not found: {0}'.format(str(interval)))
        return self._cache[key]


class SegmentAnnotation(object):
    """Annotation for contiguous time segment.

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

    """
    def __init__(self, name, tokens):
        self.name = name
        self.tokens = SortedList(tokens, key=cmp_to_key(token_cmp))
        self.interval = Interval(self.tokens[0].interval.start,
                                 self.tokens[-1].interval.end)

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
        for i in xrange(len(self.tokens)):
            if self.tokens[i] != other.tokens[i]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def annotation_at_interval(self, interval):
        """Get the annotation corresponding to an interval.

        Parameters
        ----------
        interval : Interval

        Returns
        -------
        s : list of strings
            Annotation symbols covered by the interval.
        """
        return [x.mark for x in self.tokens_at_interval(interval)]

    def tokens_at_interval(self, interval):
        """Get the annotation tokens corresponding to an interval.

        Parameters
        ----------
        interval : Interval

        Returns
        -------
        t : list of FragmentTokens
            FragmentTokens covered by the interval.
        """
        dummy_token = FragmentToken(None, interval, None)
        try:
            start = self.tokens.index_ge(dummy_token)
        except ValueError:
            return []
        try:
            stop = self.tokens.index_gt(dummy_token)
        except ValueError:
            stop = len(self.tokens)
        return tuple([x for x in self.tokens[start:stop]])


def annotation_cmp(a1, a2):
    """Comparison function for SegmentAnnotation objects.

    Compares annotations on their interval attributes.

    Parameters
    ----------
    a1, a2 : SegmentAnnotation

    Returns
    -------
    c : int
        Comparison result.

    """
    return interval_cmp(a1.interval, a2.interval)


class FragmentType(namedtuple('FragmentType', ['tokens', 'mark'])):
    """Collection of FragmentTokens.

    Parameters
    ----------
    tokens : list of FragmentToken

    mark : string, optional
        Symbol corresponding to all the tokens
    """
    def __new__(cls, tokens, mark=None):
        return super(FragmentType, cls).__new__(cls, tokens, mark)


class FragmentToken(namedtuple('FragmentToken', ['name', 'interval', 'mark'])):
    """Annotation on a single interval.

    Parameters
    ----------
    name : string
        Identifier.
    interval : Interval
        Temporal interval covered by the annotation.
    mark : string, optional
        Annotated symbol.
    """
    def __new__(cls, name, interval, mark=None):
        return super(FragmentToken, cls).__new__(cls, name, interval, mark)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                 self.name, self.interval, self.mark)

    def __hash__(self):
        return hash(hash(self.name) ^
                    hash(self.interval) ^
                    hash(self.mark))


class ClassID(namedtuple('ClassID', ['ID', 'mark'])):
    """Struct for ClassID and an optional symbol.

    Parameters
    ----------
    ID : int
        Integer identifier.
    mark : string, optional
        Symbol.
    """

    def __new__(cls, ID, mark=None):
        return super(ClassID, cls).__new__(cls, ID, mark)

    def __repr__(self):
        return '{0}({1}{2})'.format(
            self.__class__.__name__,
            self.ID,
            '({0})'.format(self.mark) if self.mark else '')


def token_cmp(t1, t2):
    """Comparison function for FragmentToken objects.

    Compares tokens on their interval.

    Parameters
    ----------
    t1, t2 : FragmentToken

    Returns
    -------
    c : int
        Comparison result.
    """
    return interval_cmp(t1.interval, t2.interval)


class Interval(object):
    """Time interval.

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

    """
    def __init__(self, start, end,
                 minimum_overlap=0.03, minimum_overlap_fraction=0.5):
        if end < start:
            raise ValueError('end must be greater than start')
        self.start = start
        self.end = end
        self.minimum_overlap = minimum_overlap
        self.minimum_overlap_fraction = minimum_overlap_fraction

    def __repr__(self):
        return '[{0}-{1}]'.format(self.start, self.end)

    def __str__(self):
        return '[{0}-{1}]'.format(self.start, self.end)

    def __eq__(self, other):
        return all(getattr(self, k) == getattr(other, k)
                   for k in self.__dict__)

    def __hash__(self):
        return hash(hash(self.start) ^ hash(self.end))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return self.end - self.start

    def overlap(self, other):
        """Calculate approximate overlap between `self` and `other`.

        Parameters
        ----------
        other : Interval
            Interval to compute overlap with.

        Returns
        -------
        o : double
            Returns the approximate overlap with `other` interval.
        """
        if self.end < other.start:
            return 0.
        if self.start > other.end:
            return 0.
        return min(self.end, other.end) - max(self.start, other.start)

    def overlaps_with(self, other):
        """Determine whether `self` overlaps with `other`.

        Returns True iff `self` overlaps at least half of `other` or at least
        30 milliseconds.

        Parameters
        ----------
        other : Interval
            Interval to determine overlap with.

        Returns
        -------
        b : boolean
            True iff `self` overlaps with `other`

        """
        over = self.overlap(other)
        if np.isclose(over, 0.0):
            return False
        time_overlaps = over > self.minimum_overlap
        frac_overlaps = over > self.minimum_overlap_fraction * len(other)
        return time_overlaps or frac_overlaps


def abuts_left(i1, i2, tol=1e-3):
    """Determine whether i1 is directly to the left of i2.

    Parameters
    ----------
    i1, i2 : Interval

    Returns
    -------
    b : boolean
        True iff i1 is directly to the left of i2.
    """
    return np.isclose(i1.end, i2.start, atol=tol)


def interval_cmp(i1, i2):
    """Interval comparison function.

    Compares two intervals as temporal objects on a timeline Interval i1 == i2
    iff i1.start == i2.start and i1.end == i2.end. If i1 overlaps with i2, the
    interval with the earliest start is considered the lesser. If i1 does not
    overlap with i2, the interval with the earliest end is the lesser.

    Parameters
    ----------
    i1, i2 : Interval
        Intervals to compare.

    Returns
    -------
    b : int
        Returns 0 iff i1 == i2, 1 iff i1 > i2, -1 iff i1 > i2.

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
