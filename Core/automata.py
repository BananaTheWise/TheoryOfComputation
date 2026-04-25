import json
from dataclasses import dataclass
from typing import Dict, Set, Tuple

import graphviz


@dataclass
class DFA:
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], str]
    start_state: str
    accept_states: Set[str]

    def accepts(self, s: str) -> bool:
        current = self.start_state
        for char in s:
            if (current, char) not in self.transitions:
                return False
            current = self.transitions[(current, char)]
        return current in self.accept_states

    def get_reachable_states(self) -> Set[str]:
        reachable = set()
        queue = [self.start_state]
        while queue:
            curr = queue.pop(0)
            if curr not in reachable:
                reachable.add(curr)
                for char in self.alphabet:
                    nxt = self.transitions.get((curr, char))
                    if nxt and nxt not in reachable:
                        queue.append(nxt)
        return reachable

    def minimize(self) -> 'DFA':
        reachable = self.get_reachable_states()
        states = reachable
        accept_states = self.accept_states & reachable

        # Initialize partition P
        non_accept = states - accept_states
        P = []
        if accept_states: P.append(accept_states)
        if non_accept: P.append(non_accept)

        W = list(P)

        while W:
            A = W.pop(0)
            for c in self.alphabet:
                X = {s for s in states if self.transitions.get((s, c)) in A}

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
                    else:
                        new_P.append(Y)
                P = new_P

        state_mapping = {}
        for part in P:
            rep = ",".join(sorted(part))
            for s in part:
                state_mapping[s] = rep

        new_states = set(state_mapping.values())
        new_start = state_mapping[self.start_state]
        new_accept = {state_mapping[s] for s in accept_states}
        new_transitions = {}
        
        for part in P:
            s = next(iter(part))
            rep = state_mapping[s]
            for c in self.alphabet:
                nxt = self.transitions.get((s, c))
                if nxt:
                    new_transitions[(rep, c)] = state_mapping[nxt]

        return DFA(
            states=new_states,
            alphabet=self.alphabet.copy(),
            transitions=new_transitions,
            start_state=new_start,
            accept_states=new_accept
        )

    def to_graphviz(self) -> graphviz.Digraph:
        dot = graphviz.Digraph(engine='dot')
        dot.attr(rankdir='LR')
        dot.node('start', shape='none', label='')

        for s in self.states:
            shape = 'doublecircle' if s in self.accept_states else 'circle'
            dot.node(s, shape=shape)

        dot.edge('start', self.start_state)

        for (src, symbol), dst in self.transitions.items():
            dot.edge(src, dst, label=symbol)

        return dot

    def to_dict(self) -> dict:
        return {
            "states": list(self.states),
            "alphabet": list(self.alphabet),
            "transitions": [{"state": k[0], "symbol": k[1], "next_state": v} for k, v in self.transitions.items()],
            "start_state": self.start_state,
            "accept_states": list(self.accept_states)
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'DFA':
        return cls(
            states=set(d["states"]),
            alphabet=set(d["alphabet"]),
            transitions={(t["state"], t["symbol"]): t["next_state"] for t in d["transitions"]},
            start_state=d["start_state"],
            accept_states=set(d["accept_states"])
        )


@dataclass
class NFA:
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], Set[str]]
    start_state: str
    accept_states: Set[str]

    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        closure = set(states)
        stack = list(states)
        while stack:
            s = stack.pop()
            eps_transitions = self.transitions.get((s, ''), set())
            for nxt in eps_transitions:
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return closure

    def accepts(self, s: str) -> bool:
        current = self.epsilon_closure({self.start_state})
        for char in s:
            next_states = set()
            for state in current:
                next_states.update(self.transitions.get((state, char), set()))
            current = self.epsilon_closure(next_states)
            if not current:
                return False
        return bool(current & self.accept_states)

    def to_dfa(self) -> DFA:
        start_closure = self.epsilon_closure({self.start_state})
        dfa_start = ",".join(sorted(start_closure))

        dfa_states = {dfa_start}
        dfa_transitions = {}
        dfa_accept = set()
        
        if start_closure & self.accept_states:
            dfa_accept.add(dfa_start)

        unmarked = [start_closure]
        marked = []

        def state_to_name(st):
            return ",".join(sorted(st)) if st else "TRAP"

        has_trap = False

        while unmarked:
            current_set = unmarked.pop(0)
            marked.append(current_set)
            current_name = state_to_name(current_set)

            for char in self.alphabet:
                next_set = set()
                for state in current_set:
                    next_set.update(self.transitions.get((state, char), set()))
                next_closure = self.epsilon_closure(next_set)
                next_name = state_to_name(next_closure)

                if not next_closure:
                    has_trap = True

                dfa_transitions[(current_name, char)] = next_name

                if next_closure not in marked and next_closure not in unmarked:
                    unmarked.append(next_closure)
                    dfa_states.add(next_name)
                    if next_closure & self.accept_states:
                        dfa_accept.add(next_name)

        if has_trap:
            dfa_states.add("TRAP")
            for char in self.alphabet:
                dfa_transitions[("TRAP", char)] = "TRAP"

        return DFA(
            states=dfa_states,
            alphabet=self.alphabet.copy(),
            transitions=dfa_transitions,
            start_state=dfa_start,
            accept_states=dfa_accept
        )

    def to_graphviz(self) -> graphviz.Digraph:
        dot = graphviz.Digraph(engine='dot')
        dot.attr(rankdir='LR')
        dot.node('start', shape='none', label='')

        for s in self.states:
            shape = 'doublecircle' if s in self.accept_states else 'circle'
            dot.node(s, shape=shape)

        dot.edge('start', self.start_state)

        for (src, symbol), dsts in self.transitions.items():
            label = symbol if symbol != '' else 'ε'
            for dst in dsts:
                dot.edge(src, dst, label=label)

        return dot

    def to_dict(self) -> dict:
        return {
            "states": list(self.states),
            "alphabet": list(self.alphabet),
            "transitions": [{"state": k[0], "symbol": k[1], "next_states": list(v)} for k, v in self.transitions.items()],
            "start_state": self.start_state,
            "accept_states": list(self.accept_states)
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'NFA':
        return cls(
            states=set(d["states"]),
            alphabet=set(d["alphabet"]),
            transitions={(t["state"], t["symbol"]): set(t["next_states"]) for t in d["transitions"]},
            start_state=d["start_state"],
            accept_states=set(d["accept_states"])
        )


def run_tests():
    print("Running Tests...")

    # --- DFA Tests ---
    # DFA Test 1: Accepts strings ending with '01'
    dfa1 = DFA(
        states={'q0', 'q1', 'q2'},
        alphabet={'0', '1'},
        transitions={
            ('q0', '0'): 'q1', ('q0', '1'): 'q0',
            ('q1', '0'): 'q1', ('q1', '1'): 'q2',
            ('q2', '0'): 'q1', ('q2', '1'): 'q0'
        },
        start_state='q0',
        accept_states={'q2'}
    )
    assert dfa1.accepts('1101') is True
    assert dfa1.accepts('000') is False
    assert dfa1.accepts('01') is True
    print("DFA Test 1 passed!")

    # DFA Test 2: JSON Serialization/Deserialization
    d1_dict = dfa1.to_dict()
    dfa1_copy = DFA.from_dict(d1_dict)
    assert dfa1_copy.accepts('1101') is True
    assert dfa1_copy.states == dfa1.states
    print("DFA Test 2 passed!")

    # DFA Test 3: Minimization
    dfa2 = DFA(
        states={'A', 'B', 'C', 'D'},
        alphabet={'a'},
        transitions={
            ('A', 'a'): 'B',
            ('B', 'a'): 'C',
            ('C', 'a'): 'D',
            ('D', 'a'): 'A'
        },
        start_state='A',
        accept_states={'A', 'C'}
    )
    min_dfa2 = dfa2.minimize()
    assert len(min_dfa2.states) == 2
    assert min_dfa2.accepts('aa') is True
    assert min_dfa2.accepts('aaa') is False
    print("DFA Test 3 passed!")

    # --- NFA Tests ---
    # NFA Test 1: Contains '101'
    nfa1 = NFA(
        states={'q0', 'q1', 'q2', 'q3'},
        alphabet={'0', '1'},
        transitions={
            ('q0', '0'): {'q0'}, ('q0', '1'): {'q0', 'q1'},
            ('q1', '0'): {'q2'},
            ('q2', '1'): {'q3'},
            ('q3', '0'): {'q3'}, ('q3', '1'): {'q3'}
        },
        start_state='q0',
        accept_states={'q3'}
    )
    assert nfa1.accepts('0010100') is True
    assert nfa1.accepts('11100') is False
    print("NFA Test 1 passed!")

    # NFA Test 2: Epsilon transitions
    nfa2 = NFA(
        states={'A', 'B', 'C'},
        alphabet={'0'},
        transitions={
            ('A', ''): {'B'},
            ('B', '0'): {'C'},
            ('C', ''): {'A'}
        },
        start_state='A',
        accept_states={'C'}
    )
    assert nfa2.accepts('0') is True
    assert nfa2.accepts('00') is True
    assert nfa2.accepts('') is False
    print("NFA Test 2 passed!")

    # NFA Test 3: Subset Construction (to_dfa)
    dfa_from_nfa1 = nfa1.to_dfa()
    assert dfa_from_nfa1.accepts('0010100') is True
    assert dfa_from_nfa1.accepts('11100') is False
    print("NFA Test 3 passed!")
    
    print("All tests passed successfully!")

if __name__ == '__main__':
    run_tests()