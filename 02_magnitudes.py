#!/usr/bin/env python3

def a_numero(texto):
    # Usamos try/except porque si 'texto' es "ERROR" o "", float() daría error y frenaría el programa.
    try:
        # strip() saca espacios o saltos de línea que puedan venir pegados
        return float(texto.strip())
    except (ValueError, AttributeError):
        # Si no se pudo convertir (ValueError) o si nos pasaron None en vez de texto (AttributeError)
        return None


def con_unidad(valor, unidad):
    # Caso especial: el cero no lleva prefijo
    if valor == 0:
        return "0 " + unidad

    # Guardamos los prefijos ordenados del más chico al más grande junto con su valor
    prefijos = [
        ("p", 1e-12),
        ("n", 1e-9),
        ("u", 1e-6),
        ("m", 1e-3),
        ("",  1.0),
        ("k", 1e3),
        ("M", 1e6),
        ("G", 1e9)
    ]

    # Trabajamos con el valor absoluto por si alguna vez entra un número negativo
    absoluto = abs(valor)
    
    # Por defecto arrancamos asumiendo el prefijo más chico ("p")
    indice = 0
    
    # Recorremos la lista para buscar qué prefijo deja al número entre 1 y 999.999...
    for i in range(len(prefijos)):
        factor = prefijos[i][1]
        if absoluto / factor >= 1.0:
            indice = i  # Mientras siga siendo >= 1, vamos subiendo de prefijo

    # Dividimos el valor original por el factor que elegimos
    prefijo_elegido = prefijos[indice][0]
    factor_elegido = prefijos[indice][1]
    escalado = valor / factor_elegido

    # Redondeamos a 3 decimales como pide la consigna
    redondeado = round(escalado, 3)

    # --- AQUÍ RESOLVEMOS LA TRAMPA DEL 999.9999 ---
    # Si al redondear llegamos a 1000 (o -1000) y todavía no estamos en "G" (el último):
    if abs(redondeado) >= 1000.0 and indice < len(prefijos) - 1:
        indice = indice + 1  # Subimos un escalón en la tabla de prefijos
        prefijo_elegido = prefijos[indice][0]
        factor_elegido = prefijos[indice][1]
        redondeado = round(valor / factor_elegido, 3)

    # Formateamos el número para que no muestre ".0" si es redondo (ej: "2 V" en vez de "2.0 V")
    if redondeado == int(redondeado):
        numero_texto = str(int(redondeado))
    else:
        numero_texto = str(redondeado)

    return numero_texto + " " + prefijo_elegido + unidad


# --- BLOQUE DE PRUEBAS ---
if __name__ == "__main__":
    # Pruebas de a_numero
    assert a_numero("1.000000E+03") == 1000.0
    assert a_numero("  2.837790E-01\n") == 0.283779
    assert a_numero("ERROR: comando desconocido") is None  # Caso raro: texto inválido
    assert a_numero("") is None  # Caso raro: cadena vacía

    # Pruebas de con_unidad (las de la tabla de la consigna)
    assert con_unidad(1000.0, "Hz") == "1 kHz"
    assert con_unidad(2500.0, "Hz") == "2.5 kHz"
    assert con_unidad(2.0, "V") == "2 V"
    assert con_unidad(0.707, "V") == "707 mV"
    assert con_unidad(0.0005, "s") == "500 us"
    assert con_unidad(0.0, "V") == "0 V"

    # Prueba de la trampa avisada en la consigna
    assert con_unidad(999.9999, "Hz") == "1 kHz"

    print("pruebas OK")