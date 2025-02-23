class RegexNode:
    def __init__(self, node_type, left=None, right=None, symbol=None):
        self.type = node_type  # 'symbol', 'concat', 'union', 'star'
        self.left = left
        self.right = right
        self.symbol = symbol
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()
        self.position = None

def build_syntax_tree(postfix):
    #Construye el árbol sintáctico a partir de la expresión en postfix.
    stack = []
    for token in postfix:
        if token == '*':
            if stack:
                node = stack.pop()
                stack.append(RegexNode('star', left=node))
        elif token == '.':
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                stack.append(RegexNode('concat', left=left, right=right))
        elif token == '|':
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                stack.append(RegexNode('union', left=left, right=right))
        else:
            stack.append(RegexNode('symbol', symbol=token))
    return stack[0] if stack else None

def assign_positions(node, pos=1, pos_to_symbol=None):
    #Asigna números de posición a las hojas del árbol (símbolos) y crea un mapeo.
    if pos_to_symbol is None:
        pos_to_symbol = {}
    if node is None:
        return pos, pos_to_symbol
    if node.type == 'symbol':
        node.position = pos
        pos_to_symbol[pos] = node.symbol
        return pos + 1, pos_to_symbol
    if node.type in ('concat', 'union'):
        pos, pos_to_symbol = assign_positions(node.left, pos, pos_to_symbol)
        pos, pos_to_symbol = assign_positions(node.right, pos, pos_to_symbol)
    elif node.type == 'star':
        pos, pos_to_symbol = assign_positions(node.left, pos, pos_to_symbol)
    return pos, pos_to_symbol

def compute_nullable_first_last(node):
    #Calcula las propiedades nullable, firstpos y lastpos de cada nodo.
    if node is None:
        return
    if node.type == 'symbol':
        node.nullable = node.symbol == 'ε'
        node.firstpos = {node.position} if node.symbol != 'ε' else set()
        node.lastpos = {node.position} if node.symbol != 'ε' else set()
    elif node.type == 'union':
        compute_nullable_first_last(node.left)
        compute_nullable_first_last(node.right)
        node.nullable = node.left.nullable or node.right.nullable
        node.firstpos = node.left.firstpos | node.right.firstpos
        node.lastpos = node.left.lastpos | node.right.lastpos
    elif node.type == 'concat':
        compute_nullable_first_last(node.left)
        compute_nullable_first_last(node.right)
        node.nullable = node.left.nullable and node.right.nullable
        node.firstpos = node.left.firstpos | node.right.firstpos if node.left.nullable else node.left.firstpos
        node.lastpos = node.left.lastpos | node.right.lastpos if node.right.nullable else node.right.lastpos
    elif node.type == 'star':
        compute_nullable_first_last(node.left)
        node.nullable = True
        node.firstpos = node.left.firstpos
        node.lastpos = node.left.lastpos

def compute_followpos(node, followpos):
    #Calcula la función followpos para cada posición en el árbol.
    if node is None:
        return
    if node.type == 'concat':
        for pos in node.left.lastpos:
            followpos.setdefault(pos, set()).update(node.right.firstpos)
    elif node.type == 'star':
        for pos in node.lastpos:
            followpos.setdefault(pos, set()).update(node.firstpos)
    compute_followpos(node.left, followpos)
    compute_followpos(node.right, followpos)

def infix_to_postfix(infix):
    #Convierte una expresión regular en notación infix a postfix.
    def add_concatenation(regex):
        result = ""
        operators = {'|', '*', '(', ')'}
        for i in range(len(regex)):
            c1 = regex[i]
            result += c1
            if i + 1 < len(regex):
                c2 = regex[i + 1]
                if c1 != '(' and c2 != ')' and c2 not in operators and c1 not in {'|'}:
                    result += '.'
        return result
    
    regex = add_concatenation(infix)
    precedence = {'*': 3, '.': 2, '|': 1}
    output, stack = [], []
    for token in regex:
        if token.isalnum() or token == 'ε':
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(token, 0):
                output.append(stack.pop())
            stack.append(token)
    while stack:
        output.append(stack.pop())
    return "".join(output)

class DirectDFA:
    def __init__(self, regex_infix):
        self.regex_postfix = infix_to_postfix(regex_infix)
        self.augmented_postfix = self.regex_postfix + '#' + '.'
        self.dfa = None

    def build_dfa(self):
        root = build_syntax_tree(self.augmented_postfix)
        if root is None:
            return None
        _, pos_to_symbol = assign_positions(root)
        compute_nullable_first_last(root)
        followpos = {}
        compute_followpos(root, followpos)
        alphabet = {sym for pos, sym in pos_to_symbol.items() if sym not in {'#', 'ε'}}
        initial_state = frozenset(root.firstpos)
        states, unmarked_states, transitions, final_states = {initial_state}, [initial_state], {}, set()
        print("pos_to_symbol:", pos_to_symbol)
        end_marker_pos = next(pos for pos, sym in pos_to_symbol.items() if sym == '#')
        while unmarked_states:
            current = unmarked_states.pop()
            if end_marker_pos in current:
                final_states.add(current)
            for symbol in alphabet:
                next_state = {pos for pos in current if pos_to_symbol[pos] == symbol and followpos.get(pos)}
                next_state_frozen = frozenset(next_state)
                transitions[(current, symbol)] = next_state_frozen
                if next_state_frozen not in states:
                    states.add(next_state_frozen)
                    unmarked_states.append(next_state_frozen)
        self.dfa = {'states': states, 'alphabet': alphabet, 'transitions': transitions, 'initial_state': initial_state, 'final_states': final_states}
        return self.dfa
