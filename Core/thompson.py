from dataclasses import dataclass
from typing import Dict, Set, Tuple

from automata import NFA
from regex_parser import (
    ASTNode,
    LiteralNode,
    UnionNode,
    ConcatNode,
    StarNode,
    PlusNode,
    QuestionNode,
    EpsilonNode,
    parse
)


class StateCounter:
    def __init__(self):
        self.count = 0

    def next_state(self) -> str:
        s = f"q{self.count}"
        self.count += 1
        return s


@dataclass
class NFAFragment:
    start_state: str
    accept_state: str
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], Set[str]]


def thompson(node: ASTNode, counter: StateCounter = None) -> NFAFragment:
    if counter is None:
        counter = StateCounter()

    if isinstance(node, EpsilonNode):
        start = counter.next_state()
        accept = counter.next_state()
        return NFAFragment(
            start_state=start,
            accept_state=accept,
            states={start, accept},
            alphabet=set(),
            transitions={(start, ''): {accept}}
        )

    elif isinstance(node, LiteralNode):
        start = counter.next_state()
        accept = counter.next_state()
        return NFAFragment(
            start_state=start,
            accept_state=accept,
            states={start, accept},
            alphabet={node.char},
            transitions={(start, node.char): {accept}}
        )

    elif isinstance(node, UnionNode):
        left_nfa = thompson(node.left, counter)
        right_nfa = thompson(node.right, counter)
        
        start = counter.next_state()
        accept = counter.next_state()
        
        states = {start, accept} | left_nfa.states | right_nfa.states
        alphabet = left_nfa.alphabet | right_nfa.alphabet
        
        transitions = {}
        for (s, c), dests in left_nfa.transitions.items():
            transitions[(s, c)] = set(dests)
        for (s, c), dests in right_nfa.transitions.items():
            if (s, c) in transitions:
                transitions[(s, c)].update(dests)
            else:
                transitions[(s, c)] = set(dests)
                
        transitions[(start, '')] = {left_nfa.start_state, right_nfa.start_state}
        transitions[(left_nfa.accept_state, '')] = {accept}
        transitions[(right_nfa.accept_state, '')] = {accept}
        
        return NFAFragment(start, accept, states, alphabet, transitions)

    elif isinstance(node, ConcatNode):
        left_nfa = thompson(node.left, counter)
        right_nfa = thompson(node.right, counter)
        
        states = left_nfa.states | right_nfa.states
        alphabet = left_nfa.alphabet | right_nfa.alphabet
        
        transitions = {}
        for (s, c), dests in left_nfa.transitions.items():
            transitions[(s, c)] = set(dests)
        for (s, c), dests in right_nfa.transitions.items():
            if (s, c) in transitions:
                transitions[(s, c)].update(dests)
            else:
                transitions[(s, c)] = set(dests)
                
        if (left_nfa.accept_state, '') in transitions:
            transitions[(left_nfa.accept_state, '')].add(right_nfa.start_state)
        else:
            transitions[(left_nfa.accept_state, '')] = {right_nfa.start_state}
            
        return NFAFragment(left_nfa.start_state, right_nfa.accept_state, states, alphabet, transitions)

    elif isinstance(node, StarNode):
        child_nfa = thompson(node.child, counter)
        
        start = counter.next_state()
        accept = counter.next_state()
        
        states = {start, accept} | child_nfa.states
        alphabet = child_nfa.alphabet
        
        transitions = {}
        for (s, c), dests in child_nfa.transitions.items():
            transitions[(s, c)] = set(dests)
            
        transitions[(start, '')] = {child_nfa.start_state, accept}
        if (child_nfa.accept_state, '') in transitions:
            transitions[(child_nfa.accept_state, '')].update({child_nfa.start_state, accept})
        else:
            transitions[(child_nfa.accept_state, '')] = {child_nfa.start_state, accept}
            
        return NFAFragment(start, accept, states, alphabet, transitions)

    elif isinstance(node, PlusNode):
        child_nfa = thompson(node.child, counter)
        
        start = counter.next_state()
        accept = counter.next_state()
        
        states = {start, accept} | child_nfa.states
        alphabet = child_nfa.alphabet
        
        transitions = {}
        for (s, c), dests in child_nfa.transitions.items():
            transitions[(s, c)] = set(dests)
            
        transitions[(start, '')] = {child_nfa.start_state}
        if (child_nfa.accept_state, '') in transitions:
            transitions[(child_nfa.accept_state, '')].update({child_nfa.start_state, accept})
        else:
            transitions[(child_nfa.accept_state, '')] = {child_nfa.start_state, accept}
            
        return NFAFragment(start, accept, states, alphabet, transitions)

    elif isinstance(node, QuestionNode):
        child_nfa = thompson(node.child, counter)
        
        start = counter.next_state()
        accept = counter.next_state()
        
        states = {start, accept} | child_nfa.states
        alphabet = child_nfa.alphabet
        
        transitions = {}
        for (s, c), dests in child_nfa.transitions.items():
            transitions[(s, c)] = set(dests)
            
        transitions[(start, '')] = {child_nfa.start_state, accept}
        if (child_nfa.accept_state, '') in transitions:
            transitions[(child_nfa.accept_state, '')].add(accept)
        else:
            transitions[(child_nfa.accept_state, '')] = {accept}
            
        return NFAFragment(start, accept, states, alphabet, transitions)

    raise ValueError(f"Unknown AST node type: {type(node)}")


def regex_to_nfa(regex_str: str) -> NFA:
    ast = parse(regex_str)
    frag = thompson(ast)
    return NFA(
        states=frag.states,
        alphabet=frag.alphabet,
        transitions=frag.transitions,
        start_state=frag.start_state,
        accept_states={frag.accept_state}
    )


def run_tests():
    print("--- Testing Thompson's Construction ---")
    test_nfa = regex_to_nfa('(a|b)*abb')
    print("Testing '(a|b)*abb' NFA:")
    
    assert test_nfa.accepts('aabb') is True
    print("'aabb' -> accepted")
    assert test_nfa.accepts('babb') is True
    print("'babb' -> accepted")
    assert test_nfa.accepts('ab') is False
    print("'ab' -> rejected")
    
    print("All tests passed!")


if __name__ == '__main__':
    run_tests()
