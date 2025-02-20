from automata.fa.dfa import DFA

def _state_to_str(state):
    if isinstance(state, frozenset):
        return "{" + ",".join(map(str, sorted(state))) + "}"
    return str(state)

def simulate_dfa(dfa_dict, input_string):
    # Convertir estados a cadena si es necesario
    state_map = {}
    for state in dfa_dict['states']:
        state_map[state] = _state_to_str(state)

    transitions = {}
    for (state, symbol), next_state in dfa_dict['transitions'].items():
        if state not in state_map or next_state not in state_map:
            print(f"Error: El estado {state} o {next_state} no está en state_map")
            continue  # Saltar esta transición problemática
        
        s_str = state_map[state]
        ns_str = state_map[next_state]

        if s_str not in transitions:
            transitions[s_str] = {}
        transitions[s_str][symbol] = ns_str

    initial_state = state_map[dfa_dict['initial_state']]
    final_states = {state_map[s] for s in dfa_dict['final_states']}

    dfa_obj = DFA(
        states=set(state_map.values()),
        input_symbols=dfa_dict['alphabet'],
        transitions=transitions,
        initial_state=initial_state,
        final_states=final_states
    )
    
    return dfa_obj.accepts_input(input_string)
