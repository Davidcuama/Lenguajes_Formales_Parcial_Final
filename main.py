#!/usr/bin/env python3
"""
Módulo principal del parser de gramáticas
Orquesta todos los componentes del sistema
"""

import sys
from collections import defaultdict
from typing import Dict, List, Set

from first_follow import FirstFollowCalculator
from ll1_parser import LL1Parser
from slr1_parser import SLR1Parser


class GrammarParser:
    """
    Clase principal que orquesta el análisis de gramáticas
    """
    
    def __init__(self):
        """Inicializa el parser con estructuras de datos necesarias."""
        # Estructuras para almacenar la gramática
        self.productions: Dict[str, List[List[str]]] = defaultdict(list)
        self.nonterminals: Set[str] = set()
        self.terminals: Set[str] = set()
        self.start_symbol: str = 'S'
        
        # Símbolos especiales
        self.epsilon = 'e'  # Representa la cadena vacía
        self.end_marker = '$'  # Marcador de fin de cadena
    
    def read_grammar(self) -> None:
        """
        Lee la gramática desde la entrada estándar.
        
        Formato esperado:
        - Primera línea: número de no terminales n
        - Siguientes n líneas: reglas de producción en formato A -> α β γ
        """
        try:
            n = int(input().strip())
            
            for _ in range(n):
                line = input().strip()
                if not line:
                    continue
                    
                # Parsear la línea de producción
                parts = line.split('->')
                if len(parts) != 2:
                    raise ValueError(f"Formato inválido en línea: {line}")
                
                left_side = parts[0].strip()
                right_side = parts[1].strip()
                
                # Agregar no terminal
                self.nonterminals.add(left_side)
                
                # Parsear el lado derecho
                if right_side == self.epsilon:
                    # Producción epsilon
                    production = [self.epsilon]
                else:
                    # Dividir por espacios
                    production = right_side.split()
                
                self.productions[left_side].append(production)
                
                # Agregar terminales y no terminales del lado derecho
                for symbol in production:
                    if symbol != self.epsilon:
                        if symbol.isupper():
                            self.nonterminals.add(symbol)
                        else:
                            self.terminals.add(symbol)
            
            # Agregar símbolo de fin de cadena
            self.terminals.add(self.end_marker)
            
            print(f"Gramática leída exitosamente:")
            print(f"No terminales: {sorted(self.nonterminals)}")
            print(f"Terminales: {sorted(self.terminals)}")
            print(f"Producciones:")
            for nt, prods in self.productions.items():
                for prod in prods:
                    print(f"  {nt} -> {' '.join(prod)}")
            print()
            
        except Exception as e:
            print(f"Error al leer la gramática: {e}")
            sys.exit(1)
    
    def run(self) -> None:
        """
        Función principal que ejecuta el programa según las especificaciones.
        """
        print("=== PARSER DE GRAMÁTICAS LL(1) Y SLR(1) ===")
        print()
        
        # Leer gramática
        self.read_grammar()
        
        # Calcular conjuntos First y Follow
        calculator = FirstFollowCalculator(
            self.productions, self.nonterminals, self.terminals
        )
        first_sets = calculator.compute_first_sets()
        follow_sets = calculator.compute_follow_sets(self.start_symbol)
        
        # Crear parsers
        ll1_parser = LL1Parser(
            self.productions, self.nonterminals, self.terminals,
            first_sets, follow_sets
        )
        
        slr1_parser = SLR1Parser(
            self.productions, self.nonterminals, self.terminals,
            first_sets, follow_sets
        )
        
        # Determinar tipo de gramática
        is_ll1 = ll1_parser.is_ll1()
        is_slr1 = slr1_parser.is_slr1()
        
        print(f"\nResultado del análisis:")
        print(f"Es LL(1): {is_ll1}")
        print(f"Es SLR(1): {is_slr1}")
        print()
        
        # Manejar casos según especificaciones
        if is_ll1 and is_slr1:
            # Caso 1: Ambos parsers disponibles
            self.handle_both_parsers(ll1_parser, slr1_parser)
        elif is_ll1 and not is_slr1:
            # Caso 2: Solo LL(1)
            self.handle_ll1_only(ll1_parser)
        elif not is_ll1 and is_slr1:
            # Caso 3: Solo SLR(1)
            self.handle_slr1_only(slr1_parser)
        else:
            # Caso 4: Ninguno
            self.handle_no_parsers()
    
    def handle_both_parsers(self, ll1_parser: LL1Parser, slr1_parser: SLR1Parser) -> None:
        """Maneja el caso donde ambos parsers están disponibles."""
        print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
        
        while True:
            choice = input().strip().upper()
            
            if choice == 'Q':
                break
            elif choice == 'T':
                ll1_parser.build_ll1_table()
                self.parse_strings_ll1(ll1_parser)
            elif choice == 'B':
                slr1_parser.print_slr1_tables()
                self.parse_strings_slr1(slr1_parser)
            else:
                print("Opción inválida. Use T, B o Q.")
                continue
            
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
    
    def handle_ll1_only(self, ll1_parser: LL1Parser) -> None:
        """Maneja el caso donde solo LL(1) está disponible."""
        print("Grammar is LL(1) (SLR(1) not available).")
        print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
        
        while True:
            choice = input().strip().upper()
            
            if choice == 'Q':
                break
            elif choice == 'T':
                ll1_parser.build_ll1_table()
                self.parse_strings_ll1(ll1_parser)
            elif choice == 'B':
                print("No es posible usar SLR(1) parser.")
            else:
                print("Opción inválida. Use T, B o Q.")
                continue
            
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
    
    def handle_slr1_only(self, slr1_parser: SLR1Parser) -> None:
        """Maneja el caso donde solo SLR(1) está disponible."""
        print("Grammar is SLR(1) (LL(1) not available).")
        print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
        
        while True:
            choice = input().strip().upper()
            
            if choice == 'Q':
                break
            elif choice == 'T':
                print("No es posible usar LL(1) parser.")
            elif choice == 'B':
                slr1_parser.print_slr1_tables()
                self.parse_strings_slr1(slr1_parser)
            else:
                print("Opción inválida. Use T, B o Q.")
                continue
            
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
    
    def handle_no_parsers(self) -> None:
        """Maneja el caso donde ningún parser está disponible."""
        print("Grammar is neither LL(1) nor SLR(1).")
        print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
        
        while True:
            choice = input().strip().upper()
            
            if choice == 'Q':
                break
            elif choice == 'T':
                print("No es posible usar LL(1) parser.")
            elif choice == 'B':
                print("No es posible usar SLR(1) parser.")
            else:
                print("Opción inválida. Use T, B o Q.")
                continue
            
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
    
    def parse_strings_ll1(self, ll1_parser: LL1Parser) -> None:
        """Analiza cadenas usando LL(1)."""
        while True:
            try:
                input_string = input().strip()
                if not input_string:
                    break
                
                result = ll1_parser.parse(input_string)
                print("yes" if result else "no")
            except EOFError:
                break
    
    def parse_strings_slr1(self, slr1_parser: SLR1Parser) -> None:
        """Analiza cadenas usando SLR(1)."""
        while True:
            try:
                input_string = input().strip()
                if not input_string:
                    break
                
                result = slr1_parser.parse(input_string)
                print("yes" if result else "no")
            except EOFError:
                break


def main():
    """Función principal del programa."""
    parser = GrammarParser()
    parser.run()


if __name__ == "__main__":
    main()
