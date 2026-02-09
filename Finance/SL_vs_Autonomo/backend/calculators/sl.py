"""
Sociedad Limitada (SL) take-home pay calculator.

Calculates net income from company billing, accounting for:
- Company expenses + gestoría
- Administrator salary + employer/employee SS
- Impuesto de Sociedades (corporate tax)
- Dividend distribution + IRPF del ahorro
- Optimal salary/dividend split finder
"""

from ..tax_engine.irpf import calcular_irpf_general, calcular_irpf_ahorro, calcular_irpf_detalle, calcular_irpf_trabajo, calcular_base_trabajo
from ..tax_engine.impuesto_sociedades import calcular_is, TipoEmpresa, determinar_tipo_empresa
from ..tax_engine.seguridad_social import calcular_ss_empleado, calcular_ss_empresa


def calcular_sl(
    facturacion_anual: float,
    salario_administrador: float = 18_000.0,
    gastos_empresa: float = 2_000.0,
    gastos_gestoria: float = 3_000.0,
    tipo_empresa: str = "micro",
    region: str = "Madrid",
    pct_dividendos: float = 1.0,  # 0.0 = retain all, 1.0 = distribute all
) -> dict:
    """
    Calculate SL net take-home pay.

    Args:
        facturacion_anual: Annual company billing (excl. IVA)
        salario_administrador: Annual admin salary (gross)
        gastos_empresa: Other deductible company expenses
        gastos_gestoria: Gestoría/accounting costs
        tipo_empresa: "startup", "micro", "sme", "general"
        region: Comunidad Autónoma
        pct_dividendos: Fraction of after-tax profit to distribute as dividends (0-1)
    """
    if facturacion_anual <= 0:
        return _empty_result(region)

    te = TipoEmpresa(tipo_empresa)

    # 1. Employer SS on admin salary
    ss_empresa = calcular_ss_empresa(salario_administrador)
    coste_ss_empresa = ss_empresa["cuota_anual"]

    # 2. Company profit before IS
    gastos_totales_empresa = (
        salario_administrador + coste_ss_empresa
        + gastos_empresa + gastos_gestoria
    )
    beneficio_antes_is = max(0, facturacion_anual - gastos_totales_empresa)

    # 3. Impuesto de Sociedades
    is_pagado = calcular_is(beneficio_antes_is, te)
    beneficio_despues_is = beneficio_antes_is - is_pagado

    # 4. Dividend distribution
    dividendos_brutos = beneficio_despues_is * pct_dividendos
    beneficio_retenido = beneficio_despues_is - dividendos_brutos

    # 5. IRPF on dividends (ahorro)
    irpf_dividendos = calcular_irpf_ahorro(dividendos_brutos)
    dividendos_netos = dividendos_brutos - irpf_dividendos

    # 6. Admin salary net (personal) — with employment income deductions
    ss_empleado = calcular_ss_empleado(salario_administrador)
    cuota_ss_empleado = ss_empleado["cuota_anual"]
    base_irpf_salario = calcular_base_trabajo(salario_administrador, cuota_ss_empleado)
    irpf_salario = calcular_irpf_trabajo(salario_administrador, cuota_ss_empleado, region)
    irpf_salario_detalle = calcular_irpf_detalle(base_irpf_salario, region)
    salario_neto = salario_administrador - cuota_ss_empleado - irpf_salario

    # 7. Total net income (salary + dividends)
    neto_total_anual = salario_neto + dividendos_netos
    neto_total_mensual = neto_total_anual / 12

    # 8. Total taxes paid
    total_impuestos = is_pagado + irpf_salario + irpf_dividendos + cuota_ss_empleado + coste_ss_empresa
    tipo_efectivo = total_impuestos / facturacion_anual if facturacion_anual > 0 else 0

    # 9. Breakdown
    breakdown = [
        {"label": "Ingreso neto personal", "amount": neto_total_anual, "color": "#059669"},
        {"label": "IRPF salario", "amount": irpf_salario, "color": "#dc2626"},
        {"label": "IRPF dividendos", "amount": irpf_dividendos, "color": "#e11d48"},
        {"label": "Impuesto Sociedades", "amount": is_pagado, "color": "#9333ea"},
        {"label": "SS empleado", "amount": cuota_ss_empleado, "color": "#ea580c"},
        {"label": "SS empresa", "amount": coste_ss_empresa, "color": "#d97706"},
        {"label": "Gastos empresa", "amount": gastos_empresa + gastos_gestoria, "color": "#6b7280"},
    ]
    if beneficio_retenido > 0:
        breakdown.append({"label": "Beneficio retenido en SL", "amount": beneficio_retenido, "color": "#2563eb"})

    return {
        "facturacion_anual": facturacion_anual,
        "salario_administrador": salario_administrador,
        "ss_empresa_anual": coste_ss_empresa,
        "gastos_totales_empresa": gastos_totales_empresa,
        "beneficio_antes_is": beneficio_antes_is,
        "is_pagado": is_pagado,
        "beneficio_despues_is": beneficio_despues_is,
        "dividendos_brutos": dividendos_brutos,
        "irpf_dividendos": irpf_dividendos,
        "dividendos_netos": dividendos_netos,
        "beneficio_retenido": beneficio_retenido,
        "salario_neto": salario_neto,
        "ss_empleado_anual": cuota_ss_empleado,
        "irpf_salario": irpf_salario,
        "irpf_salario_detalle": irpf_salario_detalle,
        "neto_total_anual": neto_total_anual,
        "neto_total_mensual": neto_total_mensual,
        "total_impuestos": total_impuestos,
        "tipo_efectivo": tipo_efectivo,
        "breakdown": breakdown,
        "region": region,
        "tipo_empresa": tipo_empresa,
        "pct_dividendos": pct_dividendos,
    }


