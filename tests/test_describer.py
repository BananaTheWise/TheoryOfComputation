# test_describer.py
import pytest
from Core.automata import DFA
from Nlg.describer import describe_dfa

class TestDescribeDFA:
    def test_returns_string(self):
        dfa = DFA(
            states={'q0','q1'},
            alphabet={'a','b'},
            transitions={('q0','a'):'q0', ('q0','b'):'q1',
                         ('q1','a'):'q0', ('q1','b'):'q1'},
            start_state='q0',
            accept_states={'q1'}
        )
        result = describe_dfa(dfa)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_language_description(self):
        dfa = DFA(
            states={'q0'},
            alphabet={'a'},
            transitions={('q0','a'):'q0'},
            start_state='q0',
            accept_states=set()
        )
        result = describe_dfa(dfa).lower()
        assert any(w in result for w in ['empty', 'nothing', 'no strings'])

    def test_even_zeros_description(self):
        dfa = DFA(
            states={'even','odd'},
            alphabet={'0','1'},
            transitions={('even','0'):'odd', ('even','1'):'even',
                         ('odd','0'):'even',  ('odd','1'):'odd'},
            start_state='even',
            accept_states={'even'}
        )
        result = describe_dfa(dfa).lower()
        assert 'even' in result
        assert '0' in result

    def test_description_is_human_readable(self):
        dfa = DFA(
            states={'q0','q1'},
            alphabet={'a','b'},
            transitions={('q0','a'):'q0', ('q0','b'):'q1',
                         ('q1','a'):'q0', ('q1','b'):'q1'},
            start_state='q0',
            accept_states={'q1'}
        )
        result = describe_dfa(dfa)
        # Should have spaces and words, not just symbols
        assert ' ' in result
        assert len(result.split()) >= 4