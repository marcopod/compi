# semantic/analyzer.py

from lark import Transformer, Token, Tree
from semantic.variable_table import VariableTable
from semantic.function_directory import FunctionDirectory
from semantic.memory_manager import MemoryManager
from semantic.semantic_cube import semantic_cube

class SemanticError(Exception):
    """Para errores semánticos."""
    pass

class SemanticAnalyzer(Transformer):
    def __init__(self):
        # — Tablas y memoria —
        self.global_vars      = VariableTable()
        self.func_dir         = FunctionDirectory()
        self.memory           = MemoryManager(base_offsets={
            'global': {'int':   0,    'float': 1000},
            'temp':   {'int': 5000,  'float': 6000},
            'const':  {'int': 2000,  'float': 3000},
        })
        self.current_function = None

        # — Pilas y lista de cuádruplos —
        self.operators   = []   # operadores pendientes
        self.operands    = []   # direcciones de operandos
        self.types       = []   # tipos de cada operando
        self.quadruples  = []   # fila de cuádruplos
        self.next_quad   = 0    # índice del próximo cuadruplo

    def _allocate_address(self, var_type: str) -> int:
        scope = self.current_function or 'global'
        return self.memory.allocate(scope, var_type)

    def _generate_quad(self, operator: str):
        # Saca op’s y tipos, chequea semantic_cube, reserva temp, encola cuadruplo
        op = self.operators.pop() if self.operators else operator
        r_addr = self.operands.pop()
        l_addr = self.operands.pop()
        r_type = self.types.pop()
        l_type = self.types.pop()

        res_type = semantic_cube[l_type][r_type][op]
        if res_type == 'error':
            raise SemanticError(f"Tipo inválido para {l_type} {op} {r_type}")

        temp = self._allocate_address(res_type)
        self.operands.append(temp)
        self.types.append(res_type)

        self.quadruples.append((op, l_addr, r_addr, temp))
        self.next_quad += 1

    # ————————————————————————————————————————————————
    # Captura de variables en expresiones: factor -> var
    # ————————————————————————————————————————————————
    def var(self, items):
        token = items[0]
        name = token.value

        if self.current_function:
            fe = self.func_dir.get_function(self.current_function)
            if fe.variables.has_variable(name):
                ve = fe.variables.get_variable(name)
            elif self.global_vars.has_variable(name):
                ve = self.global_vars.get_variable(name)
            else:
                raise SemanticError(f"Variable '{name}' no declarada.")
        else:
            if not self.global_vars.has_variable(name):
                raise SemanticError(f"Variable global '{name}' no declarada.")
            ve = self.global_vars.get_variable(name)

        self.operands.append(ve.address)
        self.types.append(ve.var_type)
        return ve.address

    # ————————————————————————————————————————————————
    # Constantes
    # ————————————————————————————————————————————————
    def CTE_INT(self, token: Token):
        addr = self.memory.allocate('const', 'int')
        self.operands.append(addr)
        self.types.append('int')
        return addr

    def CTE_FLOAT(self, token: Token):
        addr = self.memory.allocate('const', 'float')
        self.operands.append(addr)
        self.types.append('float')
        return addr

    # ————————————————————————————————————————————————
    # Operadores binarios y relacionales
    # ————————————————————————————————————————————————
    def add(self, items): self.operators.append('+'); self._generate_quad('+'); return self.operands[-1]
    def sub(self, items): self.operators.append('-'); self._generate_quad('-'); return self.operands[-1]
    def mul(self, items): self.operators.append('*'); self._generate_quad('*'); return self.operands[-1]
    def div(self, items): self.operators.append('/'); self._generate_quad('/'); return self.operands[-1]
    def gt(self,  items): self.operators.append('>'); self._generate_quad('>'); return self.operands[-1]
    def lt(self,  items): self.operators.append('<'); self._generate_quad('<'); return self.operands[-1]
    def neq(self, items): self.operators.append('!=' ); self._generate_quad('!='); return self.operands[-1]

    def group(self, items): return items[0]
    def pos(self,   items): return items[0]
    def neg(self,   items):
        zero = self.memory.allocate('const','int')
        self.operands.append(zero); self.types.append('int')
        self.operators.append('-'); self._generate_quad('-')
        return self.operands[-1]

    # ————————————————————————————————————————————————
    # Asignación
    # ————————————————————————————————————————————————
    def assign(self, items):
        expr_addr = self.operands.pop()
        expr_type = self.types.pop()

        id_token = items[0]
        name = id_token.value
        if self.current_function:
            fe = self.func_dir.get_function(self.current_function)
            if fe.variables.has_variable(name):
                ve = fe.variables.get_variable(name)
            elif self.global_vars.has_variable(name):
                ve = self.global_vars.get_variable(name)
            else:
                raise SemanticError(f"Variable '{name}' no declarada.")
        else:
            if not self.global_vars.has_variable(name):
                raise SemanticError(f"Variable global '{name}' no declarada.")
            ve = self.global_vars.get_variable(name)

        res_t = semantic_cube[ve.var_type][expr_type]['=']
        if res_t == 'error':
            raise SemanticError(f"No se puede asignar {expr_type} a {ve.var_type}")

        self.quadruples.append(('=', expr_addr, None, ve.address))
        self.next_quad += 1
        return None

    # ————————————————————————————————————————————————
    # Print
    # ————————————————————————————————————————————————
    def CTE_STRING(self, token: Token):
        # Devuelve el literal con comillas
        return token.value

    def print_list(self, items):
        # items es lista de resultados de expr o CTE_STRING
        return items

    def print_stmt(self, items):
        # items incluye tokens PRINT, LPAREN, la lista de args, RPAREN y SEMICOLON
        # Extraemos sólo la lista (el único elemento de tipo list)
        args = next((x for x in items if isinstance(x, list)), [])
        for elem in args:
            self.quadruples.append(('print', elem, None, None))
            self.next_quad += 1
        return None

    # ————————————————————————————————————————————————
    # Llamada a funciones
    # ————————————————————————————————————————————————
    def f_call(self, items):
        """
        Genera:
          ERA func_name
          PARAM addr, None, param_index
          GOSUB start_quad
        """
        # 1) Nombre de la función
        name_token = items[0]
        fname = name_token.value
        if not self.func_dir.has_function(fname):
            raise SemanticError(f"Función '{fname}' no declarada.")
        fe = self.func_dir.get_function(fname)

        # 2) Filtrar sólo argumentos reales (enteros para direcciones)
        arg_items = [i for i in items[1:] if isinstance(i, int)]
        actual_count   = len(arg_items)
        expected_count = len(fe.param_types)
        if actual_count != expected_count:
            raise SemanticError(
                f"Número incorrecto de argumentos para '{fname}': "
                f"esperados {expected_count}, recibidos {actual_count}."
            )

        # 3) Pop de pilas (en orden inverso) para direcciones y tipos
        actual_addrs = [self.operands.pop() for _ in range(actual_count)][::-1]
        actual_types = [self.types.pop()     for _ in range(actual_count)][::-1]

        # 4) ERA
        self.quadruples.append(('ERA', None, None, fname))
        self.next_quad += 1

        # 5) PARAM + chequeo por semantic_cube
        for idx, (addr, atype, expected) in enumerate(zip(actual_addrs, actual_types, fe.param_types), start=1):
            if semantic_cube[expected][atype]['='] == 'error':
                raise SemanticError(
                    f"Arg {idx} inválido para '{fname}': se esperaba {expected}, se obtuvo {atype}."
                )
            self.quadruples.append(('PARAM', addr, None, idx))
            self.next_quad += 1

        # 6) GOSUB
        self.quadruples.append(('GOSUB', None, None, fe.start_quad))
        self.next_quad += 1

        return None

    # ————————————————————————————————————————————————
    # Reglas originales sin cambio (programa, vars, param_list, func, body…)
    # ————————————————————————————————————————————————
    def programa(self, items):
        return items

    def vars(self, items):
        if items and isinstance(items[-1], list):
            nested = items[-1]; core = items[:-1]
        else:
            nested = None; core = items
        ids, tipo = [], None
        for it in core:
            if isinstance(it, Token) and it.type == 'ID':
                ids.append(it.value)
            elif isinstance(it, Tree) and it.data == 'tipo':
                tipo = it.children[0].value
        if tipo is None:
            return items
        for name in ids:
            if self.current_function is None:
                if self.global_vars.has_variable(name):
                    raise SemanticError(f"Variable global '{name}' ya declarada.")
                addr = self._allocate_address(tipo)
                self.global_vars.add_variable(name, tipo, addr)
            else:
                fe = self.func_dir.get_function(self.current_function)
                if fe.variables.has_variable(name):
                    raise SemanticError(
                        f"Variable '{name}' ya declarada en función '{self.current_function}'."
                    )
                addr = self._allocate_address(tipo)
                fe.variables.add_variable(name, tipo, addr)
        return nested or []

    def param_list(self, items):
        params = []
        for i in range(0, len(items), 3):
            name = items[i].value
            nodo_tipo = items[i+2]
            t = nodo_tipo.children[0].value if isinstance(nodo_tipo, Tree) else nodo_tipo.value
            params.append((name, t))
        return params

    def func(self, items):
        fname = items[1].value
        rawp  = items[3] or []
        if self.func_dir.has_function(fname):
            raise SemanticError(f"Función '{fname}' ya declarada.")
        self.func_dir.add_function(
            name=fname,
            return_type='void',
            param_types=[t for (_,t) in rawp],
            start_quad=self.next_quad
        )
        self.current_function = fname
        fe = self.func_dir.get_function(fname)
        for name, t in rawp:
            if fe.variables.has_variable(name):
                raise SemanticError(
                    f"Parámetro '{name}' ya declarado en función '{fname}'."
                )
            addr = self._allocate_address(t)
            fe.variables.add_variable(name, t, addr)
        return items

    def body(self, items):
        if self.current_function is not None:
            self.current_function = None
        return items
