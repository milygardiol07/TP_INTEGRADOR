#!/usr/bin/env python3
"""
resumen(valores)                       -> n, minimo, maximo, promedio, desvio
fuera_de_rango(valores, minimo, maximo) -> posiciones que se salen del rango

El desvio es el de la MUESTRA (se divide por n - 1):
    desvio = raiz( suma((v - promedio)^2) / (n - 1) )

"""

import math


def es_numero(valor):
    """True si valor es un int o float finito (no bool, no NaN, no infinito)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return math.isfinite(valor)


def resumen(valores):
    """
    Devuelve {"n", "minimo", "maximo", "promedio", "desvio"} de la serie.
    Devuelve None si la lista esta vacia o si tiene algo que no es un numero:
    un promedio calculado con un dato roto adentro no es un promedio.
    Con un solo valor el desvio es 0.0 (n - 1 seria cero).
    """
    if not valores:
        return None
    for v in valores:
        if not es_numero(v):
            return None

    n = len(valores)
    promedio = sum(valores) / n

    if n == 1:
        desvio = 0.0
    else:
        suma_cuadrados = 0.0
        for v in valores:
            suma_cuadrados += (v - promedio) ** 2
        desvio = math.sqrt(suma_cuadrados / (n - 1))

    return {
        "n": n,
        "minimo": min(valores),
        "maximo": max(valores),
        "promedio": promedio,
        "desvio": desvio,
    }


def fuera_de_rango(valores, minimo, maximo):
    """
    Devuelve la lista de posiciones (empezando en 0) de los valores que
    quedan afuera de [minimo, maximo]. Los dos extremos cuentan como adentro.
    Devuelve None si el rango esta al reves (minimo > maximo).
    """
    if minimo > maximo:
        return None
    posiciones = []
    for i, v in enumerate(valores):
        if v < minimo or v > maximo:
            posiciones.append(i)
    return posiciones


# ---- pruebas ----
if __name__ == "__main__":
    import os

    # -- a) resumen --
    # Serie clasica: promedio 5, desvio de la MUESTRA raiz(32/7) = 2,138.
    # Si se dividiera por n en vez de n - 1 daria 2,0 y esta prueba fallaria.
    r = resumen([2, 4, 4, 4, 5, 5, 7, 9])
    assert r["n"] == 8
    assert r["minimo"] == 2 and r["maximo"] == 9
    assert r["promedio"] == 5.0
    assert math.isclose(r["desvio"], math.sqrt(32 / 7))
    assert not math.isclose(r["desvio"], 2.0)          # el de la poblacion NO

    # Serie constante: desvio exactamente 0.
    assert resumen([3.0, 3.0, 3.0])["desvio"] == 0.0

    # El minimo y el maximo no dependen del orden ni de la posicion.
    r2 = resumen([1000.4, 995.5, 1004.9, 999.0])
    assert r2["minimo"] == 995.5 and r2["maximo"] == 1004.9

    # Valores negativos: el promedio puede dar 0 y el desvio no.
    r3 = resumen([-1.0, 1.0])
    assert r3["promedio"] == 0.0
    assert math.isclose(r3["desvio"], math.sqrt(2))

    # casos raros
    assert resumen([]) is None                         # lista vacia
    assert resumen(None) is None
    unico = resumen([7.5])                             # un solo valor: no divide por cero
    assert unico == {"n": 1, "minimo": 7.5, "maximo": 7.5,
                     "promedio": 7.5, "desvio": 0.0}
    assert resumen([1.0, None, 3.0]) is None           # medicion que fallo
    assert resumen([1.0, float("nan")]) is None        # NaN del log
    assert resumen([1.0, "2.0"]) is None               # texto sin convertir

    # -- b) fuera_de_rango --
    serie = [999.0, 1000.0, 1010.0, 990.0, 1001.0]
    assert fuera_de_rango(serie, 995.0, 1005.0) == [2, 3]
    # Los extremos cuentan como ADENTRO: con < o > mal puestos esto falla.
    assert fuera_de_rango([1.0, 2.0, 3.0], 1.0, 3.0) == []
    assert fuera_de_rango([0.999, 1.0, 3.0, 3.001], 1.0, 3.0) == [0, 3]
    # Devuelve posiciones, no valores: con 5 y 6 adentro de la lista se nota.
    assert fuera_de_rango([5, 6, 100], 5, 6) == [2]
    # casos raros
    assert fuera_de_rango([], 0.0, 1.0) == []          # lista vacia
    assert fuera_de_rango([5.0], 5.0, 5.0) == []       # rango de un solo punto
    assert fuera_de_rango([1.0, 2.0], 3.0, 1.0) is None  # rango al reves

    # -- control con la serie de verdad --
    # Promedio de la frecuencia de CH1 en mediciones.log a menos del 0,5 %
    # de 1000 Hz y desvio menor que 5 Hz.
    # La serie sale del ejercicio 8: si este control falla, el error esta alla.
    leer_log = __import__("08_log").leer_log

    carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta_log = os.path.join(carpeta, "mediciones.log")
    if os.path.exists(ruta_log):
        series, _ = leer_log(ruta_log)
        control = resumen(series.get(("ADS3202", "CH1", "FREQ"), []))
        assert control is not None
        # 20 tandas de CH1 a intervalos de 15 s + la linea separada con
        # tabulaciones (09:17:31). Si sale 20, se perdio el dato del tab.
        assert control["n"] == 21
        assert abs(control["promedio"] - 1000.0) / 1000.0 < 0.005
        assert control["desvio"] < 5.0
        print("control con mediciones.log: n=%d promedio=%.3f Hz desvio=%.3f Hz"
              % (control["n"], control["promedio"], control["desvio"]))
    else:
        print("control con mediciones.log salteado: no esta el archivo")

    print("pruebas OK")