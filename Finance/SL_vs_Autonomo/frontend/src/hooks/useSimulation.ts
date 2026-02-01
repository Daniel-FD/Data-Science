import { useState, useCallback } from "react";
import { simulate, SimulationRequest, SimulationResponse } from "../api/simulator";

export const useSimulation = () => {
  const [data, setData] = useState<SimulationResponse | undefined>(undefined);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const mutate = useCallback(async (payload: SimulationRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await simulate(payload);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { data, error, isLoading, mutate };
};
