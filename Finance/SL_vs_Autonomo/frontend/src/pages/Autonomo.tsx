import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import InputCard from '../components/InputCard';
import ResultHero from '../components/ResultHero';
import BreakdownBar from '../components/BreakdownBar';
import IncomeBreakdownPie from '../components/charts/IncomeBreakdownPie';
import BracketTable from '../components/BracketTable';
import LearnMore from '../components/LearnMore';
import Tooltip from '../components/Tooltip';
import { useAutonomo } from '../hooks/useAutonomo';
import PageMeta from '../components/PageMeta';
import { fetchRegions, fetchPresets, fetchAutonomoReverse } from '../api/client';

const fmt = (n: number) =>
  new Intl.NumberFormat('es-ES', { maximumFractionDigits: 0 }).format(n);

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

type CuotaMode = 'tarifa_plana' | 'normal' | 'custom';
type GastosMode = 'pct' | 'eur';

export default function Autonomo() {
  const { t } = useTranslation();
  const {
    facturacion, setFacturacion, region, setRegion,
    gastosPct, setGastosPct, tarifaPlana, setTarifaPlana, result, loading,
  } = useAutonomo();

  const [regions, setRegions] = useState<{ id: string; name: string }[]>([]);
  const [presets, setPresets] = useState<Array<{ label: string; income: number; icon: string }>>([]);
  const [cuotaMode, setCuotaMode] = useState<CuotaMode>('tarifa_plana');
  const [customCuota, setCustomCuota] = useState(300);
  const [targetNet, setTargetNet] = useState(30000);
  const [reverseResult, setReverseResult] = useState<{ salario_neto_objetivo: number; facturacion_necesaria: number } | null>(null);
  const [gastosMode, setGastosMode] = useState<GastosMode>('pct');
  const [gastosEur, setGastosEur] = useState(3000);

  useEffect(() => { fetchRegions().then((res) => setRegions(res.regions.map((r) => ({ id: r, name: r })))); }, []);
  useEffect(() => { fetchPresets().then((res) => setPresets(res.presets)).catch(() => {}); }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      fetchAutonomoReverse({ salario_neto_objetivo: targetNet, region, gastos_deducibles_pct: gastosPct / 100 })
        .then(setReverseResult).catch(() => setReverseResult(null));
    }, 500);
    return () => clearTimeout(timeout);
  }, [targetNet, region, gastosPct]);

  useEffect(() => {
    if (cuotaMode === 'tarifa_plana') setTarifaPlana(true);
    else setTarifaPlana(false);
  }, [cuotaMode, setTarifaPlana]);

  // Sync gastos between % and €
  // gastosPct from hook is decimal (0.10 = 10%), convert for display
  const gastosPctDisplay = Math.round(gastosPct * 100);
  const handleGastosPctChange = (v: number) => {
    setGastosPct(v / 100); // convert back to decimal for hook
    setGastosEur(Math.round(facturacion * v / 100));
  };
  const handleGastosEurChange = (v: number) => {
    setGastosEur(v);
    if (facturacion > 0) setGastosPct(v / facturacion); // decimal
  };
  // Update € when facturacion changes
  useEffect(() => {
    if (gastosMode === 'pct') {
      setGastosEur(Math.round(facturacion * gastosPct));
    }
  }, [facturacion, gastosPct, gastosMode]);

  return (
    <>
      <PageMeta titleKey="meta.autonomo.title" descriptionKey="meta.autonomo.desc" />
      <article className="mx-auto max-w-3xl px-4 py-12">
        <header className="mb-12">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">{t('autonomo.title')}</h1>
          <p className="mt-6 leading-relaxed text-gray-600">{t('autonomo.intro.p1')}</p>
          <p className="mt-4 leading-relaxed text-gray-600">{t('autonomo.intro.p2')}</p>
        </header>

        {/* Presets */}
        {presets.length > 0 && (
          <div className="mb-8">
            <p className="mb-3 text-sm font-medium text-gray-500">{t('presets.title')}</p>
            <div className="flex flex-wrap gap-2">
              {presets.map((p) => (
                <button
                  key={p.label}
                  onClick={() => setFacturacion(p.income)}
                  className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors ${
                    facturacion === p.income
                      ? 'border-blue-500 bg-blue-50 text-blue-700 font-medium'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:bg-blue-50'
                  }`}
                >
                  <span>{p.icon}</span>
                  <span>{p.label}</span>
                  <span className="text-gray-400">{(p.income / 1000).toFixed(0)}K</span>
                </button>
              ))}
            </div>
          </div>
        )}

        <InputCard title={t('autonomo.calculator.title')}>
          <div className="space-y-6">
            {/* 1. Billing */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                {t('autonomo.calculator.billing')}
                <Tooltip text="Lo que facturas anualmente a tus clientes (sin IVA). Es tu ingreso bruto antes de gastos e impuestos." />
              </label>
              <SliderInput min={15000} max={300000} step={1000} value={facturacion} onChange={setFacturacion} />
            </div>

            {/* 2. Gastos deducibles (primary input now) */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Gastos deducibles
                <Tooltip text="Gastos necesarios para tu actividad: alquiler oficina, material, suministros, formación, seguros, gestoría, etc. Reducen tu base imponible y por tanto tus impuestos. Deben estar justificados con factura." />
              </label>
              <div className="flex items-center gap-2 mb-3">
                <button
                  onClick={() => setGastosMode('pct')}
                  className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                    gastosMode === 'pct' ? 'bg-green-100 border-green-400 text-green-800 font-medium' : 'border-gray-200 text-gray-500'
                  }`}
                >% de facturación</button>
                <button
                  onClick={() => setGastosMode('eur')}
                  className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                    gastosMode === 'eur' ? 'bg-green-100 border-green-400 text-green-800 font-medium' : 'border-gray-200 text-gray-500'
                  }`}
                >Importe fijo (€)</button>
              </div>
              {gastosMode === 'pct' ? (
                <>
                  <SliderInput min={0} max={50} step={1} value={gastosPctDisplay} onChange={handleGastosPctChange} suffix="%" />
                  <p className="mt-1 text-xs text-gray-400">{fmt(gastosEur)} €/año</p>
                </>
              ) : (
                <>
                  <SliderInput min={0} max={Math.max(100000, facturacion * 0.5)} step={500} value={gastosEur} onChange={handleGastosEurChange} suffix="€/año" />
                  <p className="mt-1 text-xs text-gray-400">{facturacion > 0 ? `${((gastosEur / facturacion) * 100).toFixed(1)}%` : '0%'} de la facturación</p>
                </>
              )}
            </div>

            {/* 3. Region */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                {t('autonomo.calculator.region')}
                <Tooltip text="Los tramos de IRPF varían según tu comunidad autónoma. Cada comunidad fija su propio tramo autonómico." />
              </label>
              <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full rounded border px-3 py-2">
                {regions.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>

            {/* 4. Cuota de autónomos */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                {t('autonomo.calculator.cuota')}
                <Tooltip text="Cotización mensual obligatoria a la Seguridad Social. Desde 2023 se calcula por tramos según tu rendimiento neto real (facturación - gastos). Va de 230€/mes (rendimiento bajo) a 590€/mes (rendimiento alto). La tarifa plana es 87€/mes los primeros 12 meses si eres nuevo autónomo." />
              </label>
              <div className="space-y-2">
                {([
                  { mode: 'tarifa_plana' as CuotaMode, label: 'Tarifa plana (87 €/mes)', desc: 'Primeros 12 meses (ampliable a 24 si no superas el SMI)' },
                  { mode: 'normal' as CuotaMode, label: 'Por ingresos reales (2025)', desc: '230-590 €/mes según tu rendimiento neto' },
                  { mode: 'custom' as CuotaMode, label: 'Personalizada', desc: 'Introduce tu cuota manualmente' },
                ]).map(({ mode, label, desc }) => (
                  <label key={mode} className={`flex items-start gap-3 rounded-lg border p-3 cursor-pointer transition-colors ${
                    cuotaMode === mode ? 'border-green-400 bg-green-50' : 'border-gray-200 hover:border-green-200'
                  }`}>
                    <input type="radio" name="cuota" checked={cuotaMode === mode}
                      onChange={() => setCuotaMode(mode)} className="accent-green-600 mt-0.5" />
                    <div>
                      <span className="text-sm font-medium text-gray-800">{label}</span>
                      <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
                    </div>
                  </label>
                ))}
              </div>
              {cuotaMode === 'tarifa_plana' && (
                <div className="mt-3 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-800">
                  <strong>Requisitos:</strong> No haber sido autónomo en los 2 años anteriores (3 si ya la disfrutaste).
                  87 €/mes los primeros 12 meses. Ampliable otros 12 meses si tus rendimientos no superan el SMI.{' '}
                  <a href="https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/CotizacionRecaudacionTrabajadores/36537" target="_blank" rel="noopener noreferrer" className="underline text-amber-700 hover:text-amber-900">
                    Más info en la Seguridad Social
                  </a>
                </div>
              )}
              {cuotaMode === 'normal' && result?.cuota_info && (
                <div className="mt-3 rounded-lg bg-gray-50 border border-gray-200 px-3 py-2 text-xs text-gray-600">
                  Con tu rendimiento neto actual ({fmt(result.rendimiento_neto)} €/año), tu cuota sería de{' '}
                  <strong>{fmt(Math.round(result.cuota_autonomos_mensual))} €/mes</strong> ({fmt(result.cuota_autonomos_anual)} €/año).
                </div>
              )}
              {cuotaMode === 'custom' && (
                <div className="mt-3">
                  <SliderInput min={87} max={1200} step={1} value={customCuota} onChange={setCustomCuota} suffix="€/mes" />
                </div>
              )}
            </div>
          </div>
        </InputCard>

        {result && !loading && (
          <div className="mt-12 space-y-10">
            <ResultHero
              value={result.neto_mensual}
              label={t('autonomo.result.net_monthly')}
              subtitle={`${fmt(result.neto_anual)} ${t('autonomo.result.per_year')}`}
            />

            {/* Tax rate badges */}
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{t('rates.effective')}</p>
                <p className="mt-1 text-2xl font-bold text-blue-700">{(result.tipo_efectivo_total * 100).toFixed(1)}%</p>
              </div>
              <div className="flex-1 rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{t('rates.marginal')}</p>
                <p className="mt-1 text-2xl font-bold text-amber-600">{(result.tipo_marginal_irpf * 100).toFixed(1)}%</p>
              </div>
            </div>

            <BreakdownBar items={result.breakdown} total={facturacion} />

            {/* Salary equivalent */}
            <div className="rounded-lg border bg-gray-50 p-4 text-center">
              <p className="text-sm text-gray-500">{t('autonomo.result.salary_equiv')}</p>
              <p className="mt-1 text-2xl font-semibold text-gray-900">{fmt(result.salario_equivalente)} €</p>
            </div>

            <IncomeBreakdownPie items={result.breakdown} title={t('autonomo.result.breakdown')} />

            {result?.irpf_detalle && (
              <details className="mt-10 group">
                <summary className="cursor-pointer text-sm font-semibold text-green-700 hover:text-green-800">
                  {t('brackets.detail_title')}
                </summary>
                <div className="mt-4">
                  <BracketTable
                    brackets={result.irpf_detalle.brackets}
                    total={result.irpf_detalle.total}
                    effectiveRate={result.irpf_detalle.effective_rate}
                  />
                </div>
              </details>
            )}
          </div>
        )}

        {loading && (
          <div className="mt-12 flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-green-600" />
          </div>
        )}

        {/* Reverse Calculator */}
        <div className="mt-12 rounded-xl border border-indigo-100 bg-gradient-to-br from-indigo-50 to-white p-6">
          <h3 className="text-lg font-semibold text-gray-900">{t('autonomo.reverse.title')}</h3>
          <p className="mt-1 text-sm text-gray-500">{t('autonomo.reverse.desc')}</p>
          <div className="mt-4 flex flex-wrap items-end gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">{t('autonomo.reverse.target')}</label>
              <div className="flex items-center gap-1">
                <input type="number" value={targetNet} onChange={(e) => setTargetNet(Number(e.target.value))}
                  className="w-28 rounded border border-gray-300 px-3 py-2 text-right text-sm" step={1000} min={10000} max={200000} />
                <span className="text-xs text-gray-400">&euro;/a&ntilde;o</span>
              </div>
            </div>
            {reverseResult && (
              <div className="flex-1 text-center rounded-lg bg-white border border-indigo-200 p-4">
                <p className="text-xs text-gray-500 uppercase tracking-wide">{t('autonomo.reverse.result_label')}</p>
                <p className="text-3xl font-bold text-indigo-700">{fmt(reverseResult.facturacion_necesaria)} &euro;<span className="text-base font-normal text-gray-400">/a&ntilde;o</span></p>
                <p className="mt-1 text-sm text-gray-400">{fmt(Math.round(reverseResult.facturacion_necesaria / 12))} &euro;/mes</p>
              </div>
            )}
          </div>
        </div>

        <div className="mt-16 space-y-4">
          <LearnMore titleKey="autonomo.learn.cuota.title" contentKey="autonomo.learn.cuota.content" />
          <LearnMore titleKey="autonomo.learn.deductions.title" contentKey="autonomo.learn.deductions.content" />
          <LearnMore titleKey="autonomo.learn.tarifa.title" contentKey="autonomo.learn.tarifa.content" />
        </div>

        <nav className="mt-16 flex flex-wrap gap-4 border-t pt-8 text-sm">
          <Link to="/employee" className="text-green-600 hover:underline">{t('nav.link.employee')}</Link>
          <Link to="/sl" className="text-green-600 hover:underline">{t('nav.link.sl')}</Link>
          <Link to="/comparador" className="text-green-600 hover:underline">{t('nav.link.comparator')}</Link>
        </nav>
      </article>
    </>
  );
}
