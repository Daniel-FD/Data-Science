import { useState, useEffect, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PageMeta from "../components/PageMeta";
import InputCard from "../components/InputCard";
import Tooltip from "../components/Tooltip";
import LearnMore from "../components/LearnMore";
import SalaryOptimizationChart from "../components/charts/SalaryOptimizationChart";
import CapitalEvolution from "../components/charts/CapitalEvolution";
import { fetchRegions, fetchInvestmentOptimizer } from "../api/client";

const fmtCur = (v: number) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(v);

const fmtPct = (v: number) => `${(v * 100).toFixed(1)}%`;

interface SliderInputProps {
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (v: number) => void;
  suffix?: string;
  format?: (v: number) => string;
}

function SliderInput({ min, max, step, value, onChange, suffix = "\u20ac", format }: SliderInputProps) {
  return (
    <div className="flex items-center gap-4">
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value))} className="flex-1"
      />
      <div className="flex items-center gap-1">
        {format ? (
          <span className="w-24 text-right text-sm font-medium">{format(value)}</span>
        ) : (
          <>
            <input type="number" value={value} onChange={(e) => onChange(Number(e.target.value))}
              className="w-24 rounded border px-2 py-1 text-right" />
            <span className="text-sm text-gray-500">{suffix}</span>
          </>
        )}
      </div>
    </div>
  );
}

