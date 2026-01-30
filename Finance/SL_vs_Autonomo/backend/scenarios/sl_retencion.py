from __future__ import annotations

from .models import ScenarioResult, ScenarioYear, SimulationRequest
from ..tax_engine.impuesto_sociedades import calcular_is
from ..tax_engine.irpf import calcular_irpf_ahorro, calcular_irpf_general
from ..tax_engine.seguridad_social import (
    calcular_solidaridad,
    calcular_ss_empresa,
    calcular_ss_trabajador,
)


def simulate_sl_retencion(req: SimulationRequest) -> ScenarioResult:
    historial = []
    capital_sl = 0.0
    capital_personal = req.capital_inicial
    total_aportado_sl = 0.0
    total_impuestos = 0.0
    total_is = 0.0
    total_irpf = 0.0
    total_ss = 0.0

    for año in range(1, req.años + 1):
        ss_empresa = calcular_ss_empresa(req.salario_administrador)
        solidaridad = calcular_solidaridad(req.salario_administrador)
        beneficio_antes_is = (
            req.facturacion
            - req.gastos_deducibles
            - req.salario_administrador
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

        ss_trabajador = calcular_ss_trabajador(req.salario_administrador)
        irpf_salario = calcular_irpf_general(req.salario_administrador - ss_trabajador, req.region)
        salario_neto = req.salario_administrador - ss_trabajador - irpf_salario

        rent_sl = capital_sl * req.rentabilidad
        capital_sl = capital_sl + beneficio_neto + rent_sl
        total_aportado_sl += beneficio_neto

        rent_personal = capital_personal * req.rentabilidad
        capital_personal = capital_personal + rent_personal

        impuestos_año = is_pagado + irpf_salario + ss_empresa + ss_trabajador + solidaridad
        total_impuestos += impuestos_año
        total_is += is_pagado
        total_irpf += irpf_salario
        total_ss += ss_empresa + ss_trabajador + solidaridad

        historial.append(
            ScenarioYear(
                año=año,
                aportacion=beneficio_neto,
                rentabilidad=rent_sl,
                capital_acumulado=capital_sl + capital_personal,
                impuestos_pagados_año=impuestos_año,
            )
        )

    capital_total = capital_sl + capital_personal

    impuestos_rescate_sl = calcular_irpf_ahorro(capital_sl)
    plusvalias_personal = capital_personal - req.capital_inicial
    impuestos_rescate_personal = calcular_irpf_ahorro(plusvalias_personal)

    impuestos_rescate_total = impuestos_rescate_sl + impuestos_rescate_personal
    capital_neto = capital_total - impuestos_rescate_total

    renta_anual_bruta = capital_total * 0.04
    impuesto_renta_anual = calcular_irpf_ahorro(renta_anual_bruta)
    renta_anual_neta = renta_anual_bruta - impuesto_renta_anual

    return ScenarioResult(
        capital_bruto=capital_total,
        plusvalias=(capital_sl - total_aportado_sl) + plusvalias_personal,
        impuestos_rescate=impuestos_rescate_total,
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
