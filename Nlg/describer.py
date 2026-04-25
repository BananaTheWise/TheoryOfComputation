import os
import sys

# Ensure we can import from Core
core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Core'))
if core_path not in sys.path:
    sys.path.append(core_path)

from Core.automata import DFA
from Core.enumerator import enumerate_strings_lazy

def get_reaching_accept_states(dfa: DFA):
    reaching = set(dfa.accept_states)
    changed = True
    while changed:
        changed = False
        for s in dfa.states:
            if s not in reaching:
                for c in dfa.alphabet:
                    if dfa.transitions.get((s, c)) in reaching:
                        reaching.add(s)
                        changed = True
                        break
    return reaching

def is_finite_language(dfa: DFA) -> bool:
    reaching = get_reaching_accept_states(dfa)
    if dfa.start_state not in reaching:
        return True
        
    visited = set()
    rec_stack = set()
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for c in dfa.alphabet:
            nxt = dfa.transitions.get((node, c))
            if nxt and nxt in reaching:
                if nxt not in visited:
                    if dfs(nxt): return True
                elif nxt in rec_stack:
                    return True
        rec_stack.remove(node)
        return False

    return not dfs(dfa.start_state)

def get_first_n_strings(dfa: DFA, n: int = 20) -> list:
    gen = enumerate_strings_lazy(dfa, max_length=10)
    res = []
    try:
        for _ in range(n):
            res.append(next(gen))
    except StopIteration:
        pass
    return res

def accepts_everything(dfa: DFA) -> bool:
    m = dfa.minimize()
    return len(m.states) == 1 and m.start_state in m.accept_states

def accepts_nothing(dfa: DFA) -> bool:
    reaching = get_reaching_accept_states(dfa)
    return dfa.start_state not in reaching

def accepts_only_empty(dfa: DFA) -> bool:
    samples = get_first_n_strings(dfa, 2)
    return samples == [""]

def has_fixed_length(dfa: DFA):
    if not is_finite_language(dfa):
        return None
    samples = get_first_n_strings(dfa, 100)
    if not samples:
        return None
    l = len(samples[0])
    if all(len(s) == l for s in samples):
        return l
    return None

def has_required_prefix(dfa: DFA):
    samples = get_first_n_strings(dfa, 20)
    if not samples or "" in samples:
        return None
    prefix = samples[0]
    for s in samples[1:]:
        while not s.startswith(prefix) and prefix:
            prefix = prefix[:-1]
    return prefix if prefix else None

def has_required_suffix(dfa: DFA):
    samples = get_first_n_strings(dfa, 20)
    if not samples or "" in samples:
        return None
    suffix = samples[0]
    for s in samples[1:]:
        while not s.endswith(suffix) and suffix:
            suffix = suffix[1:]
    return suffix if suffix else None

def has_required_substring(dfa: DFA):
    samples = get_first_n_strings(dfa, 20)
    if not samples or "" in samples:
        return None
    s1 = samples[0]
    best_sub = ""
    for i in range(len(s1)):
        for j in range(i+1, len(s1)+1):
            sub = s1[i:j]
            if all(sub in s for s in samples):
                if len(sub) > len(best_sub):
                    best_sub = sub
    return best_sub if best_sub else None

def counts_symbol_mod(dfa: DFA):
    m = dfa.minimize()
    if len(m.states) < 2:
        return None
    if len(m.accept_states) != 1:
        return None
    
    for sym in m.alphabet:
        is_mod = True
        for state in m.states:
            for c in m.alphabet:
                nxt = m.transitions.get((state, c))
                if c != sym:
                    if nxt != state: is_mod = False
                else:
                    if nxt == state: is_mod = False
        if is_mod:
            curr = m.start_state
            visited = set()
            for _ in range(len(m.states)):
                visited.add(curr)
                curr = m.transitions.get((curr, sym))
            if len(visited) == len(m.states) and curr == m.start_state:
                curr = m.start_state
                for rem in range(len(m.states)):
                    if curr in m.accept_states:
                        return (sym, len(m.states), rem)
                    curr = m.transitions.get((curr, sym))
    return None

