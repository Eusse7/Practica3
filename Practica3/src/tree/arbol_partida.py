# src/tree/arbol_partida.py

from collections import deque # Para usar una cola eficiente (FIFO)
from .nodo_arbol import NodoArbol # Importación relativa

# Asumimos que las clases Turno y Movimiento están definidas,
# aunque no las usemos directamente aquí más que para type hinting si fuera necesario.
# from ..core.turno import Turno # Ejemplo si se necesitara el tipo Turno

class ArbolBinarioPartida:
    """
    Construye y maneja la representación de una partida de ajedrez
    como un árbol binario entrelazado por turnos.

    La estructura del árbol se basa en la descripción:
    - La raíz es "Partida".
    - Cada turno (compuesto por jugada blanca y jugada negra) se añade como hijos
      del siguiente nodo padre disponible en el árbol, siguiendo un orden similar
      a una construcción por niveles (breadth-first).
    - La jugada blanca del turno es el hijo izquierdo.
    - La jugada negra del turno es el hijo derecho.
    """

    def __init__(self):
        """
        Inicializa el árbol con un nodo raíz etiquetado como "Partida".
        """
        self.raiz = NodoArbol("Partida")

    def construir_arbol(self, turnos_validados):
        """
        Construye el árbol binario a partir de una lista de objetos Turno validados.

        Args:
            turnos_validados (list): Una lista de objetos Turno que ya han sido
                                     validados sintácticamente y de los cuales se extraerán
                                     las cadenas de las jugadas.
                                     Se espera que cada objeto Turno tenga atributos
                                     `jugada_blanca` (un objeto Movimiento) y
                                     `jugada_negra` (un objeto Movimiento o None),
                                     y que estos objetos Movimiento tengan un atributo
                                     `san_string`.

        Returns:
            NodoArbol: El nodo raíz del árbol construido.
        """
        if not turnos_validados:
            # Si no hay turnos, el árbol solo consiste en la raíz "Partida".
            return self.raiz

        # Cola para gestionar los nodos padres a los que se añadirán los siguientes hijos.
        # Se inicializa con la raíz.
        nodos_padre_potenciales = deque([self.raiz])

        for turno_actual in turnos_validados:
            if not nodos_padre_potenciales:
                # Esto no debería ocurrir si la lógica es correcta y hay turnos para procesar,
                # a menos que la partida sea más larga que los nodos padres disponibles
                # (lo cual indicaría un problema en cómo se forma el árbol o la entrada).
                print("Advertencia: Se agotaron los nodos padre potenciales antes de procesar todos los turnos.")
                break

            # Obtener el siguiente nodo de la cola que actuará como padre para este turno.
            padre_actual = nodos_padre_potenciales.popleft()

            # Crear el nodo para la jugada blanca del turno actual.
            # Se asume que turno_actual.jugada_blanca es un objeto Movimiento
            # y tiene un atributo san_string.
            if turno_actual.jugada_blanca and hasattr(turno_actual.jugada_blanca, 'san_string'):
                nodo_blanca = NodoArbol(turno_actual.jugada_blanca.san_string)
                padre_actual.izquierda = nodo_blanca
                nodos_padre_potenciales.append(nodo_blanca) # Este nodo puede ser padre en el futuro.
            else:
                # Esto sería inesperado si el turno está validado y tiene jugada blanca.
                # Se podría añadir un nodo placeholder o manejar el error.
                print(f"Advertencia: Turno {turno_actual.numero_turno} no tiene jugada blanca válida para el árbol.")


            # Crear el nodo para la jugada negra del turno actual, si existe y es válida.
            if turno_actual.jugada_negra and hasattr(turno_actual.jugada_negra, 'san_string') and turno_actual.jugada_negra.es_valido:
                nodo_negra = NodoArbol(turno_actual.jugada_negra.san_string)
                padre_actual.derecha = nodo_negra
                nodos_padre_potenciales.append(nodo_negra) # Este nodo también puede ser padre.
            elif padre_actual.izquierda is not None and (turno_actual.jugada_negra is None or not turno_actual.jugada_negra.es_valido):
                # Si hay jugada blanca pero no hay jugada negra válida (ej. fin de partida),
                # el hijo derecho del padre_actual permanece None.
                pass
            elif padre_actual.izquierda is None and turno_actual.jugada_negra and hasattr(turno_actual.jugada_negra, 'san_string'):
                 # Caso anómalo: jugada negra sin jugada blanca en el turno (no debería pasar la validación de Turno)
                 print(f"Advertencia: Turno {turno_actual.numero_turno} tiene jugada negra pero no blanca válida para el árbol.")


        return self.raiz

    def imprimir_arbol_consola(self, nodo=None, nivel=0, prefijo="R:"):
        """
        Imprime una representación textual del árbol en la consola (para depuración).
        Realiza un recorrido preorden.

        Args:
            nodo (NodoArbol, optional): El nodo actual desde el cual imprimir.
                                        Si es None, comienza desde la raíz.
            nivel (int, optional): El nivel actual de profundidad en el árbol (para indentación).
            prefijo (str, optional): Un prefijo para indicar la relación del nodo (Raíz, Izquierda, Derecha).
        """
        if nodo is None and nivel == 0: # Llamada inicial
            nodo = self.raiz

        if nodo is not None:
            print(" " * (nivel * 4) + prefijo + str(nodo.valor))
            if nodo.izquierda is not None or nodo.derecha is not None: # Solo imprimir hijos si existen
                self.imprimir_arbol_consola(nodo.izquierda, nivel + 1, "L:")
                # Solo intentar imprimir el hijo derecho si el izquierdo existe o si el derecho existe
                # para evitar imprimir "R: None" innecesariamente si solo hay hijo izquierdo.
                if nodo.derecha is not None or (nodo.izquierda is not None and nodo.derecha is None):
                     self.imprimir_arbol_consola(nodo.derecha, nivel + 1, "R:")
                elif nodo.derecha is not None: # Si solo existe el derecho (raro pero posible)
                     self.imprimir_arbol_consola(nodo.derecha, nivel + 1, "R:")


    def obtener_nodos_y_aristas_para_visualizacion(self, nodo=None, nodos_lista=None, aristas_lista=None, id_padre=None, x=0, y=0, nivel_map=None):
        """
        Prepara una lista de nodos y aristas con coordenadas básicas para una visualización simple.
        Este es un ejemplo muy básico y probablemente necesites algo más sofisticado para PyQt.

        Retorna:
            (list, list): Tupla conteniendo (lista_de_nodos, lista_de_aristas)
                          Cada nodo: {'id': int, 'label': str, 'x': int, 'y': int}
                          Cada arista: {'from': int, 'to': int}
        """
        if nodo is None:
            nodo = self.raiz
            nodos_lista = []
            aristas_lista = []
            self._node_id_counter = 0 # Para IDs únicos
            nivel_map = {0:0} # Para calcular x offset por nivel


        node_id = self._node_id_counter
        nodos_lista.append({'id': node_id, 'label': str(nodo.valor), 'x': x, 'y': y})
        self._node_id_counter += 1

        if id_padre is not None:
            aristas_lista.append({'from': id_padre, 'to': node_id})

        # Ajustes simples para espaciado (esto es muy básico)
        espacio_horizontal = 100
        espacio_vertical = 80

        if nivel_map.get(y + espacio_vertical) is None:
            nivel_map[y + espacio_vertical] = 0
        else:
            nivel_map[y + espacio_vertical] += espacio_horizontal


        if nodo.izquierda:
            self.obtener_nodos_y_aristas_para_visualizacion(
                nodo.izquierda, nodos_lista, aristas_lista, node_id,
                x - espacio_horizontal // (2**(y//espacio_vertical +1)) + nivel_map[y+espacio_vertical]//2, # Ajuste de X
                y + espacio_vertical,
                nivel_map
            )
        if nodo.derecha:
            self.obtener_nodos_y_aristas_para_visualizacion(
                nodo.derecha, nodos_lista, aristas_lista, node_id,
                x + espacio_horizontal // (2**(y//espacio_vertical +1)) + nivel_map[y+espacio_vertical]//2, # Ajuste de X
                y + espacio_vertical,
                nivel_map
            )

        return nodos_lista, aristas_lista

