#!/usr/bin/env python3
"""
Compara lo que el instrumento MIDE con lo que la fisica PREDICE.
Para una senoide:

    Vp   = Vpp / 2
    Vrms = Vp / raiz(2)

Una medicion nunca se compara con ==, porque el instrumento tiembla:
se pregunta si el error relativo cae dentro de una tolerancia.

    error = |medido - teorico| / |teorico|

Se ejecuta solo, sin el instrumento virtual:

    python3 07_verificacion.py
"""

import math

TOLERANCIA_POR_DEFECTO = 0.02      # 2 %


def es_numero(valor):
    """True si valor es un int o float finito (no bool, no NaN, no infinito)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return math.isfinite(valor)


def vrms_teorico(vpp):
    """
    Devuelve el Vrms de una senoide de vpp volt pico a pico.
    Devuelve None si vpp no es un numero o no es positivo: una tension
    pico a pico negativa no existe, y con 0 V no hay senal que verificar
    (ademas el error relativo dividiria por cero).
    """
    if not es_numero(vpp) or vpp <= 0:
        return None
    vp = vpp / 2
    return vp / math.sqrt(2)


def error_relativo(medido, teorico):
    """|medido - teorico| / |teorico|, o None si no se puede calcular."""
    if not es_numero(medido) or not es_numero(teorico) or teorico == 0:
        return None
    return abs(medido - teorico) / abs(teorico)


def coincide(medido, teorico, tolerancia=TOLERANCIA_POR_DEFECTO):
    """
    True si medido cae dentro de la tolerancia relativa de teorico.
    El borde cuenta como adentro (error == tolerancia -> True).
    Si algun dato no sirve, no se puede afirmar que coincida: False.
    """
    # Una tolerancia negativa no necesita control aparte: el error nunca
    # es negativo, asi que error <= tolerancia ya da False solo.
    if not es_numero(tolerancia):
        return False
    error = error_relativo(medido, teorico)
    if error is None:
        return False
    return error <= tolerancia


def buscar_valor(filas, canal, magnitud):
    """
    Busca en el resultado del barrido (ejercicio 6) la fila de ese canal
    y esa magnitud y devuelve su valor numerico, o None si no esta o si
    el instrumento contesto un error (valor None).
    La comparacion ignora mayusculas: "CYCRms" y "CYCRMS" son lo mismo.
    """
    for fila in filas:
        if (str(fila.get("canal", "")).upper() == canal.upper() and
                str(fila.get("magnitud", "")).upper() == magnitud.upper()):
            return fila.get("valor")
    return None


def verificar_canal(filas, canal, tolerancia=TOLERANCIA_POR_DEFECTO):
    """
    Busca el PKPK y el CYCRMS de ese canal en el barrido y dice si el
    Vrms medido coincide con el que predice la formula de la senoide.

    Devuelve un diccionario con:
        canal, vpp, vrms_medido, vrms_teorico, error, coincide, motivo
    motivo es None si se pudo verificar, o un texto que explica por que no.
    """
    vpp = buscar_valor(filas, canal, "PKPK")
    vrms_medido = buscar_valor(filas, canal, "CYCRMS")
    teorico = vrms_teorico(vpp)

    resultado = {
        "canal": canal,
        "vpp": vpp,
        "vrms_medido": vrms_medido,
        "vrms_teorico": teorico,
        "error": error_relativo(vrms_medido, teorico),
        "coincide": False,
        "motivo": None,
    }

    if vpp is None:
        resultado["motivo"] = "falta PKPK de " + canal
    elif teorico is None:
        resultado["motivo"] = "PKPK sin sentido fisico"
    elif not es_numero(vrms_medido):
        resultado["motivo"] = "falta CYCRMS de " + canal
    else:
        resultado["coincide"] = coincide(vrms_medido, teorico, tolerancia)

    return resultado


# ---- pruebas ----
if __name__ == "__main__":

    def fila(canal, magnitud, valor, crudo=None):
        """Arma una fila con el mismo formato que devuelve barrer (ej. 6)."""
        unidades = {"FREQ": "Hz", "PKPK": "V", "CYCRMS": "V"}
        if crudo is None:
            crudo = "%E" % valor if valor is not None else "ERROR: comando desconocido"
        return {"canal": canal, "magnitud": magnitud,
                "unidad": unidades.get(magnitud, ""),
                "crudo": crudo, "valor": valor}

    # -- a) vrms_teorico --
    # Valores de la tabla de la consigna: 2 V -> 707,1 mV y 0,8 V -> 282,8 mV.
    # Detecta si alguien se olvida de dividir por 2 (daria 1,414 V).
    assert math.isclose(vrms_teorico(2.0), 0.70710678, rel_tol=1e-6)
    assert math.isclose(vrms_teorico(0.8), 0.28284271, rel_tol=1e-6)
    assert vrms_teorico(2) is not None                 # un int tambien sirve
    # casos raros: datos sin sentido
    assert vrms_teorico(None) is None
    assert vrms_teorico(-2.0) is None
    assert vrms_teorico(0.0) is None
    assert vrms_teorico("2.0") is None                 # texto, no numero
    assert vrms_teorico(float("nan")) is None
    assert vrms_teorico(float("inf")) is None

    # -- b) coincide --
    assert coincide(0.7071, 0.7071)                    # identico
    assert coincide(0.7071 * 1.019, 0.7071)            # 1,9 % arriba: adentro
    assert coincide(0.7071 * 0.981, 0.7071)            # 1,9 % abajo: adentro
    assert not coincide(0.7071 * 1.021, 0.7071)        # 2,1 % arriba: afuera
    assert not coincide(0.7071 * 0.979, 0.7071)        # 2,1 % abajo: afuera (detecta si falta el abs)
    # Justo en el borde cuenta como adentro (<=, no <). Se usa 1.25 / 0.25
    # porque son exactos en binario: 1.02 - 1.0 da 0.020000000000000018 en
    # punto flotante y quedaria "afuera" por un error de redondeo.
    assert coincide(1.25, 1.0, 0.25)
    # Error RELATIVO, no absoluto: 0,5 mV contra 1 mV es un 50 % de error.
    # Una implementacion que hiciera |m - t| <= 0.02 diria que si.
    assert not coincide(0.0005, 0.001)
    # Y al reves: 15 Hz sobre 1000 Hz es 1,5 %; con error absoluto daria que no.
    assert coincide(1015.0, 1000.0)
    # La tolerancia es un parametro de verdad, no un 0.02 escondido.
    assert not coincide(1.03, 1.0)
    assert coincide(1.03, 1.0, 0.05)
    assert not coincide(1.001, 1.0, 0.0)
    # casos raros
    assert not coincide(None, 0.7071)
    assert not coincide(0.7071, None)
    assert not coincide(0.0, 0.0)                      # teorico 0: no hay division
    assert not coincide(float("nan"), 0.7071)
    assert not coincide(0.7071, 0.7071, -0.01)         # tolerancia negativa
    assert not coincide(0.7071, 0.7071, None)          # tolerancia que no es numero

    # -- c) verificar_canal --
    # Lecturas reales del instrumento (primera tanda de mediciones.log).
    barrido = [
        fila("CH1", "FREQ", 999.3761),
        fila("CH1", "PKPK", 2.005930),
        fila("CH1", "CYCRMS", 0.7090821),
        fila("CH2", "FREQ", 2491.979),
        fila("CH2", "PKPK", 0.7961074),
        fila("CH2", "CYCRMS", 0.2837790),
    ]
    v1 = verificar_canal(barrido, "CH1")
    assert v1["coincide"] is True
    assert v1["motivo"] is None
    assert v1["vpp"] == 2.005930 and v1["vrms_medido"] == 0.7090821
    assert v1["error"] < 0.02
    # CH2 tiene que leer SUS valores, no los de CH1: 0,2838 contra
    # Vpp = 0,796 coincide, pero contra Vpp = 2,006 no coincidiria nunca.
    v2 = verificar_canal(barrido, "CH2")
    assert v2["coincide"] is True
    assert math.isclose(v2["vrms_teorico"], 0.7961074 / 2 / math.sqrt(2))

    # LA PRUEBA QUE DEMUESTRA QUE LA PRUEBA SIRVE:
    # una cuadrada de 2 Vpp tiene Vrms = 1 V; la formula de la senoide no
    # se le aplica y la verificacion tiene que decir que NO.
    cuadrada = [fila("CH1", "PKPK", 2.0), fila("CH1", "CYCRMS", 1.0)]
    vc = verificar_canal(cuadrada, "CH1")
    assert vc["coincide"] is False
    assert vc["motivo"] is None                        # se pudo verificar: no coincide
    assert vc["error"] > 0.4                           # 1 contra 0,707 es ~41 %

    # El orden de las filas no importa.
    assert verificar_canal(list(reversed(barrido)), "CH1")["coincide"] is True

    # casos raros: canal que no existe, lista vacia, error del instrumento
    v3 = verificar_canal(barrido, "CH3")
    assert v3["coincide"] is False and v3["motivo"] == "falta PKPK de CH3"
    assert verificar_canal([], "CH1")["motivo"] == "falta PKPK de CH1"
    con_error = [fila("CH1", "PKPK", 2.0), fila("CH1", "CYCRMS", None)]
    ve = verificar_canal(con_error, "CH1")
    assert ve["coincide"] is False and ve["motivo"] == "falta CYCRMS de CH1"
    pkpk_roto = [fila("CH1", "PKPK", -2.0), fila("CH1", "CYCRMS", 0.7071)]
    assert verificar_canal(pkpk_roto, "CH1")["motivo"] == "PKPK sin sentido fisico"
    # La magnitud puede venir escrita como en el comando SCPI (CYCRms).
    mixto = [fila("ch1", "PKPK", 2.0), fila("CH1", "CYCRms", 0.7071)]
    assert verificar_canal(mixto, "CH1")["coincide"] is True

    print("pruebas OK")