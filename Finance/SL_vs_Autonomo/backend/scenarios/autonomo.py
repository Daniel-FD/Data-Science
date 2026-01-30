from __future__ import annotations

from .models import ScenarioResult, ScenarioYear, SimulationRequest
from ..tax_engine.autonomos import calcular_cuota_autonomos
from ..tax_engine.irpf import calcular_irpf_ahorro, calcular_irpf_general


def simulate_autonomo(req: SimulationRequest) -> ScenarioResult:
    historial = []
    capital = req.capital_inicial
    total_aportado = req.capital_inicial
    total_impuestos = 0.0
    total_irpf = 0.0
    total_cuota = 0.0

    for año in range(1, req.años + 1):
        rendimiento_neto = req.facturacion - req.gastos_deducibles
        cuota_autonomos = calcular_cuota_autonomos(rendimiento_neto, año, req.tarifa_plana)
        base_irpf = rendimiento_neto - cuota_autonomos - req.aportacion_plan_pensiones
        irpf = calcular_irpf_general(base_irpf, req.region)

        neto_disponible = rendimiento_neto - cuota_autonomos - irpf - req.aportacion_plan_pensiones
        aportacion = max(0.0, neto_disponible - req.gastos_personales)

        rent = capital * req.rentabilidad
        capital = capital + aportacion + rent
        total_aportado += aportacion
        total_impuestos += irpf + cuota_autonomos
        total_irpf += irpf
        total_cuota += cuota_autonomos

        historial.append(
            ScenarioYear(
                año=año,
                aportacion=aportacion,
                rentabilidad=rent,
                capital_acumulado=capital,
                impuestos_pagados_año=irpf + cuota_autonomos,
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
        tax_breakdown={"irpf": total_irpf, "cuota_autonomos": total_cuota},
    )
