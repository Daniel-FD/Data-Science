from __future__ import annotations

from .constants import SMI_MENSUAL, SS_EMPRESA_TIPO, SS_TRABAJADOR_TIPO, SOLIDARITY_TIERS_MENSUAL


def calcular_ss_empresa(salario_anual: float) -> float:
    return salario_anual * SS_EMPRESA_TIPO


def calcular_ss_trabajador(salario_anual: float) -> float:
    return salario_anual * SS_TRABAJADOR_TIPO


def calcular_solidaridad(salario_anual: float) -> float:
    salario_mensual = salario_anual / 12
    if salario_mensual <= 4_909.50:
        return 0.0

    base = salario_mensual - 4_909.50
    total = 0.0
    limite_anterior = 0.0
    for limite, tipo in SOLIDARITY_TIERS_MENSUAL:
        tramo = min(base, limite - limite_anterior)
        if tramo <= 0:
            break
        total += tramo * tipo
        base -= tramo
        limite_anterior = limite

    return total * 12
