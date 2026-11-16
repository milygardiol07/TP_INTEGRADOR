# Banco de mediciones automatizado en Python

Trabajo Final Integrador · Programación  
Tecnicatura Universitaria en Telecomunicaciones · UTN FRBA · Ciclo lectivo 2026  
Prof. Pablo E. Hernández · Prof. Candela Fernández Ibáñez

## Integrantes


| Martín Camillo |
| Leandro Fernandez |
| Federico Rodríguez |
| Sergio Damian Gil |
| Gardiol Milagros |

## Qué hace

Una computadora que le habla por SCPI (texto sobre TCP) al osciloscopio ADS3202
simulado por `instrumento_virtual.py`. El programa lo identifica, le pide las mediciones,
verifica que tengan sentido físico, lee el registro de una sesión anterior
(`mediciones.log`) y escribe un informe.

## Requisitos

- Python 3, **solo la biblioteca estándar** (no hay que instalar nada).

## Cómo se ejecuta

Cada archivo se ejecuta solo y al final corre sus propias pruebas (`assert`):

```
python3 01_identificacion.py
python3 02_magnitudes.py
...
python3 09_estadistica.py
```

Si el instrumento no está prendido, esos tres archivos lo avisan con un mensaje en lugar de colgarse.
El 6 corre igual sus pruebas con el instrumento de mentira antes de intentar conectarse.

## Archivos

| Archivo | Qué resuelve | Usa |
|---|---|---|
| `01_identificacion.py` | `parsear_idn`: respuesta de `*IDN?` → diccionario | |
| `02_magnitudes.py` | `a_numero` y `con_unidad` (prefijos p…G) | |
| `03_comandos.py` | `es_consulta` y `validar` | |
| `04_configurar.py` | `comandos_de_canal` | 03 (en las pruebas) |
| `05_cliente.py` | clase `Instrumento`: `enviar`, `preguntar`, `cerrar` | 01 (en las pruebas) |
| `06_barrido.py` | `barrer(instrumento, canales)` | 02, 03 y 05 |
| `07_verificacion.py` | `vrms_teorico`, `coincide`, `verificar_canal` | |
| `08_log.py` | `analizar_linea` y `leer_log` | |
| `09_estadistica.py` | `resumen` y `fuera_de_rango` | 08 (control con el log real) |
| `10_informe.py` | `armar_informe` + el programa completo | 01, 02, 05, 06, 07, 08 y 09 |
| `instrumento_virtual.py` | lo entrega la cátedra, **no se modifica** | |
| `mediciones.log` | lo entrega la cátedra, **no se modifica** | |
| `bitacora-ia.md` | registro del uso de IA | |

Los nombres de archivo empiezan con un número, así que no se pueden importar con
`import 02_magnitudes`. Por eso las piezas se reutilizan con `__import__("02_magnitudes")`.

## Algunas decisiones

- **`barrer` recibe el instrumento por parámetro.** Así se puede probar con un
  `InstrumentoFalso` que tiene un método `preguntar`, sin red y con resultados que no tiemblan.
- **Las mediciones se comparan con tolerancia, nunca con `==`.** El instrumento
  tiembla ±0,5 % en cada lectura.
- **`a_numero("NaN")` devuelve `None`.** `float("NaN")` no da error, pero tampoco es una medición.
- **`leer_log` usa `split()` sin argumento.** Así la línea separada por tabulaciones
  (09:17:31) cuenta como dato bueno.
- **`armar_informe` no imprime ni abre archivos.** Sus pruebas lo controlan: capturan
  la salida y reemplazan `open` mientras la función corre.
