import pytest

from tde.corpus import FragmentToken, Interval
from tde.goldset import extract_single, extract_batch, extract_gold_fragments

class TestExtractSingle(object):
    fragments = [[FragmentToken('wavfile1', Interval(0.0,0.1), 'a'),
                  FragmentToken('wavfile1', Interval(0.1,0.2), 'r'),
                  FragmentToken('wavfile1', Interval(0.2,0.3), 'm'),
                  FragmentToken('wavfile1', Interval(0.3,0.4), 's'),
                  FragmentToken('wavfile1', Interval(0.4,0.5), 'a')],
                 [FragmentToken('wavfile1', Interval(0.7,0.8), 'w'),
                  FragmentToken('wavfile1', Interval(0.8,0.9), 'o'),
                  FragmentToken('wavfile1', Interval(0.9,1.0), 'r'),
                  FragmentToken('wavfile1', Interval(1.0,1.1), 'm'),
                  FragmentToken('wavfile1', Interval(1.1,1.2), 's'),
                  FragmentToken('wavfile1', Interval(1.2,1.3), 'a')],
                 [FragmentToken('wavfile2', Interval(0.1,0.2), 'w'),
                  FragmentToken('wavfile2', Interval(0.2,0.3), 'o'),
                  FragmentToken('wavfile2', Interval(0.3,0.4), 'r'),
                  FragmentToken('wavfile2', Interval(0.4,0.5), 'd'),
                  FragmentToken('wavfile2', Interval(0.5,0.6), 's')]]

    def test_hit(self):
        r01 = [(FragmentToken('wavfile1', Interval(0.1,0.4), ('r', 'm', 's')),
                FragmentToken('wavfile1', Interval(0.9,1.2), ('r', 'm', 's'))),
               (FragmentToken('wavfile1', Interval(0.1,0.5), ('r', 'm', 's', 'a')),
                FragmentToken('wavfile1', Interval(0.9,1.3), ('r', 'm', 's', 'a'))),
               (FragmentToken('wavfile1', Interval(0.2,0.5), ('m', 's', 'a')),
                FragmentToken('wavfile1', Interval(1.0,1.3), ('m', 's', 'a')))]
        assert (extract_single(self.fragments[0], self.fragments[1], 3, 20, False) == r01)
        r12 = [(FragmentToken('wavfile1', Interval(0.7,1.0), ('w', 'o', 'r')),
                FragmentToken('wavfile2', Interval(0.1,0.4), ('w', 'o', 'r')))]
        assert (extract_single(self.fragments[1], self.fragments[2], 3, 20, False) == r12)

    def test_miss(self):
        assert (extract_single(self.fragments[0], self.fragments[2], 3, 20, False) == [])

    def test_same(self):
        for f in self.fragments:
            assert (extract_single(f, f, 3, 20, True) == [])

class TestExtractGoldFragments(object):
    fragments = [[FragmentToken('wavfile1', Interval(0.0,0.1), 'a'),
                  FragmentToken('wavfile1', Interval(0.1,0.2), 'r'),
                  FragmentToken('wavfile1', Interval(0.2,0.3), 'm'),
                  FragmentToken('wavfile1', Interval(0.3,0.4), 's'),
                  FragmentToken('wavfile1', Interval(0.4,0.5), 'a')],
                 [FragmentToken('wavfile1', Interval(0.7,0.8), 'w'),
                  FragmentToken('wavfile1', Interval(0.8,0.9), 'o'),
                  FragmentToken('wavfile1', Interval(0.9,1.0), 'r'),
                  FragmentToken('wavfile1', Interval(1.0,1.1), 'm'),
                  FragmentToken('wavfile1', Interval(1.1,1.2), 's'),
                  FragmentToken('wavfile1', Interval(1.2,1.3), 'a')],
                 [FragmentToken('wavfile2', Interval(0.1,0.2), 'w'),
                  FragmentToken('wavfile2', Interval(0.2,0.3), 'o'),
                  FragmentToken('wavfile2', Interval(0.3,0.4), 'r'),
                  FragmentToken('wavfile2', Interval(0.4,0.5), 'd'),
                  FragmentToken('wavfile2', Interval(0.5,0.6), 's')]]

    def test_all(self):
        r = [(FragmentToken('wavfile1', Interval(0.1,0.4), ('r', 'm', 's')),
              FragmentToken('wavfile1', Interval(0.9,1.2), ('r', 'm', 's'))),
             (FragmentToken('wavfile1', Interval(0.1,0.5), ('r', 'm', 's', 'a')),
              FragmentToken('wavfile1', Interval(0.9,1.3), ('r', 'm', 's', 'a'))),
             (FragmentToken('wavfile1', Interval(0.2,0.5), ('m', 's', 'a')),
              FragmentToken('wavfile1', Interval(1.0,1.3), ('m', 's', 'a'))),
             (FragmentToken('wavfile1', Interval(0.7,1.0), ('w', 'o', 'r')),
              FragmentToken('wavfile2', Interval(0.1,0.4), ('w', 'o', 'r')))]
        assert (extract_gold_fragments(self.fragments, 3, 20, False) == r)

