from __future__ import division
import pytest

import tde.nlp
import tde.reader

corpus = tde.reader.load_corpus_txt('tests/mockdata/tiny.phn')
disc_clsdict = tde.reader.load_classes_txt('tests/mockdata/tiny.classes', corpus)
gold_clsdict = tde.reader.load_classes_txt('tests/mockdata/tiny.classes', corpus)
def test_cover():
    assert(tde.nlp.cover(disc_clsdict) == 20.0)
    assert(tde.nlp.cover(gold_clsdict) == 20.0)


def test_coverage():
    assert(tde.nlp.coverage(disc_clsdict, gold_clsdict) == 1.0)

def test_ued():
    assert(tde.nlp.ued('kitten', 'sitting') == 3)

def test_ned():
    assert(tde.nlp.ned('kitten', 'sitting') == 3/7)

def test_NED():
    assert(tde.nlp.NED(disc_clsdict) == 0.0)
