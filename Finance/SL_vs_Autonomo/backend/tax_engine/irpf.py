"""
IRPF calculators (Income Tax).

- calcular_irpf_general: for employment/work income (uses regional brackets)
- calcular_irpf_ahorro: for savings income (dividends, capital gains) — national
- Includes mínimo personal (5,550€) as tax credit for all taxpayers
- Includes gastos deducibles del trabajador (2,000€) for employment income
- Includes reducción por rendimientos del trabajo for low employment income
"""

from typing import List, Tuple, Optional
from .constants import (
    TRAMOS_IRPF_AHORRO,
    TRAMOS_IRPF_ESTATAL,
    MINIMO_PERSONAL,
    GASTOS_DEDUCIBLES_TRABAJADOR,
    REDUCCION_TRABAJO_LIMITE_INFERIOR,
    REDUCCION_TRABAJO_MAXIMO,
    REDUCCION_TRABAJO_PENDIENTE,
)
from .regional import calcular_irpf_general_regional, _calcular_por_tramos


def calcular_irpf_ahorro(base: float) -> float:
    """
    Calculate IRPF del ahorro (savings income tax).
    Applied to dividends, capital gains, interest.
    National rates — no regional variation.

    2025 brackets:
      €0-6K: 19%, €6K-50K: 21%, €50K-200K: 23%, €200K-300K: 27%, >€300K: 30%
    """
    return _calcular_por_tramos(base, TRAMOS_IRPF_AHORRO)


def _reduccion_rendimientos_trabajo(rendimiento_neto_trabajo: float) -> float:
    """
    Reducción por rendimientos del trabajo (art. 20 LIRPF).
    Only applies to employment income (not autónomos).

    - rend_neto <= 14,852 → 7,302€ reduction
    - 14,852 < rend_neto → 7,302 - 1.4929 * (rend_neto - 14,852), min 0
    """
    if rendimiento_neto_trabajo <= 0:
        return 0.0
    if rendimiento_neto_trabajo <= REDUCCION_TRABAJO_LIMITE_INFERIOR:
        return REDUCCION_TRABAJO_MAXIMO
    reduccion = REDUCCION_TRABAJO_MAXIMO - REDUCCION_TRABAJO_PENDIENTE * (
        rendimiento_neto_trabajo - REDUCCION_TRABAJO_LIMITE_INFERIOR
    )
    return max(0.0, reduccion)


def calcular_irpf_general(
    base: float,
    region: str = "Madrid",
    es_rendimiento_trabajo: bool = False,
    minimo_personal: float = MINIMO_PERSONAL,
) -> float:
    """
    Calculate IRPF general (employment/work income tax).
    Combines estatal + autonómica portions based on region.
    Applies mínimo personal as tax credit.

    Args:
        base: Base imponible (after SS deductions, and after gastos deducibles
              del trabajador + reducción rendimientos if applicable)
        region: Comunidad Autónoma
        es_rendimiento_trabajo: If True, base should already include
              gastos_deducibles and reducción (caller handles this)
        minimo_personal: Mínimo personal y familiar (default 5,550€)
    """
    if base <= 0:
        return 0.0
    cuota_integra = calcular_irpf_general_regional(base, region)
    # Mínimo personal: compute tax at same rates on mínimo, subtract
    cuota_minimo = calcular_irpf_general_regional(minimo_personal, region)
    return max(0.0, cuota_integra - cuota_minimo)


def obtener_tipo_efectivo_irpf(base: float, region: str = "Madrid") -> float:
    """Get effective IRPF rate as a decimal (e.g., 0.25 = 25%)."""
    if base <= 0:
        return 0.0
    return calcular_irpf_general(base, region) / base


def obtener_tipo_marginal_irpf(base: float, region: str = "Madrid") -> float:
    """Get marginal IRPF rate at a given income level."""
    from .regional import get_tramos_irpf_region, _find_marginal_rate
    tramos = get_tramos_irpf_region(region)
    return _find_marginal_rate(base, tramos)


def calcular_base_trabajo(
    salario_bruto: float,
    ss_empleado: float,
) -> float:
    """
    Compute the base liquidable for employment income (rendimientos del trabajo).

    Applies:
    1. Deduct employee SS contributions
    2. Deduct 2,000€ gastos deducibles del trabajador
    3. Apply reducción por rendimientos del trabajo (for low income)
    """
    rendimiento_neto = max(0.0, salario_bruto - ss_empleado - GASTOS_DEDUCIBLES_TRABAJADOR)
    reduccion = _reduccion_rendimientos_trabajo(rendimiento_neto)
    return max(0.0, rendimiento_neto - reduccion)


def calcular_irpf_trabajo(
    salario_bruto: float,
    ss_empleado: float,
    region: str = "Madrid",
) -> float:
    """
    Calculate IRPF for employment income, applying all deductions:
    - SS employee contributions
    - 2,000€ gastos deducibles del trabajador
    - Reducción por rendimientos del trabajo
    - Mínimo personal (as tax credit)
    """
    base = calcular_base_trabajo(salario_bruto, ss_empleado)
    return calcular_irpf_general(base, region, es_rendimiento_trabajo=True)


def calcular_irpf_detalle(
    base: float,
    region: str = "Madrid",
    aplicar_minimo: bool = True,
) -> dict:
    """
    Calculate IRPF with detailed bracket breakdown.
    Returns dict with total tax, effective rate, marginal rate, and per-bracket detail.
    """
    from .regional import get_tramos_irpf_region
    tramos = get_tramos_irpf_region(region)

    if base <= 0:
        return {
            "total": 0.0,
            "effective_rate": 0.0,
            "marginal_rate": 0.0,
            "brackets": [],
            "minimo_personal": MINIMO_PERSONAL if aplicar_minimo else 0.0,
        }

    brackets = []
    restante = base
    limite_anterior = 0.0
    total = 0.0

    for limite, tipo in tramos:
        tramo = min(restante, limite - limite_anterior)
        if tramo <= 0:
            break
        tax = tramo * tipo
        total += tax
        brackets.append({
            "from": limite_anterior,
            "to": min(limite, base),
            "rate": tipo,
            "taxable": tramo,
            "tax": tax,
        })
        restante -= tramo
        limite_anterior = limite

    # Apply mínimo personal as tax credit
    minimo_credit = 0.0
    if aplicar_minimo:
        minimo_credit = _calcular_por_tramos(MINIMO_PERSONAL, tramos)
        total = max(0.0, total - minimo_credit)

    return {
        "total": total,
        "effective_rate": total / base if base > 0 else 0.0,
        "marginal_rate": brackets[-1]["rate"] if brackets else 0.0,
        "brackets": brackets,
        "minimo_personal": MINIMO_PERSONAL if aplicar_minimo else 0.0,
        "minimo_credit": minimo_credit,
    }
