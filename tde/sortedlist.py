"""Collection sorted by a key function.

"""

from bisect import bisect_right, bisect_left

class SortedList(object):
    """Collection sorted by a key function.

    SortedList is a wrapper around `bisect`, useful for fast lookup of
    orderable elements in a collection and maintaining the order in that
    collection.

    Parameters
    ----------
    iterable : sequence, optional
        Base collection to build SortedList off.
    key : func
        Compare elements with this function

    """
    def __init__(self, iterable=None, key=None):
        self._key_func = (lambda x: x) if key is None else key
        if iterable is None or iterable == () or iterable == []:
            self._k = []
            self._v = []
        else:
            self._k, self._v = [list(e)
                                for e in zip(*sorted((self._key_func(x), x)
                                                     for x in iterable))]

    def __getitem__(self, i):
        return self._v[i]

    def __len__(self):
        return len(self._v)

    def __iter__(self):
        return iter(self._v)

    def __repr__(self):
        return '[{0}]'.format(', '.join(str(x) for x in self._v))

    def __str__(self):
        return self.__repr__()

    def __contains__(self, x):
        i = bisect_left(self._k, self._key_func(x))
        return i != len(self._k) and self._v[i] == x

    def insert(self, x):
        """Insert `x`. If equal keys are found, add to the left.
        """
        key = self._key_func(x)
        i = bisect_left(self._k, key)
        self._k.insert(i, key)
        self._v.insert(i, x)

    def extend(self, iterable):
        """Insert all elements of `iterable`.
        """
        for x in iterable:
            self.insert(x)

    def remove(self, x):
        """Remove `x`. Raise ValueError if `x` is not found.
        """
        i = self.index(x)
        del self._k[i]
        del self._v[i]

    def index(self, x):
        """Find the first item equal to `x`. Raise ValueError if no such item
        is found.
        """
        i = bisect_left(self._k, self._key_func(x))
        if i != len(self._k) and self._v[i] == x:
            return i
        raise ValueError('item not found: {}'.format(x))

    def index_lt(self, x):
        """Find the index of the greatest item smaller than `x`. Raise ValueError
        if no such item is found.
        """
        i = bisect_left(self._k, self._key_func(x))
        if i > 0:
            return i - 1
        raise ValueError('no item < {}'.format(x))

    def find_lt(self, x):
        """Find the greatest item smaller than `x`. Raise ValueError if no such
        item is found.
        """
        return self._v[self.index_lt(x)]

    def index_le(self, x):
        """Find the index of the greatest item smaller than or equal to `x`.
        Raise ValueError if no such item is found.
        """
        i = bisect_right(self._k, self._key_func(x))
        if i:
            return i - 1
        raise ValueError('no item <= {}'.format(x))

    def find_le(self, x):
        """Find the greatest item smaller than or equal to `x`. Raise ValueError
        if no such item is found.
        """
        return self._v[self.index_le(x)]

    def index_gt(self, x):
        """Find the index of the smallest item greater than `x`.Raise ValueError
        if no such item is found.
        """
        i = bisect_right(self._k, self._key_func(x))
        if i != len(self._k):
            return i
        raise ValueError('no item > {}'.format(x))

    def find_gt(self, x):
        """Find the first item greater than `x`. Raise ValueError if no such
        item is found.
        """
        return self._v[self.index_gt(x)]

    def index_ge(self, x):
        """Find the index of the smallest item greater than or equal to `x`.
        Raise ValueError if no such item is found.
        """
        i = bisect_left(self._k, self._key_func(x))
        if i != len(self._k):
            return i
        raise ValueError('no item >= {}'.format(x))

    def find_ge(self, x):
        """Find the first item greater than or equal to `x`. Raise ValueError
        if no such item is found.
        """
        return self._v[self.index_ge(x)]
