import { useState, useEffect, useRef, useCallback } from "react";
import { fetchEmployee } from "../api/client";

export interface EmployeeInputs {
  salario: number;
  region: string;
  numPagas: number;
}

export interface EmployeeResult {
  salario_bruto_anual: number;
  salario_neto_anual: number;
  salario_neto_mensual: number;
  irpf_total: number;
  tipo_efectivo_irpf: number;
  tipo_marginal: number;
  seguridad_social_trabajador: number;
  seguridad_social_empresa: number;
  coste_empresa: number;
  desglose_irpf: Record<string, number>;
  [key: string]: any;
}

export function useEmployee() {
  const [salario, setSalario] = useState(30000);
  const [region, setRegion] = useState("Galicia");
  const [numPagas, setNumPagas] = useState(14);
  const [result, setResult] = useState<EmployeeResult | null>(null);
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
        const data = await fetchEmployee(
          {
            salario_bruto_anual: salario,
            region,
            num_pagas: numPagas,
          },
          controller.signal
        );
        if (!controller.signal.aborted) {
          setResult(data);
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message ?? "Error calculating employee taxes");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);
  }, [salario, region, numPagas]);

  useEffect(() => {
    calculate();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [calculate]);

  return {
    salario,
    setSalario,
    region,
    setRegion,
    numPagas,
    setNumPagas,
    result,
    loading,
    error,
  };
}
