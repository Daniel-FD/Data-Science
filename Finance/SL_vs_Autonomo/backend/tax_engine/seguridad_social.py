from __future__ import annotations

from .constants import SMI_MENSUAL, SS_EMPRESA_TIPO, SS_TRABAJADOR_TIPO, SOLIDARITY_TIERS_MENSUAL


def calcular_ss_empresa(salario_anual: float) -> float:
    return salario_anual * SS_EMPRESA_TIPO


def calcular_ss_trabajador(salario_anual: float) -> float:
    return salario_anual * SS_TRABAJADOR_TIPO


def calcular_solidaridad(salario_anual: float) -> float:
    salario_mensual = salario_anual / 12
    MIN_THRESHOLD = 4_909.50
    
    if salario_mensual <= MIN_THRESHOLD:
        return 0.0

    total = 0.0
    limite_anterior = MIN_THRESHOLD
    
    for limite, tipo in SOLIDARITY_TIERS_MENSUAL:
        if salario_mensual <= limite_anterior:
            break
        
        # Calculate the portion of salary in this bracket
        tramo_inferior = max(MIN_THRESHOLD, limite_anterior)
        tramo_superior = min(salario_mensual, limite)
        tramo = tramo_superior - tramo_inferior
        
        if tramo > 0:
            total += tramo * tipo
        
        limite_anterior = limite

    return total * 12
