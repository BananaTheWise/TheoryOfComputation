import os
import sys
import json

# Setup path so we can import from Core and Nlg
core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Core'))
nlg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Nlg'))
if core_path not in sys.path:
    sys.path.insert(0, core_path)
if nlg_path not in sys.path:
    sys.path.insert(0, nlg_path)

from Core.automata import DFA, NFA
from Core.regex_parser import parse
from Core.thompson import regex_to_nfa
from Core.subset import subset_construction, dfa_minimize
from Core.state_elim import dfa_to_regex

try:
    from Core.grammer import dfa_to_cfg, cfg_to_nfa
except ImportError:
    from Core.grammar import dfa_to_cfg, cfg_to_nfa

from Core.enumerator import enumerate_strings
from Nlg.describer import describe_dfa


def parse_dfa_from_text(text: str) -> DFA:
    states = set()
    alphabet = set()
    start = None
    accept = set()
    transitions = {}
    
    mode = None
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        
        if line.startswith('states:'):
            states = {s.strip() for s in line.split(':', 1)[1].split(',')}
        elif line.startswith('alphabet:'):
            alphabet = {a.strip() for a in line.split(':', 1)[1].split(',')}
        elif line.startswith('start:'):
            start = line.split(':', 1)[1].strip()
        elif line.startswith('accept:'):
            acc_str = line.split(':', 1)[1].strip()
            if acc_str:
                accept = {s.strip() for s in acc_str.split(',')}
        elif line.startswith('transitions:'):
            mode = 'transitions'
        elif mode == 'transitions':
            if '->' not in line:
                raise ValueError(f"Invalid transition format: {line}")
            lhs, rhs = line.split('->')
            src_char = lhs.strip()
            nxt = rhs.strip()
            if ',' not in src_char:
                raise ValueError(f"Transition lhs must be 'state,char': {src_char}")
            src, char = src_char.split(',', 1)
            src = src.strip()
            char = char.strip()
            transitions[(src, char)] = nxt
        else:
            raise ValueError(f"Unexpected line: {line}")
            
    if not states: raise ValueError("No states defined")
    if not alphabet: raise ValueError("No alphabet defined")
    if not start: raise ValueError("No start state defined")
    
    return DFA(states, alphabet, transitions, start, accept)


def parse_nfa_from_text(text: str) -> NFA:
    states = set()
    alphabet = set()
    start = None
    accept = set()
    transitions = {}
    
    mode = None
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        
        if line.startswith('states:'):
            states = {s.strip() for s in line.split(':', 1)[1].split(',')}
        elif line.startswith('alphabet:'):
            alphabet = {a.strip() for a in line.split(':', 1)[1].split(',')}
        elif line.startswith('start:'):
            start = line.split(':', 1)[1].strip()
        elif line.startswith('accept:'):
            acc_str = line.split(':', 1)[1].strip()
            if acc_str:
                accept = {s.strip() for s in acc_str.split(',')}
        elif line.startswith('transitions:'):
            mode = 'transitions'
        elif mode == 'transitions':
            if '->' not in line:
                raise ValueError(f"Invalid transition format: {line}")
            lhs, rhs = line.split('->')
            src_char = lhs.strip()
            nxt_states = {s.strip() for s in rhs.split(',')} if rhs.strip() else set()
            if ',' not in src_char:
                raise ValueError(f"Transition lhs must be 'state,char': {src_char}")
            src, char = src_char.split(',', 1)
            src = src.strip()
            char = char.strip()
            if char in ('ε', 'epsilon', 'eps'):
                char = ''
            if (src, char) not in transitions:
                transitions[(src, char)] = set()
            transitions[(src, char)].update(nxt_states)
        else:
            raise ValueError(f"Unexpected line: {line}")
            
    if not states: raise ValueError("No states defined")
    if not alphabet: raise ValueError("No alphabet defined")
    if not start: raise ValueError("No start state defined")
    
    return NFA(states, alphabet, transitions, start, accept)


def parse_cfg_from_text(text: str) -> dict:
    variables = set()
    terminals = set()
    productions = {}
    start = None
    
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        if '->' not in line:
            raise ValueError(f"Invalid production rule (missing '->'): {line}")
        
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
        if not start:
            start = lhs
        variables.add(lhs)
        
        if lhs not in productions:
            productions[lhs] = []
            
        alts = rhs.split('|')
        for alt in alts:
            alt = alt.strip()
            if alt in ('ε', 'epsilon', "''", '""'):
                productions[lhs].append("")
            else:
                parts = alt.split()
                if len(parts) == 1 and len(alt) >= 2:
                    # e.g., 'aS'
                    term, var = alt[0], alt[1:]
                    productions[lhs].append(f"{term} {var}")
                    terminals.add(term)
                    variables.add(var)
                elif len(parts) == 2:
                    term, var = parts
                    productions[lhs].append(f"{term} {var}")
                    terminals.add(term)
                    variables.add(var)
                elif len(parts) == 1:
                    term = parts[0]
                    productions[lhs].append(term)
                    terminals.add(term)
                else:
                    raise ValueError(f"Invalid RHS in production: {alt}")
                    
    if not start:
        raise ValueError("Empty CFG definition")
        
    return {
        'variables': variables,
        'terminals': terminals,
        'start': start,
        'productions': productions
    }

