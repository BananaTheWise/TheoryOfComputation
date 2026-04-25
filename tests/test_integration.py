# test_integration.py
import pytest
from controller import convert

class TestRegexInput:
    def test_basic_regex(self):
        result = convert('regex', '(a|b)*abb')
        assert result['error'] is None
        assert result['dfa'] is not None
        assert result['dfa'].accepts('abb')   == True
        assert result['dfa'].accepts('aabb')  == True
        assert result['dfa'].accepts('ab')    == False
        assert isinstance(result['regex'],  str)
        assert isinstance(result['english'], str)
        assert isinstance(result['strings'], list)

    def test_simple_regex(self):
        result = convert('regex', 'a*b')
        assert result['error'] is None
        assert result['dfa'].accepts('b')    == True
        assert result['dfa'].accepts('ab')   == True
        assert result['dfa'].accepts('aaab') == True
        assert result['dfa'].accepts('a')    == False
        assert result['dfa'].accepts('ba')   == False

    def test_invalid_regex_returns_error(self):
        result = convert('regex', '(ab**')
        assert result['error'] is not None

class TestDFAInput:
    DFA_TEXT = """states: q0,q1,q2
alphabet: a,b
start: q0
accept: q2
transitions:
  q0,a -> q1
  q1,b -> q2
  q2,a -> q1
  q2,b -> q2"""

    def test_dfa_input_parsed(self):
        result = convert('dfa', self.DFA_TEXT)
        assert result['error'] is None
        assert result['dfa'] is not None
        assert result['dfa'].accepts('ab')   == True
        assert result['dfa'].accepts('abab') == True
        assert result['dfa'].accepts('a')    == False
        assert result['dfa'].accepts('')     == False

    def test_malformed_dfa_returns_error(self):
        result = convert('dfa', 'this is not a dfa')
        assert result['error'] is not None

class TestCFGInput:
    def test_cfg_input(self):
        cfg_text = "S -> aS | bA | ε\nA -> bA | b"
        result = convert('cfg', cfg_text)
        assert result['error'] is None
        assert result['dfa'] is not None

class TestStringInput:
    def test_string_list_input(self):
        result = convert('strings', 'ab\nba\nabb\nbba')
        assert result['error'] is None
        dfa = result['dfa']
        assert dfa.accepts('ab')  == True
        assert dfa.accepts('ba')  == True
        assert dfa.accepts('abb') == True
        assert dfa.accepts('bba') == True
        assert dfa.accepts('a')   == False
        assert dfa.accepts('abc') == False

class TestAllOutputsPresent:
    def test_all_outputs_populated(self):
        result = convert('regex', 'a*b')
        assert result['dfa']     is not None
        assert result['regex']   != ''
        assert result['cfg']     != {}
        assert result['strings'] != []
        assert result['english'] != ''
        assert result['error']   is None

class TestEdgeCases:
    def test_empty_input_returns_error(self):
        result = convert('regex', '')
        assert result['error'] is not None

    def test_single_char_regex(self):
        result = convert('regex', 'a')
        assert result['error'] is None
        assert result['dfa'].accepts('a')  == True
        assert result['dfa'].accepts('aa') == False
        assert result['dfa'].accepts('')   == False

    def test_epsilon_only(self):
        result = convert('regex', 'ε')
        assert result['error'] is None
        assert result['dfa'] is not None
        assert result['dfa'].accepts('') == True

    def test_all_output_keys_always_present(self):
        """Even on error, all keys must exist"""
        result = convert('regex', '!!!invalid!!!')
        for key in ['dfa', 'regex', 'cfg', 'strings', 'english', 'error']:
            assert key in result