def encontrar_salario_optimo(
    facturacion_anual: float,
    gastos_empresa: float = 2_000.0,
    gastos_gestoria: float = 3_000.0,
    tipo_empresa: str = "micro",
    region: str = "Madrid",
    pct_dividendos: float = 1.0,
    step: float = 500.0,
) -> dict:
    """
    Find the optimal admin salary that maximizes net personal income.
    Sweeps salary from SMI to facturación and returns the best split.

    Returns the optimal result + data points for the chart.
    """
    from ..tax_engine.constants import SMI_ANUAL_2025

    min_salary = SMI_ANUAL_2025
    max_salary = min(facturacion_anual * 0.8, 200_000)

    if max_salary <= min_salary:
        result = calcular_sl(facturacion_anual, min_salary, gastos_empresa, gastos_gestoria, tipo_empresa, region, pct_dividendos)
        return {
            "optimal_salary": min_salary,
            "optimal_result": result,
            "curve": [{"salary": min_salary, "net_income": result["neto_total_anual"]}],
        }

    best_salary = min_salary
    best_net = 0.0
    curve = []

    salary = min_salary
    while salary <= max_salary:
        result = calcular_sl(facturacion_anual, salary, gastos_empresa, gastos_gestoria, tipo_empresa, region, pct_dividendos)
        net = result["neto_total_anual"]
        curve.append({
            "salary": salary,
            "net_income": net,
            "irpf_salario": result["irpf_salario"],
            "irpf_dividendos": result["irpf_dividendos"],
            "is_pagado": result["is_pagado"],
            "total_impuestos": result["total_impuestos"],
        })
        if net > best_net:
            best_net = net
            best_salary = salary
        salary += step

    # Get full result at optimal salary
    optimal_result = calcular_sl(facturacion_anual, best_salary, gastos_empresa, gastos_gestoria, tipo_empresa, region, pct_dividendos)

    return {
        "optimal_salary": best_salary,
        "optimal_result": optimal_result,
        "curve": curve,
    }


def _empty_result(region: str) -> dict:
    return {
        "facturacion_anual": 0, "salario_administrador": 0,
        "ss_empresa_anual": 0, "gastos_totales_empresa": 0,
        "beneficio_antes_is": 0, "is_pagado": 0,
        "beneficio_despues_is": 0, "dividendos_brutos": 0,
        "irpf_dividendos": 0, "dividendos_netos": 0,
        "beneficio_retenido": 0, "salario_neto": 0,
        "ss_empleado_anual": 0, "irpf_salario": 0,
        "irpf_salario_detalle": {"total": 0, "effective_rate": 0, "marginal_rate": 0, "brackets": []},
        "neto_total_anual": 0, "neto_total_mensual": 0,
        "total_impuestos": 0, "tipo_efectivo": 0,
        "breakdown": [], "region": region,
        "tipo_empresa": "micro", "pct_dividendos": 1.0,
    }
