import ply.lex as lex
import ply.yacc as yacc

# Lista de tokens (SOLO SUMAR NUMEROS)
tokens = (
    'NUMERO',
    'MAS'
)

# Reglas de expresión regular para sumas
t_MAS = r'\+'

# Regla para números (enteros o decimales)
def t_NUMERO(t):
    r'\d+(\.\d+)?'
    try:
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
    except ValueError:
        print("Valor numérico incorrecto %s" % t.value)
        t.value = 0
    return t

# Ignorar espacios y tabs
t_ignore  = ' \t'

# Manejador de errores léxicos
def t_error(t):
    print("Caracter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

##########
# Parser
##########

# Precedencia para los operadores
precedence = (
    ('left', 'MAS',),
)

# Regla inicial: expresión
def p_expresion(p):
    '''
    expresion : expresion MAS expresion
    '''
    if p[2] == '+':
        p[0] = p[1] + p[3]

# Regla para manejar números
def p_expresion_numero(p):
    'expresion : NUMERO'
    p[0] = p[1]

# Regla para manejar errores sintácticos
def p_error(p):
    if p:
        print("Error de sintaxis en '%s'" % p.value)
    else:
        print("Error de sintaxis al final de la entrada")

# Construir el parser
parser = yacc.yacc()

##########
# Analizador
##########

if __name__ == '__main__':
    try:
        while True:
            s = input('Calc > ')
            if not s:
                continue
            result = parser.parse(s)
            print("Resultado:", result)
    except EOFError:
        print("Fin del programa")
