# test_regex_parser.py
import pytest
from Core.regex_parser import parse, LiteralNode, UnionNode, ConcatNode, StarNode

class TestRegexParser:
    def test_single_char(self):
        node = parse('a')
        assert isinstance(node, LiteralNode)
        assert node.char == 'a'

    def test_union(self):
        node = parse('a|b')
        assert isinstance(node, UnionNode)

    def test_concat(self):
        node = parse('ab')
        assert isinstance(node, ConcatNode)

    def test_star(self):
        node = parse('a*')
        assert isinstance(node, StarNode)

    def test_precedence_star_before_concat(self):
        # a*b should be (a*)b not (ab)*
        node = parse('a*b')
        assert isinstance(node, ConcatNode)
        assert isinstance(node.left, StarNode)

    def test_precedence_concat_before_union(self):
        # ab|c should be (ab)|c not a(b|c)
        node = parse('ab|c')
        assert isinstance(node, UnionNode)
        assert isinstance(node.left, ConcatNode)

    def test_parentheses_override_precedence(self):
        # a(b|c) should have UnionNode on the right
        node = parse('a(b|c)')
        assert isinstance(node, ConcatNode)
        assert isinstance(node.right, UnionNode)

    def test_complex_regex(self):
        # should not raise
        parse('(a|b)*abb')
        parse('(ab|cd)*')
        parse('a+b?c')
        parse('(0|1)*00(0|1)*')

    def test_invalid_regex_raises(self):
        with pytest.raises(ValueError): parse('(ab')
        with pytest.raises(ValueError): parse('a**')
        with pytest.raises(ValueError): parse('|a')