def infix_to_postfix(infix):
    # Función para insertar explícitamente el operador de concatenación.
    def add_concatenation(exp):
        result = ""
        operators = set(['|', '*', '(', ')'])
        for i in range(len(exp)):
            c1 = exp[i]
            result += c1
            if i + 1 < len(exp):
                c2 = exp[i + 1]
                # Si c1 no es '(', c2 no es ')' ni '|' ni '*' y c1 no es '|', se inserta concatenación.
                if c1 != '(' and c2 != ')' and c2 not in ['|', '*'] and c1 not in ['|']:
                    result += '.'
        return result

    # Precedencia de operadores
    precedence = {'*': 3, '.': 2, '|': 1}
    output = []
    stack = []
    # Insertar concatenación explícita
    exp = add_concatenation(infix)
    for token in exp:
        if token.isalnum():  # Operando (letra o dígito)
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            else:
                raise ValueError("Paréntesis desbalanceados")
        else:
            # token es operador: *, . o |
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(token, 0):
                output.append(stack.pop())
            stack.append(token)
    while stack:
        if stack[-1] == '(' or stack[-1] == ')':
            raise ValueError("Paréntesis desbalanceados")
        output.append(stack.pop())
    return "".join(output)
