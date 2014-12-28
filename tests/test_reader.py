import cPickle as pickle

import pytest

from tde.data.interval import IntervalDB
from tde.util.reader import load_annotation, ReadError, \
    load_corpus_txt, read_classfile, annotate_classes, \
    tokenlists_to_corpus, read_split_single, read_split_multiple, read_annotation
from tde.data.classes import ClassID
from tde.data.fragment import FragmentToken
from tde.data.segment_annotation import SegmentAnnotation
from tde.data.interval import Interval
from tde.data.corpus import Corpus

class TestReadClasses(object):
    tiny_classes = """Class 0
f1 0.000 4.000
f2 0.000 4.000

Class 1
f1 1.000 4.000
f2 1.000 4.000

Class 2
f1 0.000 3.000
f2 0.000 3.000


"""
    tiny_corpus = """f1 0.000 1.000 a
f1 1.000 2.000 b
f1 2.000 3.000 c
f1 3.000 4.000 d
f2 0.000 1.000 a
f2 1.000 2.000 b
f2 2.000 3.000 c
f2 3.000 4.000 d

"""
    clsdict_e = {ClassID(0, None): (FragmentToken('f1', Interval(0.0,4.0), None),
                                    FragmentToken('f2', Interval(0.0,4.0), None)),
                 ClassID(1, None): (FragmentToken('f1', Interval(1.0,4.0), None),
                                    FragmentToken('f2', Interval(1.0,4.0), None)),
                 ClassID(2, None): (FragmentToken('f1', Interval(0.0,3.0), None),
                                    FragmentToken('f2', Interval(0.0,3.0), None))}
    clsdict_a = {ClassID(0, None): (FragmentToken('f1', Interval(0.0,4.0), ('a', 'b', 'c', 'd')),
                                    FragmentToken('f2', Interval(0.0,4.0), ('a', 'b', 'c', 'd'))),
                 ClassID(1, None): (FragmentToken('f1', Interval(1.0,4.0), ('b', 'c', 'd')),
                                    FragmentToken('f2', Interval(1.0,4.0), ('b', 'c', 'd'))),
                 ClassID(2, None): (FragmentToken('f1', Interval(0.0,3.0), ('a', 'b', 'c')),
                                    FragmentToken('f2', Interval(0.0,3.0), ('a', 'b', 'c')))}
    tokens = [FragmentToken('f1', Interval(0.0, 1.0), 'a'),
              FragmentToken('f1', Interval(1.0, 2.0), 'b'),
              FragmentToken('f1', Interval(2.0, 3.0), 'c'),
              FragmentToken('f1', Interval(3.0, 4.0), 'd'),
              FragmentToken('f2', Interval(0.0, 1.0), 'a'),
              FragmentToken('f2', Interval(1.0, 2.0), 'b'),
              FragmentToken('f2', Interval(2.0, 3.0), 'c'),
              FragmentToken('f2', Interval(3.0, 4.0), 'd')]
    corpus = Corpus([SegmentAnnotation('f1', tokens[:4]),
                     SegmentAnnotation('f2', tokens[4:])])

    def test_small(self):
        assert (self.clsdict_e == read_classfile(self.tiny_classes))

    def test_corpus(self):
        assert (self.corpus ==
                tokenlists_to_corpus(read_annotation(self.tiny_corpus)))

    def test_annotate(self):
        assert (self.clsdict_a ==
                annotate_classes(read_classfile(self.tiny_classes),
                                 tokenlists_to_corpus(read_annotation(self.tiny_corpus))))


class TestReadSplit(object):
    multi = """a 0.000 1.000
a 2.000 3.000
a 4.000 5.000

b 0.000 1.000
b 2.000 3.000
b 4.000 5.000
"""
    single = """a 0.000 1.000
a 2.000 3.000
a 4.000 5.000
b 0.000 1.000
b 2.000 3.000
b 4.000 5.000
"""

    multi_split = [IntervalDB({'a': [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)]}),
                   IntervalDB({'b': [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)]})]
    single_split = IntervalDB({'a': [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)],
                           'b': [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)]})

    def test_multi_multi(self):
        assert (read_split_multiple(self.multi) ==
                self.multi_split)
    def test_multi_single(self):
        assert (read_split_multiple(self.single) ==
                [self.single_split])
    def test_single_multi(self):
        assert (read_split_single(self.multi) ==
                self.single_split)
    def test_single_single(self):
        assert (read_split_single(self.single) ==
                self.single_split)


