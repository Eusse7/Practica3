# src/ui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLabel, QMessageBox,
                             QScrollArea, QFrame)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Importar las clases de lógica y visualización.
# Se usan bloques try-except para permitir pruebas aisladas si los módulos aún no están
# completamente integrados o si hay problemas con el PYTHONPATH durante el desarrollo.
try:
    from .tree_visualizer import TreeVisualizerWidget
    from ..core.partida import Partida
    from ..tree.arbol_partida import ArbolBinarioPartida
    from ..tree.nodo_arbol import NodoArbol # Necesario para type hinting si se usa
except ImportError:
    # Placeholders para el caso de que las importaciones fallen.
    # Esto es principalmente para desarrollo y no debería ocurrir en la aplicación final.
    class TreeVisualizerWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.placeholder_label = QLabel("TreeVisualizer Placeholder (Error de Importación)", self)
            layout = QHBoxLayout(self)
            layout.addWidget(self.placeholder_label)
            self.placeholder_label.setAlignment(Qt.AlignCenter)
        def set_tree_data(self, root_node):
            if hasattr(self, 'placeholder_label'):
                self.placeholder_label.setText(f"TreeVisualizer Placeholder: set_tree_data con nodo raíz: {root_node.valor if root_node else 'None'}")
            print(f"TreeVisualizer Placeholder: set_tree_data con nodo raíz: {root_node.valor if root_node else 'None'}")

    class Partida:
        def __init__(self, san_str):
            self.san_str = san_str
            self.turnos = [] # Lista de objetos Turno (placeholder)
            # Simulación simple de validación
            self.es_valida_sintacticamente = "error" not in san_str.lower()
            self.error_message = "Error simulado en la partida." if not self.es_valida_sintacticamente else None
            if self.es_valida_sintacticamente and san_str: # Simular algunos turnos
                # Para que ArbolBinarioPartida (placeholder) tenga algo que procesar
                class MovimientoPlaceholder:
                    def __init__(self, s): self.san_string = s; self.es_valido = True
                class TurnoPlaceholder:
                    def __init__(self, n, jb_str, jn_str=None):
                        self.numero_turno = n
                        self.jugada_blanca = MovimientoPlaceholder(jb_str)
                        self.jugada_negra = MovimientoPlaceholder(jn_str) if jn_str else None
                        self.es_valido = True
                moves = san_str.split()
                num_turno = 1
                for i in range(0, len(moves) -1, 3) : # Asume formato "N. Jb Jn"
                    if len(moves) > i+2 :
                        self.turnos.append(TurnoPlaceholder(num_turno, moves[i+1], moves[i+2]))
                    elif len(moves) > i+1:
                         self.turnos.append(TurnoPlaceholder(num_turno, moves[i+1]))
                    num_turno+=1


        def obtener_primer_error(self): return self.error_message
        def __str__(self): return f"Partida Placeholder (Válida: {self.es_valida_sintacticamente})"

    class ArbolBinarioPartida:
        def __init__(self):
            # Placeholder para NodoArbol si no se importó correctamente
            class NodoArbolPlaceholder:
                def __init__(self, valor): self.valor = valor; self.izquierda = None; self.derecha = None
            self.NodoArbolCls = NodoArbolPlaceholder
            self.raiz = None

        def construir_arbol(self, turnos_validados):
            if not turnos_validados:
                self.raiz = None
                return None
            self.raiz = self.NodoArbolCls("Partida") # Usar el placeholder de NodoArbol
            
            # Lógica de construcción de árbol placeholder muy simple
            if turnos_validados:
                current_parent = self.raiz
                for i, turno in enumerate(turnos_validados):
                    if turno.jugada_blanca:
                        current_parent.izquierda = self.NodoArbolCls(turno.jugada_blanca.san_string)
                        if turno.jugada_negra:
                            current_parent.derecha = self.NodoArbolCls(turno.jugada_negra.san_string)
                            # Para simplificar, el siguiente padre es el nodo de la jugada negra
                            current_parent = current_parent.derecha 
                        else:
                            break # Fin si no hay jugada negra
                    else:
                        break # Fin si no hay jugada blanca
            return self.raiz


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación analizadora de partidas de ajedrez.
    Configura la interfaz de usuario con áreas para entrada de texto, botones,
    y el visualizador del árbol.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Sintáctico de Partidas de Ajedrez")
        self.setGeometry(100, 100, 950, 750) # Posición x, y, ancho, alto iniciales.

        # Widget central y layout principal (vertical).
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10) # Espacio entre widgets.
        self.main_layout.setContentsMargins(10, 10, 10, 10) # Márgenes alrededor del layout.

        # --- Sección de Entrada SAN ---
        self.input_san_label = QLabel("<b>Ingrese la partida en Notación Algebraica Estándar (SAN):</b>")
        self.main_layout.addWidget(self.input_san_label)

        self.san_text_edit = QTextEdit()
        self.san_text_edit.setPlaceholderText("Ejemplo: 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 ...")
        self.san_text_edit.setFixedHeight(120) # Altura para el área de texto SAN.
        self.san_text_edit.setFont(QFont("Consolas", 10)) # Fuente monoespaciada para SAN.
        self.main_layout.addWidget(self.san_text_edit)
        
        # Ejemplo de partida para pruebas rápidas (tomado del PDF).
        self.san_text_edit.setText("1. d4 d5 2. Bf4 Nf6 3. e3 e6 4. c3 c5 5. Nd2 Nc6 6. Bd3 Bd6 7. Bg3 O-O 8. Ngf3 Qe7 9. Ne5 Nd7 10. Nxc6 bxc6 11. Bxd6 Qxd6 12. Nf3 a5 13. O-O Ba6 14. Re1 Rfb8 15. Rb1 Bxd3 16. Qxd3 c4 17. Qc2 f5 18. Nd2 Rb5 19. b3 cxb3 20. axb3 Rab8 21. Qa2 Qc7 22. c4 Rb4 23. cxd5 cxd5 24. Rbc1 Qb6 25. h3 a4 26. bxa4 Rb2 27. Qa3 Rxd2 28. Qe7 Qd8 29. Qxe6+ Kh8 30. Qxf5 Nf6")


        # --- Botón de Análisis ---
        self.analyze_button = QPushButton("Analizar Partida y Generar Árbol")
        self.analyze_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px; }"
                                          "QPushButton:hover { background-color: #45a049; }"
                                          "QPushButton:pressed { background-color: #3e8e41; }")
        self.analyze_button.clicked.connect(self._on_analyze_clicked)
        self.main_layout.addWidget(self.analyze_button)

        # --- Etiqueta de Estado/Error ---
        self.status_label = QLabel("Estado: Esperando partida.")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setFixedHeight(35)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;")
        self.main_layout.addWidget(self.status_label)

        # --- Visualizador del Árbol (dentro de un QScrollArea) ---
        self.tree_visualizer_widget = TreeVisualizerWidget()
        
        self.scroll_area = QScrollArea() # Permite scroll si el árbol es más grande que el área visible.
        self.scroll_area.setWidgetResizable(True) # El widget interior se redimensiona con el scroll area.
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.tree_visualizer_widget) # Poner el visualizador dentro del scroll.
        self.scroll_area.setFrameShape(QFrame.StyledPanel) # Añadir un borde al scroll area.
        
        self.main_layout.addWidget(self.scroll_area) # Añadir el QScrollArea al layout principal.

        self.show() # Mostrar la ventana principal.

    def _on_analyze_clicked(self):
        """
        Manejador del evento click del botón "Analizar Partida".
        Obtiene el texto SAN, lo procesa, y actualiza la UI con el resultado o errores.
        """
        san_input = self.san_text_edit.toPlainText().strip()
        if not san_input:
            QMessageBox.warning(self, "Entrada Vacía", "Por favor, ingrese una partida en notación SAN.")
            self.status_label.setText("Estado: Error - Entrada SAN vacía.")
            self.status_label.setStyleSheet("background-color: #FFF3CD; color: #856404; border: 1px solid #FFEEBA; padding: 5px; border-radius: 4px;")
            self.tree_visualizer_widget.set_tree_data(None) # Limpiar el visualizador del árbol.
            return

        self.status_label.setText("Estado: Analizando partida...")
        self.status_label.setStyleSheet("background-color: #CCE5FF; color: #004085; border: 1px solid #B8DAFF; padding: 5px; border-radius: 4px;") # Estilo informativo.

        try:
            # Crear el objeto Partida. La validación ocurre en su constructor.
            partida_obj = Partida(san_input)

            if partida_obj.es_valida_sintacticamente:
                self.status_label.setText("Estado: Partida VÁLIDA. Construyendo árbol...")
                self.status_label.setStyleSheet("background-color: #D4EDDA; color: #155724; border: 1px solid #C3E6CB; padding: 5px; border-radius: 4px;") # Estilo de éxito.

                # Construir el árbol binario a partir de los turnos validados.
                arbol_constructor = ArbolBinarioPartida()
                raiz_arbol = arbol_constructor.construir_arbol(partida_obj.turnos)
                
                # Pasar el nodo raíz al widget visualizador.
                self.tree_visualizer_widget.set_tree_data(raiz_arbol)
                self.status_label.setText(f"Estado: Partida VÁLIDA. Árbol generado con {len(partida_obj.turnos)} turno(s).")

            else:
                # La partida es inválida. Mostrar el error.
                error_msg = partida_obj.obtener_primer_error()
                if not error_msg: # Fallback si no hay mensaje de error específico.
                    error_msg = "Error desconocido en la sintaxis de la partida."
                
                self.status_label.setText(f"Estado: Partida INVÁLIDA.")
                self.status_label.setStyleSheet("background-color: #F8D7DA; color: #721C24; border: 1px solid #F5C6CB; padding: 5px; border-radius: 4px;") # Estilo de error.
                self.tree_visualizer_widget.set_tree_data(None) # Limpiar el árbol.
                QMessageBox.critical(self, "Error de Sintaxis", f"La partida contiene errores:\n\n{error_msg}")

        except Exception as e:
            # Capturar cualquier otra excepción inesperada durante el proceso.
            self.status_label.setText(f"Estado: Error inesperado - {type(e).__name__}.")
            self.status_label.setStyleSheet("background-color: #F8D7DA; color: #721C24; border: 1px solid #F5C6CB; padding: 5px; border-radius: 4px;")
            self.tree_visualizer_widget.set_tree_data(None)
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error inesperado durante el análisis:\n\n{e}")
            print(f"Error crítico en _on_analyze_clicked: {e}") # Imprimir en consola para depuración.
            import traceback
            traceback.print_exc() # Imprimir el stack trace completo.


# Bloque para ejecutar esta ventana de forma aislada (útil para desarrollo y pruebas).
# En la aplicación completa, `main.py` se encargará de instanciar y mostrar esta ventana.
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv) # Necesario para cualquier aplicación PyQt.
    
    # Para ayudar con importaciones relativas al ejecutar directamente:
    # Añadir el directorio padre (que debería ser 'src') al PYTHONPATH.
    # Esto es un hack común para pruebas y puede no ser necesario si tu IDE
    # o entorno de ejecución maneja bien el PYTHONPATH para el proyecto.
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir) # Esto debería ser 'src'
    # sys.path.insert(0, os.path.dirname(parent_dir)) # Añadir el directorio raíz del proyecto
    sys.path.insert(0, parent_dir) # Añadir 'src'


    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
