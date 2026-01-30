import { ScenarioResult } from "../api/simulator";
import { useTranslation } from "react-i18next";

const formatCurrency = (value: number, locale: string) =>
  new Intl.NumberFormat(locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);

type Props = {
  data: Record<string, ScenarioResult | undefined>;
};

const MetricsCards = ({ data }: Props) => {
  const { i18n } = useTranslation();

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {Object.entries(data).map(([label, result]) => (
        <div key={label} className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="text-sm text-slate-500">{label}</div>
          <div className="mt-2 text-xl font-semibold">
            {result ? formatCurrency(result.renta_mensual_neta, i18n.language) : "—"}
          </div>
          <div className="mt-1 text-sm text-slate-500">Renta mensual neta</div>
        </div>
      ))}
    </div>
  );
};

export default MetricsCards;
