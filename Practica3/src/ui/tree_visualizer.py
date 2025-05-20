# src/ui/tree_visualizer.py
from PyQt5.QtWidgets import QWidget, QSizePolicy, QLabel, QHBoxLayout
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF

# Intenta importar NodoArbol. Si falla, usa un placeholder.
# Esto es útil para pruebas aisladas o si la estructura del proyecto aún no está completa.
try:
    from ..tree.nodo_arbol import NodoArbol
except ImportError:
    # Placeholder para NodoArbol si la importación falla.
    # En una ejecución normal del proyecto, la importación relativa debería funcionar.
    class NodoArbol:
        def __init__(self, valor):
            self.valor = valor
            self.izquierda = None
            self.derecha = None
        def __str__(self):
            return str(self.valor)

class TreeVisualizerWidget(QWidget):
    """
    Un widget personalizado para dibujar el árbol binario de la partida de ajedrez.
    Hereda de QWidget y sobreescribe el método paintEvent para realizar el dibujo.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_node = None  # El nodo raíz del árbol a dibujar.
        self.node_positions = {}  # Diccionario para almacenar las coordenadas (QPointF) de cada nodo.
        
        # Parámetros de dibujo y layout
        self.node_radius = 20  # Radio de los círculos que representan los nodos.
        self.horizontal_spacing = 30  # Espacio horizontal mínimo entre nodos hermanos.
        self.vertical_spacing = 70    # Espacio vertical entre niveles del árbol.

        # Política de tamaño para que el widget se expanda con la ventana.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(600, 400) # Tamaño mínimo inicial del widget.

        # Definición de colores para los elementos del árbol (similares a la Figura 1 del PDF).
        self.color_raiz = QColor("#FFD700")         # Amarillo dorado para el nodo raíz "Partida".
        self.color_jugada_blanca = QColor("#FFFFFF")  # Blanco para nodos de jugadas blancas.
        self.color_jugada_negra = QColor("#D3D3D3")   # Gris claro para nodos de jugadas negras.
        self.color_borde_nodo = QColor("#333333")   # Gris oscuro para el borde de los nodos.
        self.color_linea = QColor("#666666")      # Gris medio para las líneas (aristas) entre nodos.
        self.color_texto = QColor("#000000")        # Negro para el texto dentro de los nodos.
        self.font_nodo = QFont("Arial", 8)          # Fuente para el texto de los nodos.

    def set_tree_data(self, root_node: NodoArbol):
        """
        Establece el nodo raíz del árbol que se va a dibujar.
        Limpia las posiciones anteriores y recalcula las nuevas si hay un nodo raíz.
        Finalmente, solicita una actualización del widget para redibujar.
        """
        self.root_node = root_node
        self.node_positions.clear() # Limpiar posiciones de nodos anteriores.
        if self.root_node:
            # Iniciar el cálculo de posiciones desde la raíz.
            # El 'x_start_offset' inicial es 0; se ajustará después para centrar.
            self._calculate_node_positions_recursive(self.root_node, x_offset=0, y_pos=self.node_radius + 20, level_width_map={})
        self.update() # Solicitar un redibujo del widget.

    def _get_subtree_leaf_count(self, node):
        """
        Calcula recursivamente el número de nodos hoja en el subárbol de 'node'.
        Esto se usa como una métrica simple para estimar el ancho del subárbol.
        """
        if node is None:
            return 0
        if node.izquierda is None and node.derecha is None:
            return 1 # Un nodo hoja cuenta como 1.
        
        return self._get_subtree_leaf_count(node.izquierda) + self._get_subtree_leaf_count(node.derecha)

    def _calculate_node_positions_recursive(self, node, x_offset, y_pos, level_width_map, current_max_x_at_level=0):
        """
        Calcula las posiciones (x, y) de los nodos de forma recursiva.
        Este es un algoritmo de layout simple. Puede requerir ajustes para árboles complejos.
        'x_offset' es el desplazamiento horizontal relativo al padre.
        'y_pos' es la coordenada y vertical para el nivel actual.
        'level_width_map' ayuda a rastrear el ancho acumulado en cada nivel para evitar solapamientos.
        """
        if node is None:
            return current_max_x_at_level

        # Estimar el ancho que ocupará el subárbol izquierdo.
        ancho_subarbol_izq_hojas = self._get_subtree_leaf_count(node.izquierda)
        # El espacio que necesita el subárbol izquierdo es su número de hojas por el espacio de un nodo.
        espacio_necesario_izq = ancho_subarbol_izq_hojas * (2 * self.node_radius + self.horizontal_spacing)

        # Calcular la posición x para el hijo izquierdo.
        x_hijo_izq = x_offset - (espacio_necesario_izq / 2.0) if node.izquierda else x_offset
        # Si hay ambos hijos, separamos un poco más.
        if node.izquierda and node.derecha:
             x_hijo_izq -= self.horizontal_spacing / 2.0


        # Recursivamente calcular posiciones para el subárbol izquierdo.
        max_x_izq = self._calculate_node_positions_recursive(node.izquierda, x_hijo_izq, y_pos + self.vertical_spacing, level_width_map, current_max_x_at_level)


        # La posición x del nodo actual se coloca después del subárbol izquierdo.
        # Si no hay hijo izquierdo, se usa el x_offset actual.
        # Si hay hijo izquierdo, el nodo actual se centra entre sus hijos o justo después del izquierdo.
        node_x_final = max_x_izq + (self.node_radius + self.horizontal_spacing / 2.0) if node.izquierda else x_offset
        if node.izquierda and node.derecha: # Centrar entre los espacios de los hijos
            ancho_subarbol_der_hojas = self._get_subtree_leaf_count(node.derecha)
            espacio_necesario_der = ancho_subarbol_der_hojas * (2 * self.node_radius + self.horizontal_spacing)
            node_x_final = x_offset # El nodo padre se queda en el x_offset original, los hijos se desplazan.


        self.node_positions[id(node)] = QPointF(node_x_final, y_pos)
        current_max_x_at_level = max(current_max_x_at_level, node_x_final + self.node_radius)


        # Calcular la posición x para el hijo derecho.
        x_hijo_der = node_x_final + (self.node_radius + self.horizontal_spacing / 2.0) if node.derecha else node_x_final
        if node.izquierda and node.derecha:
            x_hijo_der = x_offset + (espacio_necesario_izq / 2.0) + self.horizontal_spacing / 2.0

        # Recursivamente calcular posiciones para el subárbol derecho.
        max_x_der = self._calculate_node_positions_recursive(node.derecha, x_hijo_der, y_pos + self.vertical_spacing, level_width_map, current_max_x_at_level)

        return max(current_max_x_at_level, max_x_der)


    def paintEvent(self, event):
        """
        Este método se llama automáticamente cuando el widget necesita ser redibujado.
        Aquí se realiza todo el dibujo del árbol.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Habilita antialiasing para bordes suaves.

        if not self.root_node or not self.node_positions:
            # Si no hay árbol o posiciones, mostrar un mensaje.
            painter.drawText(self.rect(), Qt.AlignCenter, "Cargue una partida SAN válida para ver el árbol.")
            return

        # Calcular límites del árbol para centrarlo en el widget.
        min_x_coord = float('inf')
        max_x_coord = float('-inf')
        min_y_coord = float('inf') # Aunque y empieza positivo, es bueno tenerlo.
        max_y_coord = float('-inf')

        for pos in self.node_positions.values():
            min_x_coord = min(min_x_coord, pos.x() - self.node_radius)
            max_x_coord = max(max_x_coord, pos.x() + self.node_radius)
            min_y_coord = min(min_y_coord, pos.y() - self.node_radius)
            max_y_coord = max(max_y_coord, pos.y() + self.node_radius)

        if not self.node_positions: return # Salir si no hay posiciones calculadas.

        tree_actual_width = max_x_coord - min_x_coord
        tree_actual_height = max_y_coord - min_y_coord
        
        # Calcular desplazamientos para centrar el árbol.
        # Offset X para centrar horizontalmente.
        offset_x_global = (self.width() - tree_actual_width) / 2.0 - min_x_coord
        # Offset Y para empezar desde arriba con un margen.
        offset_y_global = self.node_radius + 10 - min_y_coord # Margen superior.

        # Ajustar el tamaño mínimo del widget si el árbol es más grande.
        # Esto ayuda a que QScrollArea funcione correctamente.
        new_min_width = int(tree_actual_width + 2 * self.node_radius) # Añadir margen
        new_min_height = int(tree_actual_height + 2 * self.node_radius)
        
        # Solo ajustar si el nuevo tamaño es mayor que el actual mínimo para evitar bucles.
        if new_min_width > self.minimumWidth() or new_min_height > self.minimumHeight():
            self.setMinimumSize(max(new_min_width, self.width()), max(new_min_height, self.height()))


        # Dibujar primero las aristas (líneas) y luego los nodos.
        self._draw_edges_recursive(painter, self.root_node, offset_x_global, offset_y_global)
        self._draw_nodes_recursive(painter, self.root_node, None, offset_x_global, offset_y_global)

    def _draw_edges_recursive(self, painter, node, offset_x, offset_y):
        """Dibuja recursivamente las aristas (líneas) del árbol."""
        if node is None or id(node) not in self.node_positions:
            return

        pos_actual_nodo = self.node_positions[id(node)] + QPointF(offset_x, offset_y)

        painter.setPen(QPen(self.color_linea, 1.5, Qt.SolidLine)) # Configurar pluma para las líneas.

        # Dibujar línea al hijo izquierdo.
        if node.izquierda and id(node.izquierda) in self.node_positions:
            pos_hijo_izq = self.node_positions[id(node.izquierda)] + QPointF(offset_x, offset_y)
            painter.drawLine(pos_actual_nodo, pos_hijo_izq)
            self._draw_edges_recursive(painter, node.izquierda, offset_x, offset_y)

        # Dibujar línea al hijo derecho.
        if node.derecha and id(node.derecha) in self.node_positions:
            pos_hijo_der = self.node_positions[id(node.derecha)] + QPointF(offset_x, offset_y)
            painter.drawLine(pos_actual_nodo, pos_hijo_der)
            self._draw_edges_recursive(painter, node.derecha, offset_x, offset_y)

    def _draw_nodes_recursive(self, painter, node, parent_for_color_check, offset_x, offset_y):
        """Dibuja recursivamente los nodos (círculos y texto) del árbol."""
        if node is None or id(node) not in self.node_positions:
            return

        pos_nodo_centro = self.node_positions[id(node)] + QPointF(offset_x, offset_y)
        # Rectángulo que define el área del círculo del nodo.
        rect_nodo = QRectF(pos_nodo_centro.x() - self.node_radius,
                             pos_nodo_centro.y() - self.node_radius,
                             2 * self.node_radius, 2 * self.node_radius)

        # Determinar el color de relleno del nodo.
        color_relleno_actual = self.color_jugada_blanca # Color por defecto.
        if node.valor == "Partida":
            color_relleno_actual = self.color_raiz
        elif parent_for_color_check: # Solo si tiene padre, para determinar si es jugada blanca o negra.
            if node == parent_for_color_check.izquierda: # Jugada blanca.
                color_relleno_actual = self.color_jugada_blanca
            elif node == parent_for_color_check.derecha: # Jugada negra.
                color_relleno_actual = self.color_jugada_negra
        
        painter.setBrush(QBrush(color_relleno_actual))
        painter.setPen(QPen(self.color_borde_nodo, 1)) # Configurar pluma para el borde del nodo.
        painter.drawEllipse(rect_nodo) # Dibujar el círculo.

        # Dibujar el texto (valor del nodo) centrado en el círculo.
        painter.setPen(QPen(self.color_texto))
        painter.setFont(self.font_nodo)
        painter.drawText(rect_nodo, Qt.AlignCenter, str(node.valor))

        # Llamadas recursivas para dibujar los hijos.
        if node.izquierda:
            self._draw_nodes_recursive(painter, node.izquierda, node, offset_x, offset_y)
        if node.derecha:
            self._draw_nodes_recursive(painter, node.derecha, node, offset_x, offset_y)

    def resizeEvent(self, event):
        """
        Se llama cuando el widget cambia de tamaño.
        Si hay un árbol cargado, se recalcula su layout y se redibuja.
        """
        super().resizeEvent(event)
        if self.root_node:
            # Recalcular posiciones con el nuevo ancho del widget como referencia para el centro.
            self.node_positions.clear()
            self._calculate_node_positions_recursive(self.root_node, x_offset=0, y_pos=self.node_radius + 20, level_width_map={})
        self.update() # Solicitar redibujo.

    def sizeHint(self):
        """Proporciona una pista sobre el tamaño ideal del widget."""
        # Podría calcularse basado en el tamaño del árbol, pero por ahora usa el mínimo.
        return self.minimumSize()

