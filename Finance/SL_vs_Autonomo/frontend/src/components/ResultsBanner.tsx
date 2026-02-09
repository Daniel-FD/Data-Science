import { ScenarioResult } from "../api/simulator";
import { useTranslation } from "react-i18next";

const formatCurrency = (value: number, locale: string) =>
  new Intl.NumberFormat(locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);

type Props = {
  bestLabel: string;
  bestResult?: ScenarioResult;
  deltaMonthly?: number;
};

const ResultsBanner = ({ bestLabel, bestResult, deltaMonthly }: Props) => {
  const { t, i18n } = useTranslation();
  if (!bestResult) return null;

  return (
    <div className="rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 p-5 text-white shadow">
      <div className="text-sm uppercase tracking-wide">{t("results.best")}</div>
      <div className="mt-1 text-2xl font-semibold">{bestLabel}</div>
      <div className="mt-3 text-lg">
        {t("results.monthly")}: {formatCurrency(bestResult.renta_mensual_neta, i18n.language)}
      </div>
      {deltaMonthly !== undefined && (
        <div className="mt-1 text-sm opacity-90">Δ {formatCurrency(deltaMonthly, i18n.language)} / mes</div>
      )}
    </div>
  );
};

export default ResultsBanner;
