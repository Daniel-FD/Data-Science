const BASE_URL = import.meta.env.VITE_API_BASE || "/api";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

function post<T>(path: string, body: any, signal?: AbortSignal): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
    signal,
  });
}

function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  return request<T>(path, { signal });
}

// Individual calculators
export const fetchEmployee = (params: any, signal?: AbortSignal) =>
  post<any>("/employee", params, signal);

export const fetchAutonomo = (params: any, signal?: AbortSignal) =>
  post<any>("/autonomo", params, signal);

export const fetchSL = (params: any, signal?: AbortSignal) =>
  post<any>("/sl", params, signal);

export const fetchOptimalSalary = (params: any, signal?: AbortSignal) =>
  post<any>("/sl/optimal-salary", params, signal);

// Comparison
export const fetchCompare = (params: any, signal?: AbortSignal) =>
  post<any>("/compare", params, signal);

export const fetchCrossover = (params: any, signal?: AbortSignal) =>
  post<any>("/compare/crossover", params, signal);

// Investment
export const fetchInvestment = (params: any, signal?: AbortSignal) =>
  post<any>("/investment", params, signal);

export const fetchInvestmentCompare = (params: any, signal?: AbortSignal) =>
  post<any>("/investment/compare", params, signal);

export const fetchSensitivity = (params: any, signal?: AbortSignal) =>
  post<any>("/investment/sensitivity", params, signal);

// Fallback regions list (matches backend REGIONES_DISPONIBLES)
const FALLBACK_REGIONS = [
  "Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria",
  "Castilla y León", "Castilla-La Mancha", "Cataluña", "Ceuta",
  "Comunidad Valenciana", "Extremadura", "Galicia", "La Rioja",
  "Madrid", "Melilla", "Murcia", "Navarra", "País Vasco",
];

// Utility
export const fetchRegions = async (signal?: AbortSignal): Promise<{ regions: string[] }> => {
  try {
    return await get<{ regions: string[] }>("/regions", signal);
  } catch {
    return { regions: FALLBACK_REGIONS };
  }
};

export const fetchPresets = (signal?: AbortSignal) =>
  get<{ presets: Array<{ label: string; income: number; icon: string }> }>(
    "/presets",
    signal
  );

export const fetchInvestmentOptimizer = (params: any, signal?: AbortSignal) =>
  post<any>("/investment/optimizer", params, signal);

export async function fetchAutonomoReverse(params: {
  salario_neto_objetivo: number;
  region: string;
  gastos_deducibles_pct?: number;
  tarifa_plana?: boolean;
}): Promise<{ salario_neto_objetivo: number; facturacion_necesaria: number }> {
  const qs = new URLSearchParams();
  qs.set("salario_neto_objetivo", String(params.salario_neto_objetivo));
  qs.set("region", params.region);
  if (params.gastos_deducibles_pct !== undefined)
    qs.set("gastos_deducibles_pct", String(params.gastos_deducibles_pct));
  if (params.tarifa_plana) qs.set("tarifa_plana", "true");
  const res = await fetch(`${BASE_URL}/autonomo/reverse?${qs}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
