import os
from lark import Lark

# Ruta al archivo BabyDuck.lark
GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "BabyDuck.lark")

# Carga la gramatica una sola vez
with open(GRAMMAR_PATH, 'r', encoding='utf-8') as f:
    _grammar = f.read()

# Crea y exporta el parser
parser = Lark(
    _grammar,
    parser="lalr",
    start="programa",
)
