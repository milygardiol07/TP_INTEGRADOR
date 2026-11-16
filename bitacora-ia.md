# Bitácora de IA

Una entrada por cada vez que se usó IA para algo que quedó en la entrega.
Herramienta: Claude Code (modelo Claude Opus 5.5), dentro de VS Code.

| Martín Camillo |
| Leandro Fernandez |
| Federico Rodríguez |
| Sergio Damian Gil |
| Gardiol Milagros |
---

## Entrada 1 · Ejercicio 6 — `barrer`

### El prompt

```
Escribí 
modelo igual a 
ADS3202 .
barrer(instrumento, canales) , que le pide al instrumento las tres magnitudes de
cada canal y devuelve una lista de diccionarios, uno por medición, con el canal, la mag
nitud, la unidad, el texto crudo que devolvió el equipo y el valor ya convertido a número.
Prof. Pablo E. Hernández · Prof. Candela Fernández Ibáñez
10 / 17
Los diez ejercicios
TUT · Programación
Los comandos son estos, y el 
:MEASUrement:CH1:FREQuency?
:MEASUrement:CH1:PKPK?
:MEASUrement:CH1:CYCRms?
? de cada uno es obligatorio:
Para CH2 es igual cambiando el número. Con dos canales y tres magnitudes, 
vuelve seis mediciones.
Si el instrumento contesta un error, el valor queda en 
barrer de
None pero el texto crudo se
guarda igual: al que después lea el informe le sirve más saber qué contestó el equipo
que ver un casillero vacío.
CÓMO PROBAR ESTO SIN PRENDER EL INSTRUMENTO
barrer recibe el instrumento por parámetro. Eso no es un detalle de estilo: es lo que te
permite probarla.
Escribí en tu archivo de pruebas una clase chiquita, de mentira, que tenga un método 
guntar y conteste siempre lo mismo, y pasásela a 
pre
barrer . Ahora podés probar el barrido
entero sin red, sin esperas y con resultados que no tiemblan.
La misma función anda con el instrumento de verdad y con el de mentira, porque lo único
que le pide es que sepa contestar 
preguntar . Guardá esta idea: es de las más útiles que te
vas a llevar de la materia
```

(El archivo `06_barrido.py` ya tenía el `InstrumentoFalso` y los `assert`. Faltaba la función `barrer`.)

### Qué contestó

La función `barrer` con una tabla `MAGNITUDES` (nombre SCPI, nombre corto, unidad)
y dos ciclos `for` anidados, uno por canal y otro por magnitud. Cada comando se arma como
`":MEASUrement:" + canal + ":" + magnitud + "?"`. Escribió además su propia `a_numero`, que devuelve
`None` para `"NaN"`, y pasó las pruebas adentro de `if __name__ == "__main__":`.

### Qué cambiaste

- La IA leyó mal el pedazo "modelo igual a ADS3202" (es la prueba del **ejercicio 5**, quedó
  pegada al copiar la consigna) y agregó una constante `MODELO = "ADS3202"` que no tenía
  nada que ver con el ejercicio 6. Se sacó.
- Su `a_numero` duplicaba la del ejercicio 2. Se arregló la del ejercicio 2 (ver entrada 3)
  y el 6 pasó a reutilizarla.

### Cómo lo verificaste

- Las pruebas que ya existían pasan: 6 mediciones, todos los comandos con `?`, el error de CH2 PKPK
  guardado como crudo con valor `None`, y el `"NaN"` también con valor `None`.
- Con el instrumento virtual prendido, `barrer(Instrumento(), ["CH1", "CH2"])` devolvió las 6
  mediciones con valores cerca de los nominales (1 kHz / 2 V y 2,5 kHz / 0,8 V).
- Se sacó a propósito el `"?"` del comando y la prueba falló.

---

## Entrada 2 · Revisión general contra la consigna

### El prompt

```
Como puedo saber que todo funciona según el tp integrador
```

(con el PDF de la consigna adjunto)

### Qué contestó

Corrió los 10 archivos, levantó el instrumento virtual y probó el 5 y el 6 contra él.
Hizo una lista de lo que faltaba: README y bitácora, pruebas en 5, 8 y 10, el programa
final del 10, código repetido entre 10 y 2, pruebas de 01 y 03 que corrían al importarlos,
y archivos sin commitear.

### Qué cambiaste

Nada en esta entrada: fue un diagnóstico. Los cambios están en la entrada 3.

### Cómo lo verificaste

Corriendo cada archivo a mano con `python3 NN_nombre.py`, con el instrumento prendido y sin él.

---

## Entrada 3 · Completar lo que faltaba (2, 5, 6, 8, 9, 10, README)

### El prompt

```
Corrige TODO lo que falta según lo que solicita el TP, incluso el README y la bitacora
```

### Qué contestó

- **01 y 03:** las pruebas pasaron adentro de `if __name__ == "__main__":`. Antes corrían
  (e imprimían) cada vez que otro archivo los importaba.
- **02:** `a_numero` ahora devuelve `None` para `"NaN"` e `"inf"`, que `float()` acepta sin error.
  Se agregaron pruebas para `None`, coma decimal, NaN, inf y negativos.
- **05:** se agregó el bloque de pruebas. Una parte va sin red, con un socket de mentira:
  respuesta partida en dos `recv`, dos respuestas pegadas, conexión cortada y puerto sin nadie.
  La otra parte va con el instrumento: `*IDN?` → `modelo == "ADS3202"`, una orden seguida
  de una consulta, una medición, un comando mal escrito y el multímetro en el puerto 5556.
- **06:** reutiliza `a_numero` del 2. Las pruebas comparan la lista exacta de comandos enviados,
  los validan con `validar` del 3 y prueban un canal inexistente y una lista vacía. También hace
  el barrido real.
- **08:** se agregó el bloque de pruebas: cada tipo de rechazo, la línea con tabulaciones,
  un archivo temporal con números de línea conocidos y el log real (exactamente 8 rechazadas,
  CH1 FREQ con 21 valores).
- **09:** el control con el log real ahora usa `leer_log` del 8 en lugar de un lector propio repetido.
- **10:** `armar_informe` reutiliza `con_unidad` (2), `resumen` (9) y `MAGNITUDES` (6).
  Se agregaron pruebas y el programa completo: identificar, barrer, verificar, leer el log e imprimir.
- **README.md** y esta bitácora.

### Qué cambiaste

- Una prueba del 10 que escribió la IA estaba mal: comparaba una línea entera sin los dos
  espacios iniciales y fallaba aunque el informe estaba bien. Se corrigió para buscar el texto
  dentro del informe.
- <!-- COMPLETAR: lo que cambien ustedes después de leerlo (nombres, textos del informe, etc.) -->

### Cómo lo verificaste

- Todos los archivos imprimen `pruebas OK`. Los ejercicios 5, 6 y 10 lo hacen con el instrumento
  prendido; sin él, avisan con un mensaje.
- **Pruebas de las pruebas:** en una copia del repositorio se rompió a propósito una cosa por vez
  y se comprobó que alguna prueba se pone en rojo:

  | Error introducido a propósito | ¿Lo detectó una prueba? |
  |---|---|
  | `barrer` manda el comando sin `?` | sí (06) |
  | `leer_log` usa `split(" ")` en vez de `split()` | sí (08) |
  | `a_numero` deja pasar `NaN` | sí (02) |
  | el informe dice siempre `COINCIDE` | sí (10) |
  | `enviar` no agrega el `"\n"` | sí (05) |

