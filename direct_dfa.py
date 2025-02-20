class RegexNode:
    def __init__(self, type, left=None, right=None, symbol=None):
        self.type = type  # 'symbol', 'concat', 'union', 'star'
        self.left = left
        self.right = right
        self.symbol = symbol
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()
        self.position = None

def build_syntax_tree(postfix):
    stack = []
    for token in postfix:
        if token == '*':
            node = stack.pop()
            stack.append(RegexNode('star', left=node))
        elif token == '.':
            right = stack.pop()
            left = stack.pop()
            stack.append(RegexNode('concat', left=left, right=right))
        elif token == '|':
            right = stack.pop()
            left = stack.pop()
            stack.append(RegexNode('union', left=left, right=right))
        else:
            stack.append(RegexNode('symbol', symbol=token))
    return stack[0]

def assign_positions(node, pos=1, pos_to_symbol=None):
    if pos_to_symbol is None:
        pos_to_symbol = {}
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
    if node.type == 'symbol':
        node.nullable = False
        node.firstpos = {node.position}
        node.lastpos = {node.position}
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
        node.lastpos = node.right.lastpos | node.left.lastpos if node.right.nullable else node.right.lastpos
    elif node.type == 'star':
        compute_nullable_first_last(node.left)
        node.nullable = True
        node.firstpos = node.left.firstpos
        node.lastpos = node.left.lastpos

def compute_followpos(node, followpos):
    if node.type == 'concat':
        for pos in node.left.lastpos:
            followpos.setdefault(pos, set()).update(node.right.firstpos)
    if node.type == 'star':
        for pos in node.lastpos:
            followpos.setdefault(pos, set()).update(node.firstpos)
    if node.type in ('union', 'concat'):
        compute_followpos(node.left, followpos)
        compute_followpos(node.right, followpos)
    elif node.type == 'star':
        compute_followpos(node.left, followpos)

class DirectDFA:
    def __init__(self, regex_postfix):
        augmented = regex_postfix + '#' + '.'
        self.augmented_regex = augmented
        self.dfa = None

    def build_dfa(self):
        root = build_syntax_tree(self.augmented_regex)
        _, pos_to_symbol = assign_positions(root)
        compute_nullable_first_last(root)
        followpos = {}
        compute_followpos(root, followpos)
        alphabet = {sym for pos, sym in pos_to_symbol.items() if sym != '#'}
        states = set()
        transitions = {}
        initial_state = frozenset(root.firstpos)
        states.add(initial_state)
        unmarked_states = [initial_state]
        final_states = set()
        end_marker_pos = next(pos for pos, sym in pos_to_symbol.items() if sym == '#')

        while unmarked_states:
            current = unmarked_states.pop()
            if end_marker_pos in current:
                final_states.add(current)
            for symbol in alphabet:
                next_state = {pos for pos in current if pos_to_symbol[pos] == symbol for pos in followpos.get(pos, set())}
                if next_state:
                    next_state_frozen = frozenset(next_state)
                    transitions[(current, symbol)] = next_state_frozen
                    if next_state_frozen not in states:
                        states.add(next_state_frozen)
                        unmarked_states.append(next_state_frozen)

        self.dfa = {
            'states': states,
            'alphabet': alphabet,
            'transitions': transitions,
            'initial_state': initial_state,
            'final_states': final_states
        }
        print("Estados del DFA:", states)
        print("Transiciones del DFA:", transitions)
        print("Estado inicial:", initial_state)
        print("Estados finales:", final_states)
        return self.dfa