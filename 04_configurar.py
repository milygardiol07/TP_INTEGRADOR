#!/usr/bin/env python3

def comandos_de_canal(canal, display, acoplamiento, sonda, escala):
    """
    Genera la lista de 4 órdenes SCPI para configurar un canal del osciloscopio ADS3202.
    Devuelve None si el canal no es CH1 ni CH2.
    """
    # 1. Validamos que el canal exista en el equipo (solo CH1 o CH2)
    if canal != "CH1" and canal != "CH2":
        return None

    # 2. Armamos cada orden respetando exactamente las mayúsculas y minúsculas
    # exigidas por el protocolo del equipo y la consigna.
    orden_display = ":" + canal + ":DISPlay " + str(display)
    orden_acoplamiento = ":" + canal + ":COUPling " + str(acoplamiento)
    orden_sonda = ":" + canal + ":PROBe " + str(sonda)
    orden_escala = ":" + canal + ":SCALe " + str(escala)

    # 3. Devolvemos los comandos en el orden exacto pedido
    return [orden_display, orden_acoplamiento, orden_sonda, orden_escala]


# --- BLOQUE DE PRUEBAS ---
if __name__ == "__main__":
    # Prueba 1: Caso exacto del ejemplo de la consigna
    esperado = [
        ":CH1:DISPlay ON",
        ":CH1:COUPling DC",
        ":CH1:PROBe 10X",
        ":CH1:SCALe 1v"
    ]
    resultado_ch1 = comandos_de_canal("CH1", "ON", "DC", "10X", "1v")
    assert resultado_ch1 == esperado

    # Prueba 2: Funcionamiento correcto con el canal 2
    resultado_ch2 = comandos_de_canal("CH2", "OFF", "AC", "1X", "500mv")
    assert resultado_ch2 is not None
    assert len(resultado_ch2) == 4
    assert resultado_ch2[0] == ":CH2:DISPlay OFF"
    assert resultado_ch2[3] == ":CH2:SCALe 500mv"

    # Prueba 3: Casos inválidos (canales inexistentes o mal escritos)
    assert comandos_de_canal("CH3", "ON", "DC", "10X", "1v") is None
    assert comandos_de_canal("ch1", "ON", "DC", "10X", "1v") is None
    assert comandos_de_canal("", "ON", "DC", "10X", "1v") is None

    # Prueba 4: "Una prueba que vale por diez" (validación cruzada con el Ejercicio 3)
    # Importamos el módulo 03_comandos.py para comprobar que los comandos generados
    # cumplen con todas las reglas sintácticas de validar().
    mod_comandos = __import__("03_comandos")
    
    for comando in resultado_ch1:
        assert mod_comandos.validar(comando) is None

    for comando in resultado_ch2:
        assert mod_comandos.validar(comando) is None

    print("pruebas OK")