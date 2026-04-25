# test_thompson.py
import pytest
from Core.thompson import regex_to_nfa

class TestThompson:
    def test_single_char(self):
        nfa = regex_to_nfa('a')
        assert nfa.accepts('a')  == True
        assert nfa.accepts('b')  == False
        assert nfa.accepts('')   == False
        assert nfa.accepts('aa') == False

    def test_union(self):
        nfa = regex_to_nfa('a|b')
        assert nfa.accepts('a') == True
        assert nfa.accepts('b') == True
        assert nfa.accepts('c') == False
        assert nfa.accepts('ab') == False

    def test_concat(self):
        nfa = regex_to_nfa('ab')
        assert nfa.accepts('ab')  == True
        assert nfa.accepts('a')   == False
        assert nfa.accepts('b')   == False
        assert nfa.accepts('abc') == False

    def test_star_zero_times(self):
        nfa = regex_to_nfa('a*')
        assert nfa.accepts('')     == True   # zero repetitions
        assert nfa.accepts('a')    == True
        assert nfa.accepts('aaa')  == True

    def test_star_rejects_wrong_char(self):
        nfa = regex_to_nfa('a*')
        assert nfa.accepts('b')   == False
        assert nfa.accepts('ab')  == False

    def test_classic_aabb(self):
        """The textbook example: (a|b)*abb"""
        nfa = regex_to_nfa('(a|b)*abb')
        assert nfa.accepts('abb')    == True
        assert nfa.accepts('aabb')   == True
        assert nfa.accepts('babb')   == True
        assert nfa.accepts('abababb')== True
        assert nfa.accepts('ab')     == False
        assert nfa.accepts('abba')   == False
        assert nfa.accepts('')       == False

    def test_plus(self):
        nfa = regex_to_nfa('a+')
        assert nfa.accepts('a')   == True
        assert nfa.accepts('aa')  == True
        assert nfa.accepts('')    == False   # + means one or more

    def test_question_mark(self):
        nfa = regex_to_nfa('ab?c')
        assert nfa.accepts('ac')  == True   # b is optional
        assert nfa.accepts('abc') == True
        assert nfa.accepts('abbc')== False