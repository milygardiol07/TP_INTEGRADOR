"""
armar_informe(idn, series, verificaciones) -> el informe como UNA cadena.

No imprime nada y no abre ningun archivo: recibe todo por parametro y
devuelve texto. El print lo hace quien la llama (el programa de abajo).

    idn             el diccionario de parsear_idn (ej. 1), o None
    series          {(equipo, canal, magnitud): [valores]} de leer_log (ej. 8)
    verificaciones  lista de diccionarios de verificar_canal (ej. 7)

Al ejecutar el archivo corren primero las pruebas (sin red) y despues el
banco completo, que necesita el instrumento virtual en otra terminal:

    python3 instrumento_virtual.py
"""

# Cada pieza se reutiliza del ejercicio que la resolvio, no se copia.
con_unidad = __import__("02_magnitudes").con_unidad
resumen = __import__("09_estadistica").resumen
MAGNITUDES = __import__("06_barrido").MAGNITUDES

# {"FREQ": "Hz", "PKPK": "V", "CYCRMS": "V"}, sacado de la misma tabla que usa barrer.
UNIDADES = {magnitud: unidad for _, magnitud, unidad in MAGNITUDES}

CANALES = ["CH1", "CH2"]


def linea_instrumento(idn):
    if not idn:
        return "Instrumento: no identificado (*IDN? no devolvio una respuesta valida)"
    return "Instrumento: %s %s  (serie %s, firmware %s)" % (
        idn["fabricante"], idn["modelo"], idn["serie"], idn["version"])


def linea_serie(clave, valores):
    equipo, canal, magnitud = clave
    nombre = "%s %s %-6s" % (equipo, canal, magnitud)
    datos = resumen(valores)
    if datos is None:
        return "  %s  sin datos validos" % nombre
    unidad = UNIDADES.get(magnitud, "")
    return "  %s  n=%-3d promedio=%-11s minimo=%-11s maximo=%s" % (
        nombre, datos["n"],
        con_unidad(datos["promedio"], unidad),
        con_unidad(datos["minimo"], unidad),
        con_unidad(datos["maximo"], unidad))


def linea_verificacion(v):
    if v["motivo"] is not None:
        return "  %s: NO SE PUDO VERIFICAR (%s)" % (v["canal"], v["motivo"])
    estado = "COINCIDE" if v["coincide"] else "NO COINCIDE"
    return "  %s: %-11s Vpp=%s  Vrms medido=%s  Vrms teorico=%s  error=%.2f %%" % (
        v["canal"], estado,
        con_unidad(v["vpp"], "V"),
        con_unidad(v["vrms_medido"], "V"),
        con_unidad(v["vrms_teorico"], "V"),
        v["error"] * 100)


def armar_informe(idn, series, verificaciones):
    """Devuelve el informe completo como una sola cadena de texto."""
    lineas = ["INFORME DEL BANCO DE MEDICIONES", "",
              linea_instrumento(idn), "",
              "Series del registro:"]
    if series:
        for clave in sorted(series):
            lineas.append(linea_serie(clave, series[clave]))
    else:
        lineas.append("  (sin series)")

    lineas += ["", "Verificacion Vrms = Vpp / (2 * raiz(2)), tolerancia 2 %:"]
    if verificaciones:
        for v in verificaciones:
            lineas.append(linea_verificacion(v))
    else:
        lineas.append("  (sin verificaciones)")

    return "\n".join(lineas)


