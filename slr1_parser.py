#!/usr/bin/env python3
"""
Módulo para parser SLR(1)
Implementa análisis sintáctico ascendente
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional


class SLR1Parser:
    """
    Clase especializada en análisis SLR(1)
    """
    
    def __init__(self, productions: Dict[str, List[List[str]]], 
                 nonterminals: Set[str], terminals: Set[str],
                 first_sets: Dict[str, Set[str]], 
                 follow_sets: Dict[str, Set[str]]):
        """
        Inicializa el parser SLR(1)
        
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
        
        # Estados y tablas SLR(1)
        self.slr1_states: List[Dict] = []
        self.slr1_gotos: Dict[Tuple[int, str], int] = {}
        self.slr1_actions: Dict[Tuple[int, str], str] = {}
    
    def is_slr1(self) -> bool:
        """
        Determina si la gramática es SLR(1).
        
        Returns:
            True si la gramática es SLR(1), False en caso contrario
        """
        print("Verificando si la gramática es SLR(1)...")
        
        # Construir estados SLR(1)
        if not self.build_slr1_states():
            print("Error al construir estados SLR(1).")
            return False
        
        print(f"Estados construidos: {len(self.slr1_states)}")
        
        # Verificar conflictos
        conflictos_encontrados = 0
        for state in self.slr1_states:
            for symbol in self.terminals | self.nonterminals:
                actions = []
                
                # Acciones de shift
                if (state['id'], symbol) in self.slr1_actions:
                    action = self.slr1_actions[(state['id'], symbol)]
                    if action.startswith('s'):
                        actions.append(action)
                
                # Acciones de reduce
                for item in state['items']:
                    if item['dot'] == len(item['production']):
                        # Item completo
                        if symbol in self.follow_sets[item['left']]:
                            actions.append(f"r{item['production_id']}")
                
                if len(actions) > 1:
                    print(f"Conflicto SLR(1) en estado {state['id']} con símbolo {symbol}: {actions}")
                    conflictos_encontrados += 1
        
        if conflictos_encontrados > 0:
            print(f"Total de conflictos encontrados: {conflictos_encontrados}")
            print("La gramática NO es SLR(1).")
            return False
        
        print("La gramática es SLR(1).")
        return True
    
    def build_slr1_states(self) -> bool:
        """
        Construye los estados del autómata SLR(1).
        
        Returns:
            True si se construye exitosamente, False en caso contrario
        """
        print("Construyendo estados SLR(1)...")
        
        # Crear producción aumentada
        augmented_start = "S'"
        self.productions[augmented_start] = [['S']]
        
        # Estado inicial
        initial_item = {
            'left': augmented_start,
            'production': ['S'],
            'dot': 0,
            'production_id': 0
        }
        
        initial_state = {
            'id': 0,
            'items': [initial_item]
        }
        
        self.slr1_states = [initial_state]
        self.slr1_gotos = {}
        self.slr1_actions = {}
        
        # Construir estados usando closure y goto
        state_id = 0
        
        while state_id < len(self.slr1_states):
            current_state = self.slr1_states[state_id]
            
            # Calcular closure
            closure_items = self.compute_closure(current_state['items'])
            current_state['items'] = closure_items
            
            # Calcular goto para cada símbolo
            for symbol in self.terminals | self.nonterminals:
                goto_items = self.compute_goto(closure_items, symbol)
                
                if goto_items:
                    # Buscar si ya existe un estado con estos items
                    existing_state_id = self.find_state_with_items(goto_items)
                    
                    if existing_state_id is None:
                        # Crear nuevo estado
                        new_state = {
                            'id': len(self.slr1_states),
                            'items': goto_items
                        }
                        self.slr1_states.append(new_state)
                        existing_state_id = new_state['id']
                    
                    # Agregar transición
                    self.slr1_gotos[(state_id, symbol)] = existing_state_id
                    
                    # Agregar acción
                    if symbol in self.terminals:
                        self.slr1_actions[(state_id, symbol)] = f"s{existing_state_id}"
            
            state_id += 1
        
        return True
    
    def compute_closure(self, items: List[Dict]) -> List[Dict]:
        """
        Calcula el closure de un conjunto de items.
        
        Args:
            items: Lista de items iniciales
            
        Returns:
            Lista de items con closure aplicado
        """
        closure = items.copy()
        changed = True
        
        while changed:
            changed = False
            
            for item in closure:
                if item['dot'] < len(item['production']):
                    next_symbol = item['production'][item['dot']]
                    
                    if next_symbol in self.nonterminals:
                        # Agregar items para este no terminal
                        for production in self.productions[next_symbol]:
                            new_item = {
                                'left': next_symbol,
                                'production': production,
                                'dot': 0,
                                'production_id': self.get_production_id(next_symbol, production)
                            }
                            
                            if new_item not in closure:
                                closure.append(new_item)
                                changed = True
        
        return closure
    
    def compute_goto(self, items: List[Dict], symbol: str) -> List[Dict]:
        """
        Calcula goto(I, X) para un conjunto de items I y símbolo X.
        
        Args:
            items: Conjunto de items
            symbol: Símbolo
            
        Returns:
            Conjunto de items resultante
        """
        goto_items = []
        
        for item in items:
            if (item['dot'] < len(item['production']) and 
                item['production'][item['dot']] == symbol):
                
                new_item = {
                    'left': item['left'],
                    'production': item['production'],
                    'dot': item['dot'] + 1,
                    'production_id': item['production_id']
                }
                goto_items.append(new_item)
        
        return self.compute_closure(goto_items)
    
    def find_state_with_items(self, items: List[Dict]) -> Optional[int]:
        """
        Busca un estado existente con los mismos items.
        
        Args:
            items: Lista de items a buscar
            
        Returns:
            ID del estado si existe, None en caso contrario
        """
        for state in self.slr1_states:
            if len(state['items']) == len(items):
                if all(item in state['items'] for item in items):
                    return state['id']
        return None
    
    def get_production_id(self, left: str, production: List[str]) -> int:
        """
        Obtiene el ID único de una producción.
        
        Args:
            left: Lado izquierdo de la producción
            production: Lado derecho de la producción
            
        Returns:
            ID único de la producción
        """
        # Implementación simple: usar hash
        return hash((left, tuple(production))) % 1000
    
    def print_slr1_tables(self) -> None:
        """
        Imprime las tablas de análisis SLR(1) de forma legible.
        """
        print("\n=== TABLAS SLR(1) ===")
        
        if not self.slr1_states:
            print("Estados SLR(1) no construidos.")
            return
        
        # Tabla ACTION
        print("\n--- TABLA ACTION ---")
        terminals = sorted(self.terminals)
        
        # Encabezados
        print(f"{'Estado':<8}", end="")
        for terminal in terminals:
            print(f"{terminal:<8}", end="")
        print()
        
        # Separador
        print("-" * (8 + 8 * len(terminals)))
        
        # Filas
        for state in self.slr1_states:
            state_id = state['id']
            print(f"{state_id:<8}", end="")
            for terminal in terminals:
                key = (state_id, terminal)
                if key in self.slr1_actions:
                    action = self.slr1_actions[(state_id, terminal)]
                    print(f"{action:<8}", end="")
                else:
                    print(f"{'':<8}", end="")
            print()
        
        # Tabla GOTO
        print("\n--- TABLA GOTO ---")
        nonterminals = sorted(self.nonterminals)
        
        # Encabezados
        print(f"{'Estado':<8}", end="")
        for nonterminal in nonterminals:
            print(f"{nonterminal:<8}", end="")
        print()
        
        # Separador
        print("-" * (8 + 8 * len(nonterminals)))
        
        # Filas
        for state in self.slr1_states:
            state_id = state['id']
            print(f"{state_id:<8}", end="")
            for nonterminal in nonterminals:
                key = (state_id, nonterminal)
                if key in self.slr1_gotos:
                    goto_state = self.slr1_gotos[(state_id, nonterminal)]
                    print(f"{goto_state:<8}", end="")
                else:
                    print(f"{'':<8}", end="")
            print()
        
        print()
    
    def parse(self, input_string: str) -> bool:
        """
        Analiza una cadena usando el parser SLR(1).
        
        Args:
            input_string: Cadena a analizar
            
        Returns:
            True si la cadena es aceptada, False en caso contrario
        """
        # Agregar símbolo de fin
        input_string += self.end_marker
        
        # Pila de análisis
        stack = [0]  # Estado inicial
        input_pos = 0
        
        while True:
            current_state = stack[-1]
            current_input = input_string[input_pos] if input_pos < len(input_string) else self.end_marker
            
            if (current_state, current_input) in self.slr1_actions:
                action = self.slr1_actions[(current_state, current_input)]
                
                if action.startswith('s'):
                    # Shift
                    next_state = int(action[1:])
                    stack.append(next_state)
                    input_pos += 1
                elif action.startswith('r'):
                    # Reduce
                    production_id = int(action[1:])
                    production = self.get_production_by_id(production_id)
                    
                    if production:
                        # Pop símbolos de la pila
                        for _ in range(len(production[1])):
                            if len(stack) > 1:
                                stack.pop()
                        
                        # Goto
                        goto_state = stack[-1]
                        if (goto_state, production[0]) in self.slr1_gotos:
                            next_state = self.slr1_gotos[(goto_state, production[0])]
                            stack.append(next_state)
                        else:
                            return False
                    else:
                        return False
                elif action == 'accept':
                    return True
                else:
                    return False
            else:
                return False
    
    def get_production_by_id(self, production_id: int) -> Optional[Tuple[str, List[str]]]:
        """
        Obtiene una producción por su ID.
        
        Args:
            production_id: ID de la producción
            
        Returns:
            Tupla (lado_izquierdo, lado_derecho) o None si no se encuentra
        """
        for left, productions in self.productions.items():
            for production in productions:
                if self.get_production_id(left, production) == production_id:
                    return (left, production)
        return None