class TestExtractBatch(object):
    fragments = [[FragmentToken('wavfile1', Interval(0.0,0.1), 'a'),
                  FragmentToken('wavfile1', Interval(0.1,0.2), 'r'),
                  FragmentToken('wavfile1', Interval(0.2,0.3), 'm'),
                  FragmentToken('wavfile1', Interval(0.3,0.4), 's'),
                  FragmentToken('wavfile1', Interval(0.4,0.5), 'a')],
                 [FragmentToken('wavfile1', Interval(0.7,0.8), 'w'),
                  FragmentToken('wavfile1', Interval(0.8,0.9), 'o'),
                  FragmentToken('wavfile1', Interval(0.9,1.0), 'r'),
                  FragmentToken('wavfile1', Interval(1.0,1.1), 'm'),
                  FragmentToken('wavfile1', Interval(1.1,1.2), 's'),
                  FragmentToken('wavfile1', Interval(1.2,1.3), 'a')],
                 [FragmentToken('wavfile2', Interval(0.1,0.2), 'w'),
                  FragmentToken('wavfile2', Interval(0.2,0.3), 'o'),
                  FragmentToken('wavfile2', Interval(0.3,0.4), 'r'),
                  FragmentToken('wavfile2', Interval(0.4,0.5), 'd'),
                  FragmentToken('wavfile2', Interval(0.5,0.6), 's')]]

    def test_all(self):
        r = [(FragmentToken('wavfile1', Interval(0.1,0.4), ('r', 'm', 's')),
              FragmentToken('wavfile1', Interval(0.9,1.2), ('r', 'm', 's'))),
             (FragmentToken('wavfile1', Interval(0.1,0.5), ('r', 'm', 's', 'a')),
              FragmentToken('wavfile1', Interval(0.9,1.3), ('r', 'm', 's', 'a'))),
             (FragmentToken('wavfile1', Interval(0.2,0.5), ('m', 's', 'a')),
              FragmentToken('wavfile1', Interval(1.0,1.3), ('m', 's', 'a'))),
             (FragmentToken('wavfile1', Interval(0.7,1.0), ('w', 'o', 'r')),
              FragmentToken('wavfile2', Interval(0.1,0.4), ('w', 'o', 'r')))]
        assert (extract_batch(self.fragments, [(0,1), (1,2), (0,2)], 3, 20) == r)

    def test_some(self):
        r = [(FragmentToken('wavfile1', Interval(0.1,0.4), ('r', 'm', 's')),
              FragmentToken('wavfile1', Interval(0.9,1.2), ('r', 'm', 's'))),
             (FragmentToken('wavfile1', Interval(0.1,0.5), ('r', 'm', 's', 'a')),
              FragmentToken('wavfile1', Interval(0.9,1.3), ('r', 'm', 's', 'a'))),
             (FragmentToken('wavfile1', Interval(0.2,0.5), ('m', 's', 'a')),
              FragmentToken('wavfile1', Interval(1.0,1.3), ('m', 's', 'a')))]
        assert (extract_batch(self.fragments, [(0, 1)], 3, 20) == r)

    def test_empty(self):
        assert (extract_batch(self.fragments, [], 3, 20) == [])
        assert (extract_batch(self.fragments, None, 3, 20) == [])

    def test_none_ix(self):
        assert (extract_batch(self.fragments, [(1,2), None], 3, 20) ==
                [(FragmentToken('wavfile1', Interval(0.7,1.0), ('w', 'o', 'r')),
                  FragmentToken('wavfile2', Interval(0.1,0.4), ('w', 'o', 'r')))])
