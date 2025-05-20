# src/app.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLabel, QMessageBox,
                             QScrollArea, QFrame)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Importar las clases de lógica y visualización desde sus respectivos módulos.
# Se usan bloques try-except para permitir que el módulo se cargue incluso si
# hay problemas de importación durante el desarrollo inicial o pruebas aisladas.
try:
    # Asume que TreeVisualizerWidget está en src/ui/tree_visualizer.py
    from .ui.tree_visualizer import TreeVisualizerWidget
    # Asume que Partida está en src/core/partida.py
    from .core.partida import Partida
    # Asume que ArbolBinarioPartida está en src/tree/arbol_partida.py
    from .tree.arbol_partida import ArbolBinarioPartida
    # Podría ser necesario para type hinting o si se instancia directamente.
    # from .tree.nodo_arbol import NodoArbol
except ImportError as e:
    print(f"Error de importación en src/app.py: {e}")
    print("Usando placeholders para las clases no encontradas. Asegúrese de que la estructura del proyecto y PYTHONPATH sean correctos.")
    # Placeholders para el caso de que las importaciones fallen.
    # Esto es principalmente para desarrollo y no debería ocurrir en la aplicación final.
    class TreeVisualizerWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.placeholder_label = QLabel("TreeVisualizer Placeholder (Error de Importación en app.py)", self)
            layout = QHBoxLayout(self)
            layout.addWidget(self.placeholder_label)
            self.placeholder_label.setAlignment(Qt.AlignCenter)
        def set_tree_data(self, root_node):
            if hasattr(self, 'placeholder_label'):
                self.placeholder_label.setText(f"TreeVisualizer Placeholder: set_tree_data con nodo raíz: {root_node.valor if root_node else 'None'}")
            print(f"TreeVisualizer Placeholder (app.py): set_tree_data con nodo raíz: {root_node.valor if root_node else 'None'}")

    class Partida:
        def __init__(self, san_str):
            self.san_str = san_str
            self.turnos = []
            self.es_valida_sintacticamente = "error" not in san_str.lower()
            self.error_message = "Error simulado en la partida (app.py)." if not self.es_valida_sintacticamente else None
            if self.es_valida_sintacticamente and san_str:
                class MovimientoPlaceholder:
                    def __init__(self, s): self.san_string = s; self.es_valido = True
                class TurnoPlaceholder:
                    def __init__(self, n, jb_str, jn_str=None):
                        self.numero_turno = n; self.jugada_blanca = MovimientoPlaceholder(jb_str)
                        self.jugada_negra = MovimientoPlaceholder(jn_str) if jn_str else None; self.es_valido = True
                moves = san_str.split(); num_turno = 1
                for i in range(0, len(moves) -1, 3):
                    if len(moves) > i+2: self.turnos.append(TurnoPlaceholder(num_turno, moves[i+1], moves[i+2]))
                    elif len(moves) > i+1: self.turnos.append(TurnoPlaceholder(num_turno, moves[i+1]))
                    num_turno+=1
        def obtener_primer_error(self): return self.error_message

    class ArbolBinarioPartida:
        def __init__(self):
            class NodoArbolPlaceholder:
                def __init__(self, valor): self.valor = valor; self.izquierda = None; self.derecha = None
            self.NodoArbolCls = NodoArbolPlaceholder; self.raiz = None
        def construir_arbol(self, turnos_validados):
            if not turnos_validados: self.raiz = None; return None
            self.raiz = self.NodoArbolCls("Partida (app.py)"); current_parent = self.raiz
            if turnos_validados:
                for turno in turnos_validados:
                    if hasattr(turno, 'jugada_blanca') and turno.jugada_blanca:
                        current_parent.izquierda = self.NodoArbolCls(turno.jugada_blanca.san_string)
                        if hasattr(turno, 'jugada_negra') and turno.jugada_negra:
                            current_parent.derecha = self.NodoArbolCls(turno.jugada_negra.san_string)
                            current_parent = current_parent.derecha
                        else: break
                    else: break
            return self.raiz


