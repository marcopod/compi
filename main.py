import sys
import os
from babyduck import parser
from semantic.analyzer import SemanticAnalyzer, SemanticError
from semantic.interpreter import Interpreter

from lark import UnexpectedInput

def main():
    # 1) Validacion de argumentos
    if len(sys.argv) != 2:
        print("Uso: python main.py <ruta_al_programa.bd>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: el archivo '{filepath}' no existe.")
        sys.exit(1)

    # 2) Leer el archivo fuente
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # 3) Parseo sintactico
    try:
        tree = parser.parse(code)
    except UnexpectedInput as e:
        print(f"Sintaxis invalida en linea {e.line}, columna {e.column}")
        sys.exit(1)

    # 4) Analisis semantico
    analyzer = SemanticAnalyzer()
    try:
        analyzer.transform(tree)
            # 5b) Mostrar cuádruplos generados
        print("Cuádruplos generados:")
        for i, quad in enumerate(analyzer.quadruples):
            op, left, right, res = quad
            print(f"{i:>3} : ( {op!r:7}, {left!r:5}, {right!r:5}, {res!r:5} )")
        print()


    except SemanticError as e:
        print("Error semantico:", e)
        sys.exit(1)

    # 5) Reporte de exito
    print("Analisis semantico exitoso\n")

    print("Variables globales:")
    for name, entry in analyzer.global_vars.all_variables().items():
        print(f"  • {name} : tipo={entry.var_type}, direccion={entry.address}")
    print()

    print("Funciones declaradas:")
    for fname, fentry in analyzer.func_dir.all_functions().items():
        print(f"  → Funcion '{fname}': retorna {fentry.return_type}, "
              f"parametros {fentry.param_types}, start_quad={fentry.start_quad}")
        vars_loc = fentry.variables.all_variables()
        if vars_loc:
            print("\tVariables locales:")
            for vname, ventry in vars_loc.items():
                print(f"\t· {vname} : tipo={ventry.var_type}, dirección={ventry.address}")
        else:
            print("\t(Sin variables locales)")
        print()

    # 6) Ejecución del programa
    print("Iniciando ejecución del programa...")
    interpreter = Interpreter(
        quadruples=analyzer.quadruples,
        global_vars=analyzer.global_vars,
        func_dir=analyzer.func_dir,
        memory=analyzer.memory
    )

    try:
        interpreter.execute()
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    main()
