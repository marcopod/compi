from dataclasses import dataclass
from typing import Dict, List
from semantic.variable_table import VariableTable

@dataclass
class FunctionEntry:
    """
    Representa la informacion de una funcion:
      - return_type: 'int', 'float' o 'void'
      - param_types: lista de tipos en orden de parametros
      - variables: VariableTable local (incluye parámetros)
      - start_quad: indice del primer cuadruplo de la funcion
    """
    return_type: str
    param_types: List[str]
    variables: VariableTable
    start_quad: int

class FunctionDirectory:
    """
    Directorio global de funciones de BabyDuck.
    Mapea nombres de función a su FunctionEntry.
    """
    def __init__(self) -> None:
        self._functions: Dict[str, FunctionEntry] = {}

    def add_function(self,
                     name: str,
                     return_type: str,
                     param_types: List[str],
                     start_quad: int) -> None:
        if name in self._functions:
            raise KeyError(f"Funcion '{name}' ya declarada.")
        var_table = VariableTable()
        # param_types solo contiene tipos; la insercion de nombres reales
        # y direcciones se hace en el Analyzer.
        entry = FunctionEntry(
            return_type=return_type,
            param_types=param_types,
            variables=var_table,
            start_quad=start_quad
        )
        self._functions[name] = entry

    def get_function(self, name: str) -> FunctionEntry:
        if name not in self._functions:
            raise KeyError(f"Funcion '{name}' no declarada.")
        return self._functions[name]

    def has_function(self, name: str) -> bool:
        return name in self._functions

    def all_functions(self) -> Dict[str, FunctionEntry]:
        return dict(self._functions)
