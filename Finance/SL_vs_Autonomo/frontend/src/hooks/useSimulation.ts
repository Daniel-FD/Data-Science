import { useMutation } from "@tanstack/react-query";
import { simulate, SimulationRequest, SimulationResponse } from "../api/simulator";

export const useSimulation = () => {
  return useMutation<SimulationResponse, Error, SimulationRequest>({
    mutationFn: (payload) => simulate(payload),
  });
};
