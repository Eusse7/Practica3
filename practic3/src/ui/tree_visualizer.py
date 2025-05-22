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
        self.root_node = None
        self.node_positions = {}
        
        self.node_radius = 22
        self.horizontal_spacing = 35
        self.vertical_spacing = 75
        self.tree_padding = 30

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(300, 200) 
        # Fondo del visualizador - Madera clara, igual que QScrollArea
        self.setStyleSheet("background-color: #C8AD7F;") 


        # Definición de colores para los elementos del árbol (tema Ajedrez)
        self.color_raiz = QColor("#8B4513")         # Marrón silla de montar (como pieza oscura)
        self.color_jugada_blanca = QColor("#F0D9B5")  # Crema (Pieza blanca)
        self.color_jugada_negra = QColor("#5C3A21")   # Marrón muy oscuro (Pieza negra)
        self.color_borde_nodo = QColor("#4A3B31")   # Borde marrón oscuro para contraste
        self.color_linea = QColor("#6B4226")      # Líneas color madera oscura
        self.color_texto_en_blanco = QColor("#3D291F") # Texto oscuro para nodos claros (blancos/raíz si es clara)
        self.color_texto_en_negro = QColor("#F0D9B5")   # Texto crema para nodos oscuros (negros/raíz si es oscura)
        self.font_nodo = QFont("Segoe UI", 8, QFont.Bold)

    def set_tree_data(self, root_node: NodoArbol):
        """
        Establece el nodo raíz del árbol que se va a dibujar.
        Limpia las posiciones anteriores, recalcula las nuevas y ajusta el tamaño del widget.
        """
        self.root_node = root_node
        self.node_positions.clear()
        if self.root_node:
            # La y_pos inicial incluye el padding superior.
            # El x_offset inicial es 0; las posiciones calculadas pueden ser negativas o positivas.
            self._calculate_node_positions_recursive(self.root_node, 
                                                     x_offset=0, 
                                                     y_pos=self.node_radius + self.tree_padding, 
                                                     level_width_map={})
            self._adjust_widget_size_to_tree_content()
        else:
            # Si no hay árbol, restaurar un tamaño mínimo pequeño.
            self.setMinimumSize(300, 200) 
            self.updateGeometry() # Notificar al layout
        self.update() # Solicitar redibujo

    def _adjust_widget_size_to_tree_content(self):
        """
        Calcula el bounding box del árbol basado en node_positions
        y ajusta el minimumSize del widget para que contenga el árbol más un padding.
        """
        if not self.node_positions:
            self.setMinimumSize(300, 200)
            self.updateGeometry()
            return

        min_x_bbox = float('inf')
        max_x_bbox = float('-inf')
        min_y_bbox = float('inf')
        max_y_bbox = float('-inf')

        for pos in self.node_positions.values():
            min_x_bbox = min(min_x_bbox, pos.x() - self.node_radius)
            max_x_bbox = max(max_x_bbox, pos.x() + self.node_radius)
            min_y_bbox = min(min_y_bbox, pos.y() - self.node_radius)
            max_y_bbox = max(max_y_bbox, pos.y() + self.node_radius)
        
        if not self.node_positions: # Debería ser redundante, pero por seguridad
             self.setMinimumSize(300,200)
             self.updateGeometry()
             return

        tree_content_width = max_x_bbox - min_x_bbox
        tree_content_height = max_y_bbox - min_y_bbox
        
        # El tamaño mínimo del widget será el tamaño del contenido del árbol más el padding en todos los lados.
        # Como min_y_bbox ya incluye el padding superior inicial (desde y_pos en _calculate_node_positions_recursive),
        # y las posiciones son relativas, el alto total es tree_content_height.
        # El padding se aplica al ancho total y al alto total.
        # Sin embargo, y_pos en _calculate_node_positions_recursive es el *centro* del nodo.
        # min_y_bbox es el borde superior del nodo más alto.
        # El y_pos inicial en _calculate_node_positions_recursive es self.node_radius + self.tree_padding.
        # Esto significa que min_y_bbox debería ser self.tree_padding.
        
        # El ancho necesario es el ancho del contenido + padding a cada lado.
        # La altura necesaria es la altura del contenido + padding arriba y abajo.
        # Las posiciones en self.node_positions son relativas a un origen (0,0) conceptual
        # donde el primer nodo se coloca en (x_offset, y_pos).
        # min_x_bbox, max_x_bbox, min_y_bbox, max_y_bbox definen el rectángulo que encierra todos los nodos.

        new_min_width = int(tree_content_width + 2 * self.tree_padding)
        new_min_height = int(tree_content_height + 2 * self.tree_padding)
        
        self.setMinimumSize(new_min_width, new_min_height)
        self.updateGeometry() # Informar al sistema de layout sobre el cambio de tamaño preferido.

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
        Aquí se realiza todo el dibujo del árbol, centrado en el widget.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.root_node or not self.node_positions:
            painter.setPen(QPen(QColor("#D8DEE9")))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(self.rect(), Qt.AlignCenter, "Cargue una partida SAN válida para ver el árbol.")
            return

        # Calcular el bounding box del contenido del árbol (en sus coordenadas locales)
        tree_min_x_bbox = float('inf')
        tree_max_x_bbox = float('-inf')
        tree_min_y_bbox = float('inf')
        tree_max_y_bbox = float('-inf')

        for pos in self.node_positions.values():
            tree_min_x_bbox = min(tree_min_x_bbox, pos.x() - self.node_radius)
            tree_max_x_bbox = max(tree_max_x_bbox, pos.x() + self.node_radius)
            tree_min_y_bbox = min(tree_min_y_bbox, pos.y() - self.node_radius)
            tree_max_y_bbox = max(tree_max_y_bbox, pos.y() + self.node_radius)
        
        if not self.node_positions: return # Seguridad

        tree_content_width = tree_max_x_bbox - tree_min_x_bbox
        tree_content_height = tree_max_y_bbox - tree_min_y_bbox

        # Calcular desplazamientos para centrar el contenido del árbol (tree_content_width/height)
        # dentro del widget actual (self.width()/height()).
        # El offset_x_global es la cantidad a sumar a las coordenadas X originales del árbol
        # para que el tree_min_x_bbox (borde izquierdo del árbol) se alinee con el inicio del área de centrado.
        offset_x_global = (self.width() - tree_content_width) / 2.0 - tree_min_x_bbox
        offset_y_global = (self.height() - tree_content_height) / 2.0 - tree_min_y_bbox
        
        # Dibujar aristas y nodos con estos offsets globales.
        self._draw_edges_recursive(painter, self.root_node, offset_x_global, offset_y_global)
        self._draw_nodes_recursive(painter, self.root_node, None, offset_x_global, offset_y_global)

    def _draw_edges_recursive(self, painter, node, offset_x, offset_y):
        """Dibuja recursivamente las aristas (líneas) del árbol."""
        if node is None or id(node) not in self.node_positions:
            return

        pos_actual_nodo = self.node_positions[id(node)] + QPointF(offset_x, offset_y)

        painter.setPen(QPen(self.color_linea, 2, Qt.SolidLine)) # Configurar pluma para las líneas, un poco más gruesa

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
        rect_nodo = QRectF(pos_nodo_centro.x() - self.node_radius,
                             pos_nodo_centro.y() - self.node_radius,
                             2 * self.node_radius, 2 * self.node_radius)

        color_relleno_actual = self.color_jugada_blanca
        texto_color_actual = self.color_texto_en_blanco

        if node.valor == "Partida" or node.valor == "Partida (app.py)": # Adaptado para placeholder también
            color_relleno_actual = self.color_raiz
            texto_color_actual = self.color_texto_en_negro # Texto claro sobre raíz oscura
        elif parent_for_color_check: 
            if node == parent_for_color_check.izquierda: # Jugada blanca.
                color_relleno_actual = self.color_jugada_blanca
                texto_color_actual = self.color_texto_en_blanco # Texto oscuro sobre nodo blanco
            elif node == parent_for_color_check.derecha: # Jugada negra.
                color_relleno_actual = self.color_jugada_negra
                texto_color_actual = self.color_texto_en_negro # Texto claro sobre nodo negro
        
        painter.setBrush(QBrush(color_relleno_actual))
        painter.setPen(QPen(self.color_borde_nodo, 1.5))
        painter.drawEllipse(rect_nodo)

        painter.setPen(QPen(texto_color_actual))
        painter.setFont(self.font_nodo)
        painter.drawText(rect_nodo, Qt.AlignCenter, str(node.valor))

        if node.izquierda:
            self._draw_nodes_recursive(painter, node.izquierda, node, offset_x, offset_y)
        if node.derecha:
            self._draw_nodes_recursive(painter, node.derecha, node, offset_x, offset_y)

    def resizeEvent(self, event):
        """
        Se llama cuando el widget cambia de tamaño.
        Solo necesitamos redibujar para que el centrado se actualice.
        """
        super().resizeEvent(event)
        self.update() 

    def sizeHint(self):
        """Proporciona una pista sobre el tamaño ideal del widget."""
        # El sizeHint debería reflejar el minimumSize actual, que se basa en el contenido.
        return self.minimumSize()

