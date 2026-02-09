export type ScenarioYear = {
  año: number;
  aportacion: number;
  rentabilidad: number;
  capital_acumulado: number;
  impuestos_pagados_año: number;
};

export type ScenarioResult = {
  capital_bruto: number;
  plusvalias: number;
  impuestos_rescate: number;
  capital_neto: number;
  renta_anual_bruta: number;
  renta_anual_neta: number;
  renta_mensual_neta: number;
  historial: ScenarioYear[];
  tax_breakdown: Record<string, number>;
};

export type OptimalSalaryPoint = {
  salario: number;
  renta_mensual_neta: number;
  impuestos_totales: number;
};

export type SimulationResponse = {
  autonomo: ScenarioResult;
  sl_retencion: ScenarioResult;
  sl_dividendos: ScenarioResult;
  sl_mixto: ScenarioResult;
  optimal_salary: number;
  optimal_salary_curve: OptimalSalaryPoint[];
  crossover: Array<{ facturacion: number; autonomo: number; sl_retencion: number; sl_dividendos: number; sl_mixto: number }>;
};

export type SimulationRequest = {
  facturacion: number;
  gastos_deducibles: number;
  gastos_personales: number;
  años: number;
  rentabilidad: number;
  capital_inicial: number;
  region: string;
  tarifa_plana: boolean;
  salario_administrador: number;
  gastos_gestoria: number;
  aportacion_plan_pensiones: number;
  turnover: number;
  company_age: number;
  is_startup: boolean;
};

const API_BASE = import.meta.env.VITE_API_BASE || "";

export const fetchRegions = async (): Promise<string[]> => {
  const res = await fetch(`${API_BASE}/api/regions`);
  return res.json();
};

export const fetchPresets = async (): Promise<Array<Record<string, number | string>>> => {
  const res = await fetch(`${API_BASE}/api/presets`);
  return res.json();
};

export const simulate = async (payload: SimulationRequest): Promise<SimulationResponse> => {
  const res = await fetch(`${API_BASE}/api/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
};
