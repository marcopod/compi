semantic_cube: dict[str, dict[str, dict[str, str]]] = {
    'int': {
        'int': {
            '+': 'int',  '-': 'int',  '*': 'int',  '/': 'int',
            '<': 'bool','>': 'bool','!=': 'bool',
            '=': 'int',
        },
        'float': {
            '+': 'float','-': 'float','*': 'float','/': 'float',
            '<': 'bool','>': 'bool','!=': 'bool',
            '=': 'error', # int = float → error
        },
    },
    'float': {
        'int': {
            '+': 'float','-': 'float','*': 'float','/': 'float',
            '<': 'bool','>': 'bool','!=': 'bool',
            '=': 'float', # float = int → válido (promocion)
        },
        'float': {
            '+': 'float','-': 'float','*': 'float','/': 'float',
            '<': 'bool','>': 'bool','!=': 'bool',
            '=': 'float',
        },
    },
}
