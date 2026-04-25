from Core.automata import DFA

def is_single_unit(r: str) -> bool:
    if not r:
        return True
    if len(r) == 1:
        return True
    if r.startswith('(') and r.endswith(')'):
        depth = 0
        for i, c in enumerate(r):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0 and i != len(r) - 1:
                return False
        return True
    if r.endswith('*'):
        if len(r) == 2:
            return True
        if r.startswith('(') and r[-2] == ')':
            depth = 0
            for i in range(len(r) - 1):
                if r[i] == '(': depth += 1
                elif r[i] == ')': depth -= 1
                if depth == 0 and i != len(r) - 2:
                    return False
            return True
    return False

def needs_parens_concat(r: str) -> bool:
    if is_single_unit(r):
        return False
    depth = 0
    for c in r:
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '|' and depth == 0:
            return True
    return False

def split_top_level_or(r: str):
    if r == '':
        return ['']
    parts = []
    depth = 0
    current = []
    for c in r:
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        if c == '|' and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(c)
    parts.append("".join(current))
    return parts

def regex_union(r1: str, r2: str) -> str:
    if r1 is None: return r2
    if r2 is None: return r1
    if r1 == r2: return r1
    
    parts1 = split_top_level_or(r1)
    parts2 = split_top_level_or(r2)
    
    all_parts = []
    for p in parts1 + parts2:
        if p not in all_parts:
            all_parts.append(p)
            
    return "|".join(all_parts)

def regex_concat(r1: str, r2: str) -> str:
    if r1 is None or r2 is None:
        return None
    if r1 == '':
        return r2
    if r2 == '':
        return r1
        
    p1 = f"({r1})" if needs_parens_concat(r1) else r1
    p2 = f"({r2})" if needs_parens_concat(r2) else r2
    return f"{p1}{p2}"

def regex_star(r: str) -> str:
    if r is None:
        return ''
    if r == '':
        return ''
    if r.endswith('*') and is_single_unit(r):
        return r
    if is_single_unit(r):
        return f"{r}*"
    return f"({r})*"

def dfa_to_regex(dfa: DFA) -> str:
    s_new = "s_new"
    a_new = "a_new"
    
    gnfa_states = set(dfa.states) | {s_new, a_new}
    transitions = {}
    
    for (src, c), dst in dfa.transitions.items():
        if (src, dst) in transitions:
            transitions[(src, dst)] = regex_union(transitions[(src, dst)], c)
        else:
            transitions[(src, dst)] = c
            
    transitions[(s_new, dfa.start_state)] = ''
    for acc in dfa.accept_states:
        if (acc, a_new) in transitions:
            transitions[(acc, a_new)] = regex_union(transitions[(acc, a_new)], '')
        else:
            transitions[(acc, a_new)] = ''
            
    # Standardize elimination order slightly to make debugging easier.
    eliminate_order = sorted(list(dfa.states))
    
    for q_mid in eliminate_order:
        in_states = [s for s in gnfa_states if (s, q_mid) in transitions and s != q_mid]
        out_states = [s for s in gnfa_states if (q_mid, s) in transitions and s != q_mid]
        
        R_mid_mid = transitions.get((q_mid, q_mid), None)
        R_mid_mid_star = regex_star(R_mid_mid)
        
        for q_in in in_states:
            for q_out in out_states:
                R_in_mid = transitions[(q_in, q_mid)]
                R_mid_out = transitions[(q_mid, q_out)]
                
                path_regex = regex_concat(regex_concat(R_in_mid, R_mid_mid_star), R_mid_out)
                
                if (q_in, q_out) in transitions:
                    transitions[(q_in, q_out)] = regex_union(transitions[(q_in, q_out)], path_regex)
                else:
                    transitions[(q_in, q_out)] = path_regex
                    
        gnfa_states.remove(q_mid)
        transitions = {k: v for k, v in transitions.items() if k[0] != q_mid and k[1] != q_mid}
        
    final_regex = transitions.get((s_new, a_new), None)
    if final_regex is None:
        return ""
    return final_regex

def run_tests():
    print("--- Testing State Elimination (DFA to Regex) ---")
    
    # DFA accepting strings over {a, b} ending in 'ab'
    dfa = DFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'a', 'b'},
        transitions={
            ('q0', 'a'): 'q1', ('q0', 'b'): 'q0',
            ('q1', 'a'): 'q1', ('q1', 'b'): 'q2',
            ('q2', 'a'): 'q1', ('q2', 'b'): 'q0'
        },
        start_state='q0',
        accept_states={'q2'}
    )
    
    regex = dfa_to_regex(dfa)
    print("DFA for strings ending in 'ab'.")
    print(f"Generated Regex: {regex}")
    print("This regex should be mathematically equivalent to (a|b)*ab.")
    
    # Testing a basic DFA that just accepts 'a'
    dfa2 = DFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'a'},
        transitions={
            ('q0', 'a'): 'q1',
            ('q1', 'a'): 'q2',
            ('q2', 'a'): 'q2'
        },
        start_state='q0',
        accept_states={'q1'}
    )
    print(f"\nRegex for 'a' only: {dfa_to_regex(dfa2)}")

if __name__ == '__main__':
    run_tests()