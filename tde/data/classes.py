"""
Objects for handling partitionings of FragmentTokens into classes.

Classes
-------
ClassID
    Class identifier. Used as keys in ClassDict.
ClassDict
    Mapping representing a partitioning.

"""

from pprint import pformat
from itertools import izip, repeat, combinations, ifilterfalse
import collections

from tde.util.functions import unique, flatten

class ClassDict(collections.Mapping):
    """
    Mapping representing the partitioning of a collection of FragmentTokens
    into classes

    Parameters
    ----------
    clsdict : dict from ClassID to tuple of FragmentToken

    Methods
    -------
    iter_fragments(with_class=False)
        Iterate over single FragmentTokens.
    iter_pairs()
        Iterate over pairs of FragmentTokens.
    restrict()
        Restrict to a collection of Intervals

    """
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

    def __eq__(self, other):
        return self.clsdict == other.clsdict

    def __ne__(self, other):
        return not self.__eq__(other)

    def pretty(self):
        return pformat(self.clsdict)

    def iter_fragments(self, with_class=False):
        """
        Iterate over FragmentTokens.

        Parameters
        ----------
        with_class : bool, optional
            Iterate over (ClassID, FragmentToken) pairs instead

        Returns
        -------
        Iterator over FragmentToken or (ClassID, FragmentToken) pairs

        """
        if with_class:
            return unique(flatten(izip(repeat(c), v)
                                  for c, v in self.clsdict.iteritems()))
        else:
            return unique(flatten(self.clsdict.itervalues()))

    def iter_pairs(self, within, order):
        """
        Iterate over FragmentToken pairs.

        Parameters
        ----------
        within : bool
            Only select pairs from the same class.
        order : bool
            Also include reverse of a pair.

        Returns
        -------
        Iterator over (FragmentToken, FragmentToken) pairs.

        """
        vals = self.clsdict.itervalues()
        if within:
            if order:
                pairs = flatten(((f1, f2), (f2, f1))
                                for fragments in vals
                                for f1, f2 in combinations(fragments, 2))
            else:
                pairs = (tuple(sorted((f1, f2),
                                      key=lambda f: (f.name, f.interval.start)))
                         for fragments in vals
                         for f1, f2 in combinations(fragments, 2))
        else: # across classes
            if order:
                pairs = (((f1, f2), (f2, f1))
                         for f1, f2 in combinations(flatten(vals), 2))
                pairs = flatten(pairs)
            else:
                pairs = (tuple(sorted((f1, f2),
                                      key=lambda f: (f.name, f.interval.start)))
                         for f1, f2 in combinations(flatten(vals), 2))
        return unique(ifilterfalse(lambda f: f[0].interval.overlaps_with(f[1].interval),
                                   pairs))

    def restrict(self, interval_db, remove_singletons=False):
        """
        Restrict the ClassDict to a set of Intervals.

        Returns a new ClassDict object with only the FragmentTokens
        that are fully covered in `interval_db`.

        Parameters
        ----------
        interval_db : IntervalDB
            Collection of Intervals
        remove_singletons : bool
            Remove classes with a single element

        Returns
        -------
        ClassDict
            New ClassDict object restricted to the fragments in `interval_db`

        """
        r = {}
        for classID, fragments in self.clsdict.iteritems():
            fs = [f for f in fragments
                  if interval_db.is_covered(f.name, f.interval)]
            if len(fs) == 0:
                pass
            elif len(fs) == 1:
                if remove_singletons:
                    pass
                else:
                    r[classID] = tuple(fs)
            else:
                r[classID] = tuple(fs)
        return ClassDict(r)


ClassID = collections.namedtuple('ClassID', ['ID', 'mark'])
ClassID.__repr__ = lambda self: '{0}({1}{2})'.format(
    self.__class__.__name__,
    self.ID,
    '({0})'.format(self.mark) if self.mark else '')
