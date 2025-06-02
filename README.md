# BabyDuck Compiler - Compilador Completo

Un compilador completo para el lenguaje de programación educativo **BabyDuck**, implementado en Python con [Lark Parser](https://github.com/lark-parser/lark). Este proyecto incluye todas las fases de compilación: análisis léxico, sintáctico, semántico, generación de código intermedio y ejecución mediante máquina virtual.

## 🚀 Inicio Rápido

### Requisitos Previos
- **Python 3.7+**
- **Biblioteca Lark**: `pip install lark`

### Instalación y Ejecución

1. **Clona el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd compi
   ```

2. **Instala las dependencias:**
   ```bash
   pip install lark
   ```

3. **Ejecuta un programa de ejemplo:**
   ```bash
   # Ejemplo básico con Fibonacci
   python main.py test/fibonacci.bd

   # Ejemplo con funciones y parámetros
   python main.py test/fibonacci_fun.bd

   # Ejemplo con tipos mixtos
   python main.py test/test_mixed.bd
   ```

4. **Ejecuta tu propio programa:**
   ```bash
   python main.py mi_programa.bd
   ```

## 📁 Estructura del Proyecto

```
compi/
├── main.py                       # 🎯 Punto de entrada principal
├── babyduck.py                   # 📝 Cargador de gramática Lark
├── BabyDuck.lark                 # 📋 Gramática formal del lenguaje
├── semantic/
│   ├── analyzer.py               # 🔍 Analizador semántico completo
│   ├── variable_table.py         # 📊 Tabla de variables por ámbito
│   ├── function_directory.py     # 📚 Directorio global de funciones
│   ├── memory_manager.py         # 💾 Gestor de direcciones virtuales
│   ├── semantic_cube.py          # 🎲 Cubo semántico para validación
│   └── interpreter.py            # ⚙️ Máquina virtual e intérprete
└── test/                         # 🧪 Programas de prueba
    ├── fibonacci.bd              # Secuencia de Fibonacci
    ├── fibonacci_fun.bd          # Fibonacci con funciones
    ├── test_mixed.bd             # Prueba de tipos mixtos
    ├── two_param_test.bd         # Funciones con parámetros
    └── program.bd                # Programa básico
```

## 📝 Lenguaje BabyDuck

### Características del Lenguaje
- **Variables**: Tipos `int` y `float` con declaración explícita
- **Funciones**: Definición de funciones `void` con parámetros
- **Estructuras de Control**: Condicionales `if-else` y ciclos `while-do`
- **Operaciones**: Aritméticas (`+`, `-`, `*`, `/`) y relacionales (`<`, `>`, `==`, `!=`)
- **Entrada/Salida**: Instrucción `print` para mostrar valores y cadenas

### Ejemplo de Programa BabyDuck

```babyduck
program fibonacci;
var a, b, temp, n, i: int;

void mostrar_fibonacci(limite: int) {
    a = 0;
    b = 1;
    i = 0;

    while (i < limite) do {
        print("F(", i, ") = ", a);
        temp = a + b;
        a = b;
        b = temp;
        i = i + 1;
    };
};

main {
    n = 8;
    print("Secuencia de Fibonacci hasta F(", n-1, "):");
    mostrar_fibonacci(n);
} end
```

## 🖥️ Salida del Compilador

Cuando ejecutas un programa, el compilador muestra:

```
Análisis semántico exitoso

Variables globales:
  • a : tipo=int, direccion=1000
  • b : tipo=int, direccion=1001
  • temp : tipo=int, direccion=1002
  • n : tipo=int, direccion=1003
  • i : tipo=int, direccion=1004

Funciones declaradas:
  → Funcion 'mostrar_fibonacci': retorna void, parametros ['int'], start_quad=0
    Variables locales:
    · limite : tipo=int, dirección=4000

Cuádruplos generados:
  0 : ( '='    , 10000, None , 1000 )
  1 : ( '='    , 10001, None , 1001 )
  2 : ( '='    , 10000, None , 1004 )
  ...

Iniciando ejecución del programa...
Secuencia de Fibonacci hasta F(7):
F(0) = 0
F(1) = 1
F(2) = 1
F(3) = 2
F(4) = 3
F(5) = 5
F(6) = 8
F(7) = 13
PROGRAMA TERMINADO
```

## 🔧 Funcionalidades del Compilador

### Análisis Completo
- ✅ **Análisis Léxico**: Reconocimiento de tokens y palabras reservadas
- ✅ **Análisis Sintáctico**: Validación de la gramática BabyDuck
- ✅ **Análisis Semántico**: Verificación de tipos y declaraciones
- ✅ **Generación de Código**: Cuádruplos como código intermedio
- ✅ **Ejecución**: Máquina virtual que interpreta los cuádruplos

### Gestión de Memoria
- **Direcciones Virtuales**: Sistema segmentado por ámbito y tipo
- **Rangos de Memoria**:
  - Variables globales: 1000-3999
  - Variables locales: 4000-6999
  - Temporales: 7000-9999
  - Constantes: 10000-12999

### Validación de Errores
- **Errores Sintácticos**: Detección de sintaxis inválida
- **Errores Semánticos**: Variables no declaradas, tipos incompatibles
- **Errores de Ejecución**: División por cero, desbordamiento de memoria

## 🧪 Programas de Prueba Incluidos

| Archivo | Descripción | Características Probadas |
|---------|-------------|-------------------------|
| `test/fibonacci.bd` | Secuencia de Fibonacci | Ciclos, variables globales, aritmética |
| `test/fibonacci_fun.bd` | Fibonacci con funciones | Funciones con parámetros, ámbitos |
| `test/test_mixed.bd` | Tipos mixtos | Promoción de tipos int/float |
| `test/two_param_test.bd` | Múltiples parámetros | Funciones con varios argumentos |
| `test/program.bd` | Programa básico | Condicionales, funciones simples |

## 🛠️ Tecnologías Utilizadas

- **Python 3.7+**: Lenguaje de implementación
- **Lark Parser**: Análisis léxico y sintáctico con gramática LALR(1)
- **Programación Orientada a Objetos**: Arquitectura modular
- **Dataclasses**: Estructuras de datos inmutables
- **Type Hints**: Documentación y validación de tipos

## ⚠️ Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'lark'"
```bash
pip install lark
```

### Error: "FileNotFoundError"
Asegúrate de que el archivo `.bd` existe y la ruta es correcta:
```bash
# Verifica que el archivo existe
ls test/fibonacci.bd

# Ejecuta desde el directorio correcto
python main.py test/fibonacci.bd
```

### Error de Sintaxis en el Programa BabyDuck
- Verifica que todas las declaraciones terminen con `;`
- Asegúrate de que el programa termine con `} end`
- Revisa que las variables estén declaradas antes de usarse

### Verificar que Todo Funciona
```bash
# Prueba rápida con el ejemplo más simple
python main.py test/program.bd
```

## 📚 Documentación Adicional

Para información detallada sobre la arquitectura interna, consulta:
- `documentacion_completa_compilador.md` - Documentación técnica completa
- `BabyDuck.lark` - Gramática formal del lenguaje
- Código fuente en `semantic/` - Implementación de cada fase

---

**Desarrollado por:** Marco Ottavio Podesta Vezzali - A00833604
**Curso:** TC3002B.503 - Implementación de Métodos Computacionales