export default function InvestmentSimulator() {
  const { t } = useTranslation();

  const [facturacion, setFacturacion] = useState(100000);
  const [gastos, setGastos] = useState(2000);
  const [region, setRegion] = useState("Galicia");
  const [rentabilidad, setRentabilidad] = useState(0.07);
  const [anos, setAnos] = useState(20);
  const [capitalInicial, setCapitalInicial] = useState(0);
  const [gastosDeduciblesPct, setGastosDeduciblesPct] = useState(10);
  const [gastosEmpresa, setGastosEmpresa] = useState(2000);
  const [gastosGestoria, setGastosGestoria] = useState(3000);
  const [tarifaPlana, setTarifaPlana] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [regions, setRegions] = useState<{ id: string; name: string }[]>([]);

  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const abortRef = useRef<AbortController>();

  useEffect(() => {
    fetchRegions().then((res) => setRegions(res.regions.map((r) => ({ id: r, name: r }))));
  }, []);

  const calculate = useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(async () => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setLoading(true);
      try {
        const data = await fetchInvestmentOptimizer(
          {
            facturacion_anual: facturacion,
            gastos_personales_mensuales: gastos,
            region,
            rentabilidad_anual: rentabilidad,
            anos,
            capital_inicial: capitalInicial,
            gastos_deducibles_pct: gastosDeduciblesPct / 100,
            gastos_empresa: gastosEmpresa,
            gastos_gestoria: gastosGestoria,
            tarifa_plana: tarifaPlana,
          },
          controller.signal
        );
        if (!controller.signal.aborted) setResult(data);
      } catch (err: any) {
        if (err.name !== "AbortError") console.error("Investment optimizer error:", err);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, 500);
  }, [facturacion, gastos, region, rentabilidad, anos, capitalInicial, gastosDeduciblesPct, gastosEmpresa, gastosGestoria, tarifaPlana]);

  useEffect(() => {
    calculate();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [calculate]);

  // Key scenarios
  const autoData = result?.autonomo;
  const keyScenarios = result?.sl_key_scenarios;
  const slOptimo = keyScenarios?.optimo;
  const slTodoSalario = keyScenarios?.todo_salario;
  const slTodoDividendos = keyScenarios?.todo_dividendos;
  const autoDetail = autoData?.detalle_fiscal;
  const slDetail = slOptimo?.detalle_fiscal;

  // Capital evolution data for chart
  const capitalEvolutionData = result && slOptimo
    ? Array.from({ length: anos }, (_, i) => {
        const point: any = { ano: i + 1 };
        const autoH = autoData?.historial?.[i];
        if (autoH) point.autonomo = autoH.capital_acumulado ?? 0;
        if (slOptimo) {
          const personalCap = slOptimo.historial_personal?.[i]?.capital_acumulado ?? 0;
          const empresaCap = slOptimo.historial_empresa?.[i]?.capital_acumulado ?? 0;
          point.sl = personalCap + empresaCap;
        }
        return point;
      })
    : [];

  // Helper: find winning scenario
  const allScenarios = autoData && slOptimo ? [
    { key: "autonomo", label: "Autónomo", neto: autoData.capital_final_neto },
    { key: "sl_todo_salario", label: "SL todo salario", neto: slTodoSalario?.total_neto ?? 0 },
    { key: "sl_optimo", label: `SL óptimo (${fmtCur(slOptimo?.salario_bruto ?? 0)})`, neto: slOptimo?.total_neto ?? 0 },
    { key: "sl_todo_dividendos", label: "SL todo dividendos", neto: slTodoDividendos?.total_neto ?? 0 },
  ] : [];
  const bestScenario = allScenarios.length > 0 ? allScenarios.reduce((a, b) => a.neto > b.neto ? a : b) : null;
  const worstScenario = allScenarios.length > 0 ? allScenarios.reduce((a, b) => a.neto < b.neto ? a : b) : null;

  return (
    <>
      <PageMeta titleKey="meta.investment_sim.title" descriptionKey="meta.investment_sim.desc" />
      <article className="mx-auto max-w-4xl px-4 py-12">
        {/* Header */}
        <header className="mb-12">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Simulador de Inversión a Largo Plazo
          </h1>
          <p className="mt-6 leading-relaxed text-gray-600">
            Simula cuánto capital puedes acumular invirtiendo tu excedente mensual.
            Compara la estrategia de <strong>autónomo</strong> (todo inversión personal) frente a
            una <strong>SL</strong> donde puedes invertir parte desde la empresa (tributando al tipo
            de Sociedades, más bajo que IRPF).
          </p>
        </header>

        {/* Calculator inputs */}
        <InputCard title="Parámetros de simulación">
          <div className="space-y-6">
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Facturación anual
                <Tooltip text="Ingresos brutos anuales que facturas a tus clientes (sin IVA)." />
              </label>
              <SliderInput min={20000} max={500000} step={5000} value={facturacion} onChange={setFacturacion} />
            </div>

            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Gastos deducibles autónomo
                <Tooltip text="Porcentaje de la facturación que corresponde a gastos del autónomo (oficina, material, etc.). Para la SL, los gastos empresa se configuran aparte." />
              </label>
              <SliderInput min={0} max={50} step={1} value={gastosDeduciblesPct} onChange={setGastosDeduciblesPct} suffix="%" />
              <p className="mt-1 text-xs text-gray-400">{fmtCur(facturacion * gastosDeduciblesPct / 100)}/año</p>
            </div>

            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Gastos de la empresa (SL)
                <Tooltip text="Gastos operativos anuales de la SL: alquiler, suministros, material, seguros, etc. NO incluye salario del administrador ni gestoría. Solo aplica al escenario de SL." />
              </label>
              <SliderInput min={0} max={100000} step={500} value={gastosEmpresa} onChange={setGastosEmpresa} suffix="€/año" />
            </div>

            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Gastos personales mensuales
                <Tooltip text="Lo que necesitas para vivir cada mes (alquiler, comida, ocio, seguros). El resto de tu neto se invierte." />
              </label>
              <SliderInput min={500} max={10000} step={100} value={gastos} onChange={setGastos} suffix="€/mes" />
            </div>

            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Comunidad autónoma
                <Tooltip text="Afecta al IRPF del salario del administrador y al IRPF del autónomo." />
              </label>
              <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full rounded border px-3 py-2">
                {regions.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Tarifa plana autónomo
                <Tooltip text="Los primeros 12 meses como autónomo la cuota es de 87€/mes (ampliable a 24 si los ingresos no superan el SMI). Solo afecta al escenario de autónomo." />
              </label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setTarifaPlana(false)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                    !tarifaPlana ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  No
                </button>
                <button
                  onClick={() => setTarifaPlana(true)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                    tarifaPlana ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  Sí (87 €/mes)
                </button>
              </div>
            </div>

            <button
              className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? "\u2212" : "+"} Opciones avanzadas
            </button>

            {showAdvanced && (
              <div className="space-y-6 border-t pt-4">
                <div>
                  <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                    Rentabilidad anual esperada
                    <Tooltip text="Rendimiento anual medio de tu cartera de inversión. El S&P 500 ha dado históricamente ~7% anualizado (~5% ajustado por inflación)." />
                  </label>
                  <SliderInput min={0.01} max={0.15} step={0.005} value={rentabilidad} onChange={setRentabilidad} format={fmtPct} />
                </div>
                <div>
                  <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                    Horizonte temporal
                    <Tooltip text="Años hasta que quieres empezar a vivir de tus inversiones (FIRE)." />
                  </label>
                  <SliderInput min={5} max={40} step={1} value={anos} onChange={setAnos} suffix="años" />
                </div>
                <div>
                  <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                    Capital inicial
                    <Tooltip text="Ahorros actuales que ya tienes invertidos." />
                  </label>
                  <SliderInput min={0} max={500000} step={5000} value={capitalInicial} onChange={setCapitalInicial} />
                </div>
                <div>
                  <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                    Gestoría SL
                    <Tooltip text="Coste anual de gestoría de la SL (200-300 €/mes). Es un gasto deducible." />
                  </label>
                  <SliderInput min={0} max={6000} step={50} value={gastosGestoria} onChange={setGastosGestoria} suffix="€/año" />
                </div>
              </div>
            )}
          </div>
        </InputCard>

        {loading && (
          <div className="mt-12 flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
          </div>
        )}

        {result && !loading && autoData && slOptimo && (
          <section className="mt-12 space-y-12">

            {/* ============================== */}
            {/* SECTION 1: Winner banner */}
            {/* ============================== */}
            {bestScenario && (
              <div className={`rounded-2xl p-6 ${
                bestScenario.key.startsWith("sl")
                  ? "bg-emerald-50 border-2 border-emerald-200"
                  : "bg-blue-50 border-2 border-blue-200"
              }`}>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">&#127942;</span>
                  <h2 className="text-xl font-bold">
                    Mejor opción: {bestScenario.label}
                  </h2>
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {fmtCur(bestScenario.neto)}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Capital neto total tras {anos} años <strong>(después de impuestos al rescate)</strong>
                </p>
                {worstScenario && bestScenario.neto > worstScenario.neto && (
                  <p className="text-sm text-gray-500 mt-1">
                    Ventaja: {fmtCur(bestScenario.neto - worstScenario.neto)} más que {worstScenario.label}
                  </p>
                )}
              </div>
            )}

            {/* ============================== */}
            {/* SECTION 2: WARNING BOX */}
            {/* ============================== */}
            <div className="rounded-xl border-2 border-amber-300 bg-amber-50 p-5">
              <h3 className="font-bold text-amber-800 flex items-center gap-2 mb-2">
                <span className="text-lg">&#9888;&#65039;</span>
                Capital acumulado ≠ dinero que recibes
              </h3>
              <p className="text-sm text-amber-900 leading-relaxed">
                Dos escenarios pueden acumular el mismo <strong>capital bruto</strong>, pero el dinero que te llevas a casa es muy diferente
                porque <strong>los impuestos al rescatar no son iguales</strong>:
              </p>
              <ul className="mt-2 text-sm text-amber-900 space-y-2 list-disc pl-5">
                <li>
                  <strong>Inversión personal</strong> (autónomo o desde salario SL): tributas por IRPF del ahorro (19-30%) solo sobre las <em>plusvalías</em> (lo ganado).
                  Si invertiste 200K y ahora valen 500K, pagas impuestos sobre 300K de ganancias, no sobre los 500K.
                </li>
                <li>
                  <strong>Inversión desde la empresa</strong> (SL): al distribuir como <em>dividendos</em>, tributas por IRPF del ahorro (19-30%) sobre <em>todo el capital</em>.
                  Todo es beneficio retenido de la SL, por tanto todo es dividendo. Si la empresa tiene 400K invertidos, pagas impuestos sobre los 400K completos.
                  Además, los rendimientos anuales de la empresa ya tributaron al IS (~21%) antes de reinvertirse.
                </li>
              </ul>
              <p className="mt-2 text-xs text-amber-800 bg-amber-100 rounded px-3 py-2 border border-amber-200">
                <strong>Mismo impuesto, diferente base:</strong> Ambos pagan IRPF del ahorro a los mismos tramos (19-30%).
                La diferencia clave es <em>sobre qué cantidad</em> se aplica: plusvalías (personal) vs. capital total (empresa/dividendos).
              </p>
              <p className="mt-2 text-sm text-amber-900 font-medium">
                Por eso, en esta simulación siempre mostramos el <strong>capital neto después de impuestos</strong> como cifra principal.
              </p>
            </div>

            {/* ============================== */}
            {/* SECTION 3: Main comparison table */}
            {/* ============================== */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                Comparativa completa tras {anos} años
                <Tooltip text="Compara los 4 escenarios: autónomo, SL con todo el ingreso como salario, SL con salario óptimo, y SL con salario mínimo (todo dividendos). Todos los datos son después de impuestos." />
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Cada columna muestra cuánto inviertes, cuánto acumulas, cuántos impuestos pagas al rescatar, y cuánto te queda realmente.
              </p>

              <div className="overflow-x-auto -mx-4 px-4">
                <table className="w-full min-w-[700px] text-sm">
                  <thead>
                    <tr className="border-b-2">
                      <th className="py-3 pr-3 text-left font-medium text-gray-500 w-40">Concepto</th>
                      <th className="py-3 px-2 text-right font-bold text-green-700">
                        <div>Autónomo</div>
                      </th>
                      <th className="py-3 px-2 text-right font-bold text-purple-600">
                        <div>SL todo salario</div>
                        <div className="text-xs font-normal text-gray-400">{fmtCur(slTodoSalario?.salario_bruto ?? 0)}</div>
                      </th>
                      <th className={`py-3 px-2 text-right font-bold ${bestScenario?.key === "sl_optimo" ? "text-emerald-700" : "text-purple-700"}`}>
                        <div>SL óptimo</div>
                        <div className="text-xs font-normal text-gray-400">{fmtCur(slOptimo?.salario_bruto ?? 0)}</div>
                      </th>
                      <th className="py-3 px-2 text-right font-bold text-purple-500">
                        <div>SL dividendos</div>
                        <div className="text-xs font-normal text-gray-400">{fmtCur(slTodoDividendos?.salario_bruto ?? 0)}</div>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700">
                    {/* Inversión mensual */}
                    <tr className="border-b">
                      <td className="py-2.5 pr-3 font-medium flex items-center">
                        Inversión mensual
                        <Tooltip text="Dinero que inviertes cada mes (personal + empresa en caso de SL)." />
                      </td>
                      <td className="py-2.5 px-2 text-right">{fmtCur(autoData.inversion_mensual)}/mes</td>
                      <td className="py-2.5 px-2 text-right">
                        {fmtCur((slTodoSalario?.inversion_personal_mensual ?? 0) + (slTodoSalario?.inversion_empresa_mensual ?? 0))}/mes
                      </td>
                      <td className="py-2.5 px-2 text-right">
                        {fmtCur((slOptimo?.inversion_personal_mensual ?? 0) + (slOptimo?.inversion_empresa_mensual ?? 0))}/mes
                      </td>
                      <td className="py-2.5 px-2 text-right">
                        {fmtCur((slTodoDividendos?.inversion_personal_mensual ?? 0) + (slTodoDividendos?.inversion_empresa_mensual ?? 0))}/mes
                      </td>
                    </tr>
                    {/* Desglose inv SL */}
                    <tr className="border-b bg-gray-50">
                      <td className="py-1.5 pr-3 text-xs text-gray-400 pl-4">↳ personal / empresa</td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">{fmtCur(autoData.inversion_mensual)} / -</td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">
                        {fmtCur(slTodoSalario?.inversion_personal_mensual ?? 0)} / {fmtCur(slTodoSalario?.inversion_empresa_mensual ?? 0)}
                      </td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">
                        {fmtCur(slOptimo?.inversion_personal_mensual ?? 0)} / {fmtCur(slOptimo?.inversion_empresa_mensual ?? 0)}
                      </td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">
                        {fmtCur(slTodoDividendos?.inversion_personal_mensual ?? 0)} / {fmtCur(slTodoDividendos?.inversion_empresa_mensual ?? 0)}
                      </td>
                    </tr>
                    {/* Capital bruto */}
                    <tr className="border-b">
                      <td className="py-2.5 pr-3 font-medium flex items-center">
                        Capital bruto
                        <Tooltip text="Capital acumulado antes de impuestos al rescate. Incluye aportaciones + plusvalías." />
                      </td>
                      <td className="py-2.5 px-2 text-right">{fmtCur(autoData.capital_final_bruto)}</td>
                      <td className="py-2.5 px-2 text-right">{fmtCur(slTodoSalario?.capital_total_bruto ?? 0)}</td>
                      <td className="py-2.5 px-2 text-right">{fmtCur(slOptimo?.capital_total_bruto ?? 0)}</td>
                      <td className="py-2.5 px-2 text-right">{fmtCur(slTodoDividendos?.capital_total_bruto ?? 0)}</td>
                    </tr>
                    {/* Impuestos rescate */}
                    <tr className="border-b bg-red-50">
                      <td className="py-2.5 pr-3 font-medium text-red-700 flex items-center">
                        Impuestos al rescate
                        <Tooltip text="IRPF del ahorro (19-30%) que pagas al liquidar. El tipo de gravamen es el mismo, pero la BASE IMPONIBLE es diferente: en inversión personal solo tributan las plusvalías; en inversión de empresa tributa TODO el capital como dividendos." />
                      </td>
                      <td className="py-2.5 px-2 text-right text-red-600 font-medium">-{fmtCur(autoData.impuestos_rescate)}</td>
                      <td className="py-2.5 px-2 text-right text-red-600 font-medium">-{fmtCur(slTodoSalario?.impuestos_total ?? 0)}</td>
                      <td className="py-2.5 px-2 text-right text-red-600 font-medium">-{fmtCur(slOptimo?.impuestos_total ?? 0)}</td>
                      <td className="py-2.5 px-2 text-right text-red-600 font-medium">-{fmtCur(slTodoDividendos?.impuestos_total ?? 0)}</td>
                    </tr>
                    {/* Desglose impuestos: personal vs empresa */}
                    <tr className="border-b bg-red-50/50">
                      <td className="py-1.5 pr-3 text-xs text-red-400 pl-4">
                        ↳ personal (plusvalías)
                        <Tooltip text="IRPF del ahorro sobre las PLUSVALÍAS de tu inversión personal. Solo pagas por lo ganado, no por lo aportado. Tramos: 19% (0-6K), 21% (6K-50K), 23% (50K-200K), 27% (200K-300K), 30% (+300K)." />
                      </td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(autoData.impuestos_rescate)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(slTodoSalario?.impuestos_personal ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(slOptimo?.impuestos_personal ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(slTodoDividendos?.impuestos_personal ?? 0)}</td>
                    </tr>
                    <tr className="border-b bg-red-50/50">
                      <td className="py-1.5 pr-3 text-xs text-red-400 pl-4">
                        ↳ empresa (dividendos)
                        <Tooltip text="IRPF del ahorro sobre el TOTAL del capital de la empresa distribuido como dividendos. A diferencia de la inversión personal, aquí tributa TODO (no solo las ganancias), porque es beneficio retenido que nunca tributó como renta personal." />
                      </td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-</td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(slTodoSalario?.impuestos_empresa ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(slOptimo?.impuestos_empresa ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-red-400">-{fmtCur(slTodoDividendos?.impuestos_empresa ?? 0)}</td>
                    </tr>
                    {/* CAPITAL NETO — MAIN ROW */}
                    <tr className="border-b-2 border-gray-900">
                      <td className="py-3 pr-3 font-bold text-gray-900 text-base">
                        Capital neto
                      </td>
                      {[
                        autoData.capital_final_neto,
                        slTodoSalario?.total_neto ?? 0,
                        slOptimo?.total_neto ?? 0,
                        slTodoDividendos?.total_neto ?? 0,
                      ].map((neto, i) => {
                        const isBest = bestScenario && neto === bestScenario.neto;
                        return (
                          <td key={i} className={`py-3 px-2 text-right font-bold text-base ${isBest ? "text-emerald-700" : "text-gray-900"}`}>
                            {isBest && <span className="text-xs">&#127942; </span>}
                            {fmtCur(neto)}
                          </td>
                        );
                      })}
                    </tr>
                    {/* FIRE monthly */}
                    <tr className="border-b">
                      <td className="py-2.5 pr-3 font-medium flex items-center">
                        FIRE: renta neta/mes
                        <Tooltip text="Si aplicas la regla del 4% (retiras un 4% anual de tu capital sin agotarlo), esta es la renta mensual neta después de impuestos." />
                      </td>
                      <td className="py-2.5 px-2 text-right font-medium">{fmtCur(autoData.rescate_fire?.renta_neta_mensual ?? 0)}/mes</td>
                      <td className="py-2.5 px-2 text-right font-medium">{fmtCur(slTodoSalario?.rescate_fire?.renta_neta_mensual ?? 0)}/mes</td>
                      <td className="py-2.5 px-2 text-right font-medium">{fmtCur(slOptimo?.rescate_fire?.renta_neta_mensual ?? 0)}/mes</td>
                      <td className="py-2.5 px-2 text-right font-medium">{fmtCur(slTodoDividendos?.rescate_fire?.renta_neta_mensual ?? 0)}/mes</td>
                    </tr>
                    {/* Tipo efectivo al rescate FIRE */}
                    <tr className="border-b bg-gray-50">
                      <td className="py-1.5 pr-3 text-xs text-gray-400 pl-4">↳ tipo efectivo FIRE</td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">{fmtPct(autoData.rescate_fire?.tipo_efectivo ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">{fmtPct(slTodoSalario?.rescate_fire?.tipo_efectivo ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">{fmtPct(slOptimo?.rescate_fire?.tipo_efectivo ?? 0)}</td>
                      <td className="py-1.5 px-2 text-right text-xs text-gray-400">{fmtPct(slTodoDividendos?.rescate_fire?.tipo_efectivo ?? 0)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ============================== */}
            {/* SECTION 4: Fiscal waterfall */}
            {/* ============================== */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                Desglose fiscal: de la facturación a la inversión
                <Tooltip text="Muestra paso a paso cómo se reduce tu facturación hasta llegar al importe que puedes invertir cada mes." />
              </h2>
              <p className="text-sm text-gray-600 mb-6">
                Con {fmtCur(facturacion)} de facturación y {fmtCur(gastos)}/mes de gastos personales:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Autónomo waterfall */}
                {autoDetail && (
                  <div className="rounded-xl border-2 border-green-200 bg-white p-5">
                    <h3 className="text-sm font-bold text-green-700 uppercase tracking-wide mb-4 flex items-center">
                      Autónomo
                      <Tooltip text="Como autónomo, pagas IRPF sobre el rendimiento neto (facturación - gastos - cuotas) y cuotas de autónomo a la SS." />
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Facturación</span>
                        <span className="font-medium">{fmtCur(autoDetail.facturacion)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span>- Gastos deducibles ({gastosDeduciblesPct}%)</span>
                        <span>-{fmtCur(autoDetail.gastos_deducibles)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span className="flex items-center">- Cuota autónomos <Tooltip text="Cuota mensual de SS por tramos (230-590€/mes en 2025)" /></span>
                        <span>-{fmtCur(autoDetail.cuota_autonomos_anual)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-1 font-medium">
                        <span>= Rendimiento neto</span>
                        <span>{fmtCur(autoDetail.rendimiento_neto)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span className="flex items-center">- IRPF <Tooltip text="IRPF progresivo sobre el rendimiento neto." /></span>
                        <span>-{fmtCur(autoDetail.irpf_anual)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-1">
                        <span className="font-bold text-gray-900">= Neto anual</span>
                        <span className="font-bold text-green-700">{fmtCur(autoDetail.neto_anual)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Neto mensual</span>
                        <span className="font-bold text-green-700">{fmtCur(autoDetail.neto_mensual)}/mes</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span>- Gastos personales</span>
                        <span>-{fmtCur(gastos)}/mes</span>
                      </div>
                      <div className="flex justify-between border-t border-green-200 pt-2 bg-green-50 -mx-5 px-5 pb-1 rounded-b-lg">
                        <span className="font-bold text-green-800">Inversión mensual</span>
                        <span className="font-bold text-green-800 text-lg">{fmtCur(autoData.inversion_mensual)}/mes</span>
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-gray-500 text-center">
                      Tipo efectivo: {fmtPct(autoDetail.tipo_efectivo)}
                    </div>
                  </div>
                )}

                {/* SL waterfall (optimal) */}
                {slDetail && (
                  <div className="rounded-xl border-2 border-purple-200 bg-white p-5">
                    <h3 className="text-sm font-bold text-purple-700 uppercase tracking-wide mb-4 flex items-center">
                      SL óptimo (salario: {fmtCur(slDetail.salario_bruto)})
                      <Tooltip text="Con la SL, tu salario tributa por IRPF + SS. El beneficio restante queda en la empresa y tributa al IS." />
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Facturación</span>
                        <span className="font-medium">{fmtCur(slDetail.facturacion)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span>- Gastos empresa + gestoría</span>
                        <span>-{fmtCur(slDetail.gastos_empresa + slDetail.gastos_gestoria)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span>- Salario bruto admin</span>
                        <span>-{fmtCur(slDetail.salario_bruto)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span className="flex items-center">- SS empresa <Tooltip text="Cotización patronal (~30,6% del salario)." /></span>
                        <span>-{fmtCur(slDetail.ss_empresa_anual)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-1 font-medium">
                        <span>= Beneficio antes IS</span>
                        <span>{fmtCur(slDetail.beneficio_antes_is)}</span>
                      </div>
                      <div className="flex justify-between text-red-600">
                        <span className="flex items-center">- Imp. Sociedades <Tooltip text="IS sobre el beneficio. Micro: 21% primeros 50K + 22% resto." /></span>
                        <span>-{fmtCur(slDetail.is_pagado)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-1 font-medium">
                        <span>= Beneficio neto empresa</span>
                        <span>{fmtCur(slDetail.beneficio_despues_is)}</span>
                      </div>

                      {/* Personal side */}
                      <div className="border-t mt-3 pt-3">
                        <p className="text-xs font-bold text-blue-600 uppercase mb-2">Tu bolsillo (salario):</p>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Salario bruto</span>
                          <span>{fmtCur(slDetail.salario_bruto)}</span>
                        </div>
                        <div className="flex justify-between text-red-600">
                          <span className="flex items-center">- SS empleado <Tooltip text="Tu cotización como trabajador (~6,47% del salario)." /></span>
                          <span>-{fmtCur(slDetail.ss_empleado_anual)}</span>
                        </div>
                        <div className="flex justify-between text-red-600">
                          <span>- IRPF salario</span>
                          <span>-{fmtCur(slDetail.irpf_salario)}</span>
                        </div>
                        <div className="flex justify-between font-medium">
                          <span>= Salario neto</span>
                          <span className="text-blue-700">{fmtCur(slDetail.salario_neto)}</span>
                        </div>
                        <div className="flex justify-between text-red-600">
                          <span>- Gastos personales</span>
                          <span>-{fmtCur(gastos)}/mes</span>
                        </div>
                      </div>

                      {/* Summary */}
                      <div className="border-t border-purple-200 pt-2 bg-purple-50 -mx-5 px-5 pb-1 rounded-b-lg space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="font-bold text-blue-700">Inversión personal</span>
                          <span className="font-bold text-blue-700">{fmtCur(slOptimo?.inversion_personal_mensual ?? 0)}/mes</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="font-bold text-purple-700 flex items-center">
                            Inversión empresa
                            <Tooltip text="Beneficio neto de la SL que se invierte dentro de la empresa. Los rendimientos tributan al IS anualmente." />
                          </span>
                          <span className="font-bold text-purple-700">{fmtCur(slOptimo?.inversion_empresa_mensual ?? 0)}/mes</span>
                        </div>
                        <div className="flex justify-between text-sm border-t border-purple-200 pt-1">
                          <span className="font-bold text-purple-900">Total inversión</span>
                          <span className="font-bold text-purple-900 text-lg">
                            {fmtCur((slOptimo?.inversion_personal_mensual ?? 0) + (slOptimo?.inversion_empresa_mensual ?? 0))}/mes
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 text-xs text-gray-500 text-center">
                      Tipo efectivo total: {fmtPct(slDetail.tipo_efectivo)}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* ============================== */}
            {/* SECTION 5: Salary optimization chart */}
            {/* ============================== */}
            {result.comparison_curve?.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                  Optimización del salario del administrador
                  <Tooltip text="En una SL puedes elegir cuánto te pagas como salario y cuánto queda como beneficio en la empresa. Este gráfico muestra el capital final neto según el salario elegido." />
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                  El punto óptimo maximiza el capital total (personal + empresa después de impuestos).
                  Más salario = más inversión personal, pero más IRPF. Menos salario = más inversión empresa, pero IS anual sobre rendimientos.
                </p>
                <SalaryOptimizationChart
                  data={result.comparison_curve}
                  autonomoLevel={autoData.capital_final_neto}
                  optimalSalary={result.optimal?.salario_optimo ?? 0}
                  title=""
                />
              </div>
            )}

            {/* ============================== */}
            {/* SECTION 6: Capital evolution chart */}
            {/* ============================== */}
            {capitalEvolutionData.length > 1 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                  Evolución del capital
                  <Tooltip text="Evolución del capital bruto año a año. El capital de la SL incluye patrimonio personal + empresa. Recuerda: el capital bruto no es lo que recibes (ver impuestos al rescate)." />
                </h2>
                <p className="text-sm text-amber-700 bg-amber-50 rounded-lg px-3 py-2 mb-4 border border-amber-200">
                  &#9888;&#65039; Este gráfico muestra el capital <strong>bruto</strong> (antes de impuestos al rescate).
                  El dinero que recibirías es menor — consulta la tabla comparativa de arriba para ver el neto real.
                </p>
                <CapitalEvolution data={capitalEvolutionData} title="" />
              </div>
            )}

            {/* ============================== */}
            {/* SECTION 7: FIRE / 4% rule */}
            {/* ============================== */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                Independencia financiera: la regla del 4%
                <Tooltip text="La regla del 4% dice que puedes retirar un 4% anual de tu capital sin agotarlo (basado en estudios históricos del mercado). Es el estándar del movimiento FIRE." />
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Retiras un 4% anual de tu capital para vivir sin trabajar. Solo pagas impuestos sobre la parte
                proporcional de plusvalías, manteniendo el tipo efectivo bajo.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* Bulk */}
                {autoData.rescate_bulk && (
                  <div className="rounded-xl border-2 border-red-200 bg-red-50 p-5">
                    <h3 className="text-sm font-bold text-red-700 uppercase tracking-wide mb-3 flex items-center">
                      Rescate de golpe (autónomo)
                      <Tooltip text="Vendes todas tus inversiones en un año. Todas las plusvalías tributan juntas." />
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Capital bruto</span>
                        <span className="font-medium">{fmtCur(autoData.capital_final_bruto)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Plusvalías</span>
                        <span className="font-medium">{fmtCur(autoData.plusvalias ?? 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">IRPF sobre plusvalías</span>
                        <span className="font-medium text-red-600">-{fmtCur(autoData.rescate_bulk.irpf)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-1 font-bold">
                        <span>Capital neto</span>
                        <span>{fmtCur(autoData.rescate_bulk.capital_neto)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tipo efectivo</span>
                        <span className="font-medium">{fmtPct(autoData.rescate_bulk.tipo_efectivo)}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* FIRE */}
                {autoData.rescate_fire && (
                  <div className="rounded-xl border-2 border-green-200 bg-green-50 p-5">
                    <h3 className="text-sm font-bold text-green-700 uppercase tracking-wide mb-3 flex items-center">
                      Retiro gradual — regla del 4% (autónomo)
                      <Tooltip text="Retiras un 4% anual de tu capital. Solo tributas sobre la parte proporcional de plusvalías cada año." />
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Renta bruta anual</span>
                        <span className="font-medium">{fmtCur(autoData.rescate_fire.renta_bruta_anual)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">IRPF anual</span>
                        <span className="font-medium text-red-600">-{fmtCur(autoData.rescate_fire.irpf_anual)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-1">
                        <span className="font-bold">Renta neta mensual</span>
                        <span className="text-xl font-bold text-green-800">{fmtCur(autoData.rescate_fire.renta_neta_mensual)}/mes</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tipo efectivo</span>
                        <span className="font-medium">{fmtPct(autoData.rescate_fire.tipo_efectivo)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {autoData.rescate_bulk && autoData.rescate_fire &&
                autoData.rescate_bulk.tipo_efectivo > autoData.rescate_fire.tipo_efectivo && (
                <p className="text-sm text-gray-600 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
                  <strong>Conclusión:</strong> El retiro gradual paga un{" "}
                  {fmtPct(autoData.rescate_bulk.tipo_efectivo - autoData.rescate_fire.tipo_efectivo)} menos de tipo efectivo.
                  Con {fmtCur(autoData.rescate_fire.renta_neta_mensual)}/mes netos puedes vivir sin agotar tu capital.
                </p>
              )}
            </div>

            {/* ============================== */}
            {/* SECTION 8: Learn more / Key concepts */}
            {/* ============================== */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900">Conceptos clave</h2>

              <LearnMore
                titleKey="comparator.learn.4pct.title"
                contentKey="comparator.learn.4pct.content"
              />

              <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
                <h3 className="font-semibold text-gray-800 mb-2">Impuestos ahora vs. impuestos en el futuro</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Como <strong>autónomo</strong>, pagas IRPF cada año sobre todos tus ingresos (tipo marginal hasta 47%+).
                  Lo que queda después de impuestos lo inviertes personalmente.
                  Al vender, solo pagas IRPF del ahorro sobre las <em>plusvalías</em> (19-30%).
                </p>
                <p className="text-sm text-gray-600 leading-relaxed mt-2">
                  Con <strong>SL</strong>, el beneficio retenido solo tributa al tipo de Sociedades (~21-22%), mucho menos que el IRPF marginal.
                  Inviertes más desde el principio, pero los rendimientos anuales de la empresa tributan al IS,
                  y al distribuir como dividendos pagas IRPF del ahorro sobre el total.
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
                <h3 className="font-semibold text-gray-800 mb-2">Doble imposición en la SL</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  El beneficio de la SL paga primero Impuesto de Sociedades (~21%). Cuando lo distribuyes como dividendos,
                  pagas además IRPF del ahorro (19-30%). Sobre 100€ de beneficio: 21€ IS + (79€ × ~20%) = ~37€ total.
                  Aun así, puede ser menor que el IRPF marginal de un autónomo en tramos altos (37-47%).
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
                <h3 className="font-semibold text-gray-800 mb-2">IS sobre rendimientos de inversión de la empresa</h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Cuando la SL invierte sus beneficios retenidos, los rendimientos
                  tributan al tipo de Sociedades <strong>cada año</strong>. Esto reduce la rentabilidad efectiva compuesta.
                  A 7% bruto con IS del 21%, la rentabilidad neta es ~5,5%, lo que a 20 años supone ~15% menos de capital
                  respecto a inversión personal (que no tributa hasta la venta).
                </p>
              </div>

              <LearnMore
                titleKey="comparator.learn.marginal.title"
                contentKey="comparator.learn.marginal.content"
              />
            </div>

          </section>
        )}

        {/* Links to detailed pages */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link to="/formulas" className="rounded-xl border-2 border-gray-200 bg-white p-5 hover:border-blue-300 hover:bg-blue-50 transition group">
            <h3 className="font-semibold text-gray-800 group-hover:text-blue-700 flex items-center gap-2">
              <span className="text-lg">&#128208;</span> Fórmulas y Metodología
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Documentación completa con todas las fórmulas en LaTeX: IRPF, SS, IS, inversión, rescate y regla del 4%.
            </p>
          </Link>
          <Link to="/analisis" className="rounded-xl border-2 border-gray-200 bg-white p-5 hover:border-purple-300 hover:bg-purple-50 transition group">
            <h3 className="font-semibold text-gray-800 group-hover:text-purple-700 flex items-center gap-2">
              <span className="text-lg">&#128202;</span> Análisis: Autónomo vs SL
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Estudio comparativo con gráficas interactivas sobre cuándo conviene cada régimen fiscal y por qué.
            </p>
          </Link>
        </div>
      </article>
    </>
  );
}
