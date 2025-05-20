# src/core/partida.py
import re
from .turno import Turno # Usar import relativo

class Partida:
    """
    Representa una partida de ajedrez completa leída en notación SAN.
    Se encarga de parsear la cadena de la partida en turnos y validar
    la sintaxis general de la partida.
    """

    # Expresión regular para parsear un turno completo.
    # Captura: 1. Número de turno, 2. Jugada blanca, 3. Jugada negra (opcional)
    # Ejemplos: "1. e4 e5", "23. cxd5", "36. Qf5+"
    _PATRON_TURNO_COMPLETO = re.compile(
        r"(\d+)\.\s*([^\s]+)(?:\s+([^\s]+))?"
        # (\d+)\.      -> Número de turno seguido de un punto. Ej: "1."
        # \s* -> Cero o más espacios.
        # ([^\s]+)      -> Jugada blanca (uno o más caracteres que no sean espacio). Ej: "e4"
        # (?:\s+        -> Grupo opcional (no capturador) para la jugada negra.
        #   ([^\s]+)    -> Jugada negra (uno o más caracteres que no sean espacio). Ej: "e5"
        # )?            -> Fin del grupo opcional.
    )

    def __init__(self, san_completa):
        """
        Inicializa una Partida.

        Args:
            san_completa (str): La cadena completa de la partida en notación SAN.
        """
        self.san_completa = san_completa.strip() if san_completa else ""
        self.turnos = []
        self.es_valida_sintacticamente = False
        self.error_parseo_general = None # Error general del parseo de la partida

        self._parsear_y_validar()

    def _parsear_y_validar(self):
        """
        Parsea la cadena SAN de la partida completa, la divide en turnos y jugadas,
        y valida la sintaxis de cada uno.
        Actualiza self.turnos, self.es_valida_sintacticamente y self.error_parseo_general.
        """
        if not self.san_completa:
            self.es_valida_sintacticamente = False # Considerar una partida vacía como inválida o válida según se requiera.
            self.error_parseo_general = "La cadena de la partida está vacía."
            return

        # Limpiar múltiples espacios entre jugadas o antes/después de números de turno
        # para facilitar el parseo con la regex.
        # Ej: "1.   e4   e5" -> "1. e4 e5"
        #     "1 . e4" -> "1. e4"
        partida_limpia = re.sub(r'\s*\.\s*', '. ', self.san_completa) # Normaliza "N . jugada" a "N. jugada"
        partida_limpia = re.sub(r'\s+', ' ', partida_limpia).strip()  # Reduce múltiples espacios a uno

        posicion_actual = 0
        turnos_encontrados = 0

        for match_turno in self._PATRON_TURNO_COMPLETO.finditer(partida_limpia):
            turnos_encontrados += 1
            if match_turno.start() != posicion_actual:
                # Hay texto entre el final del último turno parseado y el inicio del actual
                texto_residual = partida_limpia[posicion_actual:match_turno.start()].strip()
                if texto_residual: # Solo si hay caracteres no espaciales
                    self.es_valida_sintacticamente = False
                    self.error_parseo_general = (
                        f"Texto inesperado o formato incorrecto antes del turno {match_turno.group(1)}: "
                        f"'{texto_residual}'"
                    )
                    return

            num_turno_str = match_turno.group(1)
            jugada_blanca_str = match_turno.group(2)
            jugada_negra_str = match_turno.group(3) # Puede ser None

            try:
                num_turno = int(num_turno_str)
                if self.turnos and num_turno <= self.turnos[-1].numero_turno:
                    self.es_valida_sintacticamente = False
                    self.error_parseo_general = (
                        f"Error de secuencia de turnos: Turno {num_turno} encontrado después "
                        f"del turno {self.turnos[-1].numero_turno}."
                    )
                    return
                if not self.turnos and num_turno != 1 and turnos_encontrados == 1: # Si es el primer turno parseado
                    # Esta validación es opcional, algunas partidas pueden empezar en un turno N.
                    # print(f"Advertencia: La partida no comienza en el turno 1 (comienza en {num_turno}).")
                    pass


                turno_actual = Turno(num_turno, jugada_blanca_str, jugada_negra_str)
            except ValueError as ve:
                self.es_valida_sintacticamente = False
                self.error_parseo_general = f"Error al crear turno {num_turno_str}: {ve}"
                return

            self.turnos.append(turno_actual)
            if not turno_actual.es_valido:
                self.es_valida_sintacticamente = False
                # El error específico ya está en turno_actual.obtener_error_detalle()
                # Se puede propagar aquí si se desea un error general de partida más específico.
                self.error_parseo_general = turno_actual.obtener_error_detalle()
                return # Detener al primer error de sintaxis en una jugada

            posicion_actual = match_turno.end()

        # Después del bucle, verificar si sobró texto al final de la partida
        if posicion_actual < len(partida_limpia):
            texto_residual_final = partida_limpia[posicion_actual:].strip()
            if texto_residual_final: # Solo si hay caracteres no espaciales
                self.es_valida_sintacticamente = False
                self.error_parseo_general = (
                    f"Texto inesperado al final de la partida: '{texto_residual_final}'"
                )
                return

        if not self.turnos and self.san_completa: # Si no se parseó ningún turno pero había texto
            self.es_valida_sintacticamente = False
            self.error_parseo_general = "No se pudieron parsear turnos. Verifique el formato general (ej: '1. e4 e5 2. Nf3')."
            return

        if not self.turnos and not self.san_completa: # Partida vacía
             self.es_valida_sintacticamente = True # O False, según definición. Asumamos True.
             return


        self.es_valida_sintacticamente = True

    def obtener_primer_error(self):
        """
        Retorna el primer error detallado encontrado, ya sea un error general
        de parseo de la partida o un error en una jugada específica.
        """
        if self.error_parseo_general:
            return self.error_parseo_general
        for turno in self.turnos:
            if not turno.es_valido:
                return turno.obtener_error_detalle()
        return None

    def __str__(self):
        """Representación en cadena de la Partida."""
        return (f"Partida SAN: '{self.san_completa[:50]}...', "
                f"Turnos: {len(self.turnos)}, Válida: {self.es_valida_sintacticamente}")

    def __repr__(self):
        """Representación oficial del objeto."""
        return self.__str__()

