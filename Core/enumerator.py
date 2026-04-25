from typing import Generator, List, Callable, Optional
from Core.automata import DFA
from collections import deque

MAX_STATES_VISITED = 100000
MAX_STRING_LENGTH = 50

def enumerate_strings(
    dfa: DFA, 
    max_length: int, 
    on_progress: Optional[Callable[[int], None]] = None
) -> List[str]:
    """Generates all accepted strings up to a given length. Ordered by length, then lexicographically."""
    return list(enumerate_strings_lazy(dfa, max_length, on_progress))

def enumerate_strings_lazy(dfa, max_length, on_progress=None):
    count = 0

    if dfa.start_state in dfa.accept_states:
        count += 1
        if on_progress:
            on_progress(count)
        yield ""

    # Precompute states that can reach an accept state
    # This prevents the enumerator from infinitely exploring TRAP states 
    # (states from which no accept state is reachable) and causing memory explosions.
    live_states = set(dfa.accept_states)
    changed = True
    visited_size = 0
    while changed:
        changed = False
        visited_size += 1
        if visited_size > MAX_STATES_VISITED:
            raise RuntimeError("Graph explosion detected")
        for s in dfa.states:
            if s not in live_states:
                for c in dfa.alphabet:
                    if dfa.transitions.get((s, c)) in live_states:
                        live_states.add(s)
                        changed = True
                        break

    if dfa.start_state not in live_states:
        return

    queue = deque([(dfa.start_state, "")])
    sorted_alphabet = sorted(list(dfa.alphabet))
    states_visited = 0

    while queue:
        states_visited += 1
        if states_visited > MAX_STATES_VISITED:
            raise RuntimeError("Graph explosion detected")

        curr_state, curr_str = queue.popleft()

        # Stop infinite growth
        if len(curr_str) >= max_length or len(curr_str) >= MAX_STRING_LENGTH:
            continue

        for ch in sorted_alphabet:
            next_state = dfa.transitions.get((curr_state, ch))
            
            # Skip invalid transitions or trap states
            if next_state is None or next_state not in live_states:
                continue

            next_str = curr_str + ch
            queue.append((next_state, next_str))

            if next_state in dfa.accept_states:
                count += 1
                if on_progress:
                    on_progress(count)
                yield next_str

def count_strings(dfa: DFA, exact_length: int) -> int:
    """Returns exact count of accepted strings of a specific length using DP."""
    if exact_length == 0:
        return 1 if dfa.start_state in dfa.accept_states else 0

    # dp[length][state] = number of paths of `length` ending at `state`
    dp = {q: 0 for q in dfa.states}
    dp[dfa.start_state] = 1

    for _ in range(exact_length):
        next_dp = {q: 0 for q in dfa.states}
        for q in dfa.states:
            if dp[q] > 0:
                for a in dfa.alphabet:
                    nxt = dfa.transitions.get((q, a))
                    if nxt:
                        next_dp[nxt] += dp[q]
        dp = next_dp

    return sum(dp[q] for q in dfa.accept_states)

def run_tests():
    print("--- Testing DFA Enumerator ---")
    
    # DFA accepting strings ending in 'b' over {a, b}
    dfa = DFA(
        states={'q0', 'q1'},
        alphabet={'a', 'b'},
        transitions={
            ('q0', 'a'): 'q0', ('q0', 'b'): 'q1',
            ('q1', 'a'): 'q0', ('q1', 'b'): 'q1'
        },
        start_state='q0',
        accept_states={'q1'}
    )
    
    max_len = 3
    print(f"Enumerating strings up to length {max_len}...")
    
    strings = enumerate_strings(dfa, max_len)
    print(f"Found strings: {strings}")
    
    expected = ['b', 'ab', 'bb', 'aab', 'abb', 'bab', 'bbb']
    assert strings == expected, f"Expected {expected}, got {strings}"
    print("Enumeration test passed!")
    
    print("\nTesting exact string counting (DP)...")
    count_len_3 = count_strings(dfa, 3)
    print(f"Count of length 3 accepted strings: {count_len_3}")
    assert count_len_3 == 4, f"Expected 4 (aab, abb, bab, bbb), got {count_len_3}"
    print("String counting test passed!")

if __name__ == '__main__':
    run_tests()