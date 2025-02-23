from shunting_yard import infix_to_postfix
from direct_dfa import DirectDFA
from dfa_minimization import minimize_dfa
from dfa_simulation import simulate_dfa
from nfa_simulation import simulate_nfa
from visual_automata import visualize_dfa, visualize_nfa

def main():
    regex_infix = "a|(b*ab)"  # Expresión regular en notación infix
    # Convertir infix a postfix
    regex_postfix = infix_to_postfix(regex_infix)
    
    # Construir el DFA directamente a partir de la expresión regular en postfix
    direct_dfa = DirectDFA(regex_postfix)
    dfa_dict = direct_dfa.build_dfa()
    
    # Minimizar el DFA
    min_dfa = minimize_dfa(dfa_dict)
    
    # Simular el DFA con una cadena de entrada
    input_string = "abab"  
    result_dfa = simulate_dfa(dfa_dict, input_string)
    result_min_dfa = simulate_dfa(min_dfa, input_string)
    
    # Para la simulación de AFN, se debe definir un AFN. 
    nfa_dict = {
        'states': {'q0', 'q1', 'q2'},
        'alphabet': {'a', 'b'},
        'transitions': {
            'q0': {'a': {'q0', 'q1'}, 'b': {'q0'}},
            'q1': {'b': {'q2'}},
            'q2': {}
        },
        'initial_state': 'q0',
        'final_states': {'q2'}
    }
    result_nfa = simulate_nfa(nfa_dict, input_string)
    
    # Generar visualizaciones
    visualize_dfa(dfa_dict, filename='dfa')
    visualize_dfa(min_dfa, filename='min_dfa')
    visualize_nfa(nfa_dict, filename='nfa')
    
    # Imprimir resultados de simulación
    print("Simulación DFA:", result_dfa)
    print("Simulación DFA minimizado:", result_min_dfa)
    print("Simulación NFA:", result_nfa)

if __name__ == "__main__":
    main()
