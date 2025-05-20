# src/core/turno.py
from .movimiento import Movimiento # Usar import relativo dentro del paquete

class Turno:
    """
    Representa un turno completo en una partida de ajedrez.
    Un turno consiste en un número de turno, una jugada de las blancas
    y, opcionalmente, una jugada de las negras.
    """
    def __init__(self, numero_turno, san_jugada_blanca, san_jugada_negra=None):
        """
        Inicializa un objeto Turno.

        Args:
            numero_turno (int): El número de turno.
            san_jugada_blanca (str): La jugada de las blancas en notación SAN.
            san_jugada_negra (str, optional): La jugada de las negras en notación SAN.
                                               Defaults to None.
        """
        if not isinstance(numero_turno, int) or numero_turno <= 0:
            raise ValueError("El número de turno debe ser un entero positivo.")
        self.numero_turno = numero_turno

        if not san_jugada_blanca or not isinstance(san_jugada_blanca, str):
            # Aunque Movimiento maneja strings vacíos, es bueno validar aquí también.
            raise ValueError("La jugada de las blancas no puede estar vacía y debe ser una cadena.")
        self.jugada_blanca = Movimiento(san_jugada_blanca)

        self.jugada_negra = None
        if san_jugada_negra and isinstance(san_jugada_negra, str):
            self.jugada_negra = Movimiento(san_jugada_negra)
        elif san_jugada_negra is not None: # Si se proveyó algo que no es un string válido
             raise ValueError("La jugada de las negras, si se provee, debe ser una cadena.")


    @property
    def es_valido(self):
        """
        Determina si el turno es completamente válido.
        Un turno es válido si la jugada blanca es válida y, si existe,
        la jugada negra también es válida.

        Returns:
            bool: True si el turno es válido, False en caso contrario.
        """
        if not self.jugada_blanca.es_valido:
            return False
        if self.jugada_negra and not self.jugada_negra.es_valido:
            return False
        return True

    def obtener_error_detalle(self):
        """
        Retorna una descripción del primer error encontrado en el turno.
        """
        if not self.jugada_blanca.es_valido:
            return (f"Error en Turno {self.numero_turno}, jugada blanca "
                    f"'{self.jugada_blanca.san_string}': {self.jugada_blanca.tipo_error}. "
                    f"{self.jugada_blanca.descripcion_error_detallada}")
        if self.jugada_negra and not self.jugada_negra.es_valido:
            return (f"Error en Turno {self.numero_turno}, jugada negra "
                    f"'{self.jugada_negra.san_string}': {self.jugada_negra.tipo_error}. "
                    f"{self.jugada_negra.descripcion_error_detallada}")
        return None

    def __str__(self):
        """Representación en cadena del objeto Turno."""
        san_negra = self.jugada_negra.san_string if self.jugada_negra else ""
        return (f"Turno {self.numero_turno}: {self.jugada_blanca.san_string} {san_negra} "
                f"(Válido: {self.es_valido})")

    def __repr__(self):
        """Representación oficial del objeto."""
        return self.__str__()

