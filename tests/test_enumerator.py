# test_enumerator.py
import pytest
from Core.automata import DFA
from Core.enumerator import enumerate_strings, count_strings

def make_dfa_ends_in_b():
    return DFA(
        states={'q0','q1'},
        alphabet={'a','b'},
        transitions={('q0','a'):'q0', ('q0','b'):'q1',
                     ('q1','a'):'q0', ('q1','b'):'q1'},
        start_state='q0',
        accept_states={'q1'}
    )

def make_dfa_empty_language():
    return DFA(
        states={'q0'},
        alphabet={'a'},
        transitions={('q0','a'):'q0'},
        start_state='q0',
        accept_states=set()
    )

class TestEnumerateStrings:
    def test_correct_strings_returned(self):
        dfa = make_dfa_ends_in_b()
        result = enumerate_strings(dfa, max_length=3)
        assert 'b'   in result
        assert 'ab'  in result
        assert 'bb'  in result
        assert 'aab' in result
        assert 'abb' in result
        assert 'bab' in result
        assert 'bbb' in result

    def test_no_wrong_strings(self):
        dfa = make_dfa_ends_in_b()
        result = enumerate_strings(dfa, max_length=3)
        for s in result:
            assert dfa.accepts(s), f"Enumerated string '{s}' not accepted by DFA"

    def test_no_strings_beyond_max_length(self):
        dfa = make_dfa_ends_in_b()
        result = enumerate_strings(dfa, max_length=3)
        for s in result:
            assert len(s) <= 3

    def test_sorted_by_length_then_lex(self):
        dfa = make_dfa_ends_in_b()
        result = enumerate_strings(dfa, max_length=3)
        for i in range(len(result)-1):
            a, b = result[i], result[i+1]
            assert (len(a), a) <= (len(b), b)

    def test_empty_language(self):
        dfa = make_dfa_empty_language()
        assert enumerate_strings(dfa, max_length=5) == []

    def test_includes_empty_string_if_accepted(self):
        dfa = DFA(
            states={'q0'},
            alphabet={'a'},
            transitions={('q0','a'):'q0'},
            start_state='q0',
            accept_states={'q0'}
        )
        result = enumerate_strings(dfa, max_length=3)
        assert '' in result

class TestCountStrings:
    def test_count_matches_enumerate(self):
        dfa = make_dfa_ends_in_b()
        for length in range(5):
            enumerated = [s for s in enumerate_strings(dfa, length) if len(s)==length]
            counted = count_strings(dfa, length)
            assert counted == len(enumerated), f"Count mismatch at length {length}"