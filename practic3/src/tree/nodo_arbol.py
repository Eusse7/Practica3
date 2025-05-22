# src/tree/nodo_arbol.py

class NodoArbol:
    """
    Representa un nodo en el árbol binario de la partida de ajedrez.
    Cada nodo puede almacenar una jugada (como una cadena SAN) o la etiqueta "Partida" para la raíz.
    """
    def __init__(self, valor):
        """
        Inicializa un nuevo nodo del árbol.

        Args:
            valor (str): El valor que almacenará el nodo. Usualmente una jugada en notación SAN
                         o la cadena "Partida" para el nodo raíz.
        """
        self.valor = valor
        self.izquierda = None  # Hijo izquierdo, representa la jugada blanca del siguiente nivel/turno.
        self.derecha = None    # Hijo derecho, representa la jugada negra del siguiente nivel/turno.

    def __str__(self):
        """Representación en cadena del valor del nodo."""
        return str(self.valor)

    def __repr__(self):
        """Representación oficial del objeto NodoArbol."""
        return f"NodoArbol(valor='{self.valor}')"

