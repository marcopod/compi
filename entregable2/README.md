# BabyDuck Compiler (Análisis Semántico)

Este proyecto implementa el **análisis semántico** para el lenguaje de programación ficticio *BabyDuck*, como parte de un compilador construido con la herramienta [Lark](https://github.com/lark-parser/lark) en Python.

## Funcionalidad

El sistema verifica la **semántica estática** de programas escritos en BabyDuck. Esto incluye:

- Declaración y uso correcto de variables y funciones.
- Detección de errores como declaraciones duplicadas o uso de variables no definidas.
- Asignación de direcciones de memoria mediante un manejador por ámbito y tipo.
- Representación de estructuras como el *Function Directory* y la *Variable Table*.

## Estructura del Proyecto

```
babyduck/
│
├── main.py                       # Punto de entrada, ejecuta el análisis semántico
├── babyduck.py                   # Carga y compila la gramática Lark (.lark)
├── program.bd                    # Ejemplo de programa en BabyDuck
│
├── babyduck.lark                 # Gramática formal del lenguaje BabyDuck
│
└── semantic/
    ├── analyzer.py               # Analizador semántico (Transformer)
    ├── variable_table.py         # Tabla de variables por ámbito
    ├── function_directory.py     # Directorio global de funciones
    ├── memory_manager.py         # Administrador de direcciones de memoria
    └── semantic_cube.py          # Cubo semántico para operaciones válidas
```

## ▶Cómo Ejecutar

1. Clona el repositorio:

   ```bash
   git clone <url-del-repo>
   cd babyduck
   ```

2. Asegúrate de tener Python 3.7+ y la dependencia `lark`:

   ```bash
   pip install lark
   ```

3. Ejecuta el analizador con un archivo `.bd` (como `program.bd` incluido):

   ```bash
   python main.py program.bd
   ```

## Ejemplo de Programa

```babyduck
program ejemplo;
var x, y: int;

void foo() {
    print("Hola", x + y);
};

main {
    x = 3;
    y = 4;
    foo();
} end
```

## Salida Esperada

La herramienta:

- Imprime el árbol sintáctico.
- Realiza el análisis semántico.
- Muestra las variables globales y funciones válidamente declaradas.

## Tecnologías Utilizadas

- Python 3
- Lark Parser (LALR)
- Programación orientada a objetos
- Estructuras de datos con `@dataclass`