# ---- pruebas ----
if __name__ == "__main__":
    import builtins
    import io
    import os
    import sys
    from contextlib import redirect_stdout

    parsear_idn = __import__("01_identificacion").parsear_idn
    verificar_canal = __import__("07_verificacion").verificar_canal

    def fila(canal, magnitud, valor):
        return {"canal": canal, "magnitud": magnitud, "unidad": UNIDADES[magnitud],
                "crudo": "%E" % valor, "valor": valor}

    idn = parsear_idn("OWON,ADS3202,25470803,V1.2.0")
    series = {
        ("ADS3202", "CH2", "FREQ"): [2500.0, 2490.0, 2510.0],
        ("ADS3202", "CH1", "FREQ"): [999.0, 1000.0, 1001.0],
        ("ADS3202", "CH1", "PKPK"): [],
    }
    senoide = [fila("CH1", "PKPK", 2.0), fila("CH1", "CYCRMS", 0.7071)]
    cuadrada = [fila("CH2", "PKPK", 2.0), fila("CH2", "CYCRMS", 1.0)]
    verificaciones = [verificar_canal(senoide, "CH1"),
                      verificar_canal(cuadrada, "CH2"),
                      verificar_canal(senoide, "CH3")]

    # La funcion no imprime: se captura la salida y tiene que quedar vacia.
    # Y no abre archivos: mientras corre, open() queda reemplazado por una trampa.
    def open_prohibido(*_args, **_kwargs):
        raise AssertionError("armar_informe no puede abrir archivos")

    salida = io.StringIO()
    open_original = builtins.open
    builtins.open = open_prohibido
    try:
        with redirect_stdout(salida):
            informe = armar_informe(idn, series, verificaciones)
    finally:
        builtins.open = open_original
    assert salida.getvalue() == ""
    assert isinstance(informe, str)

    lineas = informe.splitlines()
    # El instrumento identificado.
    assert "Instrumento: OWON ADS3202  (serie 25470803, firmware V1.2.0)" in lineas
    # Una linea por serie, con n, promedio, minimo y maximo YA con unidades legibles
    # (999.0 tiene que verse "999 Hz" y 1001.0 "1.001 kHz", no "1001.0").
    linea_ch1 = [l for l in lineas if "CH1 FREQ" in l][0]
    assert "n=3" in linea_ch1
    assert "promedio=1 kHz" in linea_ch1
    assert "minimo=999 Hz" in linea_ch1 and "maximo=1.001 kHz" in linea_ch1
    assert "promedio=2.5 kHz" in informe
    # Ordenadas: CH1 antes que CH2 aunque en el diccionario vengan al reves.
    assert informe.index("CH1 FREQ") < informe.index("CH2 FREQ")
    # Caso raro: una serie vacia no rompe el informe.
    assert "ADS3202 CH1 PKPK    sin datos validos" in informe
    # Las tres salidas posibles de una verificacion se distinguen.
    assert any(l.startswith("  CH1: COINCIDE") for l in lineas)
    assert any(l.startswith("  CH2: NO COINCIDE") for l in lineas)   # la cuadrada
    assert "  CH3: NO SE PUDO VERIFICAR (falta PKPK de CH3)" in lineas
    assert "Vrms medido=707.1 mV" in informe

    # Caso raro: sin identificacion, sin series y sin verificaciones.
    vacio = armar_informe(None, {}, [])
    assert "no identificado" in vacio
    assert "(sin series)" in vacio and "(sin verificaciones)" in vacio

    print("pruebas OK")
    print()

    # ---- el banco de mediciones completo ----
    Instrumento = __import__("05_cliente").Instrumento
    barrer = __import__("06_barrido").barrer
    leer_log = __import__("08_log").leer_log

    try:
        osc = Instrumento()
    except OSError:
        print("No se pudo conectar a 127.0.0.1:5555.")
        print("Prende el instrumento virtual en otra terminal: python3 instrumento_virtual.py")
        sys.exit(1)
    try:
        idn = parsear_idn(osc.preguntar("*IDN?"))
        filas = barrer(osc, CANALES)
    finally:
        osc.cerrar()

    verificaciones = [verificar_canal(filas, canal) for canal in CANALES]

    carpeta = os.path.dirname(os.path.abspath(__file__))
    series, rechazadas = leer_log(os.path.join(carpeta, "mediciones.log"))

    print(armar_informe(idn, series, verificaciones))
    print()
    print("Lineas rechazadas del registro: %d" % len(rechazadas))
    for nro, _, motivo in rechazadas:
        print("  linea %3d: %s" % (nro, motivo))
