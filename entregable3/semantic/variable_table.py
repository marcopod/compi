from dataclasses import dataclass
from typing import Dict

@dataclass
class VariableEntry:
    """
    Representa una variable en un ambito:
      - var_type: 'int' o 'float'
      - address: direccion (entero) asignada por el manejador de memoria
    """
    var_type: str
    address: int

class VariableTable:
    """
    Tabla de variables para un solo alcance (global o funcion).
    Mapea nombres de variable a VariableEntry.
    """
    def __init__(self) -> None:
        self._table: Dict[str, VariableEntry] = {}

    def add_variable(self, name: str, var_type: str, address: int) -> None:
        """
        Agrega una variable al alcance. 
        Lanza KeyError si ya existe.
        """
        if name in self._table:
            raise KeyError(f"Variable '{name}' ya declarada en este alcance.")
        self._table[name] = VariableEntry(var_type, address)

    def get_variable(self, name: str) -> VariableEntry:
        """
        Recupera la entrada de una variable. 
        Lanza KeyError si no existe.
        """
        if name not in self._table:
            raise KeyError(f"Variable '{name}' no declarada en este alcance.")
        return self._table[name]

    def has_variable(self, name: str) -> bool:
        """
        Indica si la variable esta declarada en este alcance.
        """
        return name in self._table

    def all_variables(self) -> Dict[str, VariableEntry]:
        """
        Devuelve un diccionario copia de todas las variables.
        Util para asignacion de memoria o generacion de directorios.
        """
        return dict(self._table)