def describe_dfa(dfa: DFA) -> str:
    alphabet_str = "{" + ", ".join(sorted(list(dfa.alphabet))) + "}"

    if accepts_everything(dfa):
        return f"The language consists of all strings over {alphabet_str} that are any valid string."
    if accepts_nothing(dfa):
        return f"The language over {alphabet_str} is empty (accepts no strings)."
    if accepts_only_empty(dfa):
        return f"The language consists of all strings over {alphabet_str} that are the empty string."

    length = has_fixed_length(dfa)
    if length is not None:
        return f"The language consists of all strings over {alphabet_str} that have length exactly {length}."

    mod_info = counts_symbol_mod(dfa)
    if mod_info is not None:
        sym, mod, rem = mod_info
        if mod == 2 and rem == 0:
            desc = f"contain an even number of '{sym}'s"
        elif mod == 2 and rem == 1:
            desc = f"contain an odd number of '{sym}'s"
        else:
            desc = f"contain a number of '{sym}'s that is {rem} modulo {mod}"
        return f"The language consists of all strings over {alphabet_str} that {desc}."

    prefix = has_required_prefix(dfa)
    if prefix:
        return f"The language consists of all strings over {alphabet_str} that start with '{prefix}'."

    suffix = has_required_suffix(dfa)
    if suffix:
        return f"The language consists of all strings over {alphabet_str} that end with '{suffix}'."

    # fallback
    from Core.enumerator import enumerate_strings
    samples = enumerate_strings(dfa, 5)
    sample_str = ", ".join(f'"{s}"' if s else 'ε' for s in samples[:5])
    return f"The language over {alphabet_str} includes strings such as: {sample_str} ..."

def run_tests():
    print("--- Testing DFA Describer ---")
    
    # 1. Even number of '1's
    dfa1 = DFA(
        states={'q0', 'q1'}, alphabet={'0', '1'},
        transitions={
            ('q0', '0'): 'q0', ('q0', '1'): 'q1',
            ('q1', '0'): 'q1', ('q1', '1'): 'q0'
        },
        start_state='q0', accept_states={'q0'}
    )
    print("1. Expected: even number of '1's")
    print("   Result:", describe_dfa(dfa1))
    
    # 2. Ends with 'ab'
    dfa2 = DFA(
        states={'q0', 'q1', 'q2'}, alphabet={'a', 'b'},
        transitions={
            ('q0', 'a'): 'q1', ('q0', 'b'): 'q0',
            ('q1', 'a'): 'q1', ('q1', 'b'): 'q2',
            ('q2', 'a'): 'q1', ('q2', 'b'): 'q0'
        },
        start_state='q0', accept_states={'q2'}
    )
    print("\n2. Expected: end with 'ab'")
    print("   Result:", describe_dfa(dfa2))
    
    # 3. Starts with '00'
    dfa3 = DFA(
        states={'q0', 'q1', 'q2', 'q3'}, alphabet={'0', '1'},
        transitions={
            ('q0', '0'): 'q1', ('q0', '1'): 'q3',
            ('q1', '0'): 'q2', ('q1', '1'): 'q3',
            ('q2', '0'): 'q2', ('q2', '1'): 'q2',
            ('q3', '0'): 'q3', ('q3', '1'): 'q3'
        },
        start_state='q0', accept_states={'q2'}
    )
    print("\n3. Expected: start with '00'")
    print("   Result:", describe_dfa(dfa3))
    
    # 4. Contains '01'
    dfa4 = DFA(
        states={'q0', 'q1', 'q2'}, alphabet={'0', '1'},
        transitions={
            ('q0', '0'): 'q1', ('q0', '1'): 'q0',
            ('q1', '0'): 'q1', ('q1', '1'): 'q2',
            ('q2', '0'): 'q2', ('q2', '1'): 'q2'
        },
        start_state='q0', accept_states={'q2'}
    )
    print("\n4. Expected: contain '01' as a substring")
    print("   Result:", describe_dfa(dfa4))
    
    # 5. Length exactly 3
    dfa5 = DFA(
        states={'q0', 'q1', 'q2', 'q3', 'q4'}, alphabet={'a', 'b'},
        transitions={
            ('q0', 'a'): 'q1', ('q0', 'b'): 'q1',
            ('q1', 'a'): 'q2', ('q1', 'b'): 'q2',
            ('q2', 'a'): 'q3', ('q2', 'b'): 'q3',
            ('q3', 'a'): 'q4', ('q3', 'b'): 'q4',
            ('q4', 'a'): 'q4', ('q4', 'b'): 'q4',
        },
        start_state='q0', accept_states={'q3'}
    )
    print("\n5. Expected: have length exactly 3")
    print("   Result:", describe_dfa(dfa5))

if __name__ == '__main__':
    run_tests()