class AplicacionAjedrezGUI(QMainWindow):
    """
    Clase principal de la aplicación que hereda de QMainWindow.
    Configura la interfaz de usuario y maneja la lógica de interacción
    para el analizador de partidas de ajedrez.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Sintáctico de Partidas de Ajedrez")
        self.setGeometry(100, 100, 950, 750) # x, y, ancho, alto iniciales.

        # Configuración del widget central y el layout principal.
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self._crear_widgets_entrada_san()
        self._crear_boton_analisis()
        self._crear_etiqueta_estado()
        self._crear_visualizador_arbol()

        self.show() # Mostrar la ventana principal al inicializar.

    def _crear_widgets_entrada_san(self):
        """Crea los widgets para la entrada de la partida SAN."""
        self.input_san_label = QLabel("<b>Ingrese la partida en Notación Algebraica Estándar (SAN):</b>")
        self.main_layout.addWidget(self.input_san_label)

        self.san_text_edit = QTextEdit()
        self.san_text_edit.setPlaceholderText("Ejemplo: 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 ...")
        self.san_text_edit.setFixedHeight(120)
        self.san_text_edit.setFont(QFont("Consolas", 10))
        self.main_layout.addWidget(self.san_text_edit)
        
        # Ejemplo de partida para pruebas rápidas.
        self.san_text_edit.setText(
            "1. d4 d5 2. Bf4 Nf6 3. e3 e6 4. c3 c5 5. Nd2 Nc6 6. Bd3 Bd6 7. Bg3 0-0 "
            "8. Ngf3 Qe7 9. Ne5 Nd7 10. Nxc6 bxc6 11. Bxd6 Qxd6 12. Nf3 a5 13. 0-0 Ba6 "
            "14. Re1 Rfb8 15. Rb1 Bxd3 16. Qxd3 c4 17. Qc2 f5 18. Nd2 Rb5 19. b3 cxb3 "
            "20. axb3 Rab8 21. Qa2 Qc7 22. c4 Rb4 23. cxd5 cxd5 24. Rbc1 Qb6 25. h3 a4 "
            "26. bxa4 Rb2 27. Qa3 Rxd2 28. Qe7 Qd8 29. Qxe6+ Kh8 30. Qxf5 Nf6 "
            "31. g4 Ne4 32. Rf1 h6 33. Rc6 Qh4 34. Rc8+ Rxc8 35. Qxc8+ Kh7 36. Qf5+"
        )

    def _crear_boton_analisis(self):
        """Crea el botón para iniciar el análisis."""
        self.analyze_button = QPushButton("Analizar Partida y Generar Árbol")
        self.analyze_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px; }"
            "QPushButton:hover { background-color: #45a049; }"
            "QPushButton:pressed { background-color: #3e8e41; }"
        )
        self.analyze_button.clicked.connect(self._on_analyze_clicked)
        self.main_layout.addWidget(self.analyze_button)

    def _crear_etiqueta_estado(self):
        """Crea la etiqueta para mostrar el estado o errores."""
        self.status_label = QLabel("Estado: Esperando partida.")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setFixedHeight(35)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "padding: 5px; border: 1px solid #ccc; border-radius: 4px; background-color: #f0f0f0;"
        )
        self.main_layout.addWidget(self.status_label)

    def _crear_visualizador_arbol(self):
        """Crea el widget para visualizar el árbol, dentro de un QScrollArea."""
        self.tree_visualizer_widget = TreeVisualizerWidget()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.tree_visualizer_widget)
        self.scroll_area.setFrameShape(QFrame.StyledPanel)
        
        self.main_layout.addWidget(self.scroll_area)

    def _on_analyze_clicked(self):
        """
        Manejador del evento click del botón "Analizar Partida".
        Obtiene el texto SAN, lo procesa con la lógica de 'core' y 'tree',
        y actualiza la UI con el resultado o los errores.
        """
        san_input = self.san_text_edit.toPlainText().strip()
        if not san_input:
            QMessageBox.warning(self, "Entrada Vacía", "Por favor, ingrese una partida en notación SAN.")
            self.status_label.setText("Estado: Error - Entrada SAN vacía.")
            self.status_label.setStyleSheet(
                "background-color: #FFF3CD; color: #856404; border: 1px solid #FFEEBA; padding: 5px; border-radius: 4px;"
            )
            self.tree_visualizer_widget.set_tree_data(None)
            return

        self.status_label.setText("Estado: Analizando partida...")
        self.status_label.setStyleSheet(
            "background-color: #CCE5FF; color: #004085; border: 1px solid #B8DAFF; padding: 5px; border-radius: 4px;"
        )

        try:
            partida_obj = Partida(san_input)

            if partida_obj.es_valida_sintacticamente:
                self.status_label.setText("Estado: Partida VÁLIDA. Construyendo árbol...")
                self.status_label.setStyleSheet(
                    "background-color: #D4EDDA; color: #155724; border: 1px solid #C3E6CB; padding: 5px; border-radius: 4px;"
                )

                arbol_constructor = ArbolBinarioPartida()
                raiz_arbol = arbol_constructor.construir_arbol(partida_obj.turnos)
                
                self.tree_visualizer_widget.set_tree_data(raiz_arbol)
                self.status_label.setText(f"Estado: Partida VÁLIDA. Árbol generado con {len(partida_obj.turnos)} turno(s).")

            else:
                error_msg = partida_obj.obtener_primer_error()
                if not error_msg:
                    error_msg = "Error desconocido en la sintaxis de la partida."
                
                self.status_label.setText(f"Estado: Partida INVÁLIDA.")
                self.status_label.setStyleSheet(
                    "background-color: #F8D7DA; color: #721C24; border: 1px solid #F5C6CB; padding: 5px; border-radius: 4px;"
                )
                self.tree_visualizer_widget.set_tree_data(None)
                QMessageBox.critical(self, "Error de Sintaxis", f"La partida contiene errores:\n\n{error_msg}")

        except Exception as e:
            self.status_label.setText(f"Estado: Error inesperado - {type(e).__name__}.")
            self.status_label.setStyleSheet(
                "background-color: #F8D7DA; color: #721C24; border: 1px solid #F5C6CB; padding: 5px; border-radius: 4px;"
            )
            self.tree_visualizer_widget.set_tree_data(None)
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error inesperado durante el análisis:\n\n{e}")
            print(f"Error crítico en _on_analyze_clicked (app.py): {e}")
            import traceback
            traceback.print_exc()

# Este bloque permite ejecutar este archivo directamente para pruebas,
# aunque en la estructura final, `main.py` se encargará de instanciar AplicacionAjedrezGUI.
if __name__ == '__main__':
    import sys
    # Necesario para cualquier aplicación PyQt.
    q_app = QApplication(sys.argv)
    
    # Ayuda para importaciones relativas al ejecutar directamente `app.py`.
    # Esto asume que `app.py` está en `src/` y el directorio raíz del proyecto contiene `src/`.
    import os
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    project_root_path = os.path.dirname(current_script_path) # Sube un nivel a `src`
    # sys.path.insert(0, os.path.dirname(project_root_path)) # Sube otro nivel al directorio raíz del proyecto
    # Alternativamente, si la estructura es Practica_3_POO_Ajedrez/src/app.py
    # y los módulos ui, core, tree están en Practica_3_POO_Ajedrez/src/
    # entonces no se necesita manipulación de path si se ejecuta desde la raíz del proyecto.
    # Si se ejecuta src/app.py directamente, los imports ".ui" etc., deberían funcionar.

    aplicacion_gui = AplicacionAjedrezGUI()
    aplicacion_gui.show()
    sys.exit(q_app.exec_())
