"""
Social Security calculators for all regimes.

- Employee (Régimen General): worker + employer portions
- Autónomo (RETA): income-based cuota system 2025
- Solidarity contribution: new 2025 surcharge on high salaries
"""

from .constants import (
    SS_EMPLEADO_TOTAL,
    SS_EMPRESA_TOTAL,
    SS_BASE_MINIMA_MENSUAL,
    SS_BASE_MAXIMA_MENSUAL,
    SS_BASE_MAXIMA_ANUAL,
    CUOTA_AUTONOMOS_TABLA,
    TARIFA_PLANA_MENSUAL,
    TARIFA_PLANA_MESES,
    TARIFA_PLANA_EXTENDIDA_MENSUAL,
    SMI_ANUAL_2025,
    SOLIDARIDAD_TRAMOS,
)


# ============================================================
# EMPLOYEE (Régimen General)
# ============================================================

def calcular_ss_empleado(salario_bruto_anual: float) -> dict:
    """
    Calculate employee's Social Security contribution.
    Capped at maximum contribution base.

    Returns dict with annual amount and breakdown.
    """
    salario_mensual = salario_bruto_anual / 12
    base_cotizacion_mensual = max(
        SS_BASE_MINIMA_MENSUAL,
        min(salario_mensual, SS_BASE_MAXIMA_MENSUAL),
    )
    base_cotizacion_anual = base_cotizacion_mensual * 12
    cuota_anual = base_cotizacion_anual * SS_EMPLEADO_TOTAL

    return {
        "cuota_anual": cuota_anual,
        "cuota_mensual": cuota_anual / 12,
        "base_cotizacion_anual": base_cotizacion_anual,
        "tipo": SS_EMPLEADO_TOTAL,
    }


def calcular_ss_empresa(salario_bruto_anual: float) -> dict:
    """
    Calculate employer's Social Security contribution.
    This is the "hidden" cost the company pays on top of gross salary.
    """
    salario_mensual = salario_bruto_anual / 12
    base_cotizacion_mensual = max(
        SS_BASE_MINIMA_MENSUAL,
        min(salario_mensual, SS_BASE_MAXIMA_MENSUAL),
    )
    base_cotizacion_anual = base_cotizacion_mensual * 12
    cuota_anual = base_cotizacion_anual * SS_EMPRESA_TOTAL

    # Solidarity contribution for high salaries
    solidaridad = calcular_cotizacion_solidaridad(salario_bruto_anual)

    return {
        "cuota_anual": cuota_anual + solidaridad,
        "cuota_ss_base": cuota_anual,
        "cotizacion_solidaridad": solidaridad,
        "cuota_mensual": (cuota_anual + solidaridad) / 12,
        "base_cotizacion_anual": base_cotizacion_anual,
        "tipo": SS_EMPRESA_TOTAL,
        "coste_total_empresa": salario_bruto_anual + cuota_anual + solidaridad,
    }


def calcular_cotizacion_solidaridad(salario_bruto_anual: float) -> float:
    """
    Calculate solidarity contribution (2025) on salary above max base.

    Progressive tiers on the excess:
      0-10% above max: 0.92%
      10-50% above max: 1.00%
      >50% above max: 1.17%
    """
    exceso = salario_bruto_anual - SS_BASE_MAXIMA_ANUAL
    if exceso <= 0:
        return 0.0

    cotizacion = 0.0
    restante = exceso
    max_base = SS_BASE_MAXIMA_ANUAL

    for fraction_limit, rate in SOLIDARIDAD_TRAMOS:
        tramo_size = max_base * fraction_limit if fraction_limit != float("inf") else float("inf")
        # Calculate how much of the previous fractions we've consumed
        prev_limit = 0.0
        if SOLIDARIDAD_TRAMOS.index((fraction_limit, rate)) > 0:
            prev_idx = SOLIDARIDAD_TRAMOS.index((fraction_limit, rate)) - 1
            prev_limit = max_base * SOLIDARIDAD_TRAMOS[prev_idx][0]

        current_tramo = min(restante, tramo_size - prev_limit) if fraction_limit != float("inf") else restante
        if current_tramo <= 0:
            break

        cotizacion += current_tramo * rate
        restante -= current_tramo

    return cotizacion


# ============================================================
# AUTÓNOMO (RETA)
# ============================================================

def calcular_cuota_autonomos(
    rendimiento_neto_anual: float,
    tarifa_plana: bool = False,
    meses_alta: int = 12,
) -> dict:
    """
    Calculate autónomo Social Security contribution.

    Args:
        rendimiento_neto_anual: Annual net income (after deductible expenses)
        tarifa_plana: Whether new-autónomo flat rate applies
        meses_alta: Months registered as autónomo this year (1-12)

    Returns dict with annual total and monthly breakdown.
    """
    rendimiento_mensual = rendimiento_neto_anual / 12

    # Find applicable monthly cuota from income table
    cuota_mensual_normal = CUOTA_AUTONOMOS_TABLA[-1][1]  # default to max
    for limite, cuota in CUOTA_AUTONOMOS_TABLA:
        if rendimiento_mensual <= limite:
            cuota_mensual_normal = cuota
            break

    if tarifa_plana:
        # First 12 months: tarifa plana
        meses_plana = min(meses_alta, TARIFA_PLANA_MESES)
        meses_normal = max(0, meses_alta - TARIFA_PLANA_MESES)

        # Extended flat rate for months 13-24 if income < SMI
        if rendimiento_neto_anual < SMI_ANUAL_2025 and meses_alta > TARIFA_PLANA_MESES:
            meses_extendida = min(meses_normal, 12)
            meses_normal = max(0, meses_normal - 12)
            cuota_total = (
                meses_plana * TARIFA_PLANA_MENSUAL
                + meses_extendida * TARIFA_PLANA_EXTENDIDA_MENSUAL
                + meses_normal * cuota_mensual_normal
            )
        else:
            cuota_total = (
                meses_plana * TARIFA_PLANA_MENSUAL
                + meses_normal * cuota_mensual_normal
            )

        cuota_mensual_efectiva = cuota_total / meses_alta if meses_alta > 0 else 0
    else:
        cuota_total = cuota_mensual_normal * meses_alta
        cuota_mensual_efectiva = cuota_mensual_normal

    return {
        "cuota_anual": cuota_total,
        "cuota_mensual": cuota_mensual_efectiva,
        "cuota_mensual_normal": cuota_mensual_normal,
        "tarifa_plana_aplicada": tarifa_plana,
        "rendimiento_mensual": rendimiento_mensual,
    }
