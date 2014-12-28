"""
Object for handling full annotation of corpus.

Classes
-------
Corpus
    Container for full segmental annotation of a corpus.

"""

from functools import cmp_to_key
from pprint import pformat
import collections

from tde.data.sorted_list import SortedList
from tde.data.segment_annotation import annotation_cmp
from tde.data.fragment import FragmentToken
from tde.util.functions import flatten


class Corpus(collections.Mapping):
    """
    Corpus annotation.

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
                self.segment_annotations[fa.name] = \
                    SortedList([fa], key=cmp_to_key(annotation_cmp))
        self._cache = {}

    def __eq__(self, other):
        if not isinstance(other, Corpus):
            return False
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
        return iter(self.segment_annotations)

    def __repr__(self):
        return '<Corpus - {0} segments, {1} names>'.format(
            sum(map(len, self.values())), len(self))

    def __str__(self):
        return pformat(self.segment_annotations)

    def clear(self):
        self._cache = {}

    def iter_fragments(self):
        return flatten(self.iter_segments())

    def iter_segments(self):
        return flatten(self.itervalues())

    def restrict(self, interval_db):
        """
        Return a new Corpus, containing only the annotations for the
        specified names.

        Parameters
        ----------
        names : list of strings
            List of identifiers to restrict the Corpus to. Supplied identifiers
            must be valid (i.e. must be in self.keys()).

        Returns
        -------
        Corpus
            New Corpus object.
        """
        sa = []
        for k in self:
            for s in self[k]:
                r = s.restrict(interval_db)
                if len(r.tokens) > 0:
                    sa.append(r)
        return Corpus(sa)

    def annotation(self, name, interval):
        """
        Find the annotation covering an interval.

        Parameters
        ----------
        name : string
            Identifier.
        interval : Interval
            Time segment.

        Returns
        -------
        list of strings
            Symbols covered by the interval.
        """
        return tuple(x.mark for x in self.tokens(name, interval))

    def annotation_exact(self, name, interval):
        return tuple(x.mark for x in self.tokens_exact(name, interval))

    def tokens_exact(self, name, interval):
        tokens = self.tokens(name, interval)
        if tokens[0].interval.start != interval.start and \
           tokens[-1].interval.end != interval.end:
            raise ValueError('exact tokens not found')
        return tokens

    def tokens(self, name, interval):
        """
        Find the FragmentTokens covering an interval.

        Parameters
        ----------
        name : string
            Identifier.
        interval : Interval
            Time segment.

        Returns
        -------
        list of tokens
            FragmentTokens covered by the interval.
        """
        key = (name, interval)
        if not key in self._cache:
            try:
                fa_for_filename = self[name]
            except KeyError:
                raise KeyError('no such name: {0}'.format(name))
            dummy_token = FragmentToken(name, interval, None)
            try:
                fa = fa_for_filename.find_le(dummy_token)
            except ValueError:
                raise ValueError('interval not found: {0}'.format(str(interval)))
            if (fa.interval.overlap(interval)) > 0:
                self._cache[key] = fa.tokens_at_interval(interval)
            else:
                raise ValueError('interval not found: {0}'.format(str(interval)))
        return self._cache[key]
