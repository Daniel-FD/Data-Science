import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import InputCard from '../components/InputCard';
import ResultHero from '../components/ResultHero';
import BreakdownBar from '../components/BreakdownBar';
import IncomeBreakdownPie from '../components/charts/IncomeBreakdownPie';
import BracketTable from '../components/BracketTable';
import LearnMore from '../components/LearnMore';
import { useEmployee } from '../hooks/useEmployee';
import PageMeta from '../components/PageMeta';
import { fetchRegions, fetchPresets } from '../api/client';

const fmt = (n: number) =>
  new Intl.NumberFormat('es-ES', { maximumFractionDigits: 0 }).format(n);

interface SliderInputProps {
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (v: number) => void;
  suffix?: string;
}

function SliderInput({ min, max, step, value, onChange, suffix = '€' }: SliderInputProps) {
  return (
    <div className="flex items-center gap-4">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="flex-1"
      />
      <div className="flex items-center gap-1">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-24 rounded border px-2 py-1 text-right"
        />
        <span className="text-sm text-gray-500">{suffix}</span>
      </div>
    </div>
  );
}

export default function Employee() {
  const { t } = useTranslation();
  const { salario, setSalario, region, setRegion, numPagas, setNumPagas, result, loading } = useEmployee();
  const [regions, setRegions] = useState<{ id: string; name: string }[]>([]);
  const [presets, setPresets] = useState<Array<{ label: string; income: number; icon: string }>>([]);

  useEffect(() => {
    fetchRegions().then((res) => setRegions(res.regions.map((r) => ({ id: r, name: r }))));
  }, []);
  useEffect(() => { fetchPresets().then((res) => setPresets(res.presets)).catch(() => {}); }, []);

  return (
    <>
      <PageMeta titleKey="meta.employee.title" descriptionKey="meta.employee.desc" />
      <article className="mx-auto max-w-3xl px-4 py-12">
        {/* Editorial intro */}
        <header className="mb-12">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            {t('employee.title')}
          </h1>
          <p className="mt-6 leading-relaxed text-gray-600">{t('employee.intro.p1')}</p>
          <p className="mt-4 leading-relaxed text-gray-600">{t('employee.intro.p2')}</p>
          <p className="mt-4 leading-relaxed text-gray-600">{t('employee.intro.p3')}</p>
        </header>

        {/* Presets */}
        {presets.length > 0 && (
          <div className="mb-8">
            <p className="mb-3 text-sm font-medium text-gray-500">{t('presets.title')}</p>
            <div className="flex flex-wrap gap-2">
              {presets.map((p) => (
                <button
                  key={p.label}
                  onClick={() => setSalario(p.income)}
                  className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm transition-colors ${
                    salario === p.income
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

        {/* Calculator */}
        <InputCard title={t('employee.calculator.title')}>
          <div className="space-y-6">
            {/* Gross salary */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                {t('employee.calculator.salary')}
              </label>
              <SliderInput min={15000} max={200000} step={500} value={salario} onChange={setSalario} />
            </div>

            {/* Region */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                {t('employee.calculator.region')}
              </label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full rounded border px-3 py-2"
              >
                {regions.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>

            {/* Pagas */}
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">
                {t('employee.calculator.pagas')}
              </label>
              <div className="flex gap-4">
                {[12, 14].map((n) => (
                  <label key={n} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="pagas"
                      checked={numPagas === n}
                      onChange={() => setNumPagas(n)}
                      className="accent-blue-600"
                    />
                    <span className="text-sm text-gray-700">{n} {t('employee.calculator.pagas_label')}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Expandable advanced section placeholder */}
          <details className="mt-6">
            <summary className="cursor-pointer text-sm font-medium text-blue-600">
              {t('employee.calculator.advanced')}
            </summary>
            <p className="mt-3 text-sm text-gray-400">{t('employee.calculator.advanced_placeholder')}</p>
          </details>
        </InputCard>

        {/* Results */}
        {result && !loading && (
          <div className="mt-12 space-y-10">
            <ResultHero
              value={result.salario_neto_mensual}
              label={t('employee.result.net_monthly')}
              subtitle={`${fmt(result.salario_neto_anual)} ${t('employee.result.per_year')}`}
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

            <BreakdownBar
              items={result.breakdown}
              total={salario}
            />

            <ResultHero
              value={result.coste_total_empresa_anual}
              label={t('employee.result.employer_cost')}
              subtitle={t('employee.result.employer_cost_subtitle')}
            />

            {/* Employer Breakdown Bar */}
            {result.employer_breakdown && (
              <div className="mt-4">
                <p className="mb-2 text-sm font-medium text-gray-500">{t('employee.result.employer_breakdown_title')}</p>
                <BreakdownBar items={result.employer_breakdown} total={result.coste_total_empresa_anual} />
              </div>
            )}

            <IncomeBreakdownPie items={result.breakdown} title={t('employee.result.breakdown')} />

            {result?.irpf_detalle && (
              <details className="mt-10 group">
                <summary className="cursor-pointer text-sm font-semibold text-blue-700 hover:text-blue-800">
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
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
          </div>
        )}

        {/* Learn more */}
        <div className="mt-16 space-y-4">
          <LearnMore titleKey="employee.learn.irpf.title" contentKey="employee.learn.irpf.content" />
          <LearnMore titleKey="employee.learn.pagas.title" contentKey="employee.learn.pagas.content" />
          <LearnMore titleKey="employee.learn.employer.title" contentKey="employee.learn.employer.content" />
        </div>

        {/* Links */}
        <nav className="mt-16 flex flex-wrap gap-4 border-t pt-8 text-sm">
          <Link to="/autonomo" className="text-blue-600 hover:underline">{t('nav.link.autonomo')}</Link>
          <Link to="/sl" className="text-blue-600 hover:underline">{t('nav.link.sl')}</Link>
          <Link to="/comparador" className="text-blue-600 hover:underline">{t('nav.link.comparator')}</Link>
        </nav>
      </article>
    </>
  );
}
