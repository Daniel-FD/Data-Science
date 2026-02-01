"""
Long-term investment simulator.

Given a monthly investment amount (net income - living expenses),
projects capital growth over time and calculates:
- Capital evolution year by year
- Monthly passive income (4% rule)
- Years to financial independence
- Sensitivity analysis (returns × years matrix)
- Bulk withdrawal vs FIRE-style annual withdrawal comparison

Key tax considerations:
- Personal portfolio: gains taxed at IRPF ahorro on withdrawal
- SL company portfolio: investment returns taxed at IS annually,
  then full distribution taxed at IRPF ahorro as dividends
- Bulk withdrawal hits higher IRPF ahorro brackets vs annual FIRE withdrawals
"""

from typing import List, Optional
from ..tax_engine.irpf import calcular_irpf_ahorro
from ..tax_engine.impuesto_sociedades import calcular_is, TipoEmpresa
from ..tax_engine.constants import REGLA_4_PERCENT
from ..calculators.autonomo import calcular_autonomo
from ..calculators.sl import calcular_sl


def simular_inversion(
    aportacion_mensual: float,
    rentabilidad_anual: float = 0.07,
    anos: int = 20,
    capital_inicial: float = 0.0,
    objetivo_renta_mensual: float = 2_000.0,
) -> dict:
    """
    Simulate long-term personal investment growth.

    Args:
        aportacion_mensual: Monthly investment amount (EUR)
        rentabilidad_anual: Expected annual return (decimal, e.g. 0.07)
        anos: Investment horizon in years
        capital_inicial: Starting capital
        objetivo_renta_mensual: Monthly passive income target (for FI calc)
    """
    historial = []
    capital = capital_inicial
    total_aportado = capital_inicial

    for ano in range(1, anos + 1):
        aportacion_anual = aportacion_mensual * 12
        rentabilidad = capital * rentabilidad_anual
        capital = capital + aportacion_anual + rentabilidad
        total_aportado += aportacion_anual

        # 4% rule passive income — use actual gains ratio for tax calc
        renta_bruta_anual = capital * REGLA_4_PERCENT
        gains_ratio = (capital - total_aportado) / capital if capital > 0 else 0
        plusvalias_en_renta = renta_bruta_anual * gains_ratio
        irpf_renta = calcular_irpf_ahorro(plusvalias_en_renta)
        renta_neta_anual = renta_bruta_anual - irpf_renta
        renta_neta_mensual = renta_neta_anual / 12

        historial.append({
            "ano": ano,
            "aportacion_anual": aportacion_anual,
            "rentabilidad": rentabilidad,
            "capital_acumulado": capital,
            "total_aportado": total_aportado,
            "plusvalias": capital - total_aportado,
            "renta_neta_mensual": renta_neta_mensual,
        })

    # Final results
    plusvalias_total = capital - total_aportado

    # Bulk withdrawal: all gains taxed in one year
    irpf_rescate_bulk = calcular_irpf_ahorro(plusvalias_total)
    capital_neto_bulk = capital - irpf_rescate_bulk

    # FIRE withdrawal: 4% rule, annual — gains proportional
    renta_bruta_final = capital * REGLA_4_PERCENT
    gains_ratio_final = plusvalias_total / capital if capital > 0 else 0
    plusvalias_en_renta_final = renta_bruta_final * gains_ratio_final
    irpf_renta_fire = calcular_irpf_ahorro(plusvalias_en_renta_final)
    renta_neta_fire = renta_bruta_final - irpf_renta_fire

    # Years to financial independence
    anos_fi = _calcular_anos_fi(
        aportacion_mensual, rentabilidad_anual, capital_inicial, objetivo_renta_mensual
    )

    return {
        "capital_bruto": capital,
        "total_aportado": total_aportado,
        "plusvalias": plusvalias_total,
        "irpf_rescate": irpf_rescate_bulk,
        "capital_neto": capital_neto_bulk,
        # FIRE-style annual withdrawal
        "renta_bruta_anual": renta_bruta_final,
        "renta_neta_anual": renta_neta_fire,
        "renta_neta_mensual": renta_neta_fire / 12,
        "irpf_renta_anual_fire": irpf_renta_fire,
        # Bulk vs FIRE comparison
        "rescate_bulk": {
            "capital_neto": capital_neto_bulk,
            "irpf": irpf_rescate_bulk,
            "tipo_efectivo": irpf_rescate_bulk / capital if capital > 0 else 0,  # effective rate on total capital
            "tipo_efectivo_sobre_base": irpf_rescate_bulk / plusvalias_total if plusvalias_total > 0 else 0,  # rate on taxable gains only
        },
        "rescate_fire": {
            "renta_bruta_anual": renta_bruta_final,
            "renta_neta_anual": renta_neta_fire,
            "renta_neta_mensual": renta_neta_fire / 12,
            "irpf_anual": irpf_renta_fire,
            "tipo_efectivo": irpf_renta_fire / renta_bruta_final if renta_bruta_final > 0 else 0,  # effective rate on total withdrawal
            "tipo_efectivo_sobre_base": irpf_renta_fire / plusvalias_en_renta_final if plusvalias_en_renta_final > 0 else 0,  # rate on taxable base only
        },
        "anos_independencia_financiera": anos_fi,
        "objetivo_renta_mensual": objetivo_renta_mensual,
        "aportacion_mensual": aportacion_mensual,
        "rentabilidad_anual": rentabilidad_anual,
        "historial": historial,
    }


