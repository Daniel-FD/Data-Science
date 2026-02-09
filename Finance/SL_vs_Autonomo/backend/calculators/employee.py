"""
Employee (Asalariado) take-home pay calculator.

Calculates net salary from gross, accounting for:
- Employee Social Security contributions
- IRPF withholding (regional)
- Employer cost (hidden SS)
"""

from ..tax_engine.irpf import calcular_irpf_trabajo, calcular_base_trabajo, calcular_irpf_detalle
from ..tax_engine.seguridad_social import calcular_ss_empleado, calcular_ss_empresa


def calcular_asalariado(
    salario_bruto_anual: float,
    region: str = "Madrid",
    num_pagas: int = 14,
) -> dict:
    """
    Calculate employee net take-home pay.

    Args:
        salario_bruto_anual: Annual gross salary in EUR
        region: Comunidad Autónoma for IRPF calculation
        num_pagas: Number of payments per year (12 or 14)

    Returns complete breakdown including employer costs.
    """
    if salario_bruto_anual <= 0:
        return _empty_result(num_pagas)

    # 1. Employee Social Security
    ss_empleado = calcular_ss_empleado(salario_bruto_anual)
    cuota_ss_anual = ss_empleado["cuota_anual"]

    # 2. IRPF on salary (employment income deductions applied)
    base_irpf = calcular_base_trabajo(salario_bruto_anual, cuota_ss_anual)
    irpf_anual = calcular_irpf_trabajo(salario_bruto_anual, cuota_ss_anual, region)
    irpf_detalle = calcular_irpf_detalle(base_irpf, region)

    # 3. Net salary
    salario_neto_anual = salario_bruto_anual - cuota_ss_anual - irpf_anual
    salario_neto_mensual = salario_neto_anual / num_pagas

    # 4. Total deductions
    total_deducido = cuota_ss_anual + irpf_anual
    tipo_efectivo_total = total_deducido / salario_bruto_anual if salario_bruto_anual > 0 else 0

    # 5. Employer cost (hidden)
    ss_empresa = calcular_ss_empresa(salario_bruto_anual)
    coste_total_empresa = ss_empresa["coste_total_empresa"]

    # 6. Breakdown for visualization (where each euro goes)
    breakdown = [
        {"label": "Salario neto", "amount": salario_neto_anual, "color": "#059669"},
        {"label": "IRPF", "amount": irpf_anual, "color": "#dc2626"},
        {"label": "Seguridad Social (empleado)", "amount": cuota_ss_anual, "color": "#ea580c"},
    ]

    # Employer breakdown (iceberg)
    employer_breakdown = [
        {"label": "Salario bruto", "amount": salario_bruto_anual, "color": "#2563eb"},
        {"label": "SS empresa", "amount": ss_empresa["cuota_ss_base"], "color": "#ea580c"},
    ]
    if ss_empresa["cotizacion_solidaridad"] > 0:
        employer_breakdown.append({
            "label": "Cotización solidaridad",
            "amount": ss_empresa["cotizacion_solidaridad"],
            "color": "#dc2626",
        })

    return {
        "salario_bruto_anual": salario_bruto_anual,
        "salario_bruto_mensual": salario_bruto_anual / num_pagas,
        "ss_empleado_anual": cuota_ss_anual,
        "ss_empleado_mensual": cuota_ss_anual / num_pagas,
        "base_irpf": base_irpf,
        "irpf_anual": irpf_anual,
        "irpf_mensual": irpf_anual / num_pagas,
        "irpf_detalle": irpf_detalle,
        "salario_neto_anual": salario_neto_anual,
        "salario_neto_mensual": salario_neto_mensual,
        "tipo_efectivo_total": tipo_efectivo_total,
        "tipo_efectivo_irpf": irpf_detalle["effective_rate"],
        "tipo_marginal_irpf": irpf_detalle["marginal_rate"],
        "total_deducido_anual": total_deducido,
        # Employer
        "ss_empresa_anual": ss_empresa["cuota_anual"],
        "coste_total_empresa_anual": coste_total_empresa,
        "coste_total_empresa_mensual": coste_total_empresa / num_pagas,
        # Visualizations
        "breakdown": breakdown,
        "employer_breakdown": employer_breakdown,
        "num_pagas": num_pagas,
        "region": region,
    }


def _empty_result(num_pagas: int) -> dict:
    return {
        "salario_bruto_anual": 0,
        "salario_bruto_mensual": 0,
        "ss_empleado_anual": 0,
        "ss_empleado_mensual": 0,
        "base_irpf": 0,
        "irpf_anual": 0,
        "irpf_mensual": 0,
        "irpf_detalle": {"total": 0, "effective_rate": 0, "marginal_rate": 0, "brackets": []},
        "salario_neto_anual": 0,
        "salario_neto_mensual": 0,
        "tipo_efectivo_total": 0,
        "tipo_efectivo_irpf": 0,
        "tipo_marginal_irpf": 0,
        "total_deducido_anual": 0,
        "ss_empresa_anual": 0,
        "coste_total_empresa_anual": 0,
        "coste_total_empresa_mensual": 0,
        "breakdown": [],
        "employer_breakdown": [],
        "num_pagas": num_pagas,
        "region": "Madrid",
    }
