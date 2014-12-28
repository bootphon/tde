from tde.data.classes import ClassDict, ClassID
from tde.data.interval import Interval, IntervalDB
from tde.data.fragment import FragmentToken

class TestClassDict(object):
    tokens = [FragmentToken('a', Interval(0, 1), 'm1'),
              FragmentToken('b', Interval(2, 3), 'm1'),
              FragmentToken('c', Interval(2, 3), 'm1'),
              FragmentToken('b', Interval(0, 1), 'm2'),
              FragmentToken('c', Interval(0, 1), 'm2')]
    id0 = ClassID(0, 'c1')
    id1 = ClassID(1, 'c2')

    d1 = {id0: (tokens[0], tokens[1])}
    d2 = {id0: (tokens[0],)}
    d3 = {id0: tuple()}
    d4 = {id0: (tokens[0], tokens[2]),
          id1: (tokens[3], tokens[4])}
    c1 = ClassDict(d1)
    c2 = ClassDict(d2)
    c3 = ClassDict(d3)
    c4 = ClassDict(d4)

    def test_restrict(self):
        db1 = IntervalDB({'a': [Interval(0, 1)],
                          'b': [Interval(0, 3)],
                          'c': [Interval(0, 3)]})
        assert (self.c1.restrict(db1) == self.c1)
        assert (self.c2.restrict(db1) == self.c2)
        assert (self.c2.restrict(db1, remove_singletons=True) == ClassDict({}))
        assert (self.c3.restrict(db1) == ClassDict({}))
        assert (self.c4.restrict(db1) == self.c4)

        db2 = IntervalDB({'a': [Interval(0, 1)],
                          'c': [Interval(0, 3)]})
        assert (self.c1.restrict(db2) == self.c2)
        assert (self.c2.restrict(db2) == self.c2)
        assert (self.c2.restrict(db2, remove_singletons=True) == ClassDict({}))
        assert (self.c3.restrict(db2) == ClassDict({}))
        assert (self.c4.restrict(db2) ==
                ClassDict({self.id0: (self.tokens[0], self.tokens[2]),
                           self.id1: (self.tokens[4],)}))
        assert (self.c4.restrict(db2, remove_singletons=True) ==
                ClassDict({self.id0: (self.tokens[0], self.tokens[2])}))

    def test_iter_fragments(self):
        assert (list(self.c1.iter_fragments()) ==
                [self.tokens[0], self.tokens[1]])
        assert (list(self.c2.iter_fragments()) ==
                [self.tokens[0]])
        assert (list(self.c3.iter_fragments()) ==
                [])
        assert (list(self.c4.iter_fragments()) ==
                [self.tokens[0], self.tokens[2], self.tokens[3], self.tokens[4]])


    def test_iter_fragments_with_class(self):
        assert (list(self.c1.iter_fragments(with_class=True)) ==
                [(self.id0, self.tokens[0]), (self.id0, self.tokens[1])])
        assert (list(self.c2.iter_fragments(with_class=True)) ==
                [(self.id0, self.tokens[0])])
        assert (list(self.c3.iter_fragments(with_class=True)) == [])
        assert (list(self.c4.iter_fragments(with_class=True)) ==
                [(self.id0, self.tokens[0]), (self.id0, self.tokens[2]),
                 (self.id1, self.tokens[3]), (self.id1, self.tokens[4])])

    def test_iter_pairs_across_set(self):
        within = False
        order = False
        assert (list(self.c1.iter_pairs(within, order)) ==
                [(self.tokens[0], self.tokens[1])])
        assert (list(self.c2.iter_pairs(within, order)) == [])
        assert (list(self.c3.iter_pairs(within, order)) == [])
        assert (set(self.c4.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[2]),
                     (self.tokens[0], self.tokens[3]),
                     (self.tokens[0], self.tokens[4]),
                     (self.tokens[2], self.tokens[3]),
                     (self.tokens[2], self.tokens[4]),
                     (self.tokens[3], self.tokens[4])]))

    def test_iter_pairs_across_order(self):
        within = False
        order = True
        assert (set(self.c1.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[1]),
                     (self.tokens[1], self.tokens[0])]))
        assert (list(self.c2.iter_pairs(within, order)) == [])
        assert (list(self.c3.iter_pairs(within, order)) == [])
        assert (set(self.c4.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[2]),
                     (self.tokens[2], self.tokens[0]),
                     (self.tokens[0], self.tokens[3]),
                     (self.tokens[3], self.tokens[0]),
                     (self.tokens[0], self.tokens[4]),
                     (self.tokens[4], self.tokens[0]),
                     (self.tokens[2], self.tokens[3]),
                     (self.tokens[3], self.tokens[2]),
                     (self.tokens[2], self.tokens[4]),
                     (self.tokens[4], self.tokens[2]),
                     (self.tokens[3], self.tokens[4]),
                     (self.tokens[4], self.tokens[3])]))

    def test_iter_pairs_within_set(self):
        within = True
        order = False
        assert (set(self.c1.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[1])]))
        assert (list(self.c2.iter_pairs(within, order)) == [])
        assert (list(self.c3.iter_pairs(within, order)) == [])
        assert (set(self.c4.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[2]),
                     (self.tokens[3], self.tokens[4])]))

    def test_iter_pairs_within_order(self):
        within = True
        order = True
        assert (set(self.c1.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[1]),
                     (self.tokens[1], self.tokens[0])]))
        assert (list(self.c2.iter_pairs(within, order)) == [])
        assert (list(self.c3.iter_pairs(within, order)) == [])
        assert (set(self.c4.iter_pairs(within, order)) ==
                set([(self.tokens[0], self.tokens[2]),
                     (self.tokens[2], self.tokens[0]),
                     (self.tokens[3], self.tokens[4]),
                     (self.tokens[4], self.tokens[3])]))




class TestClassID(object):
    def test_mark(self):
        cid = ClassID(1, 'markymark')
        assert (cid.ID == 1)
        assert (cid.mark == 'markymark')
        assert (repr(cid) == 'ClassID(1(markymark))')

    def test_no_mark(self):
        cid = ClassID(1, None)
        assert (cid.ID == 1)
        assert (cid.mark is None)
        assert (repr(cid) == 'ClassID(1)')
