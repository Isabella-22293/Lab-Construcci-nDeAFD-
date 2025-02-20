#Generación visual de autómatas 
#Se pueden generar visualizaciones para AFD y AFN.

from graphviz import Digraph

def visualize_dfa(dfa_dict, filename='dfa'):
    """Genera una visualización del AFD y la guarda en un archivo (por defecto, 'dfa.pdf')."""
    dot = Digraph(comment='DFA')
    # Convertir estados a cadenas para etiquetado
    state_labels = {}
    for state in dfa_dict['states']:
        if isinstance(state, frozenset):
            label = "{" + ",".join(map(str, sorted(state))) + "}"
        else:
            label = str(state)
        state_labels[state] = label
        shape = 'doublecircle' if state in dfa_dict['final_states'] else 'circle'
        dot.node(label, shape=shape)
    # Nodo de inicio invisible
    dot.node('', shape='none')
    dot.edge('', state_labels[dfa_dict['initial_state']])
    # Agregar transiciones
    for (state, symbol), next_state in dfa_dict['transitions'].items():
        dot.edge(state_labels[state], state_labels[next_state], label=symbol)
    dot.render(filename, format='pdf', cleanup=True)

def visualize_nfa(nfa_dict, filename='nfa'):
    """Genera una visualización del AFN y la guarda en un archivo (por defecto, 'nfa.pdf')."""
    dot = Digraph(comment='NFA')
    # Nodos: se asume que los estados ya son cadenas
    for state in nfa_dict['states']:
        shape = 'doublecircle' if state in nfa_dict['final_states'] else 'circle'
        dot.node(state, shape=shape)
    # Nodo de inicio invisible
    dot.node('', shape='none')
    dot.edge('', nfa_dict['initial_state'])
    # Agregar transiciones: nfa_dict['transitions'] es un dict: estado -> dict (símbolo -> conjunto de estados)
    for state, trans in nfa_dict['transitions'].items():
        for symbol, targets in trans.items():
            for target in targets:
                dot.edge(state, target, label=symbol)
    dot.render(filename, format='pdf', cleanup=True)