SKIP_HUGE = True

class TestReadAnnotationFile(object):
    def test_read_small(self):
        contents = """f1 0.000 0.100 a
f1 0.100 0.200 r
f1 0.200 0.300 m
f1 0.300 0.400 s
f1 0.400 0.500 a
f1 0.700 0.800 w
f1 0.800 0.900 o
f1 0.900 1.000 r
f1 1.000 1.100 m
f1 1.100 1.200 s
f1 1.200 1.300 a
f2 0.100 0.200 w
f2 0.200 0.300 o
f2 0.300 0.400 r
f2 0.400 0.500 d
f2 0.500 0.600 s
"""
        tokens = [FragmentToken('f1', Interval(0.0, 0.1), 'a'),
                  FragmentToken('f1', Interval(0.1, 0.2), 'r'),
                  FragmentToken('f1', Interval(0.2, 0.3), 'm'),
                  FragmentToken('f1', Interval(0.3, 0.4), 's'),
                  FragmentToken('f1', Interval(0.4, 0.5), 'a'),
                  FragmentToken('f1', Interval(0.7, 0.8), 'w'),
                  FragmentToken('f1', Interval(0.8, 0.9), 'o'),
                  FragmentToken('f1', Interval(0.9, 1.0), 'r'),
                  FragmentToken('f1', Interval(1.0, 1.1), 'm'),
                  FragmentToken('f1', Interval(1.1, 1.2), 's'),
                  FragmentToken('f1', Interval(1.2, 1.3), 'a'),
                  FragmentToken('f2', Interval(0.1, 0.2), 'w'),
                  FragmentToken('f2', Interval(0.2, 0.3), 'o'),
                  FragmentToken('f2', Interval(0.3, 0.4), 'r'),
                  FragmentToken('f2', Interval(0.4, 0.5), 'd'),
                  FragmentToken('f2', Interval(0.5, 0.6), 's')]
        corpus = Corpus([SegmentAnnotation('f1', tokens[0:5]),
                         SegmentAnnotation('f1', tokens[5:11]),
                         SegmentAnnotation('f2', tokens[11:])])

        assert ([tokens[0:5], tokens[5:11], tokens[11:]] ==
                read_annotation(contents))
        assert (tokenlists_to_corpus(read_annotation(contents)) ==
                corpus)

    def test_huge(self):
        with open('tests/mockdata/dev.phn.annotation.pkl', 'rb') as fid:
            corpus = pickle.load(fid)
        assert (corpus == load_annotation('tests/mockdata/dev.phn'))

    def test_badline(self):
        with pytest.raises(ReadError):
            load_annotation('tests/mockdata/mockcorpus_small_badline.phn')

    def test_badinterval(self):
        with pytest.raises(ReadError):
            load_annotation('tests/mockdata/mockcorpus_small_badinterval.phn')

    def test_badfloat(self):
        with pytest.raises(ReadError):
            load_annotation('tests/mockdata/mockcorpus_small_badfloat.phn')

class TestCorpusAnnotationFromPhoneFile(object):


    def test_dev(self):
        fname = 'tests/mockdata/dev.phn'
        corpus1 = tokenlists_to_corpus(load_annotation(fname))
        corpus2 = load_corpus_txt(fname)
        assert (corpus1 == corpus2)



if __name__ == '__main__':
    fname = 'tests/mockdata/mockcorpus_small.phn'
    corpus1 = tokenlists_to_corpus(load_annotation(fname))
    corpus2 = load_corpus_txt(fname)
    assert (corpus1 == corpus2)
