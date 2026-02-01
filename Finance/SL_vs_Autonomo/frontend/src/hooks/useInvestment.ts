import { useState, useEffect, useRef, useCallback } from "react";
import { fetchInvestment } from "../api/client";

export interface InvestmentInputs {
  aportacion: number;
  rentabilidad: number;
  anos: number;
  capitalInicial: number;
  objetivo: number;
}

export interface InvestmentResult {
  capital_bruto: number;
  plusvalias: number;
  impuestos_rescate: number;
  capital_neto: number;
  renta_anual_bruta: number;
  renta_anual_neta: number;
  renta_mensual_neta: number;
  historial: Array<{
    año: number;
    aportacion: number;
    rentabilidad: number;
    capital_acumulado: number;
    impuestos_pagados_año: number;
  }>;
  [key: string]: any;
}

export function useInvestment() {
  const [aportacion, setAportacion] = useState(1000);
  const [rentabilidad, setRentabilidad] = useState(0.07);
  const [anos, setAnos] = useState(20);
  const [capitalInicial, setCapitalInicial] = useState(0);
  const [objetivo, setObjetivo] = useState(2000);
  const [result, setResult] = useState<InvestmentResult | null>(null);
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
        const data = await fetchInvestment(
          {
            aportacion_mensual: aportacion,
            rentabilidad_anual: rentabilidad,
            anos,
            capital_inicial: capitalInicial,
            objetivo_renta_mensual: objetivo,
          },
          controller.signal
        );
        if (!controller.signal.aborted) {
          setResult(data);
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError(err.message ?? "Error calculating investment");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);
  }, [aportacion, rentabilidad, anos, capitalInicial, objetivo]);

  useEffect(() => {
    calculate();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [calculate]);

  return {
    aportacion,
    setAportacion,
    rentabilidad,
    setRentabilidad,
    anos,
    setAnos,
    capitalInicial,
    setCapitalInicial,
    objetivo,
    setObjetivo,
    result,
    loading,
    error,
  };
}
