UNIDADES = {"FREQ": "Hz", "PKPK": "V", "CYCRMS": "V"}
PREFIJOS = [(1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ")]


def formatear(valor, unidad):
    """Valor con prefijo SI y 4 cifras significativas: 0.2837 V -> '283.7 mV'."""
    if valor == 0:
        return f"0 {unidad}"
    for factor, prefijo in PREFIJOS:
        if abs(valor) >= factor:
            return f"{valor / factor:.4g} {prefijo}{unidad}"
    return f"{valor:.4g} {unidad}"


def _texto_verificacion(resultado):
    if resultado is True:
        return "OK"
    if resultado is False:
        return "FALLA"
    return str(resultado)


def armar_informe(idn, series, verificaciones):
    """Devuelve el informe como una sola cadena. No imprime ni abre archivos."""
    lineas = [f"Instrumento: {idn.strip()}", "", "Series:"]

    for clave in sorted(series):
        equipo, canal, magnitud = clave
        valores = series[clave]
        if not valores:
            continue
        unidad = UNIDADES.get(magnitud, "")
        promedio = sum(valores) / len(valores)
        lineas.append(
            f"  {equipo} {canal} {magnitud}: n={len(valores)}, "
            f"promedio={formatear(promedio, unidad)}, "
            f"mín={formatear(min(valores), unidad)}, "
            f"máx={formatear(max(valores), unidad)}"
        )

    lineas += ["", "Verificaciones:"]
    for canal in sorted(verificaciones):
        lineas.append(f"  {canal}: {_texto_verificacion(verificaciones[canal])}")

    return "\n".join(lineas)