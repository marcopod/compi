from typing import Dict, Union, Tuple

class MemoryManager:
    """
    Gestiona la asignación de direcciones virtuales por ámbito y tipo.
    Implementa rangos específicos para cada tipo de memoria:
    - Global: 1000-1999 (int), 2000-2999 (float), 3000-3999 (bool)
    - Local: 4000-4999 (int), 5000-5999 (float), 6000-6999 (bool)
    - Temporal: 7000-7999 (int), 8000-8999 (float), 9000-9999 (bool)
    - Constante: 10000-10999 (int), 11000-11999 (float), 12000-12999 (bool)
    """
    def __init__(self):
        # Definición de rangos de memoria (sin solapamientos)
        self.ranges = {
            'global': {
                'int': (1000, 1999),
                'float': (2000, 2999),
                'bool': (3000, 3999)
            },
            'local': {
                'int': (4000, 4999),
                'float': (5000, 5999),
                'bool': (6000, 6999)
            },
            'temp': {
                'int': (7000, 7999),
                'float': (8000, 8999),
                'bool': (9000, 9999)
            },
            'const': {
                'int': (10000, 10999),
                'float': (11000, 11999),
                'bool': (12000, 12999)
            }
        }
        # Contadores actuales por ámbito y tipo
        self._counters = {}
        # Tabla de constantes para evitar duplicados
        self._const_table = {}

    def allocate(self, scope: str, var_type: str) -> int:
        """
        Asigna una dirección virtual para una variable o temporal.
        Args:
            scope: 'global', 'local', 'temp' o 'const'
            var_type: 'int' o 'float'
        Returns:
            Dirección virtual asignada
        Raises:
            MemoryError: Si se agota el rango de memoria
        """
        if scope not in self._counters:
            self._counters[scope] = {
                'int': self.ranges[scope]['int'][0],
                'float': self.ranges[scope]['float'][0],
                'bool': self.ranges[scope]['bool'][0]
            }

        current = self._counters[scope][var_type]
        if current > self.ranges[scope][var_type][1]:
            raise MemoryError(f"Se agotó la memoria para {scope} {var_type}")

        self._counters[scope][var_type] += 1
        return current

    def allocate_constant(self, value: Union[int, float]) -> int:
        """
        Asigna una dirección virtual para una constante.
        Reutiliza direcciones para constantes idénticas.
        Args:
            value: Valor de la constante
        Returns:
            Dirección virtual asignada
        """
        # Si la constante ya existe, reutilizar su dirección
        if value in self._const_table:
            return self._const_table[value]

        # Determinar el tipo y asignar nueva dirección
        var_type = 'int' if isinstance(value, int) else 'float'
        addr = self.allocate('const', var_type)
        self._const_table[value] = addr
        return addr

    def allocate_temp(self, var_type: str) -> int:
        """
        Asigna una dirección virtual para una variable temporal.
        Args:
            var_type: 'int' o 'float'
        Returns:
            Dirección virtual asignada
        """
        return self.allocate('temp', var_type)

    def check_memory_limits(self, scope: str, var_type: str) -> bool:
        """
        Verifica si hay memoria disponible en el rango especificado.
        Args:
            scope: Ámbito de memoria
            var_type: Tipo de dato
        Returns:
            True si hay memoria disponible, False en caso contrario
        """
        if scope not in self._counters:
            return True
        current = self._counters[scope][var_type]
        limit = self.ranges[scope][var_type][1]
        return current <= limit

    def get_constant_address(self, value: Union[int, float]) -> int:
        """
        Obtiene la dirección de una constante existente.
        Args:
            value: Valor de la constante
        Returns:
            Dirección virtual de la constante
        Raises:
            KeyError: Si la constante no existe
        """
        if value not in self._const_table:
            raise KeyError(f"Constante {value} no encontrada")
        return self._const_table[value]
