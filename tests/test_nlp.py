from __future__ import division

from tde.data.interval import Interval
from tde.measures.nlp import collapse, cover, coverage, ued, ned, NED
from tde.util.reader import load_corpus_txt, load_classes_txt

def test_collapse():
    is1 = [Interval(0, 1), Interval(2,3),
           Interval(4, 5)]
    assert(collapse(is1) == is1)
    is2 = [Interval(0, 1), Interval(1,2)]
    assert(collapse(is2) == [Interval(0, 2)])
    is3 = [Interval(0, 1), Interval(2, 3),
           Interval(0, 1.5)]
    assert(collapse(is3) == [Interval(0, 1.5),
                                     Interval(2,3)])
    is4 = [Interval(0, 1), Interval(2, 3),
           Interval(0, 10)]
    assert(collapse(is4) == [Interval(0.,10)])

corpus = load_corpus_txt('tests/mockdata/tiny.phn')
disc_clsdict = load_classes_txt('tests/mockdata/tiny.classes', corpus)
gold_clsdict = load_classes_txt('tests/mockdata/tiny.classes', corpus)

def test_cover():
    assert(cover(disc_clsdict) == 8.0)
    assert(cover(gold_clsdict) == 8.0)

def test_coverage():
    assert(coverage(disc_clsdict, gold_clsdict) == 1.0)

def test_ued():
    assert(ued('kitten', 'sitting') == 3)

def test_ned():
    assert(ned('kitten', 'sitting') == 3/7)

def test_NED():
    assert(NED(disc_clsdict) == 0.0)
