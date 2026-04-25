from Core.automata import DFA, NFA

def dfa_to_cfg(dfa: DFA) -> dict:
    variables = {f"V_{q}" for q in dfa.states}
    terminals = set(dfa.alphabet)
    start = f"V_{dfa.start_state}"
    productions = {v: [] for v in variables}
    
    for (q, a), p in dfa.transitions.items():
        productions[f"V_{q}"].append(f"{a} V_{p}")
        
    for q in dfa.accept_states:
        productions[f"V_{q}"].append("")
        
    return {
        'variables': variables,
        'terminals': terminals,
        'start': start,
        'productions': productions
    }

def cfg_to_nfa(cfg: dict) -> NFA:
    states = set(cfg['variables'])
    alphabet = set(cfg['terminals'])
    start_state = cfg['start']
    accept_states = set()
    transitions = {}
    
    final_state = "F_acc"
    while final_state in states:
        final_state += "'"
    
    for var, prods in cfg['productions'].items():
        for prod in prods:
            if prod == "":
                accept_states.add(var)
            else:
                parts = prod.split()
                if len(parts) == 2:
                    a, B = parts
                    if (var, a) not in transitions:
                        transitions[(var, a)] = set()
                    transitions[(var, a)].add(B)
                    states.add(B)
                    alphabet.add(a)
                elif len(parts) == 1:
                    a = parts[0]
                    if (var, a) not in transitions:
                        transitions[(var, a)] = set()
                    transitions[(var, a)].add(final_state)
                    states.add(final_state)
                    accept_states.add(final_state)
                    alphabet.add(a)
                    
    return NFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start_state=start_state,
        accept_states=accept_states
    )

def cfg_to_string(cfg: dict) -> str:
    lines = []
    lines.append(f"Variables: {{ {', '.join(sorted(cfg['variables']))} }}")
    lines.append(f"Terminals: {{ {', '.join(sorted(cfg['terminals']))} }}")
    lines.append(f"Start: {cfg['start']}")
    lines.append("Productions:")
    for var in sorted(cfg['productions'].keys()):
        prods = cfg['productions'][var]
        if not prods:
            continue
        rhs_list = []
        for p in prods:
            if p == "":
                rhs_list.append("ε")
            else:
                rhs_list.append(p)
        lines.append(f"  {var} -> {' | '.join(rhs_list)}")
    return "\n".join(lines)

def run_tests():
    print("--- Testing DFA <-> CFG Conversion ---")
    
    # DFA for strings ending in 'ab'
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
    
    # 1. Convert DFA to CFG
    cfg = dfa_to_cfg(dfa)
    print("Generated CFG:")
    print(cfg_to_string(cfg))
    
    # 2. Convert CFG to NFA
    nfa = cfg_to_nfa(cfg)
    
    # 3. Convert NFA to DFA for comparison
    dfa_round_trip = nfa.to_dfa()
    
    test_strings = [
        "", "a", "b", "ab", "bab", "aab", "aba", "bbab", "abba"
    ]
    
    print("\nVerifying round-trip conversions (DFA -> CFG -> NFA -> DFA):")
    for s in test_strings:
        original_result = dfa.accepts(s)
        round_trip_result = dfa_round_trip.accepts(s)
        assert original_result == round_trip_result, f"Failed on string '{s}'. Original: {original_result}, Round Trip: {round_trip_result}"
        print(f"  '{s}': {round_trip_result}")
        
    print("\nAll tests passed successfully!")

if __name__ == '__main__':
    run_tests()