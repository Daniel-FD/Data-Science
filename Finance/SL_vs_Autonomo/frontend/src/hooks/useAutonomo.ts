import { useState, useEffect, useRef, useCallback } from "react";
import { fetchAutonomo } from "../api/client";

export interface AutonomoInputs {
  facturacion: number;
  region: string;
  gastosPct: number;
  tarifaPlana: boolean;
}

export interface AutonomoResult {
  facturacion_anual: number;
  gastos_deducibles: number;
  rendimiento_neto: number;
  cuota_autonomos: number;
  base_imponible_irpf: number;
  irpf_total: number;
  tipo_efectivo_irpf: number;
  tipo_marginal: number;
  neto_anual: number;
  neto_mensual: number;
  desglose_irpf: Record<string, number>;
  [key: string]: any;
}

export function useAutonomo() {
  const [facturacion, setFacturacion] = useState(30000);
  const [region, setRegion] = useState("Galicia");
  const [gastosPct, setGastosPct] = useState(0.1);
  const [tarifaPlana, setTarifaPlana] = useState(false);
  const [result, setResult] = useState<AutonomoResult | null>(null);
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
        const data = await fetchAutonomo(
          {
            facturacion_anual: facturacion,
            region,
            gastos_deducibles_pct: gastosPct,
            tarifa_plana: tarifaPlana,
          },
          controller.signal
        );
        if (!controller.signal.aborted) {
          setResult(data);
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message ?? "Error calculating autonomo taxes");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);
  }, [facturacion, region, gastosPct, tarifaPlana]);

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
    region,
    setRegion,
    gastosPct,
    setGastosPct,
    tarifaPlana,
    setTarifaPlana,
    result,
    loading,
    error,
  };
}
