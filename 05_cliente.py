#!/usr/bin/env python3
"""
Ejercicio 5: El cliente SCPI
"""

import socket

class Instrumento:
    def __init__(self, host="127.0.0.1", puerto=5555):
        """Crea el socket TCP y se conecta al instrumento virtual."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, puerto))
        # Preparamos un archivo de lectura para recibir líneas de texto fácilmente
        self._archivo_lectura = self.socket.makefile("r", encoding="utf-8")

    def enviar(self, comando):
        """Manda una orden (sin respuesta esperada) terminada en \n."""
        if not comando.endswith("\n"):
            comando += "\n"
        self.socket.sendall(comando.encode("utf-8"))

    def preguntar(self, comando):
        """Manda una consulta (?) y devuelve la respuesta del instrumento limpia."""
        if not comando.endswith("\n"):
            comando += "\n"
        self.socket.sendall(comando.encode("utf-8"))
        # Lee la respuesta que devuelve el servidor hasta el salto de línea (\n)
        respuesta = self._archivo_lectura.readline()
        return respuesta.strip()

    def cerrar(self):
        """Cierra la conexión de red."""
        self._archivo_lectura.close()
        self.socket.close()


# --------------------------------------------------------------------
# PRUEBA MINIMA DE LA CONSIGNA
# --------------------------------------------------------------------
if __name__ == "__main__":
    print("Conectándose al instrumento virtual...")
    
    # 1. Creamos el objeto Instrumento apuntando al osciloscopio (puerto 5555)
    inst = Instrumento("127.0.0.1", 5555)
    
    # 2. Le preguntamos la identificación con *IDN?
    respuesta_cruda = inst.preguntar("*IDN?")
    print(f"Lo que devolvió el instrumento: {respuesta_cruda}")
    
    # 3. Verificamos que devuelva exactamente lo que pide la consigna
    assert respuesta_cruda == "OWON,ADS3202,25470803,V1.2.0", "La identificación no coincide"
    
    # 4. Cerramos la conexión
    inst.cerrar()
    
    print("¡Prueba del Ejercicio 5 exitosa!")