# test_subset.py
import pytest
from Core.automata import NFA
from Core.subset import subset_construction, dfa_minimize
from Core.thompson import regex_to_nfa

class TestSubsetConstruction:
    def test_result_is_dfa(self):
        nfa = regex_to_nfa('a|b')
        dfa = subset_construction(nfa)
        # DFA: every (state, symbol) has exactly one transition
        for state in dfa.states:
            for sym in dfa.alphabet:
                key = (state, sym)
                assert key in dfa.transitions, f"Missing transition {key}"
                assert isinstance(dfa.transitions[key], str)  # single state, not a set

    def test_same_language_as_nfa(self):
        for regex in ['a|b', 'a*b', '(a|b)*abb', 'ab?c', 'a+']:
            nfa = regex_to_nfa(regex)
            dfa = subset_construction(nfa)
            test_strings = ['', 'a', 'b', 'ab', 'ba', 'abb', 'aab', 'bab', 'abc']
            for s in test_strings:
                assert nfa.accepts(s) == dfa.accepts(s), \
                    f"Mismatch on regex '{regex}' with string '{s}'"

    def test_no_duplicate_states(self):
        nfa = regex_to_nfa('(a|b)*abb')
        dfa = subset_construction(nfa)
        assert len(dfa.states) == len(set(dfa.states))

class TestDFAMinimize:
    def test_minimized_accepts_same_language(self):
        nfa = regex_to_nfa('(a|b)*abb')
        dfa = subset_construction(nfa)
        min_dfa = dfa_minimize(dfa)
        test_strings = ['', 'a', 'b', 'ab', 'abb', 'aabb', 'babb', 'abba']
        for s in test_strings:
            assert dfa.accepts(s) == min_dfa.accepts(s), \
                f"Mismatch after minimization on string '{s}'"

    def test_minimized_has_fewer_or_equal_states(self):
        nfa = regex_to_nfa('(a|b)*abb')
        dfa = subset_construction(nfa)
        min_dfa = dfa_minimize(dfa)
        assert len(min_dfa.states) <= len(dfa.states)