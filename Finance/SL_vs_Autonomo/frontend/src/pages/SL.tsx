import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import InputCard from '../components/InputCard';
import ResultHero from '../components/ResultHero';
import BreakdownBar from '../components/BreakdownBar';
import OptimalSalary from '../components/charts/OptimalSalary';
import IncomeBreakdownPie from '../components/charts/IncomeBreakdownPie';
import BracketTable from '../components/BracketTable';
import LearnMore from '../components/LearnMore';
import Tooltip from '../components/Tooltip';
import { useSL } from '../hooks/useSL';
import PageMeta from '../components/PageMeta';
import { fetchRegions, fetchPresets } from '../api/client';

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

export default function SL() {
  const { t } = useTranslation();
  const {
    facturacion, setFacturacion, salario, setSalario,
    gastosEmpresa, setGastosEmpresa, gestoria, setGestoria,
    tipoEmpresa, setTipoEmpresa, region, setRegion,
    pctDividendos, setPctDividendos, result, optimalData, loading,
  } = useSL();

  const [regions, setRegions] = useState<{ id: string; name: string }[]>([]);
  const [presets, setPresets] = useState<Array<{ label: string; income: number; icon: string }>>([]);
  useEffect(() => { fetchRegions().then((res) => setRegions(res.regions.map((r) => ({ id: r, name: r })))); }, []);
  useEffect(() => { fetchPresets().then((res) => setPresets(res.presets)).catch(() => {}); }, []);

  const optSalary = optimalData?.optimal_salary ?? 0;
  const optNeto = optimalData?.optimal_result?.neto_total_mensual ?? 0;

  return (
    <>
      <PageMeta titleKey="meta.sl.title" descriptionKey="meta.sl.desc" />
      <article className="mx-auto max-w-3xl px-4 py-12">
        <header className="mb-12">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">{t('sl.title')}</h1>
          <p className="mt-6 leading-relaxed text-gray-600">{t('sl.intro.p1')}</p>
          <p className="mt-4 leading-relaxed text-gray-600">{t('sl.intro.p2')}</p>
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

        <InputCard title={t('sl.calculator.title')}>
          <div className="space-y-6">
            {/* 1. Company billing */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                {t('sl.calculator.billing')}
                <Tooltip text="Facturación total anual de la SL antes de gastos. Es lo que factura la empresa a sus clientes (sin IVA)." />
              </label>
              <SliderInput min={30000} max={500000} step={1000} value={facturacion} onChange={setFacturacion} />
            </div>

            {/* 2. Company expenses (deductible) */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                Gastos deducibles de la empresa
                <Tooltip text="Gastos operativos de la SL: alquiler, suministros, material, seguros, viajes, etc. Se deducen antes de calcular el beneficio. NO incluye salario del administrador ni gestoría (se configuran aparte)." />
              </label>
              <SliderInput min={0} max={100000} step={500} value={gastosEmpresa} onChange={setGastosEmpresa} suffix="€/año" />
              {facturacion > 0 && (
                <p className="mt-1 text-xs text-gray-400">
                  {((gastosEmpresa / facturacion) * 100).toFixed(1)}% de la facturación
                </p>
              )}
            </div>

            {/* 3. Admin salary */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                {t('sl.calculator.salary')}
                <Tooltip text="Salario bruto anual que te asignas como administrador de la SL. Tributa como rendimiento del trabajo (IRPF progresivo + SS). El resto del beneficio de la empresa puede repartirse como dividendos (tributan al IRPF del ahorro: 19-30%) o retenerse en la empresa." />
              </label>
              <SliderInput min={15876} max={Math.min(facturacion * 0.8, 200000)} step={500} value={salario} onChange={setSalario} />
              {optimalData && (
                <div className="mt-2 flex items-center gap-2">
                  <button
                    onClick={() => setSalario(optSalary)}
                    className="text-xs px-2.5 py-1 rounded-full bg-purple-100 text-purple-700 border border-purple-300 hover:bg-purple-200 transition-colors font-medium"
                  >
                    Usar salario óptimo: {fmt(optSalary)} €
                  </button>
                  <Tooltip text={`El salario óptimo de ${fmt(optSalary)} €/año maximiza tu renta neta total (salario + dividendos = ${fmt(Math.round(optNeto))} €/mes). Este cálculo busca el equilibrio entre IRPF progresivo del salario y la doble imposición IS + IRPF ahorro de los dividendos.`} />
                </div>
              )}
            </div>

            {/* 4. Region */}
            <div>
              <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                {t('sl.calculator.region')}
                <Tooltip text="Afecta al IRPF sobre el salario del administrador. Cada comunidad tiene tramos autonómicos distintos." />
              </label>
              <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full rounded border px-3 py-2">
                {regions.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Expandable advanced */}
          <details className="mt-6">
            <summary className="cursor-pointer text-sm font-medium text-purple-600">{t('sl.calculator.advanced')}</summary>
            <div className="mt-4 space-y-5">
              <div>
                <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                  {t('sl.calculator.gestoria')}
                  <Tooltip text="Coste de la gestoría o asesoría fiscal de la SL. Suele ser 200-300 €/mes. Es un gasto deducible para la empresa." />
                </label>
                <SliderInput min={0} max={6000} step={50} value={gestoria} onChange={setGestoria} />
              </div>
              <div>
                <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                  {t('sl.calculator.company_type')}
                  <Tooltip text="El tipo de IS depende del tamaño de la empresa. Microempresa (<1M€): 21% primeros 50K + 22% resto. Startup (primeros 2 ejercicios con beneficio): 15%. PYME/General: 25%." />
                </label>
                <select value={tipoEmpresa} onChange={(e) => setTipoEmpresa(e.target.value)}
                  className="w-full rounded border px-3 py-2">
                  <option value="micro">Microempresa (&lt;1M€ facturación) — IS 21-22%</option>
                  <option value="startup">Startup (primeros 2 años) — IS 15%</option>
                  <option value="sme">PYME (1M-10M€) — IS 25%</option>
                  <option value="general">General (&gt;10M€) — IS 25%</option>
                </select>
              </div>
              <div>
                <label className="mb-2 flex items-center text-sm font-medium text-gray-700">
                  {t('sl.calculator.dividends_pct')}
                  <Tooltip text="Porcentaje del beneficio después de IS que se reparte como dividendos. 100% = cobras todo el beneficio. 0% = todo se retiene en la empresa (tributó IS pero no IRPF del ahorro). Lo retenido puede reinvertirse dentro de la SL." />
                </label>
                <SliderInput min={0} max={100} step={1} value={pctDividendos} onChange={setPctDividendos} suffix="%" />
              </div>
            </div>
          </details>
        </InputCard>

        {result && !loading && (
          <div className="mt-12 space-y-10">
            {/* Main result: explain what it includes */}
            <div className="text-center">
              <ResultHero
                value={result.neto_total_mensual}
                label="Renta neta mensual total"
                subtitle="Salario neto + dividendos netos (después de todos los impuestos)"
              />
              {/* Detailed breakdown of what makes up the total */}
              <div className="mt-4 flex flex-wrap justify-center gap-6 text-sm">
                <div className="text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Salario neto</p>
                  <p className="text-lg font-bold text-blue-700">{fmt(Math.round(result.salario_neto / 12))} €/mes</p>
                </div>
                <div className="text-center text-gray-300 text-lg font-light self-end">+</div>
                <div className="text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Dividendos netos</p>
                  <p className="text-lg font-bold text-purple-700">{fmt(Math.round(result.dividendos_netos / 12))} €/mes</p>
                </div>
                {result.beneficio_retenido > 0 && (
                  <>
                    <div className="text-center text-gray-300 text-lg font-light self-end">|</div>
                    <div className="text-center">
                      <p className="text-xs text-gray-500 uppercase tracking-wide flex items-center justify-center">
                        Retenido en SL
                        <Tooltip text="Beneficio que queda en la empresa. Ya tributó al IS pero no al IRPF del ahorro. Puede reinvertirse o repartirse más adelante." />
                      </p>
                      <p className="text-lg font-bold text-blue-500">{fmt(Math.round(result.beneficio_retenido / 12))} €/mes</p>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Explanation banner */}
            <div className="rounded-lg bg-purple-50 border border-purple-200 px-4 py-3 text-sm text-purple-800">
              <p>
                <strong>¿Cómo se calcula?</strong> Tu SL factura {fmt(facturacion)} €/año.
                Tras pagar tu salario ({fmt(salario)} €), SS empresa ({fmt(result.ss_empresa_anual)} €),
                gastos ({fmt(gastosEmpresa + gestoria)} €) y el Impuesto de Sociedades ({fmt(result.is_pagado)} €),
                {pctDividendos > 0 ? ` se reparten ${fmt(Math.round(result.dividendos_brutos))} € en dividendos (de los que ${fmt(Math.round(result.irpf_dividendos))} € son IRPF del ahorro).` : ' el beneficio se retiene íntegramente en la empresa.'}
              </p>
            </div>

            {/* Tax rate badges */}
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{t('rates.effective')}</p>
                <p className="mt-1 text-2xl font-bold text-blue-700">{(result.tipo_efectivo * 100).toFixed(1)}%</p>
              </div>
              {result.irpf_salario_detalle && (
                <div className="flex-1 rounded-lg border border-gray-200 bg-white p-4 text-center">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{t('rates.marginal')}</p>
                  <p className="mt-1 text-2xl font-bold text-amber-600">{(result.irpf_salario_detalle.marginal_rate * 100).toFixed(1)}%</p>
                </div>
              )}
            </div>

            <BreakdownBar items={result.breakdown} total={facturacion} />

            {optimalData && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                  {t('sl.result.optimal_salary')}
                  <Tooltip text="El gráfico muestra tu renta neta total (salario + dividendos) para cada nivel de salario. El punto óptimo equilibra el IRPF progresivo del salario con la doble imposición (IS + IRPF ahorro) de los dividendos. A la izquierda: mucho dividendo (doble imposición alta). A la derecha: mucho salario (IRPF marginal alto)." />
                </h3>
                <OptimalSalary
                  curve={optimalData.curve.map(p => ({ salary: p.salary, net_income: p.net_income, total_impuestos: p.total_impuestos }))}
                  optimalSalary={optimalData.optimal_salary}
                  title=""
                />
              </div>
            )}

            <IncomeBreakdownPie items={result.breakdown} title={t('sl.result.breakdown')} />

            {result?.irpf_salario_detalle && (
              <details className="mt-10 group">
                <summary className="cursor-pointer text-sm font-semibold text-purple-700 hover:text-purple-800">
                  {t('brackets.detail_title')}
                </summary>
                <div className="mt-4">
                  <BracketTable
                    brackets={result.irpf_salario_detalle.brackets}
                    total={result.irpf_salario_detalle.total}
                    effectiveRate={result.irpf_salario_detalle.effective_rate}
                  />
                </div>
              </details>
            )}

            {/* Important caveats */}
            <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800 space-y-2">
              <p className="font-semibold">Consideraciones importantes:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>El salario del administrador debe estar aprobado en estatutos o junta. Si no se aprueba remuneración, formalmente el cargo es gratuito.</li>
                <li>Hacienda puede considerar que un salario excesivamente bajo es una estrategia para eludir impuestos, especialmente si la empresa tiene beneficios elevados.</li>
                <li>La Seguridad Social del administrador (~37% total: 6,47% empleado + 30,6% empresa) es un coste significativo que reduce el beneficio de la SL.</li>
                <li>El coste de constitución (~600-1.500€) y gestoría mensual (200-300€) hacen que la SL solo merezca la pena a partir de cierto nivel de facturación.</li>
              </ul>
            </div>
          </div>
        )}

        {loading && (
          <div className="mt-12 flex justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-purple-600" />
          </div>
        )}

        <div className="mt-16 space-y-4">
          <LearnMore titleKey="sl.learn.is.title" contentKey="sl.learn.is.content" />
          <LearnMore titleKey="sl.learn.doble.title" contentKey="sl.learn.doble.content" />
          <LearnMore titleKey="sl.learn.when.title" contentKey="sl.learn.when.content" />
        </div>

        <nav className="mt-16 flex flex-wrap gap-4 border-t pt-8 text-sm">
          <Link to="/employee" className="text-purple-600 hover:underline">{t('nav.link.employee')}</Link>
          <Link to="/autonomo" className="text-purple-600 hover:underline">{t('nav.link.autonomo')}</Link>
          <Link to="/comparador" className="text-purple-600 hover:underline">{t('nav.link.comparator')}</Link>
        </nav>
      </article>
    </>
  );
}
