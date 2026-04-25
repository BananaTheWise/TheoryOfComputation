# test_grammar.py
import pytest
from Core.automata import DFA
from Core.grammer import dfa_to_cfg, cfg_to_nfa
from Core.subset import subset_construction, dfa_minimize

def make_simple_dfa():
    return DFA(
        states={'q0','q1'},
        alphabet={'a','b'},
        transitions={('q0','a'):'q0', ('q0','b'):'q1',
                     ('q1','a'):'q0', ('q1','b'):'q1'},
        start_state='q0',
        accept_states={'q1'}
    )

class TestDFAtoCFG:
    def test_returns_required_keys(self):
        cfg = dfa_to_cfg(make_simple_dfa())
        assert 'variables'   in cfg
        assert 'terminals'   in cfg
        assert 'start'       in cfg
        assert 'productions' in cfg

    def test_one_variable_per_state(self):
        dfa = make_simple_dfa()
        cfg = dfa_to_cfg(dfa)
        assert len(cfg['variables']) == len(dfa.states)

    def test_terminals_match_alphabet(self):
        dfa = make_simple_dfa()
        cfg = dfa_to_cfg(dfa)
        assert cfg['terminals'] == dfa.alphabet

    def test_accept_states_have_epsilon(self):
        cfg = dfa_to_cfg(make_simple_dfa())
        # Find variable for q1 (accept state)
        var_q1 = next(v for v in cfg['variables'] if 'q1' in v)
        assert '' in cfg['productions'][var_q1]

class TestCFGtoNFA:
    def test_round_trip_same_language(self):
        original_dfa = make_simple_dfa()
        cfg = dfa_to_cfg(original_dfa)
        nfa = cfg_to_nfa(cfg)
        restored_dfa = dfa_minimize(subset_construction(nfa))
        test_strings = ['', 'a', 'b', 'ab', 'ba', 'abb', 'aab', 'bab']
        for s in test_strings:
            assert original_dfa.accepts(s) == restored_dfa.accepts(s), \
                f"Round-trip CFG mismatch on '{s}'"