from automata.fa.dfa import DFA

def _state_to_str(state):
    """Convierte un estado (por ejemplo, un frozenset) a una representación de cadena."""
    if isinstance(state, frozenset):
        return "{" + ",".join(map(str, sorted(state))) + "}"
    return str(state)

def minimize_dfa(dfa_dict):
    # Crear un mapeo consistente de cada estado original a su representación en cadena.
    state_map = {}
    # Agregar los estados que ya están en dfa_dict['states']
    for state in dfa_dict['states']:
        state_map[state] = _state_to_str(state)
    # Asegurarse de incluir en el mapeo aquellos estados que aparecen en las transiciones
    for (origin, symbol), dest in dfa_dict['transitions'].items():
        if origin not in state_map:
            state_map[origin] = _state_to_str(origin)
        if dest not in state_map:
            state_map[dest] = _state_to_str(dest)
    
    # El conjunto de todos los estados (en forma de cadena)
    all_states = set(state_map.values())
    
    # Construir el diccionario de transiciones usando el mapeo creado
    new_transitions = {}
    for (origin, symbol), dest in dfa_dict['transitions'].items():
        origin_str = state_map[origin]
        dest_str = state_map[dest]
        if origin_str not in new_transitions:
            new_transitions[origin_str] = {}
        new_transitions[origin_str][symbol] = dest_str
    
    # Completar el DFA para que sea total: para cada estado y cada símbolo debe existir una transición.
    # Se utiliza un estado sumidero "sink" para las transiciones faltantes.
    sink = "sink"
    all_states.add(sink)
    for state in all_states:
        if state not in new_transitions:
            new_transitions[state] = {}
        for symbol in dfa_dict['alphabet']:
            if symbol not in new_transitions[state]:
                new_transitions[state][symbol] = sink
    # El estado sink tiene transiciones a sí mismo para todo el alfabeto.
    new_transitions[sink] = { symbol: sink for symbol in dfa_dict['alphabet'] }
    
    # Definir el estado inicial y los estados finales usando el mapeo
    initial_state = state_map[dfa_dict['initial_state']]
    final_states = { state_map[s] for s in dfa_dict['final_states'] }
    
    # (Opcional) Imprimir para depuración:
    # print("Estados:", all_states)
    # print("Transiciones:")
    # for s, trans in new_transitions.items():
    #     print(f"  {s}: {trans}")
    
    # Crear el objeto DFA de automata-lib
    dfa_obj = DFA(
        states=all_states,
        input_symbols=dfa_dict['alphabet'],
        transitions=new_transitions,
        initial_state=initial_state,
        final_states=final_states
    )
    
    # Minimizar el DFA
    min_dfa_obj = dfa_obj.minify()
    
    # Convertir el DFA minimizado de vuelta a nuestro formato de diccionario
    minimized_dfa = {
        'states': min_dfa_obj.states,
        'alphabet': min_dfa_obj.input_symbols,
        'transitions': {
            (state, symbol): dest
            for state, trans in min_dfa_obj.transitions.items()
            for symbol, dest in trans.items()
        },
        'initial_state': min_dfa_obj.initial_state,
        'final_states': min_dfa_obj.final_states
    }
    return minimized_dfa
