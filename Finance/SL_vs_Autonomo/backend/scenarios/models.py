from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    facturacion: float = Field(105_000, ge=0)
    gastos_deducibles: float = Field(2_000, ge=0)
    gastos_personales: float = Field(12_000, ge=0)
    años: int = Field(10, ge=1, le=50)
    rentabilidad: float = Field(0.06, ge=0, le=1)
    capital_inicial: float = Field(0, ge=0)
    region: str = Field("Galicia")
    tarifa_plana: bool = Field(True)
    salario_administrador: float = Field(18_000, ge=0)
    gastos_gestoria: float = Field(3_000, ge=0)
    aportacion_plan_pensiones: float = Field(5_750, ge=0)
    turnover: float = Field(105_000, ge=0)
    company_age: int = Field(1, ge=0)
    is_startup: bool = Field(True)


class ScenarioYear(BaseModel):
    año: int
    aportacion: float
    rentabilidad: float
    capital_acumulado: float
    impuestos_pagados_año: float


class ScenarioResult(BaseModel):
    capital_bruto: float
    plusvalias: float
    impuestos_rescate: float
    capital_neto: float
    renta_anual_bruta: float
    renta_anual_neta: float
    renta_mensual_neta: float
    historial: List[ScenarioYear]
    tax_breakdown: Dict[str, float]


class OptimalSalaryPoint(BaseModel):
    salario: float
    renta_mensual_neta: float
    impuestos_totales: float


class SimulationResponse(BaseModel):
    autonomo: ScenarioResult
    sl_retencion: ScenarioResult
    sl_dividendos: ScenarioResult
    sl_mixto: ScenarioResult
    optimal_salary: float
    optimal_salary_curve: List[OptimalSalaryPoint]
    crossover: List[Dict[str, float]]
