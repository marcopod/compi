# BabyDuck Compiler (Análisis Semántico)

Este proyecto implementa el **análisis semántico** para el lenguaje de programación ficticio *BabyDuck*, como parte de un compilador construido con la herramienta [Lark](https://github.com/lark-parser/lark) en Python.

## Funcionalidad

El sistema verifica la **semántica estática** de programas escritos en BabyDuck. Esto incluye:

- Declaración y uso correcto de variables y funciones.
- Detección de errores como declaraciones duplicadas o uso de variables no definidas.
- Asignación de direcciones de memoria mediante un manejador por ámbito y tipo.
- Representación de estructuras como el *Function Directory* y la *Variable Table*.

## Estructura del Proyecto

