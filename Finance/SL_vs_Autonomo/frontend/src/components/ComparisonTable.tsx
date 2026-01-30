import { ScenarioResult } from "../api/simulator";
import { useTranslation } from "react-i18next";

const formatCurrency = (value: number, locale: string) =>
  new Intl.NumberFormat(locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);

type Props = {
  data: Record<string, ScenarioResult | undefined>;
};

const ComparisonTable = ({ data }: Props) => {
  const { i18n } = useTranslation();
  const rows = [
    { label: "Capital neto", key: "capital_neto" },
    { label: "Impuestos rescate", key: "impuestos_rescate" },
    { label: "Renta anual neta", key: "renta_anual_neta" },
    { label: "Renta mensual neta", key: "renta_mensual_neta" },
  ];

  return (
    <div className="overflow-x-auto rounded-xl border bg-white">
      <table className="w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-2 text-left">Métrica</th>
            {Object.keys(data).map((label) => (
              <th key={label} className="px-4 py-2 text-left">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key} className="border-t">
              <td className="px-4 py-2 font-medium">{row.label}</td>
              {Object.values(data).map((result, idx) => (
                <td key={idx} className="px-4 py-2">
                  {result ? formatCurrency((result as any)[row.key], i18n.language) : "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ComparisonTable;
