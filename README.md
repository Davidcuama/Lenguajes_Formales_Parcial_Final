# Proyecto Final - Compiladores
## Implementación de Parsers LL(1) y SLR(1)

Este proyecto implementa algoritmos para análisis sintáctico de gramáticas libres de contexto, específicamente parsers LL(1) y SLR(1).

### Características Implementadas

1. **Cálculo de conjuntos First y Follow** (10%)
   - Algoritmos iterativos para calcular First y Follow
   - Manejo correcto de producciones epsilon
   - Visualización de los conjuntos calculados

2. **Parser LL(1) (Top-Down)** (20%)
   - Detección de recursión izquierda
   - Detección de factorización izquierda
   - Construcción de tabla de análisis LL(1)
   - Algoritmo de parsing LL(1)

3. **Parser SLR(1) (Bottom-Up)** (20%)
   - Construcción de estados SLR(1)
   - Cálculo de closure y goto
   - Detección de conflictos SLR(1)
   - Algoritmo de parsing SLR(1)

4. **Manejo de Input/Output según especificaciones**
   - Lectura de gramáticas en formato especificado
   - Manejo de los 4 casos de uso
   - Interfaz interactiva para selección de parser

### Formato de Entrada

El programa espera la entrada en el siguiente formato:

```
n
A -> α1 α2 ... αk
B -> β1 β2 ... βm
...
```

Donde:
- `n` es el número de no terminales
- Cada línea contiene una regla de producción
- `e` representa la cadena vacía (epsilon)
- Los no terminales son letras mayúsculas
- Los terminales son caracteres que no son letras mayúsculas

### Casos de Uso

El programa maneja 4 casos según el tipo de gramática:

1. **Gramática es tanto LL(1) como SLR(1)**
   - Muestra menú de selección de parser
   - Permite alternar entre parsers
   - Opción de salir (Q)

2. **Gramática es solo LL(1)**
   - Muestra "Grammar is LL(1)."
   - Usa parser LL(1) automáticamente

3. **Gramática es solo SLR(1)**
   - Muestra "Grammar is SLR(1)."
   - Usa parser SLR(1) automáticamente

4. **Gramática no es ni LL(1) ni SLR(1)**
   - Muestra "Grammar is neither LL(1) nor SLR(1)."
   - Termina el programa

### Archivos de Prueba

Se incluyen varios archivos de prueba:

- `test_ll1.txt`: Gramática LL(1) simple
- `test_slr1.txt`: Gramática SLR(1) simple  
- `test_both.txt`: Gramática que es tanto LL(1) como SLR(1)
- `test_neither.txt`: Gramática que no es ni LL(1) ni SLR(1)

### Uso del Programa

```bash
python grammar_parser.py
```

Luego ingrese la gramática según el formato especificado.

### Ejemplo de Uso

```
3
S -> A
A -> a A b
A -> e
```

Para esta gramática, el programa:
1. Calcula First y Follow sets
2. Determina que es LL(1)
3. Muestra "Grammar is LL(1)."
4. Espera cadenas para analizar
5. Responde "yes" o "no" para cada cadena

### Estructura del Código

- `GrammarParser`: Clase principal que implementa todos los algoritmos
- Métodos para cálculo de First y Follow
- Métodos para construcción de parsers LL(1) y SLR(1)
- Métodos para análisis de cadenas
- Manejo de entrada y salida según especificaciones

### Comentarios

El código está completamente comentado en español, explicando:
- Propósito de cada método
- Algoritmos implementados
- Parámetros y valores de retorno
- Lógica de negocio
- Casos especiales manejados

### Requisitos

- Python 3.6+
- No se requieren librerías externas
