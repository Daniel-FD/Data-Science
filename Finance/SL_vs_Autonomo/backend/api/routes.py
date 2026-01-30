from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter

from ..scenarios.models import SimulationRequest, SimulationResponse
from ..scenarios.autonomo import simulate_autonomo
from ..scenarios.sl_retencion import simulate_sl_retencion
from ..scenarios.sl_dividendos import simulate_sl_dividendos
from ..scenarios.sl_mixto import optimize_salary
from ..tax_engine.regional import list_regions

router = APIRouter()


@router.get("/regions")
def regions() -> List[str]:
    return list_regions()


@router.get("/presets")
def presets() -> List[Dict[str, Any]]:
    return [
        {"label": "Programador 80K", "facturacion": 80_000, "gastos_deducibles": 2_000, "gastos_personales": 18_000},
        {"label": "Consultor 120K", "facturacion": 120_000, "gastos_deducibles": 4_000, "gastos_personales": 24_000},
        {"label": "Diseñador 45K", "facturacion": 45_000, "gastos_deducibles": 1_500, "gastos_personales": 15_000},
    ]


@router.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest) -> SimulationResponse:
    req.turnover = req.turnover or req.facturacion

    autonomo = simulate_autonomo(req)
    sl_retencion = simulate_sl_retencion(req)
    sl_dividendos = simulate_sl_dividendos(req)
    sl_mixto, best_salary, curve = optimize_salary(req)

    crossover = []
    for facturacion in range(30_000, 300_001, 10_000):
        temp = req.model_copy()
        temp.facturacion = facturacion
        temp.turnover = facturacion
        a = simulate_autonomo(temp).renta_mensual_neta
        b = simulate_sl_retencion(temp).renta_mensual_neta
        c = simulate_sl_dividendos(temp).renta_mensual_neta
        d = optimize_salary(temp)[0].renta_mensual_neta
        crossover.append(
            {
                "facturacion": float(facturacion),
                "autonomo": a,
                "sl_retencion": b,
                "sl_dividendos": c,
                "sl_mixto": d,
            }
        )

    return SimulationResponse(
        autonomo=autonomo,
        sl_retencion=sl_retencion,
        sl_dividendos=sl_dividendos,
        sl_mixto=sl_mixto,
        optimal_salary=best_salary,
        optimal_salary_curve=curve,
        crossover=crossover,
    )
