# semantic/interpreter.py

class RuntimeError(Exception):
    """Para errores en tiempo de ejecución."""
    pass

class Interpreter:
    def __init__(self, quadruples, global_vars, func_dir, memory):
        self.quadruples = quadruples
        self.global_vars = global_vars
        self.func_dir = func_dir
        self.memory = memory

        # Execution state
        self.instruction_pointer = 0
        self.call_stack = []
        self.memory_values = {}  # address -> value mapping
        self.current_function_call = None  # Current function being called
        self.param_values = {}  # Parameter values for current function call

        # Initialize global variables to 0
        for name, var_entry in global_vars.all_variables().items():
            self.memory_values[var_entry.address] = 0

        # Initialize constants from memory manager
        for value, addr in memory._const_table.items():
            self.memory_values[addr] = value

    def execute(self):
        """Execute the quadruples starting from the main program."""

        # Find main program start (after all function definitions)
        main_start = 0  # Default to start from beginning if no functions
        last_endfunc = -1

        # Find the last ENDFUNC quadruple to determine where main program starts
        for i, (op, _, _, _) in enumerate(self.quadruples):
            if op == 'ENDFUNC':
                last_endfunc = i

        # If we found any ENDFUNC, main starts after the last one
        # Otherwise, main starts from the beginning (quadruple 0)
        if last_endfunc >= 0:
            main_start = last_endfunc + 1

        self.instruction_pointer = main_start

        while self.instruction_pointer < len(self.quadruples):
            quad = self.quadruples[self.instruction_pointer]
            op, left, right, result = quad

            # Debug output (optional - can be disabled)
            # print(f"Executing {self.instruction_pointer}: {quad}")

            if op == '=':
                self._execute_assign(left, result)
            elif op == 'print':
                self._execute_print(left)
            elif op == 'PRINT_END':
                self._execute_print_end()
            elif op == '+':
                self._execute_arithmetic(left, right, result, lambda a, b: a + b)
            elif op == '-':
                self._execute_arithmetic(left, right, result, lambda a, b: a - b)
            elif op == '*':
                self._execute_arithmetic(left, right, result, lambda a, b: a * b)
            elif op == '/':
                self._execute_arithmetic(left, right, result, lambda a, b: a / b)
            elif op == '>':
                self._execute_comparison(left, right, result, lambda a, b: a > b)
            elif op == '<':
                self._execute_comparison(left, right, result, lambda a, b: a < b)
            elif op == '==':
                self._execute_comparison(left, right, result, lambda a, b: a == b)
            elif op == '!=':
                self._execute_comparison(left, right, result, lambda a, b: a != b)
            elif op == 'GOTOF':
                self._execute_gotof(left, result)
                continue  # Don't increment IP
            elif op == 'GOTO':
                self._execute_goto(result)
                continue  # Don't increment IP
            elif op == 'ERA':
                self._execute_era(result)
            elif op == 'PARAM':
                self._execute_param(left, result)
            elif op == 'GOSUB':
                self._execute_gosub(result)
                continue  # Don't increment IP
            elif op == 'ENDFUNC':
                self._execute_endfunc()
                continue  # Don't increment IP
            else:
                print(f"Warning: Unknown operation '{op}' at quad {self.instruction_pointer}")

            self.instruction_pointer += 1
        
        print("\nPROGRAMA TERMINADO")

    def _get_value(self, address):
        """Get value from memory address or return the address if it's a literal."""
        if isinstance(address, str) and address.startswith('"') and address.endswith('"'):
            # String literal
            return address[1:-1]  # Remove quotes
        elif address in self.memory_values:
            return self.memory_values[address]
        else:
            # Assume it's a literal value
            return address

    def _execute_assign(self, source_addr, dest_addr):
        """Execute assignment: dest = source"""
        value = self._get_value(source_addr)
        self.memory_values[dest_addr] = value

    def _execute_print(self, address):
        """Execute print statement"""
        value = self._get_value(address)
        print(value, end="")

    def _execute_print_end(self):
        """Execute end of print statement - add newline"""
        print()  # Print newline to end the current print statement

    def _execute_arithmetic(self, left_addr, right_addr, result_addr, operation):
        """Execute arithmetic operation"""
        left_val = self._get_value(left_addr)
        right_val = self._get_value(right_addr)
        result = operation(left_val, right_val)
        self.memory_values[result_addr] = result

    def _execute_comparison(self, left_addr, right_addr, result_addr, operation):
        """Execute comparison operation"""
        left_val = self._get_value(left_addr)
        right_val = self._get_value(right_addr)
        result = operation(left_val, right_val)
        self.memory_values[result_addr] = 1 if result else 0  # Store as int

    def _execute_gotof(self, condition_addr, target_quad):
        """Execute conditional jump (GOTOF)"""
        condition = self._get_value(condition_addr)
        if not condition:  # If condition is false (0)
            self.instruction_pointer = target_quad
        else:
            self.instruction_pointer += 1

    def _execute_goto(self, target_quad):
        """Execute unconditional jump (GOTO)"""
        self.instruction_pointer = target_quad

    def _execute_era(self, func_name):
        """Execute ERA (activation record)"""
        # Prepare for function call - store function name for parameter passing
        self.current_function_call = func_name
        self.param_values = {}

    def _execute_param(self, param_addr, param_index):
        """Execute parameter passing"""
        # Get the value from the parameter address
        value = self._get_value(param_addr)
        # Store the parameter value for the current function call
        self.param_values[param_index] = value

    def _execute_gosub(self, target_quad):
        """Execute function call (GOSUB)"""
        # Push return address to call stack
        self.call_stack.append(self.instruction_pointer + 1)

        # Set up parameter values in function's local memory
        if hasattr(self, 'current_function_call') and hasattr(self, 'param_values'):
            func_name = self.current_function_call
            if self.func_dir.has_function(func_name):
                func_entry = self.func_dir.get_function(func_name)
                # Get parameter names and addresses from function's variable table
                param_names = []
                for var_name, var_entry in func_entry.variables.all_variables().items():
                    param_names.append((var_name, var_entry.address))

                # Sort by parameter order (assuming they were added in order)
                param_names.sort(key=lambda x: x[1])  # Sort by address

                # Assign parameter values to their addresses
                for i, (param_name, param_addr) in enumerate(param_names[:len(self.param_values)]):
                    if (i + 1) in self.param_values:
                        self.memory_values[param_addr] = self.param_values[i + 1]

        self.instruction_pointer = target_quad

    def _execute_endfunc(self):
        """Execute end of function (ENDFUNC)"""
        if self.call_stack:
            # Return to caller
            self.instruction_pointer = self.call_stack.pop()
        else:
            # End of main program
            self.instruction_pointer = len(self.quadruples)
