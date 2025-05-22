# src/core/movimiento.py
import re

class Movimiento:
    """
    Representa una jugada individual en notación algebraica estándar (SAN).
    Se encarga de validar la sintaxis de la jugada contra una gramática BNF simplificada.
    """

    # --- Definiciones de expresiones regulares basadas en la gramática BNF ---
    # Componentes básicos
    _LETRA = r"[a-h]"
    _NUMERO = r"[1-8]"
    _CASILLA = rf"{_LETRA}{_NUMERO}"  # Ej: e4, g8
    _PIEZA = r"[KQRBN]"  # Rey, Dama, Torre, Alfil, Caballo

    # Componentes opcionales de una jugada
    _DESAMBIGUACION_OPCIONAL = rf"(?:{_LETRA}|{_NUMERO}|{_LETRA}{_NUMERO})?" # Ej: R, R1, Ra, Rae (opcional)
    _CAPTURA_OPCIONAL = r"x?"  # 'x' (opcional)
    _PROMOCION_OPCIONAL = rf"(?:={_PIEZA})?"  # Ej: =Q (opcional)
    _JAQUE_MATE_OPCIONAL = r"[+#]?"  # '+' o '#' (opcional)

    # Patrones para tipos de jugada completos (anclados al inicio y fin de la cadena ^$)
    # <enroque> ::= "0-0" | "0-0-0"
    # La BNF no incluye jaque/mate para enroque directamente, pero es común en SAN.
    # Sin embargo, nos ceñiremos estrictamente a la BNF proporcionada.
    _PATRON_ENROQUE = re.compile(r"^(0-0|0-0-0)$")

    # <movimiento_pieza> ::= <pieza> <desambiguacion>? <captura>? <casilla> <promocion>? <jaque_mate>?
    # Nota: La promoción para piezas que no son peones es inusual en SAN estándar,
    # pero está en la BNF proporcionada y la respetaremos.
    _PATRON_MOVIMIENTO_PIEZA = re.compile(
        rf"^{_PIEZA}{_DESAMBIGUACION_OPCIONAL}{_CAPTURA_OPCIONAL}{_CASILLA}{_PROMOCION_OPCIONAL}{_JAQUE_MATE_OPCIONAL}$"
    )

    # <peon_avance> ::= <casilla> <promocion>? <jaque_mate>?
    _PATRON_PEON_AVANCE = re.compile(
        rf"^{_CASILLA}{_PROMOCION_OPCIONAL}{_JAQUE_MATE_OPCIONAL}$"
    )

    # <peon_captura> ::= <letra> "x" <casilla> <promocion>? <jaque_mate>?
    _PATRON_PEON_CAPTURA = re.compile(
        rf"^{_LETRA}x{_CASILLA}{_PROMOCION_OPCIONAL}{_JAQUE_MATE_OPCIONAL}$"
    )
    # --- Fin de las definiciones de expresiones regulares ---

    def __init__(self, san_string):
        """
        Inicializa un objeto Movimiento.

        Args:
            san_string (str): La cadena de la jugada en notación SAN (ej: "e4", "Nf3", "0-0").
        """
        self.san_string = san_string.strip() if san_string else ""
        self.es_valido = False
        self.tipo_error = "" # Descripción breve del error
        self.descripcion_error_detallada = "" # Podría usarse para más detalles

        # Validar inmediatamente al crear la instancia
        self._validar_sintaxis()

    def _validar_sintaxis(self):
        """
        Valida la jugada almacenada en self.san_string contra la gramática BNF.
        Actualiza self.es_valido y self.tipo_error.
        """
        if not self.san_string:
            self.es_valido = False
            self.tipo_error = "Jugada vacía"
            self.descripcion_error_detallada = "La cadena de la jugada no puede estar vacía."
            return

        # Intentar hacer match con cada tipo de jugada definida en la BNF
        # <jugada> ::= <enroque> | <movimiento_pieza> | <movimiento_peon>
        # <movimiento_peon> ::= <peon_captura> | <peon_avance>

        # 1. Intentar <enroque>
        if self._PATRON_ENROQUE.fullmatch(self.san_string):
            self.es_valido = True
            # Validar adicionalmente si la promoción o jaque/mate se incluyó erróneamente
            # según la BNF estricta de <enroque> (que no los tiene).
            # Sin embargo, nuestro patrón ya es estricto.
            return

        # 2. Intentar <movimiento_pieza>
        if self._PATRON_MOVIMIENTO_PIEZA.fullmatch(self.san_string):
            # Validaciones adicionales específicas para movimientos de pieza si fueran necesarias.
            # Por ejemplo, la promoción aquí es permitida por la BNF dada, aunque inusual.
            self.es_valido = True
            return

        # 3. Intentar <peon_avance>
        if self._PATRON_PEON_AVANCE.fullmatch(self.san_string):
            # Validar que la casilla de destino sea válida (ya cubierto por _CASILLA)
            # Validar que si hay promoción, la pieza sea válida (ya cubierto por _PIEZA en _PROMOCION_OPCIONAL)
            self.es_valido = True
            return

        # 4. Intentar <peon_captura>
        if self._PATRON_PEON_CAPTURA.fullmatch(self.san_string):
            self.es_valido = True
            return

        # Si ninguna regla coincide, la jugada es inválida
        self.es_valido = False
        self.tipo_error = "Sintaxis inválida"
        self.descripcion_error_detallada = (
            f"La jugada '{self.san_string}' no cumple con ninguna regla de la gramática BNF proporcionada. "
            f"Verifique el formato (ej: pieza, casilla, captura, promoción, jaque/mate)."
        )
        # Podríamos intentar dar pistas más específicas analizando partes de la jugada,
        # pero para este ejercicio, un error general basado en la BNF es suficiente.

    def __str__(self):
        """Representación en cadena del objeto Movimiento."""
        return f"Movimiento({self.san_string}, Válido: {self.es_valido}, Error: {self.tipo_error})"

    def __repr__(self):
        """Representación oficial del objeto."""
        return self.__str__()

