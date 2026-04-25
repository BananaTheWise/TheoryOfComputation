# test_state_elim.py
import pytest
from Core.thompson import regex_to_nfa
from Core.subset import subset_construction, dfa_minimize
from Core.state_elim import dfa_to_regex

def regex_round_trip(original_regex, test_strings):
    """Convert regex → NFA → DFA → regex → NFA → DFA, check same language"""
    nfa1 = regex_to_nfa(original_regex)
    dfa1 = dfa_minimize(subset_construction(nfa1))
    recovered_regex = dfa_to_regex(dfa1)
    nfa2 = regex_to_nfa(recovered_regex)
    dfa2 = dfa_minimize(subset_construction(nfa2))
    for s in test_strings:
        assert dfa1.accepts(s) == dfa2.accepts(s), \
            f"Round-trip failed: original='{original_regex}', recovered='{recovered_regex}', string='{s}'"

class TestStateElimination:
    def test_returns_string(self):
        nfa = regex_to_nfa('ab')
        dfa = dfa_minimize(subset_construction(nfa))
        result = dfa_to_regex(dfa)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_round_trip_simple(self):
        regex_round_trip('ab', ['', 'a', 'b', 'ab', 'abc', 'ba'])

    def test_round_trip_union(self):
        regex_round_trip('a|b', ['', 'a', 'b', 'c', 'ab', 'ba'])

    def test_round_trip_star(self):
        regex_round_trip('a*', ['', 'a', 'aa', 'aaa', 'b', 'ab'])

    def test_round_trip_complex(self):
        strings = ['', 'a', 'b', 'ab', 'abb', 'aabb', 'babb', 'abba', 'ba']
        regex_round_trip('(a|b)*abb', strings)

    def test_dead_dfa_returns_empty_or_none(self):
        from Core.automata import DFA
        dead = DFA(
            states={'q0'},
            alphabet={'a','b'},
            transitions={('q0','a'):'q0', ('q0','b'):'q0'},
            start_state='q0',
            accept_states=set()
        )
        result = dfa_to_regex(dead)
        assert result in ['', '∅', 'None', None]