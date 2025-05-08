from lark import Transformer, Token, Tree
from semantic.variable_table import VariableTable
from semantic.function_directory import FunctionDirectory
from semantic.memory_manager import MemoryManager

class SemanticError(Exception):
    """Para errores semanticos."""
    pass

class SemanticAnalyzer(Transformer):
    def __init__(self):
        self.global_vars = VariableTable()
        self.func_dir = FunctionDirectory()
        # Contadores de direcciones por ambito y tipo
        self.memory = MemoryManager(base_offsets={
            'global': {'int': 0, 'float': 1000}, # ejemplo de offsets distintos
            'temp':   {'int': 5000, 'float': 6000},
        })
        self.current_function = None

    def _allocate_address(self, var_type: str) -> int:
        scope = self.current_function or 'global'
        return self.memory.allocate(scope, var_type)

    def programa(self, items):
        # [PROGRAM, ID, SEMICOLON, vars, funcs, MAIN, body, END]
        return items

    def vars(self, items):
        # Separar core de recursión
        if items and isinstance(items[-1], list):
            nested = items[-1]
            core   = items[:-1]
        else:
            nested = None
            core   = items

        # Extraer IDs y tipo
        ids, tipo = [], None
        for it in core:
            if isinstance(it, Token) and it.type == 'ID':
                ids.append(it.value)
            elif isinstance(it, Tree) and it.data == 'tipo':
                tipo = it.children[0].value # 'int' o 'float'

        # epsilon-case
        if tipo is None:
            return items

        # Registrar variables
        for name in ids:
            if self.current_function is None:
                if self.global_vars.has_variable(name):
                    raise SemanticError(f"Variable global '{name}' ya declarada.")
                addr = self._allocate_address(tipo)
                self.global_vars.add_variable(name, tipo, addr)
            else:
                func_entry = self.func_dir.get_function(self.current_function)
                if func_entry.variables.has_variable(name):
                    raise SemanticError(
                        f"Variable '{name}' ya declarada en funcion '{self.current_function}'."
                    )
                addr = self._allocate_address(tipo)
                func_entry.variables.add_variable(name, tipo, addr)

        return nested or []

    def param_list(self, items):
        """
        Devuelve lista de tuplas [(name, tipo), ...]
        items = [ID, COLON, tipo, (COMMA, ID, COLON, tipo)*]
        """
        params = []
        for i in range(0, len(items), 3):
            name = items[i].value
            tipo_node = items[i+2]
            if isinstance(tipo_node, Tree) and tipo_node.data == 'tipo':
                tipo = tipo_node.children[0].value
            else:
                tipo = items[i+2].value
            params.append((name, tipo))
        return params

    def func(self, items):
        # items = [VOID, ID(name), LPAREN, raw_params, RPAREN, vars, body, SEMICOLON]
        func_name  = items[1].value
        raw_params = items[3] or []

        if self.func_dir.has_function(func_name):
            raise SemanticError(f"Funcion '{func_name}' ya declarada.")

        # 1) Registrar funcion sin variables locales aun
        start_quad = 0  # luego lo ajustas con tu contador de cuadruplos
        self.func_dir.add_function(
            name=func_name,
            return_type='void',
            param_types=[t for (_, t) in raw_params],
            start_quad=start_quad
        )

        # 2) Cambiar de ambito
        self.current_function = func_name
        func_entry = self.func_dir.get_function(func_name)

        # 3) Registrar parametros EN ORDEN en la tabla local
        for name, tipo in raw_params:
            if func_entry.variables.has_variable(name):
                raise SemanticError(
                    f"Parametro '{name}' ya declarado en funcion '{func_name}'."
                )
            addr = self._allocate_address(tipo)
            func_entry.variables.add_variable(name, tipo, addr)

        return items

    def body(self, items):
        # Al salir de cualquier bloque, si estabamos en funcion, volvemos a global
        if self.current_function is not None:
            self.current_function = None
        return items