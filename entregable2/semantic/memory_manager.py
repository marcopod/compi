from typing import Dict

class MemoryManager:
    """
    Gestiona contadores de direcciones por ambito y tipo.
    Permite configurar offsets base por segmento (global, local, temp, const).
    """
    def __init__(self, base_offsets: Dict[str, Dict[str, int]] = None):
        # base_offsets = {'global': {'int':0,'float':1000}, 'func1': {...}, ...}
        self._base = base_offsets or {}
        self._counters = {}
    
    def allocate(self, scope: str, var_type: str) -> int:
        # Inicializa el contador si es primera vez
        if scope not in self._counters:
            base = self._base.get(scope, {}).get(var_type, 0)
            self._counters[scope] = { 'int': base, 'float': base }
        addr = self._counters[scope][var_type]
        self._counters[scope][var_type] += 1
        return addr
