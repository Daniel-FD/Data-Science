import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import Sidebar, { SidebarValues } from "../components/Sidebar";
import ResultsBanner from "../components/ResultsBanner";
import MetricsCards from "../components/MetricsCards";
import ComparisonTable from "../components/ComparisonTable";
import DetailTabs from "../components/DetailTabs";
import Explanations from "../components/Explanations";
import CapitalEvolution from "../components/charts/CapitalEvolution";
import MonthlyIncome from "../components/charts/MonthlyIncome";
import TaxWaterfall from "../components/charts/TaxWaterfall";
import EffectiveTaxRate from "../components/charts/EffectiveTaxRate";
import OptimalSalary from "../components/charts/OptimalSalary";
import TaxComposition from "../components/charts/TaxComposition";
import SensitivityHeatmap from "../components/charts/SensitivityHeatmap";
import CrossoverPoint from "../components/charts/CrossoverPoint";
import { fetchPresets, fetchRegions } from "../api/simulator";
import { useSimulation } from "../hooks/useSimulation";

const Simulator = () => {
  const { t } = useTranslation();
  const [regions, setRegions] = useState<string[]>([]);
  const [presets, setPresets] = useState<any[]>([]);
  const [values, setValues] = useState<SidebarValues>({
    region: "Galicia",
    facturacion: 105000,
    gastos_deducibles: 2000,
    gastos_personales: 12000,
    salario_administrador: 18000,
    gastos_gestoria: 3000,
    capital_inicial: 0,
    rentabilidad: 0.06,
    años: 10,
    tarifa_plana: true,
    company_age: 1,
    turnover: 105000,
    is_startup: true,
    aportacion_plan_pensiones: 5750,
  });

  const simulation = useSimulation();

  useEffect(() => {
    fetchRegions().then(setRegions).catch(() => setRegions([]));
    fetchPresets().then(setPresets).catch(() => setPresets([]));
  }, []);

  const onPreset = (preset: any) => {
    setValues({
      ...values,
      facturacion: preset.facturacion,
      gastos_deducibles: preset.gastos_deducibles,
      gastos_personales: preset.gastos_personales,
      turnover: preset.facturacion,
    });
  };

  const onSimulate = () => {
    simulation.mutate({
      facturacion: values.facturacion,
      gastos_deducibles: values.gastos_deducibles,
      gastos_personales: values.gastos_personales,
      años: values.años,
      rentabilidad: values.rentabilidad,
      capital_inicial: values.capital_inicial,
      region: values.region,
      tarifa_plana: values.tarifa_plana,
      salario_administrador: values.salario_administrador,
      gastos_gestoria: values.gastos_gestoria,
      aportacion_plan_pensiones: values.aportacion_plan_pensiones,
      turnover: values.turnover,
      company_age: values.company_age,
      is_startup: values.is_startup,
    });
  };

  const results = simulation.data;

  const scenarios = useMemo(() => {
    if (!results) return {};
    return {
      Autónomo: results.autonomo,
      "SL + Retención": results.sl_retencion,
      "SL + Dividendos": results.sl_dividendos,
      "SL Mixta": results.sl_mixto,
    } as Record<string, any>;
  }, [results]);

  const bestLabel = useMemo(() => {
    if (!results) return "";
    const entries = Object.entries(scenarios);
    if (!entries.length) return "";
    const best = entries.reduce((acc, cur) =>
      cur[1].renta_mensual_neta > acc[1].renta_mensual_neta ? cur : acc
    );
    return best[0];
  }, [results, scenarios]);

  const bestResult = bestLabel ? scenarios[bestLabel] : undefined;
  const simpleAutonomo = results?.autonomo;
  const simpleSL = results?.sl_retencion;
  const simpleDelta =
    simpleAutonomo && simpleSL ? simpleSL.renta_mensual_neta - simpleAutonomo.renta_mensual_neta : undefined;
  const simpleVerdict = useMemo(() => {
    if (simpleDelta === undefined) return "";
    if (simpleDelta > 0) return t("article.simple.verdict.sl");
    if (simpleDelta < 0) return t("article.simple.verdict.autonomo");
    return t("article.simple.verdict.neutral");
  }, [simpleDelta, t]);

  const effectiveRates = useMemo(
    () =>
      Array.from({ length: 15 }).map((_, idx) => ({
        income: 30000 + idx * 20000,
        rate: 0.15 + idx * 0.01,
      })),
    []
  );

  const heatmapData = useMemo(
    () =>
      Array.from({ length: 36 }).map((_, idx) => ({
        x: idx % 6,
        y: Math.floor(idx / 6),
        value: 100000 + idx * 1500,
      })),
    []
  );

  const cardClass = "rounded-lg border border-slate-200 bg-white p-4";

  return (
    <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_360px]">
      <article className="space-y-10">
        <header className="space-y-4">
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{t("article.kicker")}</p>
          <h1 className="text-3xl font-semibold leading-tight text-slate-900">{t("article.title")}</h1>
          <p className="text-base text-slate-600">{t("article.subtitle")}</p>
          <p className="text-xs text-slate-500">{t("article.meta")}</p>
          <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">
              {t("article.toc.title")}
            </p>
            <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-600">
              <a className="hover:text-slate-900" href="#objective">
                {t("article.toc.objective")}
              </a>
              <a className="hover:text-slate-900" href="#method">
                {t("article.toc.method")}
              </a>
              <a className="hover:text-slate-900" href="#assumptions">
                {t("article.toc.assumptions")}
              </a>
              <a className="hover:text-slate-900" href="#step-1">
                {t("article.toc.step1")}
              </a>
              <a className="hover:text-slate-900" href="#step-2">
                {t("article.toc.step2")}
              </a>
              <a className="hover:text-slate-900" href="#visuals">
                {t("article.toc.visuals")}
              </a>
              <a className="hover:text-slate-900" href="#details">
                {t("article.toc.details")}
              </a>
            </div>
          </div>
        </header>

        <section id="objective" className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700">
            {t("article.objective.title")}
          </h2>
          <p className="text-sm text-slate-600">{t("article.objective.body")}</p>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
            <li>{t("article.objective.points.1")}</li>
            <li>{t("article.objective.points.2")}</li>
            <li>{t("article.objective.points.3")}</li>
          </ul>
        </section>

        <section id="method" className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700">
            {t("article.method.title")}
          </h2>
          <p className="text-sm text-slate-600">{t("article.method.body")}</p>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
            <li>{t("article.method.points.1")}</li>
            <li>{t("article.method.points.2")}</li>
            <li>{t("article.method.points.3")}</li>
          </ul>
        </section>

        <section id="assumptions" className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700">
            {t("article.assumptions.title")}
          </h2>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
            <li>{t("article.assumptions.points.1")}</li>
            <li>{t("article.assumptions.points.2")}</li>
            <li>{t("article.assumptions.points.3")}</li>
          </ul>
        </section>

        <section id="step-1" className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700">
            {t("article.simple.title")}
          </h2>
          <p className="text-sm text-slate-600">{t("article.simple.body")}</p>
          <div className={cardClass}>
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">{t("article.simple.autonomo")}</span>
                <span className="font-semibold">
                  {simpleAutonomo ? simpleAutonomo.renta_mensual_neta.toFixed(2) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">{t("article.simple.sl")}</span>
                <span className="font-semibold">
                  {simpleSL ? simpleSL.renta_mensual_neta.toFixed(2) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between border-t pt-3 text-sm">
                <span className="text-slate-600">{t("article.simple.delta")}</span>
                <span className={`font-semibold ${simpleDelta && simpleDelta >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                  {simpleDelta !== undefined ? simpleDelta.toFixed(2) : "—"}
                </span>
              </div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{simpleVerdict}</p>
              <p className="text-xs text-slate-500">{t("article.simple.note")}</p>
            </div>
          </div>
        </section>

        <section id="step-2" className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700">
            {t("article.results.title")}
          </h2>
          <p className="text-sm text-slate-600">{t("article.results.body")}</p>

          <ResultsBanner
            bestLabel={bestLabel}
            bestResult={bestResult}
            deltaMonthly={
              bestResult && results ? bestResult.renta_mensual_neta - results.autonomo.renta_mensual_neta : undefined
            }
          />

          <MetricsCards data={scenarios} />

          <div className={cardClass}>
            <TaxWaterfall data={scenarios} />
          </div>

          <ComparisonTable data={scenarios as any} />
        </section>

        <section id="visuals" className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">
              {t("article.sections.capital")}
            </h3>
            <div className={cardClass}>
              <CapitalEvolution data={Object.entries(scenarios).map(([, s]) => ({ ano: 0, ...(s as any) })) as any} title={t("article.sections.capital")} />
            </div>
            <div className={cardClass}>
              <MonthlyIncome data={scenarios} />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">
              {t("article.sections.tax")}
            </h3>
            <div className={cardClass}>
              <EffectiveTaxRate data={effectiveRates} />
            </div>
            <div className={cardClass}>
              <OptimalSalary
                curve={(results?.optimal_salary_curve || []).map(p => ({ salary: p.salario, net_income: p.renta_mensual_neta, total_impuestos: p.impuestos_totales }))}
                optimalSalary={results?.optimal_salary || 0}
                title={t("article.sections.tax")}
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className={cardClass}>
                <TaxComposition result={results?.autonomo} />
              </div>
              <div className={cardClass}>
                <TaxComposition result={results?.sl_mixto} />
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">
              {t("article.sections.sensitivity")}
            </h3>
            <SensitivityHeatmap
              matrix={heatmapData.map(row => [row.value])}
              title={t("article.sections.sensitivity")}
            />
            <div className={cardClass}>
              <CrossoverPoint data={results?.crossover || []} />
            </div>
          </div>
        </section>

        <section id="details" className="space-y-4">
          <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-600">
            {t("article.sections.details")}
          </h3>
          <DetailTabs data={scenarios} />
          <Explanations />
        </section>

        <div className="text-xs text-slate-500">{t("disclaimer")}</div>
      </article>

      <aside className="space-y-4">
        <div className="sticky top-6">
          <Sidebar
            values={values}
            regions={regions.length ? regions : [values.region]}
            presets={presets}
            onChange={setValues}
            onPreset={onPreset}
            onSimulate={onSimulate}
          />
        </div>
      </aside>
    </div>
  );
};

export default Simulator;
