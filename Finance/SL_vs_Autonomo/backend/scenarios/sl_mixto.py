from __future__ import annotations

from typing import List, Tuple

from .models import ScenarioResult, ScenarioYear, SimulationRequest, OptimalSalaryPoint
from ..tax_engine.constants import SMI_ANUAL
from ..tax_engine.impuesto_sociedades import calcular_is
from ..tax_engine.irpf import calcular_irpf_ahorro, calcular_irpf_general
from ..tax_engine.seguridad_social import (
    calcular_solidaridad,
    calcular_ss_empresa,
    calcular_ss_trabajador,
)


def _simulate_with_salary(req: SimulationRequest, salario: float) -> ScenarioResult:
    historial = []
    capital = req.capital_inicial
    total_aportado = req.capital_inicial
    total_is = 0.0
    total_irpf = 0.0
    total_ss = 0.0

    for año in range(1, req.años + 1):
        ss_empresa = calcular_ss_empresa(salario)
        solidaridad = calcular_solidaridad(salario)
        beneficio_antes_is = (
            req.facturacion
            - req.gastos_deducibles
            - salario
            - ss_empresa
            - req.gastos_gestoria
            - solidaridad
        )

        is_pagado = calcular_is(
            beneficio_antes_is,
            req.turnover,
            req.company_age,
            req.is_startup,
        )
        beneficio_neto = beneficio_antes_is - is_pagado

        ss_trabajador = calcular_ss_trabajador(salario)
        irpf_salario = calcular_irpf_general(salario - ss_trabajador, req.region)
        salario_neto = salario - ss_trabajador - irpf_salario

        irpf_dividendos = calcular_irpf_ahorro(max(0.0, beneficio_neto))
        dividendos_netos = max(0.0, beneficio_neto - irpf_dividendos)

        ingresos_netos_totales = salario_neto + dividendos_netos
        aportacion = max(0.0, ingresos_netos_totales - req.gastos_personales)

        rent = capital * req.rentabilidad
        capital = capital + aportacion + rent
        total_aportado += aportacion

        impuestos_año = (
            is_pagado + irpf_salario + irpf_dividendos + ss_empresa + ss_trabajador + solidaridad
        )
        total_is += is_pagado
        total_irpf += irpf_salario + irpf_dividendos
        total_ss += ss_empresa + ss_trabajador + solidaridad

        historial.append(
            ScenarioYear(
                año=año,
                aportacion=aportacion,
                rentabilidad=rent,
                capital_acumulado=capital,
                impuestos_pagados_año=impuestos_año,
            )
        )

    plusvalias = capital - total_aportado
    impuestos_rescate = calcular_irpf_ahorro(plusvalias)
    capital_neto = capital - impuestos_rescate

    renta_anual_bruta = capital * 0.04
    impuesto_renta_anual = calcular_irpf_ahorro(renta_anual_bruta * 0.5)
    renta_anual_neta = renta_anual_bruta - impuesto_renta_anual

    return ScenarioResult(
        capital_bruto=capital,
        plusvalias=plusvalias,
        impuestos_rescate=impuestos_rescate,
        capital_neto=capital_neto,
        renta_anual_bruta=renta_anual_bruta,
        renta_anual_neta=renta_anual_neta,
        renta_mensual_neta=renta_anual_neta / 12,
        historial=historial,
        tax_breakdown={
            "is": total_is,
            "irpf": total_irpf,
            "ss": total_ss,
            "gestoria": req.gastos_gestoria * req.años,
        },
    )


def optimize_salary(req: SimulationRequest) -> Tuple[ScenarioResult, float, List[OptimalSalaryPoint]]:
    start = max(SMI_ANUAL, 0)
    end = max(req.facturacion, start)
    step = 500

    best_salary = start
    best_result = None
    curve: List[OptimalSalaryPoint] = []

    salario = start
    while salario <= end:
        result = _simulate_with_salary(req, salario)
        impuestos_totales = sum(result.tax_breakdown.values()) + result.impuestos_rescate
        curve.append(
            OptimalSalaryPoint(
                salario=salario,
                renta_mensual_neta=result.renta_mensual_neta,
                impuestos_totales=impuestos_totales,
            )
        )
        if best_result is None or result.renta_mensual_neta > best_result.renta_mensual_neta:
            best_result = result
            best_salary = salario
        salario += step

    return best_result, best_salary, curve
