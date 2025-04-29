from lark import Lark, Transformer, UnexpectedInput
from pprint import pprint # Para imprimir bonito


grammar = r"""
// ──────────── Ignore whitespace & newlines ────────────
%import common.WS_INLINE
%import common.NEWLINE
%import common.ESCAPED_STRING
%ignore WS_INLINE
%ignore NEWLINE

// ──────────── Terminals ────────────
PROGRAM: "program"
VAR:     "var"
MAIN:    "main"
VOID:    "void"
INT:     "int"
FLOAT:   "float"
WHILE:   "while"
DO:      "do"
END:     "end"
IF:      "if"
ELSE:    "else"
PRINT:   "print"

CTE_STRING: ESCAPED_STRING
CTE_FLOAT:  /\d+\.\d+/
CTE_INT:    /\d+/

ID: /[a-zA-Z_][a-zA-Z0-9_]*/

PLUS:      "+"
MINUS:     "-"
MULT:      "*"
DIV:       "/"
LT:        "<"
GT:        ">"
NEQ:       "!="
ASSIGN:    "="
SEMICOLON: ";"
COMMA:     ","
LPAREN:    "("
RPAREN:    ")"
LBRACE:    "{"
RBRACE:    "}"
COLON:     ":"

// ──────────── Grammar ────────────
?start: programa

programa: PROGRAM ID SEMICOLON vars funcs MAIN body END

vars: VAR ID (COMMA ID)* COLON tipo SEMICOLON vars
    | -> empty

tipo: INT | FLOAT

funcs: func*

func: VOID ID LPAREN param_list RPAREN vars body SEMICOLON

param_list: (ID COLON tipo (COMMA ID COLON tipo)*)?

body: LBRACE statement* RBRACE

statement: assign
    | print_stmt
    | f_call
    | condition
    | cycle

assign: ID ASSIGN expr SEMICOLON

print_stmt: PRINT LPAREN print_list RPAREN SEMICOLON
print_list: (expr | CTE_STRING) (COMMA (expr | CTE_STRING))*

f_call: ID LPAREN (expr (COMMA expr)*)? RPAREN SEMICOLON

condition: IF LPAREN expr RPAREN body (ELSE body)? SEMICOLON

cycle: WHILE LPAREN expr RPAREN DO body SEMICOLON

?expr: expr GT expr -> gt
    | expr LT expr -> lt
    | expr NEQ expr -> neq
    | sum

?sum: sum PLUS term -> add
    | sum MINUS term -> sub
    | term

?term: term MULT factor -> mul
    | term DIV factor  -> div
    | factor

?factor: LPAREN expr RPAREN -> group
    | PLUS factor -> pos
    | MINUS factor -> neg
    | ID
    | CTE_FLOAT -> float
    | CTE_INT -> int
"""

# Praser
parser = Lark(grammar, parser="lalr")

# Transformer para el AST
class ASTBuilder(Transformer):
    def ID(self, tok):         return str(tok)
    def CTE_INT(self, tok):    return int(tok)
    def CTE_FLOAT(self, tok):  return float(tok)
    def CTE_STRING(self, tok): return tok[1:-1].encode().decode('unicode_escape')

    def add(self, ch): return ("add", ch[0], ch[1])
    def sub(self, ch): return ("sub", ch[0], ch[1])
    def mul(self, ch): return ("mul", ch[0], ch[1])
    def div(self, ch): return ("div", ch[0], ch[1])
    def gt(self,  ch): return ("gt", ch[0], ch[1])
    def lt(self,  ch): return ("lt", ch[0], ch[1])
    def neq(self, ch): return ("neq", ch[0], ch[1])
    def pos(self, ch): return ch[0]
    def neg(self, ch): return ("neg", ch[0])
    def group(self, ch): return ch[0]

    def programa(self, ch):
        # ch = [ ID, vars, funcs, body ]
        return ("programa", ch)

    def assign(self, ch):
        # ch = [ ID, expr ]
        return ("assign", ch[0], ch[1])

    def print_stmt(self, ch):
        # ch = [ [items...] ]
        return ("print", ch[0])

    def print_list(self, ch):
        return ch

    def f_call(self, ch):
        # ch = [ ID, *args ]
        return ("call", ch[0], ch[1:])

    def condition(self, ch):
        # ch = [expr, body, (else_body?)]
        if len(ch)==3:
            return ("if", ch[0], ch[1], ch[2])
        return ("if", ch[0], ch[1])

    def cycle(self, ch):
        # ch = [expr, body]
        return ("while", ch[0], ch[1])

    def func(self, ch):
        # ch = [ ID, params?, vars, body ]
        return ("func", ch[0], ch[1], ch[2], ch[3])

def main():
    program_code = """program ejemplo;
    var x, y: int;
    void foo() {
        print("Hola", x + y);
    };
    main {
        x = 3;
        y = 4;
        foo();
    } end
    """

    try:
        tree = parser.parse(program_code)
        print(tree.pretty())
    except UnexpectedInput as e:
        print(f"Sintaxis inválida en línea {e.line}, columna {e.column}")
        return

    ast = ASTBuilder().transform(tree)
    pprint(ast, width=120)

if __name__ == "__main__":
    main()
