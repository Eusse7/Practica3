# Practica_3_POO_Ajedrez/main.py

import sys
# Importa QApplication de PyQt5 (o PyQt6 si es la versión que estás usando).
from PyQt5.QtWidgets import QApplication
# from PyQt6.QtWidgets import QApplication # Descomenta si usas PyQt6 y comenta la anterior

# Importa la clase principal de la aplicación GUI desde src/app.py.
# Se asume que el archivo src/app.py existe y contiene la clase AplicacionAjedrezGUI.
try:
    from src.app import AplicacionAjedrezGUI
except ModuleNotFoundError:
    print("ERROR CRÍTICO: No se pudo importar 'AplicacionAjedrezGUI' desde 'src.app'.")
    print("Verifique que el archivo 'src/app.py' exista y esté en la ubicación correcta.")
    print("Asegúrese también de que la carpeta 'src' sea reconocida como un paquete (debería tener un archivo __init__.py, aunque a veces no es estrictamente necesario para imports directos).")
    print("Si está ejecutando desde la raíz del proyecto, la estructura de carpetas debe ser correcta.")
    sys.exit(1) # Terminar la aplicación si no se puede importar la clase principal.
except Exception as e:
    print(f"ERROR CRÍTICO: Ocurrió un error inesperado al importar 'AplicacionAjedrezGUI': {e}")
    sys.exit(1)


def iniciar_aplicacion():
    """
    Punto de entrada principal para la aplicación de Ajedrez.
    Inicializa y ejecuta la interfaz gráfica de usuario.
    """
    # Crea una instancia de QApplication. Es necesaria para cualquier aplicación GUI de PyQt.
    # sys.argv permite pasar argumentos de línea de comandos a la aplicación, si los hubiera.
    aplicacion_qt = QApplication(sys.argv)

    # Crea una instancia de la ventana principal de tu aplicación.
    # La clase AplicacionAjedrezGUI (definida en src/app.py) se encarga
    # de configurar la UI, conectar señales y slots, etc.
    ventana_principal = AplicacionAjedrezGUI()

    # Nota: La llamada a ventana_principal.show() ya se hace dentro del __init__
    # de la clase AplicacionAjedrezGUI que te proporcioné.
    # Por lo tanto, no es estrictamente necesario llamarla de nuevo aquí,
    # pero no causa problemas si se hace. Para mayor claridad, se puede omitir aquí.
    # ventana_principal.show()

    # Inicia el bucle de eventos de la aplicación.
    # El programa saldrá de este bucle solo cuando se cierre la ventana principal.
    # sys.exit() asegura una terminación limpia de la aplicación.
    sys.exit(aplicacion_qt.exec_())

if __name__ == "__main__":
    # Este bloque se ejecuta solo si el script se ejecuta directamente
    # (es decir, no si se importa como un módulo en otro script).
    # Es la convención estándar para iniciar una aplicación Python.
    print("Iniciando la aplicación Analizador de Ajedrez desde main.py...")
    iniciar_aplicacion()