import pytest
from tde.data.fragment import FragmentToken, FragmentType, token_cmp
from tde.data.interval import Interval


class TestFragmentToken(object):
    def test_mark(self):
        ft = FragmentToken('name', Interval(0, 1), 'markymark')
        assert (ft.name == 'name')
        assert (ft.interval == Interval(0,1))
        assert (ft.mark == 'markymark')

    def test_no_mark(self):
        ft = FragmentToken('name', Interval(0, 1), None)
        assert (ft.name == 'name')
        assert (ft.interval == Interval(0,1))
        assert (ft.mark is None)


class TestFragmentType(object):
    tokens = [
        FragmentToken('a', Interval(0.0, 0.1), 'a'),
        FragmentToken('a', Interval(0.1, 0.2), 'r'),
        FragmentToken('a', Interval(0.2, 0.3), 'm'),
        FragmentToken('a', Interval(0.3, 0.4), 's'),
        FragmentToken('a', Interval(0.4, 0.5), 'a')]

    def test_mark(self):
        ft = FragmentType(self.tokens, 'markymark')
        assert (ft.tokens == self.tokens)
        assert (ft.mark == 'markymark')

    def test_no_mark(self):
        ft = FragmentType(self.tokens, None)
        assert (ft.tokens == self.tokens)
        assert (ft.mark is None)


class TestTokenCmp(object):
    f1 = FragmentToken('a', Interval(0.0, 0.5), None)
    f2 = FragmentToken('a', Interval(0.5, 1.5), None)
    f3 = FragmentToken('a', Interval(1.3, 1.4), None)
    f4 = FragmentToken('b', Interval(0, 1), None)

    def test_invalid_comparison(self):
        with pytest.raises(ValueError):
            token_cmp(self.f1, self.f4)

    def test_token_eq(self):
        assert (token_cmp(self.f1, self.f1) == 0)
        assert (token_cmp(self.f2, self.f2) == 0)
        assert (token_cmp(self.f3, self.f3) == 0)

    def test_token_cmp(self):
        assert (token_cmp(self.f1, self.f2) == -1)
        assert (token_cmp(self.f1, self.f3) == -1)
        assert (token_cmp(self.f2, self.f1) == 1)
        assert (token_cmp(self.f3, self.f1) == 1)

        assert (token_cmp(self.f2, self.f3) == 0)
        assert (token_cmp(self.f3, self.f2) == 0)
