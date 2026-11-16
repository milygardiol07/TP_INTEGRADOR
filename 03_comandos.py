def es_consulta(comando):
    # Si el comando llega vacio, no es una consulta
    if not comando:
        return False
    # Preguntamos si el ultimo caracter del texto es "?"
    return comando.endswith("?")


def validar(comando):
    # Guardia 1: No puede estar vacio
    if not comando:
        return "El comando no puede estar vacio"
    # Guardia 2: Empieza con ':' o con '*'
    if not (comando.startswith(":") or comando.startswith("*")):
        return "El comando debe empezar con ':' o con '*'"
    # Guardia 3: No hay dos espacios seguidos
    if "  " in comando:
        return "No hay dos espacios seguidos"
    # Guardia 4: Hay a lo sumo un '?'
    if comando.count("?") > 1:
        return "Hay a lo sumo un '?'"
    # Guardia 5: Si hay un '?', obligatoriamente tiene que estar al final
    if "?" in comando and not comando.endswith("?"):
        return "El '?' va al final"
    # Guardias 6 y 7: Revisamos los espacios (argumentos)
    if es_consulta(comando):
        # Regla: "Una consulta no lleva argumento" (Cero espacios)
        if " " in comando:
            return "Una consulta no lleva argumento"
    else:
        # Regla: "Una orden lleva un solo argumento" (Exactamente 1 espacio)
        if comando.count(" ") != 1:
            return "Una orden lleva un solo argumento"
    # Si paso todos los controles, devolvemos la "nada" (todo OK).
    return None


# ---- PRUEBAS (ASSERT) ----
if __name__ == "__main__":
    # 1. Casos de exito (comandos perfectos que deben devolver None o True/False)
    assert es_consulta(":MEASUrement:CH1:FREQuency?") == True
    assert es_consulta(":CH1:DISPlay ON") == False
    assert validar("*IDN?") is None
    assert validar(":CH1:DISPlay ON") is None

    # 2. Casos que rompen reglas especificas
    assert validar("") == "El comando no puede estar vacio"
    assert validar("CH1:DISPlay ON") == "El comando debe empezar con ':' o con '*'"
    assert validar(":CH1:  DISPlay ON") == "No hay dos espacios seguidos"
    assert validar(":CH1:DISPlay??") == "Hay a lo sumo un '?'"
    assert validar(":CH1:DIS?Play") == "El '?' va al final"

    # 3. Validaciones de argumentos para ordenes (2 espacios o 0 espacios)
    assert validar(":CH1:SCALe 1 v") == "Una orden lleva un solo argumento"
    assert validar(":CH1:DISPlay") == "Una orden lleva un solo argumento"

    # 4. Validaciones de argumentos para consultas (con un espacio de mas)
    assert validar(":CH1:DISPlay ON?") == "Una consulta no lleva argumento"

    print("pruebas OK")
