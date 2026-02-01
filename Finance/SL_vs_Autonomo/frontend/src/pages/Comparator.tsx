import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import InputCard from '../components/InputCard';
import CrossoverChart from '../components/charts/CrossoverChart';
import LearnMore from '../components/LearnMore';
import Tooltip from '../components/Tooltip';
import PageMeta from '../components/PageMeta';
import {
  fetchAutonomo, fetchSL, fetchOptimalSalary, fetchCrossover, fetchRegions,
} from '../api/client';

const fmt = (n: number) =>
  new Intl.NumberFormat('es-ES', { maximumFractionDigits: 0 }).format(n);
const fmtPct = (v: number) => `${(v * 100).toFixed(1)}%`;

function SliderInput({
  min, max, step, value, onChange, suffix = '€',
}: {
  min: number; max: number; step: number; value: number; onChange: (v: number) => void; suffix?: string;
}) {
  return (
    <div className="flex items-center gap-4">
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value))} className="flex-1" />
      <div className="flex items-center gap-1">
        <input type="number" value={value} onChange={(e) => onChange(Number(e.target.value))}
          className="w-24 rounded border px-2 py-1 text-right" />
        <span className="text-sm text-gray-500">{suffix}</span>
      </div>
    </div>
  );
}

export default function Comparator() {
  const { t } = useTranslation();

  const [income, setIncome] = useState(30000);
  const [region, setRegion] = useState('Galicia');
  const [regions, setRegions] = useState<{ id: string; name: string }[]>([]);
  const [gastosPct, setGastosPct] = useState(0.10);
  const [gastosEmpresa, setGastosEmpresa] = useState(2000);
  const [gastosGestoria, setGastosGestoria] = useState(3000);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Results
  const [autoResult, setAutoResult] = useState<any>(null);
  const [slAllSalary, setSlAllSalary] = useState<any>(null);
  const [slAllDividends, setSlAllDividends] = useState<any>(null);
  const [optimalData, setOptimalData] = useState<any>(null);
  const [crossoverData, setCrossoverData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRegions().then((res) => setRegions(res.regions.map((r) => ({ id: r, name: r }))));
  }, []);

  const loadComparison = useCallback(async () => {
    setLoading(true);
    try {
      // SMI = minimum salary, max salary = income - costs
      const minSalary = 15876;
      const maxSalary = Math.max(minSalary, income - (gastosEmpresa + gastosGestoria));

      const [auto, slMax, slMin, optimal, cross] = await Promise.all([
        fetchAutonomo({ facturacion_anual: income, region, gastos_deducibles_pct: gastosPct }),
        // SL "all salary": admin takes everything as salary (high salary, minimal dividends)
        fetchSL({
          facturacion_anual: income, salario_administrador: maxSalary,
          gastos_empresa: gastosEmpresa, gastos_gestoria: gastosGestoria, tipo_empresa: 'micro',
          region, pct_dividendos: 1.0,
        }),
        // SL "all dividends": admin takes minimum salary, rest as dividends
        fetchSL({
          facturacion_anual: income, salario_administrador: minSalary,
          gastos_empresa: gastosEmpresa, gastos_gestoria: gastosGestoria, tipo_empresa: 'micro',
          region, pct_dividendos: 1.0,
        }),
        fetchOptimalSalary({
          facturacion_anual: income, gastos_empresa: gastosEmpresa, gastos_gestoria: gastosGestoria,
          tipo_empresa: 'micro', region, pct_dividendos: 1.0,
        }),
        fetchCrossover({ region }),
      ]);
      setAutoResult(auto);
      setSlAllSalary(slMax);
      setSlAllDividends(slMin);
      setOptimalData(optimal);
      setCrossoverData(cross);
    } catch (e) {
      console.warn('Compare failed:', e);
    } finally {
      setLoading(false);
    }
  }, [income, region, gastosPct, gastosEmpresa, gastosGestoria]);

  useEffect(() => {
    const timeout = setTimeout(loadComparison, 400);
    return () => clearTimeout(timeout);
  }, [loadComparison]);

  const autoNeto = autoResult?.neto_mensual ?? 0;
  const slMaxSalNeto = slAllSalary?.neto_total_mensual ?? 0;
  const slMinSalNeto = slAllDividends?.neto_total_mensual ?? 0;
  const optSalary = optimalData?.optimal_salary ?? 0;
  const optNeto = optimalData?.optimal_result?.neto_total_mensual ?? 0;
  const bestNeto = Math.max(autoNeto, optNeto);
  const bestIsAuto = autoNeto >= optNeto;

  // All 4 scenarios for bar chart
  const scenarios = [
    { label: 'Autónomo', net: autoNeto, color: 'bg-green-500', key: 'auto' },
    { label: `SL todo salario (${fmt(Math.max(15876, income - (gastosEmpresa + gastosGestoria)))}€)`, net: slMaxSalNeto, color: 'bg-purple-300', key: 'sl-max' },
    { label: `SL salario óptimo (${fmt(optSalary)}€)`, net: optNeto, color: 'bg-purple-600', key: 'sl-opt' },
    { label: `SL todo dividendos (${fmt(15876)}€ salario)`, net: slMinSalNeto, color: 'bg-purple-400', key: 'sl-min' },
  ];
  const maxNet = Math.max(...scenarios.map(s => s.net));

  return (
    <>
      <PageMeta titleKey="meta.comparator.title" descriptionKey="meta.comparator.desc" />
      <article className="mx-auto max-w-3xl px-4 py-12">
        <header className="mb-12">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Comparador: Autónomo vs Sociedad Limitada
          </h1>
          <p className="mt-6 leading-relaxed text-gray-600">
            Compara cuánto cobrarías neto con la misma facturación como autónomo o a través de una SL.
            Mostramos <strong>tres escenarios de SL</strong>: todo como salario, todo como dividendos,
            y el <strong>salario óptimo</strong> que maximiza tu neto.
          </p>
          <p className="mt-3 text-sm text-gray-500 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
            <strong>Nota:</strong> Aquí el administrador cobra todos los beneficios (salario + dividendos),
            sin dejar dinero retenido. Si quieres ver el efecto de retener e invertir dentro de la SL, usa el{' '}
            <Link to="/simulador-inversion" className="text-blue-600 underline">Simulador de Inversión</Link>.
          </p>
        </header>

        {/* Inputs */}
        <InputCard title="Parámetros de facturación">
          <div className="space-y-6">
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Facturación anual bruta
                <Tooltip text="Ingresos totales anuales antes de gastos e impuestos. Es lo que facturas a tus clientes." />
              </label>
              <SliderInput min={15000} max={300000} step={1000} value={income} onChange={setIncome} />
            </div>
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Comunidad autónoma
                <Tooltip text="Los tipos de IRPF varían según la comunidad. Cada comunidad fija su propio tramo autonómico." />
              </label>
              <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full rounded border px-3 py-2">
                {regions.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Gastos deducibles (autónomo)
                <Tooltip text="Porcentaje de la facturación que corresponde a gastos deducibles (material, oficina, etc.). Solo aplica para el cálculo de autónomo." />
              </label>
              <SliderInput min={0} max={50} step={1} value={Math.round(gastosPct * 100)}
                onChange={(v) => setGastosPct(v / 100)} suffix="%" />
            </div>

            <button
              className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? "\u2212" : "+"} Gastos de la SL
            </button>

            {showAdvanced && (
              <div className="space-y-6 border-t pt-4">
                <div>
                  <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                    Gastos de la empresa (SL)
                    <Tooltip text="Gastos operativos anuales de la SL: alquiler, suministros, material, seguros, etc. NO incluye salario del administrador ni gestoría." />
                  </label>
                  <SliderInput min={0} max={50000} step={500} value={gastosEmpresa} onChange={setGastosEmpresa} suffix="€/año" />
                </div>
                <div>
                  <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                    Gestoría SL
                    <Tooltip text="Coste anual de la gestoría/asesoría fiscal de la SL. Obligatorio en la práctica para la contabilidad y presentación de impuestos." />
                  </label>
                  <SliderInput min={1000} max={10000} step={500} value={gastosGestoria} onChange={setGastosGestoria} suffix="€/año" />
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

        {autoResult && optimalData && !loading && (
          <section className="mt-12 space-y-10">
            {/* Best regime banner */}
            <div className={`rounded-2xl p-6 text-center ${
              bestIsAuto ? 'bg-green-50 border-2 border-green-200' : 'bg-purple-50 border-2 border-purple-200'
            }`}>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Mejor opción</p>
              <p className="mt-2 text-2xl font-bold">
                {bestIsAuto ? 'Autónomo' : `SL (salario óptimo: ${fmt(optSalary)} €/año)`}
              </p>
              <p className="mt-1 text-3xl font-bold text-gray-900">{fmt(Math.round(bestNeto))} €/mes neto</p>
              {Math.abs(autoNeto - optNeto) * 12 > 100 && (
                <p className="mt-2 text-sm text-gray-600">
                  Ahorras <strong>{fmt(Math.round(Math.abs(autoNeto - optNeto) * 12))} €/año</strong> respecto a la otra opción
                </p>
              )}
            </div>

            {/* Bar chart: all 4 scenarios */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                Neto mensual por escenario
                <Tooltip text="Compara el neto mensual del autónomo con tres configuraciones de SL: todo salario (máximo IRPF, sin dividendos), todo dividendos (salario mínimo, doble imposición), y salario óptimo (equilibrio entre ambos)." />
              </h3>
              {scenarios.map((item) => {
                const pct = maxNet > 0 ? (item.net / maxNet) * 100 : 0;
                const isBest = Math.abs(item.net - bestNeto) < 1;
                return (
                  <div key={item.key} className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className={`font-medium ${isBest ? 'text-gray-900' : 'text-gray-600'}`}>
                        {item.label}
                        {isBest && <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">Mejor</span>}
                      </span>
                      <span className="font-semibold text-gray-900">{fmt(Math.round(item.net))} €/mes</span>
                    </div>
                    <div className="h-8 w-full rounded-full bg-gray-100 overflow-hidden">
                      <div className={`h-full rounded-full ${item.color} transition-all duration-500`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Side-by-side: Autónomo vs SL optimal */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Autónomo card */}
              <div className={`rounded-xl border-2 p-6 ${bestIsAuto ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-white'}`}>
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  Autónomo
                  {bestIsAuto && <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">Mejor</span>}
                </h3>
                <p className="mt-3 text-3xl font-bold">{fmt(Math.round(autoNeto))} €<span className="text-base font-normal text-gray-500">/mes</span></p>
                <p className="text-sm text-gray-500">{fmt(Math.round(autoResult.neto_anual))} €/año</p>

                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 flex items-center">IRPF <Tooltip text="Impuesto sobre la Renta. Se aplica sobre el rendimiento neto (facturación - gastos - cuotas)." /></span>
                    <span className="font-medium">{fmt(autoResult.irpf_anual)} €/año</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 flex items-center">Cuotas SS <Tooltip text="Cuotas de autónomo a la Seguridad Social. En 2025 van de 230€ a 590€/mes según rendimiento." /></span>
                    <span className="font-medium">{fmt(autoResult.cuota_autonomos_anual)} €/año</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Tipo efectivo</span>
                    <span className="font-medium">{fmtPct(autoResult.tipo_efectivo_total)}</span>
                  </div>
                </div>
              </div>

              {/* SL optimal card */}
              <div className={`rounded-xl border-2 p-6 ${!bestIsAuto ? 'border-purple-300 bg-purple-50' : 'border-gray-200 bg-white'}`}>
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  SL (salario óptimo)
                  {!bestIsAuto && <span className="text-xs bg-purple-600 text-white px-2 py-0.5 rounded-full">Mejor</span>}
                </h3>
                <p className="mt-3 text-3xl font-bold">{fmt(Math.round(optNeto))} €<span className="text-base font-normal text-gray-500">/mes</span></p>
                <p className="text-sm text-gray-500">{fmt(Math.round(optNeto * 12))} €/año · salario: {fmt(optSalary)} €</p>

                {optimalData?.optimal_result && (
                  <div className="mt-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 flex items-center">Imp. Sociedades <Tooltip text="Impuesto de Sociedades sobre el beneficio de la empresa." /></span>
                      <span className="font-medium">{fmt(optimalData.optimal_result.is_pagado)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 flex items-center">IRPF salario <Tooltip text="IRPF sobre el salario del administrador." /></span>
                      <span className="font-medium">{fmt(optimalData.optimal_result.irpf_salario)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 flex items-center">IRPF dividendos <Tooltip text="IRPF del ahorro sobre los dividendos." /></span>
                      <span className="font-medium">{fmt(optimalData.optimal_result.irpf_dividendos)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 flex items-center">SS total <Tooltip text="SS empleado + SS empresa." /></span>
                      <span className="font-medium">{fmt(optimalData.optimal_result.ss_empleado_anual + optimalData.optimal_result.ss_empresa_anual)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tipo efectivo total</span>
                      <span className="font-medium">{fmtPct(optimalData.optimal_result.tipo_efectivo)}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Explanation: How SL salary optimization works */}
            <div className="rounded-lg bg-blue-50 border border-blue-200 px-4 py-3 text-sm text-blue-900 space-y-2">
              <p className="font-semibold flex items-center">
                ¿Cómo funciona el salario óptimo de la SL?
                <Tooltip text="La SL permite elegir cuánto cobras como salario y cuánto como dividendos. Cada opción tiene una tributación diferente." />
              </p>
              <p className="text-xs leading-relaxed">
                En una SL, puedes repartir los beneficios entre <strong>salario</strong> (tributa por IRPF progresivo: 19-47%) y{' '}
                <strong>dividendos</strong> (tributan al IS ~21% + IRPF del ahorro 19-30%, combinado ~37-45%).
              </p>
              <ul className="text-xs space-y-1 list-disc list-inside">
                <li><strong>Todo salario ({fmt(Math.max(15876, income - (gastosEmpresa + gastosGestoria)))} €):</strong> Paga mucho IRPF progresivo en tramos altos, pero evita la doble imposición de dividendos. Resultado: {fmt(Math.round(slMaxSalNeto))} €/mes.</li>
                <li><strong>Todo dividendos (salario mínimo {fmt(15876)} €):</strong> Minimiza el IRPF del salario, pero todo el beneficio pasa por IS + IRPF ahorro (doble imposición). Resultado: {fmt(Math.round(slMinSalNeto))} €/mes.</li>
                <li><strong>Salario óptimo ({fmt(optSalary)} €):</strong> El equilibrio que minimiza la carga fiscal total. Resultado: {fmt(Math.round(optNeto))} €/mes.</li>
              </ul>
              <p className="text-xs text-blue-700 mt-1">
                El punto óptimo depende de tu facturación y comunidad autónoma. Generalmente se sitúa donde el tipo marginal del IRPF del salario iguala al tipo efectivo combinado de IS + IRPF ahorro de los dividendos.
              </p>
            </div>

            {/* SL extremes comparison table */}
            {slAllSalary && slAllDividends && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Detalle de los tres escenarios de SL</h3>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[480px] text-sm">
                    <thead>
                      <tr className="border-b text-left">
                        <th className="py-3 pr-4 font-medium text-gray-500">Concepto</th>
                        <th className="py-3 px-3 font-medium text-purple-600 text-right">Todo salario</th>
                        <th className="py-3 px-3 font-medium text-purple-800 text-right">Óptimo</th>
                        <th className="py-3 pl-3 font-medium text-purple-500 text-right">Todo dividendos</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-600">
                      {[
                        { label: 'Salario bruto', vals: [slAllSalary.salario_administrador, optimalData?.optimal_result?.salario_administrador ?? 0, slAllDividends.salario_administrador] },
                        { label: 'IRPF salario', vals: [slAllSalary.irpf_salario, optimalData?.optimal_result?.irpf_salario ?? 0, slAllDividends.irpf_salario] },
                        { label: 'SS total', vals: [slAllSalary.ss_empleado_anual + slAllSalary.ss_empresa_anual, (optimalData?.optimal_result?.ss_empleado_anual ?? 0) + (optimalData?.optimal_result?.ss_empresa_anual ?? 0), slAllDividends.ss_empleado_anual + slAllDividends.ss_empresa_anual] },
                        { label: 'Imp. Sociedades', vals: [slAllSalary.is_pagado, optimalData?.optimal_result?.is_pagado ?? 0, slAllDividends.is_pagado] },
                        { label: 'Dividendos brutos', vals: [slAllSalary.dividendos_brutos, optimalData?.optimal_result?.dividendos_brutos ?? 0, slAllDividends.dividendos_brutos] },
                        { label: 'IRPF dividendos', vals: [slAllSalary.irpf_dividendos, optimalData?.optimal_result?.irpf_dividendos ?? 0, slAllDividends.irpf_dividendos] },
                      ].map(({ label, vals }) => (
                        <tr key={label} className="border-b">
                          <td className="py-2 pr-4 font-medium text-gray-700">{label}</td>
                          {vals.map((v, i) => (
                            <td key={i} className="py-2 px-3 text-right">{fmt(Math.round(v))} €</td>
                          ))}
                        </tr>
                      ))}
                      <tr className="border-t-2 font-bold">
                        <td className="py-3 pr-4 text-gray-900">Neto mensual</td>
                        <td className="py-3 px-3 text-right text-purple-600">{fmt(Math.round(slMaxSalNeto))} €</td>
                        <td className="py-3 px-3 text-right text-purple-800">{fmt(Math.round(optNeto))} €</td>
                        <td className="py-3 pl-3 text-right text-purple-500">{fmt(Math.round(slMinSalNeto))} €</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Crossover chart */}
            {crossoverData && (
              <CrossoverChart
                points={(crossoverData.points || []).map((p: any) => ({ ...p }))}
                crossovers={(crossoverData.crossovers || []).map((c: any) => c.approximate_income)}
                title="¿A qué facturación conviene cambiar?"
              />
            )}

            {/* Qualitative comparison */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Comparativa cualitativa</h3>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[480px] text-sm">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="py-3 pr-4 font-medium text-gray-500">Aspecto</th>
                      <th className="py-3 px-4 font-medium text-green-700">Autónomo</th>
                      <th className="py-3 pl-4 font-medium text-purple-700">Sociedad Limitada</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-600">
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700">Coste de creación</td>
                      <td className="py-3 px-4">Gratis (alta en AEAT+TGSS)</td>
                      <td className="py-3 pl-4">~600-1.500€ (notaría, registro, capital social)</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700">Coste mensual gestoría</td>
                      <td className="py-3 px-4">~60-100 €/mes</td>
                      <td className="py-3 pl-4">~200-300 €/mes</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700 flex items-center">Responsabilidad <Tooltip text="Como autónomo respondes con tu patrimonio personal. La SL limita la responsabilidad al capital social." /></td>
                      <td className="py-3 px-4 text-red-600">Ilimitada (patrimonio personal)</td>
                      <td className="py-3 pl-4 text-green-600">Limitada al capital social</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700">Complejidad administrativa</td>
                      <td className="py-3 px-4">Baja</td>
                      <td className="py-3 pl-4">Media-Alta (contabilidad, cuentas anuales, libros)</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700 flex items-center">Flexibilidad fiscal <Tooltip text="La SL permite elegir cuánto salario cobrar, cuántos dividendos repartir y cuánto retener para inversión." /></td>
                      <td className="py-3 px-4">Baja (todo tributa al IRPF)</td>
                      <td className="py-3 pl-4 text-green-600">Alta (salario + dividendos + retención)</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700 flex items-center">Inversión en la empresa <Tooltip text="Con SL puedes reinvertir beneficios tributando solo al 21-22% IS, en lugar del tipo marginal de IRPF que puede llegar al 47%+." /></td>
                      <td className="py-3 px-4">No aplica (todo es renta personal)</td>
                      <td className="py-3 pl-4 text-green-600">Sí (IS 21-22% vs IRPF hasta 47%+)</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 pr-4 font-medium text-gray-700">Cotización SS</td>
                      <td className="py-3 px-4">Cuota fija por tramos (230-590€/mes)</td>
                      <td className="py-3 pl-4">% sobre salario (~37% total empleado+empresa)</td>
                    </tr>
                    <tr>
                      <td className="py-3 pr-4 font-medium text-gray-700">Prestaciones (baja, jubilación)</td>
                      <td className="py-3 px-4">Base reguladora según cuota elegida</td>
                      <td className="py-3 pl-4">Base reguladora según salario administrador</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}

        {/* Learn more */}
        <div className="mt-16 space-y-4">
          <LearnMore
            titleKey="comparator.learn.marginal.title"
            contentKey="comparator.learn.marginal.content"
          />
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
            <strong>¿Quieres simular tu inversión a largo plazo?</strong>{" "}
            Visita el <Link to="/simulador-inversion" className="underline font-medium">Simulador de Inversión</Link> para
            ver la regla del 4%, independencia financiera y comparar estrategias de rescate con impuestos detallados.
          </div>
        </div>

        {/* Links */}
        <nav className="mt-16 flex flex-wrap gap-4 border-t pt-8 text-sm">
          <Link to="/autonomo" className="text-blue-600 hover:underline">Calculadora Autónomo</Link>
          <Link to="/sl" className="text-blue-600 hover:underline">Calculadora SL</Link>
          <Link to="/simulador-inversion" className="text-blue-600 hover:underline">Simulador de Inversión (avanzado)</Link>
        </nav>

        <p className="mt-12 text-center text-xs text-gray-400">{t('disclaimer')}</p>
      </article>
    </>
  );
}
