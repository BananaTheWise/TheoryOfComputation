from Core.automata import NFA, DFA
from Core.thompson import regex_to_nfa

def subset_construction(nfa: NFA, trace: bool = False) -> DFA:
    # 1. Start state = epsilon_closure({nfa.start_state})
    start_set = frozenset(nfa.epsilon_closure({nfa.start_state}))
    
    # 2. Each DFA state = a frozenset of NFA states
    # 5. Name DFA states as 'q0', 'q1', ... in discovery order
    dfa_states_map = {start_set: 'q0'}
    unprocessed = [start_set]
    
    dfa_transitions = {}
    
    if trace:
        print("--- Subset Construction Trace ---")
        print(f"Initial start state closure: {set(start_set)} -> q0")
        
    # 3. For each unprocessed DFA state and each alphabet symbol:
    while unprocessed:
        curr_set = unprocessed.pop(0)
        curr_name = dfa_states_map[curr_set]
        
        if trace:
            print(f"\nProcessing DFA state {curr_name} (NFA states: {set(curr_set)})")
            
        for c in nfa.alphabet:
            # Compute move(state_set, symbol)
            move_set = set()
            for s in curr_set:
                move_set.update(nfa.transitions.get((s, c), set()))
                
            # Apply epsilon_closure to get the next DFA state
            next_set = frozenset(nfa.epsilon_closure(move_set))
            
            if not next_set:
                # If you want to skip trap states or add an explicit trap state.
                # Usually standard DFA requires a trap state if there's no transition.
                # We will just add an explicit TRAP state.
                next_set = frozenset({'TRAP'})
                
            if next_set not in dfa_states_map:
                new_name = f'q{len(dfa_states_map)}'
                dfa_states_map[next_set] = new_name
                unprocessed.append(next_set)
                if trace:
                    print(f"  On '{c}', move to new state {new_name} (NFA states: {set(next_set)})")
            else:
                if trace:
                    print(f"  On '{c}', move to existing state {dfa_states_map[next_set]}")
                    
            dfa_transitions[(curr_name, c)] = dfa_states_map[next_set]

    # Explicit TRAP state handling
    trap_set = frozenset({'TRAP'})
    if trap_set in dfa_states_map:
        trap_name = dfa_states_map[trap_set]
        for c in nfa.alphabet:
            dfa_transitions[(trap_name, c)] = trap_name

    # 4. A DFA state is accepting if it contains any NFA accept state
    dfa_states = set(dfa_states_map.values())
    dfa_start_state = dfa_states_map[start_set]
    dfa_accept_states = {
        name for state_set, name in dfa_states_map.items() 
        if state_set & nfa.accept_states
    }
    
    if trace:
        print("\n--- Final DFA ---")
        print(f"States: {dfa_states}")
        print(f"Start State: {dfa_start_state}")
        print(f"Accept States: {dfa_accept_states}")
        print("Transitions:")
        for (s, c), nxt in dfa_transitions.items():
            print(f"  {s} --{c}--> {nxt}")

    return DFA(
        states=dfa_states,
        alphabet=nfa.alphabet.copy(),
        transitions=dfa_transitions,
        start_state=dfa_start_state,
        accept_states=dfa_accept_states
    )


def trace(nfa: NFA) -> DFA:
    """A worked trace function that prints each step of subset construction."""
    return subset_construction(nfa, trace=True)


def dfa_minimize(dfa: DFA, trace: bool = False) -> DFA:
    # Hopcroft's partition refinement algorithm
    # 1. Get reachable states
    reachable = set()
    queue = [dfa.start_state]
    while queue:
        curr = queue.pop(0)
        if curr not in reachable:
            reachable.add(curr)
            for c in dfa.alphabet:
                nxt = dfa.transitions.get((curr, c))
                if nxt and nxt not in reachable:
                    queue.append(nxt)
                    
    states = reachable
    accept_states = dfa.accept_states & reachable
    non_accept = states - accept_states
    
    # 2. Initial Partition
    P = []
    if accept_states: P.append(frozenset(accept_states))
    if non_accept: P.append(frozenset(non_accept))
    
    W = list(P)
    
    if trace:
        print("\n--- DFA Minimization Trace ---")
        print(f"Initial partition: {[set(p) for p in P]}")
        
    while W:
        A = W.pop(0)
        if trace:
            print(f"\nProcessing set A: {set(A)}")
        for c in dfa.alphabet:
            # X = set of states that transition to A on symbol c
            X = frozenset(s for s in states if dfa.transitions.get((s, c)) in A)
            if not X:
                continue
            
            new_P = []
            for Y in P:
                intersection = Y & X
                difference = Y - X
                if intersection and difference:
                    new_P.append(intersection)
                    new_P.append(difference)
                    if Y in W:
                        W.remove(Y)
                        W.append(intersection)
                        W.append(difference)
                    else:
                        if len(intersection) <= len(difference):
                            W.append(intersection)
                        else:
                            W.append(difference)
                    if trace:
                        print(f"  Split {set(Y)} into {set(intersection)} and {set(difference)} on symbol '{c}'")
                else:
                    new_P.append(Y)
            P = new_P

    state_mapping = {}
    for i, part in enumerate(P):
        rep = f"p{i}"
        for s in part:
            state_mapping[s] = rep

    new_states = set(state_mapping.values())
    new_start = state_mapping[dfa.start_state]
    new_accept = {state_mapping[s] for s in accept_states}
    new_transitions = {}
    for s in states:
        for c in dfa.alphabet:
            nxt = dfa.transitions.get((s, c))
            if nxt:
                new_transitions[(state_mapping[s], c)] = state_mapping[nxt]

    if trace:
        print("\n--- Minimized DFA ---")
        print(f"Final states: {new_states}")
        
    return DFA(
        states=new_states,
        alphabet=dfa.alphabet.copy(),
        transitions=new_transitions,
        start_state=new_start,
        accept_states=new_accept
    )


def run_tests():
    print("Converting NFA for '(a|b)*abb' to DFA using subset construction...")
    
    # Using the thompson construction from previous steps
    nfa = regex_to_nfa('(a|b)*abb')
    
    # 1. Test Subset Construction Trace
    dfa = trace(nfa)
    
    # 2. Verify DFA correctly accepts and rejects
    assert dfa.accepts('aabb') is True, "DFA failed to accept 'aabb'"
    assert dfa.accepts('babb') is True, "DFA failed to accept 'babb'"
    assert dfa.accepts('ab') is False, "DFA failed to reject 'ab'"
    print("\nSubset Construction tests passed! ('aabb', 'babb' accepted; 'ab' rejected)")

    # 3. Test Minimization
    min_dfa = dfa_minimize(dfa, trace=True)
    assert min_dfa.accepts('aabb') is True
    assert min_dfa.accepts('babb') is True
    assert min_dfa.accepts('ab') is False
    print("\nDFA Minimization tests passed!")


if __name__ == '__main__':
    run_tests()
