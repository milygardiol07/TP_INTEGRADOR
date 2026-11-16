#!/usr/bin/env python3
"""
Ejercicio 6: El barrido de mediciones
Tecnicatura Universitaria en Telecomunicaciones — UTN FRBA
"""

def a_numero(texto):
    """
    Función auxiliar (del Ejercicio 2): convierte texto científico (ej: 1.000000E+03) 
    a un número float. Devuelve None si el texto no es un número o es un error.
    """
    if not texto or "ERROR" in texto or "NaN" in texto:
        return None
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        return None

def barrer(instrumento, canales):
    """
    Recorre los canales indicados y consulta Frecuencia, Vpp y Vrms.
    Devuelve una lista de diccionarios con el detalle de cada medición.
    """
    # Definimos las magnitudes, sus unidades oficiales y la plantilla SCPI
    magnitudes = [
        ("FREQ", "Hz", ":MEASUrement:{}:FREQuency?"),
        ("PKPK", "V", ":MEASUrement:{}:PKPK?"),
        ("CYCRMS", "V", ":MEASUrement:{}:CYCRms?")
    ]
    
    resultados = []
    
    for canal in canales:
        for mag_nombre, unidad, plantilla_cmd in magnitudes:
            # 1. Armamos el comando SCPI dinámicamente para el canal actual
            comando = plantilla_cmd.format(canal)
            
            # 2. Le preguntamos al instrumento (puede ser real o de mentira)
            texto_crudo = instrumento.preguntar(comando)
            
            # 3. Convertimos el texto a número flotante (o None si hubo error)
            valor_num = a_numero(texto_crudo)
            
            # 4. Guardamos el diccionario con el formato pedido
            resultados.append({
                "canal": canal,
                "magnitud": mag_nombre,
                "unidad": unidad,
                "crudo": texto_crudo,
                "valor": valor_num
            })
            
    return resultados


# --------------------------------------------------------------------
# PRUEBAS (assert) USANDO UN INSTRUMENTO DE MENTIRA (MOCK)
# --------------------------------------------------------------------
class InstrumentoFalso:
    """
    Instrumento simulado que cumple con la consigna: tiene un método 
    'preguntar' y devuelve valores predeterminados sin tocar la red.
    """
    def preguntar(self, comando):
        if "FREQuency" in comando:
            return "1.000000E+03"
        elif "PKPK" in comando:
            return "2.000000E+00"
        elif "CYCRms" in comando:
            return "7.071068E-01"
        return "ERROR: comando desconocido"

if __name__ == "__main__":
    # Creamos nuestro instrumento falso de prueba
    fake_inst = InstrumentoFalso()
    
    # Ejecutamos el barrido para un canal ("CH1")
    datos_barrido = barrer(fake_inst, ["CH1"])
    
    # Prueba 1: Verificar que devuelva exactamente 3 mediciones para 1 canal
    assert len(datos_barrido) == 3, f"Esperado 3 mediciones, obtuve {len(datos_barrido)}"
    
    # Prueba 2: Validar contenido y conversión numérica del primer elemento (FREQ)
    assert datos_barrido[0]["canal"] == "CH1"
    assert datos_barrido[0]["magnitud"] == "FREQ"
    assert datos_barrido[0]["unidad"] == "Hz"
    assert datos_barrido[0]["crudo"] == "1.000000E+03"
    assert datos_barrido[0]["valor"] == 1000.0
    
    # Prueba 3: Validar el valor de PKPK
    assert datos_barrido[1]["valor"] == 2.0
    
    # Prueba si pasamos dos canales ("CH1", "CH2") -> Debería devolver 6 mediciones
    datos_dos_canales = barrer(fake_inst, ["CH1", "CH2"])
    assert len(datos_dos_canales) == 6, f"Esperado 6 mediciones para 2 canales, obtuve {len(datos_dos_canales)}"
    
    print("Pruebas del Ejercicio 6 (Barrido) OK")