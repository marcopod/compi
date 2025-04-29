import unittest
from lark import UnexpectedInput
from BabyDuck import parser, ASTBuilder

class TestCompiler(unittest.TestCase):
    
    def parse_and_transform(self, code):
        tree = parser.parse(code)
        ast = ASTBuilder().transform(tree)
        return ast

    # --- 1. Pruebas de programas completos ---
    def test_programa_minimo(self):
        code = "program a; main {} end"
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    def test_programa_con_vars(self):
        code = "program b; var x: int; main {} end"
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    # --- 2. Declaraciones de variables ---
    def test_vars_tipo_int(self):
        code = "program a; var x, y: int; main {} end"
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    def test_vars_tipo_float(self):
        code = "program a; var a: float; main {} end"
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")


    # --- 3. Statements ---
    def test_asignacion(self):
        code = "program a; main { x = 5; } end"
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    def test_llamada_funcion(self):
        code = 'program a; main { foo(1, 2); } end'
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    def test_condicional_if_else(self):
        code = 'program a; main { if (x != y) {} else {} ; } end'
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    def test_ciclo_while(self):
        code = 'program a; main { while (x > 0) do {} ; } end'
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    # --- 4. Expresiones ---
    def test_expresion_aritmetica_simple(self):
        code = 'program a; main { x = x + y; } end'
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

    def test_expresion_aritmetica_anidada(self):
        code = 'program a; main { x = (x - 2) * 3; } end'
        ast = self.parse_and_transform(code)
        self.assertEqual(ast[0], "programa")

if __name__ == '__main__':
    unittest.main()
