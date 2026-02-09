import { useState, useEffect, useRef, useCallback } from "react";
import { fetchSL, fetchOptimalSalary } from "../api/client";

export interface SLInputs {
  facturacion: number;
  salario: number;
  gastosEmpresa: number;
  gestoria: number;
  tipoEmpresa: string;
  region: string;
  pctDividendos: number;
}

export interface SLResult {
  facturacion_anual: number;
  salario_administrador: number;
  beneficio_antes_is: number;
  impuesto_sociedades: number;
  beneficio_despues_is: number;
  dividendos_brutos: number;
  retencion_dividendos: number;
  dividendos_netos: number;
  irpf_salario: number;
  neto_salario_mensual: number;
  neto_dividendos_mensual: number;
  neto_total_mensual: number;
  neto_total_anual: number;
  tipo_efectivo_total: number;
  [key: string]: any;
}

export interface OptimalSalaryData {
  optimal_salary: number;
  optimal_result: any;
  curve: Array<{
    salary: number;
    net_income: number;
    total_impuestos: number;
    irpf_salario: number;
    irpf_dividendos: number;
    is_pagado: number;
  }>;
}

export function useSL() {
  const [facturacion, setFacturacion] = useState(100000);
  const [salario, setSalario] = useState(18000);
  const [gastosEmpresa, setGastosEmpresa] = useState(2000);
  const [gestoria, setGestoria] = useState(3000);
  const [tipoEmpresa, setTipoEmpresa] = useState("micro");
  const [region, setRegion] = useState("Galicia");
  const [pctDividendos, setPctDividendos] = useState(1.0);
  const [result, setResult] = useState<SLResult | null>(null);
  const [optimalData, setOptimalData] = useState<OptimalSalaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const abortRef = useRef<AbortController>();

  const calculate = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(async () => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        const [slData, optData] = await Promise.all([
          fetchSL(
            {
              facturacion_anual: facturacion,
              salario_administrador: salario,
              gastos_empresa: gastosEmpresa,
              gastos_gestoria: gestoria,
              tipo_empresa: tipoEmpresa,
              region,
              pct_dividendos: pctDividendos,
            },
            controller.signal
          ),
          fetchOptimalSalary(
            {
              facturacion_anual: facturacion,
              gastos_empresa: gastosEmpresa,
              gastos_gestoria: gestoria,
              tipo_empresa: tipoEmpresa,
              region,
              pct_dividendos: pctDividendos,
            },
            controller.signal
          ),
        ]);

        if (!controller.signal.aborted) {
          setResult(slData);
          setOptimalData(optData);
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message ?? "Error calculating SL taxes");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);
  }, [facturacion, salario, gastosEmpresa, gestoria, tipoEmpresa, region, pctDividendos]);

  useEffect(() => {
    calculate();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [calculate]);

  return {
    facturacion,
    setFacturacion,
    salario,
    setSalario,
    gastosEmpresa,
    setGastosEmpresa,
    gestoria,
    setGestoria,
    tipoEmpresa,
    setTipoEmpresa,
    region,
    setRegion,
    pctDividendos,
    setPctDividendos,
    result,
    optimalData,
    loading,
    error,
  };
}
