# test_automata.py
import pytest
from Core.automata import DFA, NFA

# ── DFA TESTS ──────────────────────────────────────────

def make_dfa_ends_in_b():
    """DFA accepting strings over {a,b} that end in 'b'"""
    return DFA(
        states={'q0', 'q1'},
        alphabet={'a', 'b'},
        transitions={('q0','a'):'q0', ('q0','b'):'q1',
                     ('q1','a'):'q0', ('q1','b'):'q1'},
        start_state='q0',
        accept_states={'q1'}
    )

def make_dfa_even_zeros():
    """DFA accepting binary strings with even number of 0s"""
    return DFA(
        states={'even', 'odd'},
        alphabet={'0', '1'},
        transitions={('even','0'):'odd', ('even','1'):'even',
                     ('odd','0'):'even',  ('odd','1'):'odd'},
        start_state='even',
        accept_states={'even'}
    )

class TestDFAAccepts:
    def test_ends_in_b_accepts(self):
        dfa = make_dfa_ends_in_b()
        assert dfa.accepts('b')    == True
        assert dfa.accepts('ab')   == True
        assert dfa.accepts('aab')  == True
        assert dfa.accepts('bab')  == True
        assert dfa.accepts('abb')  == True

    def test_ends_in_b_rejects(self):
        dfa = make_dfa_ends_in_b()
        assert dfa.accepts('')     == False
        assert dfa.accepts('a')    == False
        assert dfa.accepts('ba')   == False
        assert dfa.accepts('bba')  == False

    def test_empty_string_not_accepted(self):
        dfa = make_dfa_ends_in_b()
        assert dfa.accepts('') == False

    def test_even_zeros_accepts(self):
        dfa = make_dfa_even_zeros()
        assert dfa.accepts('')     == True   # 0 zeros = even
        assert dfa.accepts('00')   == True
        assert dfa.accepts('11')   == True
        assert dfa.accepts('0011') == True
        assert dfa.accepts('1001') == True

    def test_even_zeros_rejects(self):
        dfa = make_dfa_even_zeros()
        assert dfa.accepts('0') == False  # 1 zero → reject
        assert dfa.accepts('000') == False  # 3 zeros → reject
        assert dfa.accepts('10') == False  # 1 zero → reject
        assert dfa.accepts('1110') == False  # 1 zero → reject
        assert dfa.accepts('10010') == False  # 3 zeros → reject

    def test_accepts_only_empty_string(self):
        dfa = DFA(
            states={'q0'},
            alphabet={'a'},
            transitions={('q0','a'):'q0'},
            start_state='q0',
            accept_states={'q0'}
        )
        assert dfa.accepts('') == True
        assert dfa.accepts('a') == True  # this DFA accepts everything

    def test_dead_state_dfa(self):
        """DFA that accepts nothing"""
        dfa = DFA(
            states={'q0'},
            alphabet={'a','b'},
            transitions={('q0','a'):'q0', ('q0','b'):'q0'},
            start_state='q0',
            accept_states=set()
        )
        assert dfa.accepts('') == False
        assert dfa.accepts('a') == False
        assert dfa.accepts('ab') == False

class TestDFASerialization:
    def test_to_dict_and_back(self):
        dfa = make_dfa_ends_in_b()
        d = dfa.to_dict()
        restored = DFA.from_dict(d)
        assert restored.accepts('ab')  == True
        assert restored.accepts('aa')  == False
        assert restored.states        == dfa.states
        assert restored.alphabet      == dfa.alphabet
        assert restored.accept_states == dfa.accept_states

# ── NFA TESTS ──────────────────────────────────────────

def make_nfa_ends_in_ab():
    """NFA accepting strings ending in 'ab'"""
    return NFA(
        states={'q0','q1','q2'},
        alphabet={'a','b'},
        transitions={
            ('q0','a'):{'q0','q1'},
            ('q0','b'):{'q0'},
            ('q1','b'):{'q2'},
        },
        start_state='q0',
        accept_states={'q2'}
    )

class TestNFAAccepts:
    def test_ends_in_ab_accepts(self):
        nfa = make_nfa_ends_in_ab()
        assert nfa.accepts('ab')   == True
        assert nfa.accepts('aab')  == True
        assert nfa.accepts('bab')  == True
        assert nfa.accepts('abab') == True

    def test_ends_in_ab_rejects(self):
        nfa = make_nfa_ends_in_ab()
        assert nfa.accepts('')     == False
        assert nfa.accepts('a')    == False
        assert nfa.accepts('b')    == False
        assert nfa.accepts('ba')   == False
        assert nfa.accepts('aba')  == False

class TestEpsilonClosure:
    def test_epsilon_closure_no_epsilon(self):
        nfa = make_nfa_ends_in_ab()
        assert nfa.epsilon_closure({'q0'}) == {'q0'}

    def test_epsilon_closure_with_epsilon(self):
        nfa = NFA(
            states={'q0','q1','q2'},
            alphabet={'a'},
            transitions={
                ('q0',''):{'q1'},
                ('q1',''):{'q2'},
                ('q2','a'):{'q2'},
            },
            start_state='q0',
            accept_states={'q2'}
        )
        assert nfa.epsilon_closure({'q0'}) == {'q0','q1','q2'}

class TestNFAtoDFA:
    def test_converted_dfa_same_language(self):
        nfa = make_nfa_ends_in_ab()
        dfa = nfa.to_dfa()
        assert dfa.accepts('ab')   == True
        assert dfa.accepts('aab')  == True
        assert dfa.accepts('bab')  == True
        assert dfa.accepts('')     == False
        assert dfa.accepts('a')    == False
        assert dfa.accepts('ba')   == False