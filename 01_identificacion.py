def parsear_idn(respuesta):
    # 1. Si la respuesta no es un texto o esta vacia, devolvemos None
    if not respuesta or not isinstance(respuesta, str):
        return None
    # 2. Si el instrumento devolvio un mensaje de error, no sirve
    if "ERROR" in respuesta:
        return None
    # 3. Separamos por comas y limpiamos los espacios de mas en cada campo
    campos = [campo.strip() for campo in respuesta.split(",")]
    # 4. Validamos que tenga al menos 4 campos (osciloscopio)
    if len(campos) < 4:
        return None
    # 5. Armamos y devolvemos el diccionario.
    # (Si el multimetro manda un 5to campo, simplemente se ignora y no se usa aqui)
    return {
        "fabricante": campos[0],
        "modelo": campos[1],
        "serie": campos[2],
        "version": campos[3]
    }


# ---- PRUEBAS (ASSERT) ----
if __name__ == "__main__":
    # Caso 1: Respuesta normal de un osciloscopio (4 campos)
    assert parsear_idn("OWON ,ADS3202 ,25470803 ,V1.2.0") == {
        "fabricante": "OWON",
        "modelo": "ADS3202",
        "serie": "25470803",
        "version": "V1.2.0"
    }

    # Caso 2: Respuesta normal de un multimetro (5 campos, descarta el ultimo)
    assert parsear_idn("OWON ,XDM1041 ,25470803 ,V4.4.0 ,3") == {
        "fabricante": "OWON",
        "modelo": "XDM1041",
        "serie": "25470803",
        "version": "V4.4.0"
    }

    # Caso 3: Campos con espacios molestos de mas alrededor
    assert parsear_idn(" OWON , ADS3202 , 25470803 , V1.2.0 ") == {
        "fabricante": "OWON",
        "modelo": "ADS3202",
        "serie": "25470803",
        "version": "V1.2.0"
    }

    # Caso 4 (Raro): Cadena vacia
    assert parsear_idn("") is None

    # Caso 5 (Raro): Respuesta de error del instrumento
    assert parsear_idn("ERROR: comando desconocido") is None

    # Caso 6 (Raro): Menos de 4 campos (faltan datos)
    assert parsear_idn("OWON ,ADS3202 ,25470803") is None

    print("pruebas OK")