def convert(input_type: str, input_text: str) -> dict:
    result = {
        'dfa': None,
        'regex': '',
        'cfg': {},
        'strings': [],
        'english': '',
        'error': None
    }

    # 🚨 Fix: prevent empty input issues
    if not input_text or not input_text.strip():
        result['error'] = 'Input cannot be empty.'
        return result

    try:
        dfa = None

        if input_type == 'regex':
            normalized = input_text.strip()
            if normalized in ('ε', 'epsilon', 'eps'):
                normalized = ''

            if normalized == '':
                from Core.automata import DFA
                dfa = DFA(
                    states={'q0', 'dead'},
                    alphabet=set(),
                    transitions={},
                    start_state='q0',
                    accept_states={'q0'}
                )
            else:
                nfa = regex_to_nfa(normalized)
                dfa = dfa_minimize(subset_construction(nfa))

        elif input_type == 'dfa':
            dfa = parse_dfa_from_text(input_text)
            dfa = dfa_minimize(dfa)

        elif input_type == 'nfa':
            nfa = parse_nfa_from_text(input_text)
            dfa = subset_construction(nfa)
            dfa = dfa_minimize(dfa)

        elif input_type == 'cfg':
            cfg = parse_cfg_from_text(input_text)
            nfa = cfg_to_nfa(cfg)
            dfa = subset_construction(nfa)
            dfa = dfa_minimize(dfa)

        elif input_type == 'strings':
            lines = [l.strip() for l in input_text.strip().splitlines() if l.strip()]
            if not lines:
                raise ValueError("No strings provided.")
            dfa = strings_to_dfa(lines)

        else:
            raise ValueError(f"Unknown input type: {input_type}")

        # ✅ Only fill result if DFA exists
        if dfa:
            result['dfa'] = dfa
            result['regex'] = dfa_to_regex(dfa)
            result['cfg'] = dfa_to_cfg(dfa)
            result['strings'] = enumerate_strings(dfa, 6)
            result['english'] = describe_dfa(dfa)

    # 🎯 IMPORTANT FIXES BELOW
    except ValueError as e:
        result['error'] = str(e)

    except RecursionError:
        result['error'] = 'Input too complex or caused infinite recursion.'

    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'

    return result

def run_tests():
    print("--- Integration Tests ---")
    
    # 1. Regex test
    print("Test 1: Regex '(a|b)*abb'")
    res1 = convert('regex', '(a|b)*abb')
    assert res1['error'] is None, f"Regex Error: {res1['error']}"
    assert 'aabb' in res1['strings'], "Regex conversion failed: missing 'aabb'"
    assert 'ab' not in res1['strings'], "Regex conversion failed: falsely accepted 'ab'"
    print("Test 1 Passed.")
    
    # 2. DFA Text test
    print("Test 2: DFA Custom Format")
    dfa_text = '''
states: q0,q1,q2
alphabet: a,b
start: q0
accept: q2
transitions:
  q0,a -> q1
  q0,b -> q0
  q1,a -> q1
  q1,b -> q2
  q2,a -> q1
  q2,b -> q0
'''
    res2 = convert('dfa', dfa_text)
    assert res2['error'] is None, f"DFA Error: {res2['error']}"
    assert 'ab' in res2['strings'], "DFA conversion failed: missing 'ab'"
    print("Test 2 Passed.")
    
    # 3. CFG Text test
    print("Test 3: CFG Format")
    cfg_text = '''
    S -> a S | b A | b
    A -> a A | a
    '''
    res3 = convert('cfg', cfg_text)
    assert res3['error'] is None, f"CFG Error: {res3['error']}"
    assert 'ba' in res3['strings'], "CFG conversion failed: missing 'ba'"
    assert 'bb' not in res3['strings'], "CFG conversion failed: falsely accepted 'bb'"
    print("Test 3 Passed.")
    
    print("All tests passed!")

# controller.py — add this function

def strings_to_dfa(string_list: list) -> 'DFA':
    """Build a DFA from a finite list of strings using a trie."""
    from Core.automata import DFA

    # Build trie as a dict of dicts
    trie = {}

    for s in string_list:
        node = trie
        for ch in s:
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node['__accept__'] = True  # mark end of word

    # Convert trie nodes to DFA states
    # Each unique trie node dict gets a state name
    states = set()
    transitions = {}
    accept_states = set()
    alphabet = set(ch for s in string_list for ch in s)

    # Add a dead state for invalid transitions
    dead = 'dead'
    states.add(dead)

    # BFS over trie to assign state names
    from collections import deque
    queue = deque()
    node_to_state = {}
    node_to_state[id(trie)] = 'q0'
    states.add('q0')
    if trie.get('__accept__'):
        accept_states.add('q0')
    queue.append((trie, 'q0'))

    counter = 1
    while queue:
        node, state_name = queue.popleft()
        for ch in alphabet:
            if ch in node:
                child = node[ch]
                child_id = id(child)
                if child_id not in node_to_state:
                    new_state = f'q{counter}'
                    counter += 1
                    node_to_state[child_id] = new_state
                    states.add(new_state)
                    if child.get('__accept__'):
                        accept_states.add(new_state)
                    queue.append((child, new_state))
                transitions[(state_name, ch)] = node_to_state[child_id]
            else:
                transitions[(state_name, ch)] = dead  # goes to dead state

    # Dead state loops on everything
    for ch in alphabet:
        transitions[(dead, ch)] = dead

    return DFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state='q0',
        accept_states=accept_states
    )

if __name__ == '__main__':
    run_tests()