def simular_inversion_empresa(
    aportacion_mensual: float,
    rentabilidad_anual: float = 0.07,
    anos: int = 20,
    capital_inicial: float = 0.0,
    tipo_empresa: TipoEmpresa = TipoEmpresa.MICRO,
) -> dict:
    """
    Simulate investment within an SL company.

    Key difference from personal: investment returns are taxed at IS (corporate tax)
    each year, reducing the effective compound rate.

    Args:
        aportacion_mensual: Monthly investment from retained earnings
        rentabilidad_anual: Expected gross annual return
        anos: Investment horizon
        capital_inicial: Starting company capital
        tipo_empresa: Company type for IS rate
    """
    historial = []
    capital = capital_inicial
    total_aportado = capital_inicial

    for ano in range(1, anos + 1):
        aportacion_anual = aportacion_mensual * 12
        rentabilidad_bruta = capital * rentabilidad_anual
        # Company pays IS on investment returns each year
        is_sobre_rentabilidad = calcular_is(rentabilidad_bruta, tipo_empresa)
        rentabilidad_neta = rentabilidad_bruta - is_sobre_rentabilidad
        capital = capital + aportacion_anual + rentabilidad_neta
        total_aportado += aportacion_anual

        historial.append({
            "ano": ano,
            "aportacion_anual": aportacion_anual,
            "rentabilidad_bruta": rentabilidad_bruta,
            "is_sobre_rentabilidad": is_sobre_rentabilidad,
            "rentabilidad_neta": rentabilidad_neta,
            "capital_acumulado": capital,
            "total_aportado": total_aportado,
        })

    return {
        "capital_bruto": capital,
        "total_aportado": total_aportado,
        "historial": historial,
    }


def _calcular_anos_fi(
    aportacion_mensual: float,
    rentabilidad_anual: float,
    capital_inicial: float,
    objetivo_mensual: float,
) -> Optional[int]:
    """Calculate years to reach financial independence (4% rule target)."""
    if aportacion_mensual <= 0 and capital_inicial <= 0:
        return None

    objetivo_capital = (objetivo_mensual * 12) / REGLA_4_PERCENT  # Capital needed
    capital = capital_inicial

    for ano in range(1, 100):
        capital = capital * (1 + rentabilidad_anual) + aportacion_mensual * 12
        if capital >= objetivo_capital:
            return ano

    return None  # Not achievable in 100 years


def generar_sensibilidad(
    aportacion_mensual: float,
    capital_inicial: float = 0.0,
    rentabilidades: Optional[List[float]] = None,
    horizontes: Optional[List[int]] = None,
) -> dict:
    """
    Generate sensitivity matrix: final capital for different returns × horizons.
    """
    if rentabilidades is None:
        rentabilidades = [0.03, 0.05, 0.07, 0.09, 0.11]
    if horizontes is None:
        horizontes = [5, 10, 15, 20, 25, 30]

    matrix = []
    for rent in rentabilidades:
        row = {"rentabilidad": rent, "values": {}}
        for anos in horizontes:
            result = simular_inversion(aportacion_mensual, rent, anos, capital_inicial)
            row["values"][str(anos)] = {
                "capital_neto": result["capital_neto"],
                "renta_mensual": result["renta_neta_mensual"],
            }
        matrix.append(row)

    return {
        "rentabilidades": rentabilidades,
        "horizontes": horizontes,
        "matrix": matrix,
    }


