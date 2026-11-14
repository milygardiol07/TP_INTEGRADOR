import math
from datetime import datetime

CANALES = {"CH1", "CH2"}
MAGNITUDES = {"FREQ", "PKPK", "CYCRMS"}


def analizar_linea(linea):
    """Devuelve (medicion, motivo).
    - Línea válida:     (medicion, None)
    - Línea rechazada:  (None, motivo)
    - Línea ignorada:   (None, None)  # en blanco o comentario
    """
    texto = linea.strip()
    if texto == "" or texto.startswith("#"):
        return None, None

    campos = texto.split()          
    if len(campos) != 6:
        return None, f"no tiene seis campos (tiene {len(campos)})"

    fecha, hora, equipo, canal, magnitud, valor = campos

    try:
        datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None, f"fecha u hora imposible: {fecha} {hora}"

    if canal not in CANALES:
        return None, f"canal inválido: {canal}"

    if magnitud not in MAGNITUDES:
        return None, f"magnitud inválida: {magnitud}"

    try:
        numero = float(valor)
    except ValueError:
        return None, f"valor no numérico: {valor}"
    if not math.isfinite(numero):   
        return None, f"valor no numérico: {valor}"

    return (equipo, canal, magnitud, numero), None


def leer_log(ruta):
    """Devuelve (series, rechazadas).
    series: {(equipo, canal, magnitud): [valores]}
    rechazadas: [(nro_linea, linea, motivo)]
    """
    series = {}
    rechazadas = []

    with open(ruta, encoding="utf-8") as f:
        for nro, linea in enumerate(f, start=1):
            medicion, motivo = analizar_linea(linea)
            if medicion is not None:
                equipo, canal, magnitud, valor = medicion
                series.setdefault((equipo, canal, magnitud), []).append(valor)
            elif motivo is not None:
                rechazadas.append((nro, linea.rstrip("\n"), motivo))

    return series, rechazadas