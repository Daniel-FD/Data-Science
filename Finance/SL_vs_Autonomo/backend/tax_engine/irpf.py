from __future__ import annotations

from typing import List, Tuple

from .constants import TRAMOS_AHORRO_2025
from .regional import get_regional_brackets


def _calcular_tramos(base: float, tramos: List[Tuple[float, float]]) -> float:
    if base <= 0:
        return 0.0
    impuesto = 0.0
    restante = base
    limite_anterior = 0.0
    for limite, tipo in tramos:
        tramo = min(restante, limite - limite_anterior)
        if tramo <= 0:
            break
        impuesto += tramo * tipo
        restante -= tramo
        limite_anterior = limite
    return impuesto


def calcular_irpf_ahorro(base: float) -> float:
    return _calcular_tramos(base, TRAMOS_AHORRO_2025)


def calcular_irpf_general(base: float, region: str) -> float:
    tramos = get_regional_brackets(region)
    return _calcular_tramos(base, tramos)
