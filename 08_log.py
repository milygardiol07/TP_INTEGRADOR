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

# ---- pruebas ----
if __name__ == "__main__":
    import os
    import tempfile

    # -- a) analizar_linea --
    buena = "2026-09-08 09:14:02 ADS3202 CH1 FREQ 1.000431E+03"
    assert analizar_linea(buena) == (("ADS3202", "CH1", "FREQ", 1000.431), None)
    assert analizar_linea(buena + "\n") == (("ADS3202", "CH1", "FREQ", 1000.431), None)

    # La linea con tabulaciones es BUENA: con split(" ") se perderia.
    con_tabs = "2026-09-08\t09:17:31\tADS3202\tCH1\tFREQ\t1.001000E+03"
    assert analizar_linea(con_tabs) == (("ADS3202", "CH1", "FREQ", 1001.0), None)

    # Se ignoran (ni medicion ni motivo): en blanco y comentarios.
    assert analizar_linea("") == (None, None)
    assert analizar_linea("   \n") == (None, None)
    assert analizar_linea("# reconexion del puerto LAN") == (None, None)

    # Se rechazan: siempre (None, motivo), con un motivo que dice por que.
    def motivo(linea):
        medicion, razon = analizar_linea(linea)
        assert medicion is None and razon is not None
        return razon

    assert motivo("2026-09-08 09:15:01 ADS3202 CH2 PKPK").startswith("no tiene seis campos")
    assert motivo(buena + " VERIFICADO").startswith("no tiene seis campos")
    assert motivo("2026-09-08 25:61:00 ADS3202 CH2 FREQ 2.5E+03").startswith("fecha u hora imposible")
    assert motivo("2026-02-30 09:00:00 ADS3202 CH2 FREQ 2.5E+03").startswith("fecha u hora imposible")
    assert motivo("2026-09-08 09:16:31 ADS3202 CH3 FREQ 1.0E+03").startswith("canal inválido")
    assert motivo("2026-09-08 09:17:01 ADS3202 CH1 TEMP 3.15E+02").startswith("magnitud inválida")
    assert motivo("2026-09-08 09:15:31 ADS3202 CH1 PKPK 2,003812").startswith("valor no numérico")
    # float("NaN") no falla: si no se controlara aparte, entraria un NaN a la serie.
    assert motivo("2026-09-08 09:16:01 ADS3202 CH2 CYCRMS NaN").startswith("valor no numérico")
    assert motivo("2026-09-08 09:16:01 ADS3202 CH2 CYCRMS inf").startswith("valor no numérico")

    # -- b) leer_log con un archivo armado a mano --
    contenido = "\n".join([
        "# encabezado",
        "",
        "2026-09-08 09:00:00 ADS3202 CH1 FREQ 1.0E+03",
        "2026-09-08 09:00:00 ADS3202 CH1 PKPK 2.0E+00",
        "2026-09-08 09:00:15 ADS3202 CH1 FREQ 1.002E+03",
        "2026-09-08 09:00:30 ADS3202 CH9 FREQ 1.0E+03",
        "2026-09-08\t09:00:45\tADS3202\tCH1\tFREQ\t9.98E+02",
    ]) + "\n"
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False,
                                     encoding="utf-8") as tmp:
        tmp.write(contenido)
    try:
        series, rechazadas = leer_log(tmp.name)
    finally:
        os.remove(tmp.name)
    # Agrupa por (equipo, canal, magnitud) y respeta el orden del archivo.
    assert series == {("ADS3202", "CH1", "FREQ"): [1000.0, 1002.0, 998.0],
                      ("ADS3202", "CH1", "PKPK"): [2.0]}
    # El numero de linea es el del archivo (empieza en 1, cuenta comentarios y blancos).
    assert rechazadas == [(6, "2026-09-08 09:00:30 ADS3202 CH9 FREQ 1.0E+03",
                           "canal inválido: CH9")]

    # Caso raro: archivo vacio -> nada que agrupar, nada rechazado.
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as tmp:
        pass
    try:
        assert leer_log(tmp.name) == ({}, [])
    finally:
        os.remove(tmp.name)

    # -- c) el registro real de la catedra --
    carpeta = os.path.dirname(os.path.abspath(__file__))
    series, rechazadas = leer_log(os.path.join(carpeta, "mediciones.log"))
    # Son exactamente 8 las lineas rotas del archivo.
    assert [nro for nro, _, _ in rechazadas] == [24, 37, 52, 65, 78, 92, 118, 132]
    # CH1 FREQ tiene 21: 20 tandas + la linea con tabulaciones (09:17:31).
    # Si diera 20, se habria perdido un dato bueno.
    assert len(series[("ADS3202", "CH1", "FREQ")]) == 21
    assert len(series) == 6
    assert all(len(v) == 20 for k, v in series.items()
               if k != ("ADS3202", "CH1", "FREQ"))

    print("rechazadas en mediciones.log:")
    for nro, linea, razon in rechazadas:
        print("  linea %3d: %s" % (nro, razon))
    print("pruebas OK")
