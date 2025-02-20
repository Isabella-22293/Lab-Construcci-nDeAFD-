from automata.fa.nfa import NFA

def simulate_nfa(nfa_dict, input_string):
    nfa = NFA(
        states=nfa_dict['states'],
        input_symbols=nfa_dict['alphabet'],
        transitions=nfa_dict['transitions'],
        initial_state=nfa_dict['initial_state'],
        final_states=nfa_dict['final_states']
    )
    return nfa.accepts_input(input_string)
