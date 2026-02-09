"""
Autónomo (Self-Employed / Freelancer) take-home pay calculator.

Calculates net income from billing, accounting for:
- Deductible expenses
- Cuota de autónomos (SS, income-based 2025)
- Tarifa plana option
- IRPF general (regional)
- Reverse calculator: salary equivalent
"""

from typing import Optional

from ..tax_engine.irpf import calcular_irpf_general, calcular_irpf_detalle
from ..tax_engine.seguridad_social import calcular_cuota_autonomos


def calcular_autonomo(
    facturacion_anual: float,
    region: str = "Madrid",
    gastos_deducibles_pct: float = 0.10,
    gastos_deducibles_fijos: float = 0.0,
    tarifa_plana: bool = False,
    cuota_personalizada: Optional[float] = None,
) -> dict:
    """
    Calculate autónomo net take-home pay.

    Args:
        facturacion_anual: Annual billing (what clients pay you, excl. IVA)
        region: Comunidad Autónoma
        gastos_deducibles_pct: Deductible expenses as % of billing (0.0-1.0)
        gastos_deducibles_fijos: Fixed deductible expenses (EUR/year)
        tarifa_plana: Whether tarifa plana applies (new autónomo)
        cuota_personalizada: Override monthly cuota (None = auto-calculate)
    """
    if facturacion_anual <= 0:
        return _empty_result(region)

    # 1. Deductible expenses
    gastos_variables = facturacion_anual * gastos_deducibles_pct
    gastos_totales = gastos_variables + gastos_deducibles_fijos
    rendimiento_neto = max(0, facturacion_anual - gastos_totales)

    # 2. Cuota de autónomos
    if cuota_personalizada is not None:
        cuota_info = {
            "cuota_anual": cuota_personalizada * 12,
            "cuota_mensual": cuota_personalizada,
            "cuota_mensual_normal": cuota_personalizada,
            "tarifa_plana_aplicada": False,
            "rendimiento_mensual": rendimiento_neto / 12,
        }
    else:
        cuota_info = calcular_cuota_autonomos(
            rendimiento_neto_anual=rendimiento_neto,
            tarifa_plana=tarifa_plana,
        )
    cuota_anual = cuota_info["cuota_anual"]

    # 3. IRPF (base = rendimiento neto - cuota autónomos)
    # Note: mínimo personal is applied inside calcular_irpf_detalle as tax credit
    base_irpf = max(0, rendimiento_neto - cuota_anual)
    irpf_detalle = calcular_irpf_detalle(base_irpf, region)
    irpf_anual = irpf_detalle["total"]

    # 4. Net income
    neto_anual = rendimiento_neto - cuota_anual - irpf_anual
    neto_mensual = neto_anual / 12

    # 5. Effective rates
    total_impuestos = cuota_anual + irpf_anual
    tipo_efectivo_total = total_impuestos / facturacion_anual if facturacion_anual > 0 else 0

    # 6. Reverse calculator: what salary would give the same net?
    # Approximate by iterating (employee with same net)
    salario_equivalente = _calcular_salario_equivalente(neto_anual, region)

    # 7. Breakdown
    breakdown = [
        {"label": "Ingreso neto", "amount": neto_anual, "color": "#059669"},
        {"label": "IRPF", "amount": irpf_anual, "color": "#dc2626"},
        {"label": "Cuota autónomos", "amount": cuota_anual, "color": "#ea580c"},
        {"label": "Gastos deducibles", "amount": gastos_totales, "color": "#6b7280"},
    ]

    return {
        "facturacion_anual": facturacion_anual,
        "facturacion_mensual": facturacion_anual / 12,
        "gastos_deducibles": gastos_totales,
        "rendimiento_neto": rendimiento_neto,
        "cuota_autonomos_anual": cuota_anual,
        "cuota_autonomos_mensual": cuota_info["cuota_mensual"],
        "cuota_info": cuota_info,
        "base_irpf": base_irpf,
        "irpf_anual": irpf_anual,
        "irpf_mensual": irpf_anual / 12,
        "irpf_detalle": irpf_detalle,
        "neto_anual": neto_anual,
        "neto_mensual": neto_mensual,
        "tipo_efectivo_total": tipo_efectivo_total,
        "tipo_efectivo_irpf": irpf_detalle["effective_rate"],
        "tipo_marginal_irpf": irpf_detalle["marginal_rate"],
        "total_impuestos_anual": total_impuestos,
        "salario_equivalente": salario_equivalente,
        "breakdown": breakdown,
        "region": region,
        "tarifa_plana": tarifa_plana,
    }


def _calcular_salario_equivalente(neto_objetivo: float, region: str) -> float:
    """
    Find the gross employee salary that produces the same net income.
    Uses binary search for efficiency.
    """
    from .employee import calcular_asalariado

    if neto_objetivo <= 0:
        return 0.0

    lo, hi = 0.0, neto_objetivo * 3
    for _ in range(50):  # converge quickly
        mid = (lo + hi) / 2
        result = calcular_asalariado(mid, region, 12)
        if result["salario_neto_anual"] < neto_objetivo:
            lo = mid
        else:
            hi = mid

    return round((lo + hi) / 2, 2)


def calcular_facturacion_para_salario(
    salario_neto_objetivo: float,
    region: str = "Madrid",
    gastos_deducibles_pct: float = 0.10,
    tarifa_plana: bool = False,
) -> float:
    """
    Reverse calculator: what must an autónomo bill to match a given net salary?
    """
    if salario_neto_objetivo <= 0:
        return 0.0

    lo, hi = 0.0, salario_neto_objetivo * 4
    for _ in range(50):
        mid = (lo + hi) / 2
        result = calcular_autonomo(mid, region, gastos_deducibles_pct, tarifa_plana=tarifa_plana)
        if result["neto_anual"] < salario_neto_objetivo:
            lo = mid
        else:
            hi = mid

    return round((lo + hi) / 2, 2)


def _empty_result(region: str) -> dict:
    return {
        "facturacion_anual": 0, "facturacion_mensual": 0,
        "gastos_deducibles": 0, "rendimiento_neto": 0,
        "cuota_autonomos_anual": 0, "cuota_autonomos_mensual": 0,
        "cuota_info": {}, "base_irpf": 0,
        "irpf_anual": 0, "irpf_mensual": 0,
        "irpf_detalle": {"total": 0, "effective_rate": 0, "marginal_rate": 0, "brackets": []},
        "neto_anual": 0, "neto_mensual": 0,
        "tipo_efectivo_total": 0, "tipo_efectivo_irpf": 0, "tipo_marginal_irpf": 0,
        "total_impuestos_anual": 0, "salario_equivalente": 0,
        "breakdown": [], "region": region, "tarifa_plana": False,
    }
