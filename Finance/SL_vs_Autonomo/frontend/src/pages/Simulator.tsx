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

  return (
    <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
      <Sidebar
        values={values}
        regions={regions.length ? regions : [values.region]}
        presets={presets}
        onChange={setValues}
        onPreset={onPreset}
        onSimulate={onSimulate}
      />

      <div className="space-y-6">
        <ResultsBanner
          bestLabel={bestLabel}
          bestResult={bestResult}
          deltaMonthly={
            bestResult && results ? bestResult.renta_mensual_neta - results.autonomo.renta_mensual_neta : undefined
          }
        />

        <MetricsCards data={scenarios} />

        <div className="rounded-xl border bg-white p-4">
          <TaxWaterfall data={scenarios} />
        </div>

        <ComparisonTable data={scenarios} />

        <div className="rounded-xl border bg-white p-4">
          <CapitalEvolution data={scenarios} />
        </div>

        <div className="rounded-xl border bg-white p-4">
          <MonthlyIncome data={scenarios} />
        </div>

        <div className="rounded-xl border bg-white p-4">
          <EffectiveTaxRate data={effectiveRates} />
        </div>

        <div className="rounded-xl border bg-white p-4">
          <OptimalSalary data={results?.optimal_salary_curve || []} />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border bg-white p-4">
            <TaxComposition result={results?.autonomo} />
          </div>
          <div className="rounded-xl border bg-white p-4">
            <TaxComposition result={results?.sl_mixto} />
          </div>
        </div>

        <SensitivityHeatmap data={heatmapData} />

        <div className="rounded-xl border bg-white p-4">
          <CrossoverPoint data={results?.crossover || []} />
        </div>

        <DetailTabs data={scenarios} />

        <Explanations />

        <div className="text-xs text-slate-500">{t("disclaimer")}</div>
      </div>
    </div>
  );
};

export default Simulator;