def comparar_escenarios_inversion(
    neto_empleado_mensual: float,
    neto_autonomo_mensual: float,
    neto_sl_mensual: float,
    gastos_mensuales: float,
    rentabilidad_anual: float = 0.07,
    anos: int = 20,
    capital_inicial: float = 0.0,
) -> dict:
    """
    Compare investment outcomes for all 3 tax regimes.

    Each regime produces different net income → different monthly investment.
    """
    scenarios = {}
    for name, neto in [
        ("employee", neto_empleado_mensual),
        ("autonomo", neto_autonomo_mensual),
        ("sl", neto_sl_mensual),
    ]:
        aportacion = max(0, neto - gastos_mensuales)
        result = simular_inversion(aportacion, rentabilidad_anual, anos, capital_inicial)
        result["neto_mensual_disponible"] = neto
        result["gastos_mensuales"] = gastos_mensuales
        scenarios[name] = result

    # Find best scenario
    best = max(scenarios.items(), key=lambda x: x[1]["capital_neto"])

    return {
        "scenarios": scenarios,
        "best_scenario": best[0],
        "gastos_mensuales": gastos_mensuales,
        "rentabilidad_anual": rentabilidad_anual,
        "anos": anos,
    }


def optimizar_inversion_autonomo_vs_sl(
    facturacion_anual: float,
    gastos_personales_mensuales: float,
    region: str = "Madrid",
    rentabilidad_anual: float = 0.07,
    anos: int = 20,
    capital_inicial: float = 0.0,
    gastos_deducibles_pct: float = 0.10,
    tarifa_plana: bool = False,
    gastos_empresa: float = 2000.0,
    gastos_gestoria: float = 3000.0,
    tipo_empresa: str = "micro",
    num_salary_steps: int = 50,
) -> dict:
    """
    Find the optimal salary for an SL administrator to maximize long-term
    investment capital, and compare against the autonomo regime.

    Key insight: SL company investment returns are taxed at IS annually,
    reducing the effective compound rate. When finally withdrawing as
    dividends, the full distribution is taxed at IRPF ahorro.
    """
    from ..tax_engine.constants import SMI_ANUAL_2025

    te = TipoEmpresa(tipo_empresa)

    # --- Autonomo scenario ---
    auto = calcular_autonomo(
        facturacion_anual, region, gastos_deducibles_pct,
        tarifa_plana=tarifa_plana,
    )
    invest_mensual = max(0, auto["neto_mensual"] - gastos_personales_mensuales)
    auto_sim = simular_inversion(invest_mensual, rentabilidad_anual, anos, capital_inicial)

    # --- SL salary sweep ---
    min_salary = max(SMI_ANUAL_2025, gastos_personales_mensuales * 12)
    max_salary = max(min_salary, facturacion_anual - gastos_empresa - gastos_gestoria - 1)
    n = num_salary_steps
    salaries = [min_salary + (max_salary - min_salary) * i / (n - 1) for i in range(n)]

    sl_scenarios = []  # type: List[dict]
    comparison_curve = []  # type: List[dict]
    best_total = -1.0
    best_idx = 0

    for idx, salary in enumerate(salaries):
        sl = calcular_sl(
            facturacion_anual, salary, gastos_empresa, gastos_gestoria,
            tipo_empresa, region, pct_dividendos=0.0,
        )
        personal_monthly = max(0, sl["salario_neto"] / 12 - gastos_personales_mensuales)
        personal_sim = simular_inversion(personal_monthly, rentabilidad_anual, anos, capital_inicial)

        # Company investment: returns taxed at IS each year
        company_monthly = sl["beneficio_despues_is"] / 12
        company_sim = simular_inversion_empresa(
            company_monthly, rentabilidad_anual, anos, 0, te,
        )

        # Withdrawal: full company capital distributed as dividends
        company_tax = calcular_irpf_ahorro(company_sim["capital_bruto"])
        company_neto = company_sim["capital_bruto"] - company_tax
        total_neto = personal_sim["capital_neto"] + company_neto

        scenario = {
            "salario_bruto": salary,
            "salario_neto_mensual": sl["salario_neto"] / 12,
            "inversion_personal_mensual": personal_monthly,
            "inversion_empresa_mensual": company_monthly,
            "capital_personal_neto": personal_sim["capital_neto"],
            "capital_empresa_bruto": company_sim["capital_bruto"],
            "capital_empresa_neto": company_neto,
            "total_neto": total_neto,
        }
        sl_scenarios.append(scenario)

        comparison_curve.append({
            "salario": salary,
            "capital_neto_total": total_neto,
            "capital_personal": personal_sim["capital_neto"],
            "capital_empresa": company_neto,
        })

        if total_neto > best_total:
            best_total = total_neto
            best_idx = idx

    # --- Build detailed scenario for a given salary ---
    def _build_detailed_scenario(salary: float, label: str) -> dict:
        """Compute full investment simulation + rescue breakdown for one SL salary."""
        sl_calc = calcular_sl(
            facturacion_anual, salary, gastos_empresa, gastos_gestoria,
            tipo_empresa, region, pct_dividendos=0.0,
        )
        p_monthly = max(0, sl_calc["salario_neto"] / 12 - gastos_personales_mensuales)
        p_sim = simular_inversion(p_monthly, rentabilidad_anual, anos, capital_inicial)
        c_monthly = sl_calc["beneficio_despues_is"] / 12
        c_sim = simular_inversion_empresa(c_monthly, rentabilidad_anual, anos, 0, te)

        # Personal rescue: only gains taxed
        personal_bruto = p_sim["capital_bruto"]
        personal_aportado = p_sim["total_aportado"]
        personal_plusvalias = personal_bruto - personal_aportado
        personal_irpf = calcular_irpf_ahorro(personal_plusvalias)
        personal_neto = personal_bruto - personal_irpf

        # Company rescue: full capital distributed as dividends
        company_bruto = c_sim["capital_bruto"]
        company_aportado = c_sim["total_aportado"]
        company_irpf = calcular_irpf_ahorro(company_bruto)
        company_neto = company_bruto - company_irpf

        total_bruto = personal_bruto + company_bruto
        total_impuestos = personal_irpf + company_irpf
        total_neto = personal_neto + company_neto

        # FIRE 4% rule for the combined scenario
        fire_renta_bruta = total_bruto * REGLA_4_PERCENT
        # Personal portion: only gains ratio is taxable
        p_ratio = personal_plusvalias / personal_bruto if personal_bruto > 0 else 0
        p_fire_withdrawal = (personal_bruto / total_bruto * fire_renta_bruta) if total_bruto > 0 else 0
        p_fire_taxable = p_fire_withdrawal * p_ratio  # only gains portion
        # Company portion: full distribution is taxable (dividends)
        c_fire_withdrawal = (company_bruto / total_bruto * fire_renta_bruta) if total_bruto > 0 else 0
        c_fire_taxable = c_fire_withdrawal  # 100% taxable as dividends
        # Combined into single IRPF ahorro call for correct progressive brackets
        fire_taxable_combined = p_fire_taxable + c_fire_taxable
        fire_irpf = calcular_irpf_ahorro(fire_taxable_combined)
        fire_renta_neta = fire_renta_bruta - fire_irpf

        return {
            "label": label,
            "salario_bruto": salary,
            "salario_neto_mensual": sl_calc["salario_neto"] / 12,
            "inversion_personal_mensual": p_monthly,
            "inversion_empresa_mensual": c_monthly,
            # Bruto (before rescue taxes)
            "capital_personal_bruto": personal_bruto,
            "capital_empresa_bruto": company_bruto,
            "capital_total_bruto": total_bruto,
            # Aportado
            "total_aportado_personal": personal_aportado,
            "total_aportado_empresa": company_aportado,
            # Rescue taxes
            "impuestos_personal": personal_irpf,
            "impuestos_empresa": company_irpf,
            "impuestos_total": total_impuestos,
            # Neto (after rescue taxes)
            "capital_personal_neto": personal_neto,
            "capital_empresa_neto": company_neto,
            "total_neto": total_neto,
            # FIRE
            "rescate_fire": {
                "renta_bruta_anual": fire_renta_bruta,
                "renta_neta_anual": fire_renta_neta,
                "renta_neta_mensual": fire_renta_neta / 12,
                "irpf_anual": fire_irpf,
                "tipo_efectivo": fire_irpf / fire_renta_bruta if fire_renta_bruta > 0 else 0,  # effective rate on total withdrawal
                "tipo_efectivo_sobre_base": fire_irpf / fire_taxable_combined if fire_taxable_combined > 0 else 0,  # rate on taxable base only
            },
            "rescate_bulk": {
                "capital_neto": total_neto,
                "irpf": total_impuestos,
                "tipo_efectivo": total_impuestos / total_bruto if total_bruto > 0 else 0,  # effective rate on total capital
                "tipo_efectivo_sobre_base": total_impuestos / (personal_plusvalias + company_bruto)
                    if (personal_plusvalias + company_bruto) > 0 else 0,  # rate on taxable base only
            },
            # Historial for charts
            "historial_personal": p_sim["historial"],
            "historial_empresa": c_sim["historial"],
            # Fiscal detail
            "detalle_fiscal": {
                "facturacion": facturacion_anual,
                "gastos_empresa": gastos_empresa,
                "gastos_gestoria": gastos_gestoria,
                "salario_bruto": salary,
                "ss_empleado_anual": sl_calc.get("ss_empleado_anual", 0),
                "ss_empresa_anual": sl_calc.get("ss_empresa_anual", 0),
                "irpf_salario": sl_calc.get("irpf_salario", 0),
                "salario_neto": sl_calc.get("salario_neto", 0),
                "beneficio_antes_is": sl_calc.get("beneficio_antes_is", 0),
                "is_pagado": sl_calc.get("is_pagado", 0),
                "beneficio_despues_is": sl_calc.get("beneficio_despues_is", 0),
                "tipo_efectivo": sl_calc.get("tipo_efectivo", 0),
            },
        }

    # Attach historial only for the optimal scenario
    best_salary = salaries[best_idx]

    auto_total = auto_sim["capital_neto"]
    all_totals = [auto_total] + [s["total_neto"] for s in sl_scenarios]
    overall_worst = min(all_totals)
    overall_best_total = max(best_total, auto_total)

    if auto_total >= best_total:
        regime = "autonomo"
        opt_salary = None  # type: Optional[float]
    else:
        regime = "sl"
        opt_salary = best_salary

    # --- Build 3 key SL scenarios with full detail ---
    scenario_todo_salario = _build_detailed_scenario(max_salary, "todo_salario")
    scenario_optimo = _build_detailed_scenario(best_salary, "optimo")
    scenario_todo_dividendos = _build_detailed_scenario(min_salary, "todo_dividendos")

    # Build detailed tax breakdowns for display
    auto_detail = {
        "facturacion": facturacion_anual,
        "gastos_deducibles": auto.get("gastos_deducibles", facturacion_anual * gastos_deducibles_pct),
        "rendimiento_neto": auto.get("rendimiento_neto", 0),
        "cuota_autonomos_anual": auto.get("cuota_autonomos_anual", 0),
        "irpf_anual": auto.get("irpf_anual", 0),
        "tipo_efectivo": auto.get("tipo_efectivo_total", auto.get("tipo_efectivo", 0)),
        "neto_anual": auto.get("neto_anual", 0),
        "neto_mensual": auto["neto_mensual"],
    }

    return {
        "autonomo": {
            "neto_mensual": auto["neto_mensual"],
            "inversion_mensual": invest_mensual,
            "capital_final_bruto": auto_sim["capital_bruto"],
            "total_aportado": auto_sim["total_aportado"],
            "plusvalias": auto_sim["plusvalias"],
            "impuestos_rescate": auto_sim["irpf_rescate"],
            "capital_final_neto": auto_sim["capital_neto"],
            "rescate_bulk": auto_sim["rescate_bulk"],
            "rescate_fire": auto_sim["rescate_fire"],
            "historial": auto_sim["historial"],
            "detalle_fiscal": auto_detail,
        },
        "sl_scenarios": sl_scenarios,
        "sl_key_scenarios": {
            "todo_salario": scenario_todo_salario,
            "optimo": scenario_optimo,
            "todo_dividendos": scenario_todo_dividendos,
        },
        "optimal": {
            "regime": regime,
            "salario_optimo": opt_salary,
            "capital_total_neto": overall_best_total,
            "ventaja_vs_peor": overall_best_total - overall_worst,
            "detalle_fiscal_sl": scenario_optimo["detalle_fiscal"],
        },
        "comparison_curve": comparison_curve,
    }
