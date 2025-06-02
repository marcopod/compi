# semantic/analyzer.py

from lark import Transformer, Visitor, Token, Tree
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
        self.memory           = MemoryManager()
        self.current_function = None

        # — Pilas y lista de cuádruplos —
        self.operators   = []   # operadores pendientes
        self.operands    = []   # direcciones de operandos
        self.types       = []   # tipos de cada operando
        self.quadruples  = []   # fila de cuádruplos
        self.next_quad   = 0    # índice del próximo cuadruplo

        # — Pilas para saltos —
        self.jump_stack = []    # Para manejar saltos anidados

        # — Enhanced context management —
        self.function_stack = []  # Stack to track function context during transformation

    def transform(self, tree):
        # Two-pass approach: first pass to collect function signatures
        self._collect_function_signatures(tree)
        return super().transform(tree)

    def _transform_tree(self, tree):
        """Override to manage function context during transformation"""
        # Check if this is a function node and manage context
        if hasattr(tree, 'data') and tree.data == 'func':
            fname = tree.children[1].value
            # Set function context for the entire function subtree
            old_function = self.current_function
            self.current_function = fname

            try:
                # Transform the function node normally
                result = super()._transform_tree(tree)
                return result
            finally:
                # Restore previous context
                self.current_function = old_function
        else:
            # For non-function nodes, just transform normally
            return super()._transform_tree(tree)

    def _collect_function_signatures(self, node):
        """First pass: collect all function signatures"""
        if hasattr(node, 'data') and node.data == 'func':
            fname = node.children[1].value
            param_list_node = node.children[3]

            # Process parameter list
            if param_list_node and param_list_node.children:
                rawp = self._extract_params(param_list_node.children)
            else:
                rawp = []

            # Add function to directory
            if not self.func_dir.has_function(fname):
                self.func_dir.add_function(
                    name=fname,
                    return_type='void',
                    param_types=[t for (_,t) in rawp],
                    start_quad=0  # Will be updated during second pass
                )

                # Add parameters to function's variable table
                fe = self.func_dir.get_function(fname)
                for name, t in rawp:
                    if not fe.variables.has_variable(name):
                        addr = self.memory.allocate('local', t)
                        fe.variables.add_variable(name, t, addr)

        # Recursively process children
        if hasattr(node, 'children'):
            for child in node.children:
                if hasattr(child, 'data'):
                    self._collect_function_signatures(child)

    def _extract_params(self, items):
        """Extract parameters from parameter list items"""
        params = []
        i = 0
        while i < len(items):
            if i + 2 < len(items):
                name_item = items[i]
                name = name_item.value if hasattr(name_item, 'value') else str(name_item)
                nodo_tipo = items[i+2]
                if hasattr(nodo_tipo, 'children'):
                    t = nodo_tipo.children[0].value
                else:
                    t = nodo_tipo.value if hasattr(nodo_tipo, 'value') else str(nodo_tipo)
                params.append((name, t))
                i += 3
                if i < len(items) and hasattr(items[i], 'value') and items[i].value == ',':
                    i += 1
            else:
                break
        return params

    def _allocate_address(self, var_type: str) -> int:
        """
        Asigna una dirección virtual para una variable.
        Usa el ámbito global o local según el contexto.
        """
        scope = 'local' if self.current_function else 'global'
        return self.memory.allocate(scope, var_type)

    def _generate_quad(self, operator: str):
        """
        Genera un cuádruplo para una operación.
        Maneja la asignación de temporales y verificación de tipos.
        """
        op = self.operators.pop() if self.operators else operator
        r_addr = self.operands.pop()
        l_addr = self.operands.pop()
        r_type = self.types.pop()
        l_type = self.types.pop()

        res_type = semantic_cube[l_type][r_type][op]
        if res_type == 'error':
            raise SemanticError(f"Tipo inválido para {l_type} {op} {r_type}")

        # Asignar dirección temporal para el resultado
        temp = self.memory.allocate_temp(res_type)
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
        """
        Maneja constantes enteras.
        Reutiliza direcciones para constantes idénticas.
        """
        value = int(token.value)
        addr = self.memory.allocate_constant(value)
        self.operands.append(addr)
        self.types.append('int')
        return addr

    def CTE_FLOAT(self, token: Token):
        """
        Maneja constantes flotantes.
        Reutiliza direcciones para constantes idénticas.
        """
        value = float(token.value)
        addr = self.memory.allocate_constant(value)
        self.operands.append(addr)
        self.types.append('float')
        return addr

    def int(self, items):
        """
        Maneja la regla 'int' que viene de CTE_INT -> int en la gramática.
        El items[0] es un Token CTE_INT.
        """
        token = items[0]
        if hasattr(token, 'value'):
            # Es un Token, procesarlo como CTE_INT
            return self.CTE_INT(token)
        else:
            # Ya fue procesado, simplemente retornarlo
            return token

    def float(self, items):
        """
        Maneja la regla 'float' que viene de CTE_FLOAT -> float en la gramática.
        El items[0] es un Token CTE_FLOAT.
        """
        token = items[0]
        if hasattr(token, 'value'):
            # Es un Token, procesarlo como CTE_FLOAT
            return self.CTE_FLOAT(token)
        else:
            # Ya fue procesado, simplemente retornarlo
            return token

    # ————————————————————————————————————————————————
    # Operadores binarios y relacionales
    # ————————————————————————————————————————————————
    def add(self, items): self.operators.append('+'); self._generate_quad('+'); return self.operands[-1]
    def sub(self, items): self.operators.append('-'); self._generate_quad('-'); return self.operands[-1]
    def mul(self, items): self.operators.append('*'); self._generate_quad('*'); return self.operands[-1]
    def div(self, items): self.operators.append('/'); self._generate_quad('/'); return self.operands[-1]
    def gt(self,  items): self.operators.append('>'); self._generate_quad('>'); return self.operands[-1]
    def lt(self,  items): self.operators.append('<'); self._generate_quad('<'); return self.operands[-1]
    def eq(self,  items): self.operators.append('=='); self._generate_quad('=='); return self.operands[-1]
    def neq(self, items): self.operators.append('!=' ); self._generate_quad('!='); return self.operands[-1]

    def group(self, items): return items[0]
    def pos(self,   items): return items[0]
    def neg(self,   items):
        """
        Maneja operador unario negativo.
        Usa constante 0 y operador de resta.
        """
        zero = self.memory.allocate_constant(0)
        self.operands.append(zero)
        self.types.append('int')
        self.operators.append('-')
        self._generate_quad('-')
        return self.operands[-1]

    # ————————————————————————————————————————————————
    # Asignación
    # ————————————————————————————————————————————————
    def assign(self, items):
        """
        Maneja asignaciones.
        Verifica tipos y genera cuádruplo de asignación.
        """
        expr_addr = self.operands.pop()
        expr_type = self.types.pop()

        id_token = items[0]
        name = id_token.value

        # Buscar variable en ámbito actual o global
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

        # Verificar compatibilidad de tipos
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
            # Skip comma tokens - they are just separators, not values to print
            if isinstance(elem, Token) and elem.type == 'COMMA':
                continue
            self.quadruples.append(('print', elem, None, None))
            self.next_quad += 1

        # Add PRINT_END quadruple to mark the end of this print statement
        self.quadruples.append(('PRINT_END', None, None, None))
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

        # 2) Contar argumentos reales basándose en los parámetros esperados
        # Los argumentos ya fueron procesados y están en las pilas operands/types
        expected_count = len(fe.param_types)

        # Verificar que tenemos suficientes operandos en la pila
        if len(self.operands) < expected_count:
            raise SemanticError(
                f"Número incorrecto de argumentos para '{fname}': "
                f"esperados {expected_count}, recibidos {len(self.operands)}."
            )

        actual_count = expected_count  # Asumimos que el parser validó la sintaxis correctamente

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
        """
        Maneja declaraciones de variables.
        Asigna direcciones virtuales según el ámbito.
        """
        if items and isinstance(items[-1], list):
            nested = items[-1]
            core = items[:-1]
        else:
            nested = None
            core = items

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
                # Variable global
                if self.global_vars.has_variable(name):
                    raise SemanticError(f"Variable global '{name}' ya declarada.")
                addr = self._allocate_address(tipo)
                self.global_vars.add_variable(name, tipo, addr)
            else:
                # Variable local
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
        # Handle the parameter list structure: ID COLON tipo (COMMA ID COLON tipo)*
        i = 0
        while i < len(items):
            if i + 2 < len(items):
                name_item = items[i]
                name = name_item.value if isinstance(name_item, Token) else str(name_item)
                # Skip the colon (items[i+1])
                nodo_tipo = items[i+2]
                t = nodo_tipo.children[0].value if isinstance(nodo_tipo, Tree) else nodo_tipo.value
                params.append((name, t))
                i += 3  # Move past ID, COLON, tipo
                # Skip comma if present
                if i < len(items) and isinstance(items[i], Token) and items[i].value == ',':
                    i += 1
            else:
                break
        return params

    def func(self, items):
        fname = items[1].value

        # Function should already be in directory from first pass
        if not self.func_dir.has_function(fname):
            raise SemanticError(f"Función '{fname}' no encontrada en primera pasada.")

        # The function body has already been processed, so we need to set
        # the correct start address. For simplicity, the first function starts at 0.
        fe = self.func_dir.get_function(fname)
        # Simple approach: first function starts at 0
        if fe.start_quad == 0:  # Only set if not already set
            fe.start_quad = 0

        # Generate ENDFUNC at the end of the function
        self.quadruples.append(('ENDFUNC', None, None, None))
        self.next_quad += 1

        return items

    def body(self, items):
        # Don't generate ENDFUNC here - it will be generated by the func method
        return items

    # ————————————————————————————————————————————————
    # Estatutos condicionales y cíclicos
    # ————————————————————————————————————————————————
    def condition(self, items):
        """
        Maneja estatutos condicionales if-else.
        Genera cuádruplos:
        1. GOTOF para saltar si la condición es falsa
        2. Código del bloque if
        3. GOTO para saltar el bloque else
        4. Código del bloque else (si existe)
        """
        # items[0] = expr (condición)
        # items[1] = body (bloque if)
        # items[2] = body (bloque else, opcional)

        # 1. Evaluar condición
        cond_addr = self.operands.pop()
        cond_type = self.types.pop()

        if cond_type != 'bool':
            raise SemanticError("La condición debe ser de tipo booleano")

        # 2. Generar GOTOF
        self.quadruples.append(('GOTOF', cond_addr, None, None))
        if_false = self.next_quad
        self.next_quad += 1

        # 3. Código del bloque if
        if_body = items[1]

        # 4. Si hay else, generar GOTO para saltar el bloque else
        if len(items) > 2:
            self.quadruples.append(('GOTO', None, None, None))
            goto_end = self.next_quad
            self.next_quad += 1

        # 5. Actualizar el GOTOF con la dirección correcta
        if len(items) > 2:
            self.quadruples[if_false] = ('GOTOF', cond_addr, None, self.next_quad)
        else:
            self.quadruples[if_false] = ('GOTOF', cond_addr, None, self.next_quad)

        # 6. Si hay else, procesar su bloque
        if len(items) > 2:
            else_body = items[2]
            # Actualizar el GOTO con la dirección después del else
            self.quadruples[goto_end] = ('GOTO', None, None, self.next_quad)

        return None

    def cycle(self, items):
        """
        Maneja estatutos cíclicos while.

        IMPORTANTE: En Lark Transformer, los nodos se procesan bottom-up,
        por lo que cuando llegamos aquí, la condición y el cuerpo ya fueron procesados.

        Necesitamos reorganizar los cuádruplos para crear la estructura correcta:
        1. condition_start: Evaluación de condición
        2. GOTOF: Saltar al final si es falsa
        3. body: Cuerpo del ciclo
        4. GOTO: Volver a condition_start
        5. end: Continuar después del ciclo
        """
        # items[0] = expr (condición)
        # items[1] = body (cuerpo del ciclo)

        # Buscar el resultado booleano en las pilas
        if not self.operands or not self.types:
            raise SemanticError("Error interno: pilas vacías en cycle")

        bool_index = -1
        for i, t in enumerate(self.types):
            if t == 'bool':
                bool_index = i
                break

        if bool_index == -1:
            raise SemanticError("No se encontró resultado booleano para la condición del while")

        # Extraer el resultado booleano
        cond_addr = self.operands.pop(bool_index)
        cond_type = self.types.pop(bool_index)

        if cond_type != 'bool':
            raise SemanticError(f"La condición debe ser de tipo booleano, pero es {cond_type}")

        # Encontrar dónde está la evaluación de la condición
        # Buscar el cuádruplo que genera cond_addr
        condition_quad = -1
        for i, (op, left, right, result) in enumerate(self.quadruples):
            if result == cond_addr:
                condition_quad = i
                break

        if condition_quad == -1:
            raise SemanticError("No se encontró el cuádruplo de evaluación de condición")

        # Generar GOTOF justo después de la condición
        # Insertar GOTOF después del cuádruplo de condición
        gotof_quad = ('GOTOF', cond_addr, None, None)  # Se actualizará después
        self.quadruples.insert(condition_quad + 1, gotof_quad)
        self.next_quad += 1

        # Ajustar índices debido a la inserción
        gotof_index = condition_quad + 1

        # Generar GOTO al final para volver al inicio de la condición
        self.quadruples.append(('GOTO', None, None, condition_quad))
        self.next_quad += 1

        # Actualizar el GOTOF con la dirección de salida (después del GOTO)
        self.quadruples[gotof_index] = ('GOTOF', cond_addr, None, self.next_quad)

        return None
