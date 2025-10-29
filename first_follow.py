#!/usr/bin/env python3
"""
Módulo para cálculo de conjuntos First y Follow
Implementa algoritmos para gramáticas libres de contexto
"""

from collections import defaultdict
from typing import Dict, List, Set


class FirstFollowCalculator:
    """
    Clase especializada en el cálculo de conjuntos First y Follow
    """
    
    def __init__(self, productions: Dict[str, List[List[str]]], 
                 nonterminals: Set[str], terminals: Set[str]):
        """
        Inicializa el calculador con la gramática
        
        Args:
            productions: Diccionario de producciones
            nonterminals: Conjunto de no terminales
            terminals: Conjunto de terminales
        """
        self.productions = productions
        self.nonterminals = nonterminals
        self.terminals = terminals
        self.epsilon = 'e'
        
        # Conjuntos calculados
        self.first_sets: Dict[str, Set[str]] = defaultdict(set)
        self.follow_sets: Dict[str, Set[str]] = defaultdict(set)
    
    def compute_first_sets(self) -> Dict[str, Set[str]]:
        """
        Calcula los conjuntos First para todos los símbolos de la gramática.
        
        Returns:
            Diccionario con los conjuntos First
        """
        print("Calculando conjuntos First...")
        
        # Inicializar First para terminales
        for terminal in self.terminals:
            self.first_sets[terminal].add(terminal)
        
        # Inicializar First para no terminales
        for nonterminal in self.nonterminals:
            self.first_sets[nonterminal] = set()
        
        # Algoritmo iterativo para calcular First
        changed = True
        iteration = 0
        
        while changed:
            changed = False
            iteration += 1
            
            for nonterminal in self.nonterminals:
                old_size = len(self.first_sets[nonterminal])
                
                for production in self.productions[nonterminal]:
                    if production == [self.epsilon]:
                        # Regla epsilon
                        self.first_sets[nonterminal].add(self.epsilon)
                    else:
                        # Agregar First del primer símbolo
                        first_symbol = production[0]
                        self.first_sets[nonterminal].update(
                            self.first_sets[first_symbol] - {self.epsilon}
                        )
                        
                        # Si el primer símbolo puede derivar epsilon, continuar
                        i = 0
                        while (i < len(production) and 
                               self.epsilon in self.first_sets[production[i]]):
                            i += 1
                            if i < len(production):
                                self.first_sets[nonterminal].update(
                                    self.first_sets[production[i]] - {self.epsilon}
                                )
                        
                        # Si todos los símbolos pueden derivar epsilon
                        if i == len(production):
                            self.first_sets[nonterminal].add(self.epsilon)
                
                if len(self.first_sets[nonterminal]) > old_size:
                    changed = True
            
            print(f"Iteración {iteration}: First sets actualizados")
        
        # Mostrar conjuntos First
        print("\nConjuntos First:")
        for symbol in sorted(self.nonterminals | self.terminals):
            first_set = sorted(self.first_sets[symbol])
            print(f"First({symbol}) = {{{', '.join(first_set)}}}")
        print()
        
        return self.first_sets
    
    def compute_follow_sets(self, start_symbol: str = 'S') -> Dict[str, Set[str]]:
        """
        Calcula los conjuntos Follow para todos los no terminales.
        
        Args:
            start_symbol: Símbolo inicial de la gramática
            
        Returns:
            Diccionario con los conjuntos Follow
        """
        print("Calculando conjuntos Follow...")
        
        # Inicializar Follow sets
        for nonterminal in self.nonterminals:
            self.follow_sets[nonterminal] = set()
        
        # Paso 1: $ ∈ Follow(S)
        self.follow_sets[start_symbol].add('$')
        
        # Algoritmo iterativo para calcular Follow
        changed = True
        iteration = 0
        
        while changed:
            changed = False
            iteration += 1
            
            for nonterminal in self.nonterminals:
                old_size = len(self.follow_sets[nonterminal])
                
                # Buscar todas las producciones donde aparece este no terminal
                for left_side, productions in self.productions.items():
                    for production in productions:
                        for i, symbol in enumerate(production):
                            if symbol == nonterminal:
                                # Caso A -> αBβ
                                if i + 1 < len(production):
                                    beta = production[i + 1:]
                                    # Agregar First(β) - {ε} a Follow(B)
                                    first_beta = self.compute_first_of_string(beta)
                                    self.follow_sets[nonterminal].update(
                                        first_beta - {self.epsilon}
                                    )
                                    
                                    # Si ε ∈ First(β), agregar Follow(A) a Follow(B)
                                    if self.epsilon in first_beta:
                                        self.follow_sets[nonterminal].update(
                                            self.follow_sets[left_side]
                                        )
                                else:
                                    # Caso A -> αB (B está al final)
                                    self.follow_sets[nonterminal].update(
                                        self.follow_sets[left_side]
                                    )
                
                if len(self.follow_sets[nonterminal]) > old_size:
                    changed = True
            
            print(f"Iteración {iteration}: Follow sets actualizados")
        
        # Mostrar conjuntos Follow
        print("\nConjuntos Follow:")
        for nonterminal in sorted(self.nonterminals):
            follow_set = sorted(self.follow_sets[nonterminal])
            print(f"Follow({nonterminal}) = {{{', '.join(follow_set)}}}")
        print()
        
        return self.follow_sets
    
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
