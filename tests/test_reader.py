import cPickle as pickle

import pytest

from tde.reader import read_annotation_file, ReadError, \
    load_corpus_txt, read_classfile, \
    tokenlists_to_corpus

SKIP_HUGE = True

class TestReadAnnotationFile(object):
    # frozen tests
    def test_small(self):
        with open('tests/mockdata/mockcorpus_small.phn.pkl', 'rb') as fid:
            corpus = pickle.load(fid)
        assert (corpus == read_annotation_file('tests/mockdata/mockcorpus_small.phn'))

    def test_big(self):
        with open('tests/mockdata/mockcorpus_big.phn.pkl', 'rb') as fid:
            corpus = pickle.load(fid)
        assert (corpus == read_annotation_file('tests/mockdata/mockcorpus_big.phn'))

    @pytest.mark.skipif(SKIP_HUGE, reason='SKIPPING HUGE')
    def test_huge(self):
        with open('tests/mockdata/mockcorpus_huge.phn.pkl', 'rb') as fid:
            corpus = pickle.load(fid)
        assert (corpus == read_annotation_file('tests/mockdata/mockcorpus_huge.phn'))

    def test_badline(self):
        with pytest.raises(ReadError):
            read_annotation_file('tests/mockdata/mockcorpus_small_badline.phn')

    def test_badinterval(self):
        with pytest.raises(ReadError):
            read_annotation_file('tests/mockdata/mockcorpus_small_badinterval.phn')

    def test_badfloat(self):
        with pytest.raises(ReadError):
            read_annotation_file('tests/mockdata/mockcorpus_small_badfloat.phn')

class TestCorpusAnnotationFromPhoneFile(object):
    def test_small(self):
        fname = 'tests/mockdata/mockcorpus_small.phn'
        corpus1 = tokenlists_to_corpus(read_annotation_file(fname))
        corpus2 = load_corpus_txt(fname)
        assert (corpus1 == corpus2)

    def test_big(self):
        fname = 'tests/mockdata/mockcorpus_big.phn'
        corpus1 = tokenlists_to_corpus(read_annotation_file(fname))
        corpus2 = load_corpus_txt(fname)
        assert (corpus1 == corpus2)

    @pytest.mark.skipif(SKIP_HUGE, reason='SKIPPING HUGE')
    def test_huge(self):
        fname = 'tests/mockdata/mockcorpus_huge.phn'
        corpus1 = tokenlists_to_corpus(read_annotation_file(fname))
        corpus2 = load_corpus_txt(fname)
        assert (corpus1 == corpus2)

class TestReadClassFile(object):
    def test_small(self):
        fname = 'tests/mockdata/mockcorpus_small_perfect.classes'
        with open(fname + '.pkl', 'rb') as fid:
            c = pickle.load(fid)
        assert (c == read_classfile(fname))


if __name__ == '__main__':
    fname = 'tests/mockdata/mockcorpus_small.phn'
    corpus1 = tokenlists_to_corpus(read_annotation_file(fname))
    corpus2 = load_corpus_txt(fname)
    assert (corpus1 == corpus2)
