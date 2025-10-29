#!/usr/bin/env python3
"""
Módulo para parser LL(1)
Implementa análisis sintáctico descendente
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple


class LL1Parser:
    """
    Clase especializada en análisis LL(1)
    """
    
    def __init__(self, productions: Dict[str, List[List[str]]], 
                 nonterminals: Set[str], terminals: Set[str],
                 first_sets: Dict[str, Set[str]], 
                 follow_sets: Dict[str, Set[str]]):
        """
        Inicializa el parser LL(1)
        
        Args:
            productions: Diccionario de producciones
            nonterminals: Conjunto de no terminales
            terminals: Conjunto de terminales
            first_sets: Conjuntos First calculados
            follow_sets: Conjuntos Follow calculados
        """
        self.productions = productions
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.epsilon = 'e'
        self.end_marker = '$'
        
        # Tabla de análisis LL(1)
        self.ll1_table: Dict[Tuple[str, str], List[str]] = {}
    
    def is_ll1(self) -> bool:
        """
        Determina si la gramática es LL(1).
        
        Returns:
            True si la gramática es LL(1), False en caso contrario
        """
        print("Verificando si la gramática es LL(1)...")
        
        # Verificar recursión izquierda
        if self.has_left_recursion():
            print("La gramática tiene recursión izquierda. No es LL(1).")
            return False
        
        # Verificar factorización izquierda
        if self.has_left_factoring():
            print("La gramática tiene factorización izquierda. No es LL(1).")
            return False
        
        # Verificar condición LL(1) para cada no terminal
        for nonterminal in self.nonterminals:
            productions = self.productions[nonterminal]
            
            for i in range(len(productions)):
                for j in range(i + 1, len(productions)):
                    prod1 = productions[i]
                    prod2 = productions[j]
                    
                    first1 = self.compute_first_of_string(prod1)
                    first2 = self.compute_first_of_string(prod2)
                    
                    # Verificar intersección
                    intersection = first1.intersection(first2)
                    if intersection:
                        print(f"Intersección en First sets para {nonterminal}: {intersection}")
                        return False
                    
                    # Verificar caso epsilon
                    if self.epsilon in first1:
                        follow_intersection = first2.intersection(self.follow_sets[nonterminal])
                        if follow_intersection:
                            print(f"Intersección con Follow para {nonterminal}: {follow_intersection}")
                            return False
                    
                    if self.epsilon in first2:
                        follow_intersection = first1.intersection(self.follow_sets[nonterminal])
                        if follow_intersection:
                            print(f"Intersección con Follow para {nonterminal}: {follow_intersection}")
                            return False
        
        print("La gramática es LL(1).")
        return True
    
    def has_left_recursion(self) -> bool:
        """
        Verifica si la gramática tiene recursión izquierda.
        
        Returns:
            True si hay recursión izquierda, False en caso contrario
        """
        for nonterminal in self.nonterminals:
            for production in self.productions[nonterminal]:
                if production and production[0] == nonterminal:
                    return True
        return False
    
    def has_left_factoring(self) -> bool:
        """
        Verifica si la gramática tiene factorización izquierda.
        
        Returns:
            True si hay factorización izquierda, False en caso contrario
        """
        for nonterminal in self.nonterminals:
            productions = self.productions[nonterminal]
            
            for i in range(len(productions)):
                for j in range(i + 1, len(productions)):
                    prod1 = productions[i]
                    prod2 = productions[j]
                    
                    # Verificar prefijo común
                    min_len = min(len(prod1), len(prod2))
                    for k in range(min_len):
                        if prod1[k] != prod2[k]:
                            break
                        if k > 0:  # Hay un prefijo común de longitud > 0
                            return True
        
        return False
    
    def build_ll1_table(self) -> bool:
        """
        Construye la tabla de análisis LL(1).
        
        Returns:
            True si se construye exitosamente, False en caso contrario
        """
        print("Construyendo tabla LL(1)...")
        
        self.ll1_table = {}
        
        for nonterminal in self.nonterminals:
            for production in self.productions[nonterminal]:
                first_alpha = self.compute_first_of_string(production)
                
                # Para cada terminal en First(α)
                for terminal in first_alpha - {self.epsilon}:
                    key = (nonterminal, terminal)
                    if key in self.ll1_table:
                        print(f"Conflicto en tabla LL(1): {key}")
                        return False
                    self.ll1_table[key] = production
                
                # Si ε ∈ First(α), agregar Follow(A)
                if self.epsilon in first_alpha:
                    for terminal in self.follow_sets[nonterminal]:
                        key = (nonterminal, terminal)
                        if key in self.ll1_table:
                            print(f"Conflicto en tabla LL(1): {key}")
                            return False
                        self.ll1_table[key] = production
        
        print("Tabla LL(1) construida exitosamente.")
        self.print_ll1_table()
        return True
    
    def print_ll1_table(self) -> None:
        """
        Imprime la tabla de análisis LL(1) de forma legible.
        """
        print("\n=== TABLA LL(1) ===")
        
        if not self.ll1_table:
            print("Tabla LL(1) vacía.")
            return
        
        # Obtener todos los terminales y no terminales únicos
        terminals = sorted(self.terminals - {self.epsilon})
        nonterminals = sorted(self.nonterminals)
        
        # Crear encabezados
        print(f"{'No Terminal':<12}", end="")
        for terminal in terminals:
            print(f"{terminal:<8}", end="")
        print()
        
        # Imprimir separador
        print("-" * (12 + 8 * len(terminals)))
        
        # Imprimir filas
        for nonterminal in nonterminals:
            print(f"{nonterminal:<12}", end="")
            for terminal in terminals:
                key = (nonterminal, terminal)
                if key in self.ll1_table:
                    production = self.ll1_table[key]
                    prod_str = " ".join(production) if production != [self.epsilon] else "ε"
                    print(f"{prod_str:<8}", end="")
                else:
                    print(f"{'':<8}", end="")
            print()
        
        print()
    
    def compute_first_of_string(self, symbols: List[str]) -> Set[str]:
        """
        Calcula First para una cadena de símbolos.
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Conjunto First de la cadena
        """
        if not symbols:
            return {self.epsilon}
        
        first_set = set()
        i = 0
        
        while i < len(symbols):
            symbol = symbols[i]
            first_set.update(self.first_sets[symbol] - {self.epsilon})
            
            if self.epsilon not in self.first_sets[symbol]:
                break
            
            i += 1
        
        # Si todos los símbolos pueden derivar epsilon
        if i == len(symbols):
            first_set.add(self.epsilon)
        
        return first_set
    
    def parse(self, input_string: str) -> bool:
        """
        Analiza una cadena usando el parser LL(1).
        
        Args:
            input_string: Cadena a analizar
            
        Returns:
            True si la cadena es aceptada, False en caso contrario
        """
        # Agregar símbolo de fin
        input_string += self.end_marker
        
        # Pila de análisis
        stack = [self.end_marker, 'S']  # Símbolo inicial
        input_pos = 0
        
        while stack:
            top = stack[-1]
            current_input = input_string[input_pos] if input_pos < len(input_string) else self.end_marker
            
            if top == current_input == self.end_marker:
                return True
            
            if top == current_input:
                stack.pop()
                input_pos += 1
            elif top in self.terminals:
                return False
            else:
                # No terminal
                key = (top, current_input)
                if key not in self.ll1_table:
                    return False
                
                production = self.ll1_table[key]
                stack.pop()
                
                # Agregar símbolos de la producción en orden inverso
                if production != [self.epsilon]:
                    for symbol in reversed(production):
                        stack.append(symbol)
        
        return False
