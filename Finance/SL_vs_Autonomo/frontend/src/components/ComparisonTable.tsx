import { useTranslation } from "react-i18next";

/* eslint-disable @typescript-eslint/no-explicit-any */
interface ComparisonTableProps {
  data: { employee: any; autonomo: any; sl: any };
  highlight?: string;
}

const fmtCur = (v: number): string =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(v);

const fmtPct = (v: number): string =>
  new Intl.NumberFormat("es-ES", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(v);

/** Normalize each regime's raw API response into a common shape for the table. */
function normalize(regime: string, raw: any) {
  if (regime === "employee") {
    return {
      ingreso_bruto: raw.salario_bruto_anual ?? 0,
      seguridad_social: raw.ss_empleado_anual ?? 0,
      irpf: raw.irpf_anual ?? 0,
      impuesto_sociedades: 0,
      neto_anual: raw.salario_neto_anual ?? 0,
      neto_mensual: raw.salario_neto_mensual ?? 0,
      tipo_efectivo: raw.tipo_efectivo_total ?? 0,
    };
  }
  if (regime === "autonomo") {
    return {
      ingreso_bruto: raw.facturacion_anual ?? 0,
      seguridad_social: raw.cuota_autonomos_anual ?? 0,
      irpf: raw.irpf_anual ?? 0,
      impuesto_sociedades: 0,
      neto_anual: raw.neto_anual ?? 0,
      neto_mensual: raw.neto_mensual ?? 0,
      tipo_efectivo: raw.tipo_efectivo_total ?? 0,
    };
  }
  // sl
  return {
    ingreso_bruto: raw.facturacion_anual ?? 0,
    seguridad_social: raw.ss_empleado_anual ?? 0,
    irpf: (raw.irpf_salario ?? 0) + (raw.irpf_dividendos ?? 0),
    impuesto_sociedades: raw.is_pagado ?? 0,
    neto_anual: raw.neto_total_anual ?? 0,
    neto_mensual: raw.neto_total_mensual ?? 0,
    tipo_efectivo: raw.tipo_efectivo ?? 0,
  };
}

type NormalizedRow = ReturnType<typeof normalize>;

type RowDef = {
  labelKey: string;
  field: keyof NormalizedRow;
  format: "currency" | "percent";
};

const rows: RowDef[] = [
  { labelKey: "table.ingreso_bruto", field: "ingreso_bruto", format: "currency" },
  { labelKey: "table.seguridad_social", field: "seguridad_social", format: "currency" },
  { labelKey: "table.irpf", field: "irpf", format: "currency" },
  { labelKey: "table.impuesto_sociedades", field: "impuesto_sociedades", format: "currency" },
  { labelKey: "table.neto_anual", field: "neto_anual", format: "currency" },
  { labelKey: "table.neto_mensual", field: "neto_mensual", format: "currency" },
  { labelKey: "table.tipo_efectivo", field: "tipo_efectivo", format: "percent" },
];

const regimeKeys = ["employee", "autonomo", "sl"] as const;
const regimeLabels: Record<string, string> = {
  employee: "Asalariado",
  autonomo: "Autónomo",
  sl: "SL",
};

const ComparisonTable = ({ data, highlight }: ComparisonTableProps) => {
  const { t } = useTranslation();

  const normalized: Record<string, NormalizedRow> = {
    employee: normalize("employee", data.employee),
    autonomo: normalize("autonomo", data.autonomo),
    sl: normalize("sl", data.sl),
  };

  const formatValue = (value: number, format: "currency" | "percent") =>
    format === "currency" ? fmtCur(value) : fmtPct(value);

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[500px] text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="py-3 pr-4 text-left font-semibold text-gray-700">
              {t("table.metric", "Métrica")}
            </th>
            {regimeKeys.map((key) => (
              <th
                key={key}
                className={`py-3 px-4 text-right font-semibold ${
                  highlight === key ? "bg-accent-50 text-accent-700" : "text-gray-700"
                }`}
              >
                {regimeLabels[key]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.field} className="border-b border-gray-100">
              <td className="py-2.5 pr-4 text-gray-600">
                {t(row.labelKey, row.labelKey)}
              </td>
              {regimeKeys.map((key) => (
                <td
                  key={key}
                  className={`py-2.5 px-4 text-right tabular-nums ${
                    highlight === key ? "bg-accent-50 font-medium text-accent-700" : "text-gray-900"
                  }`}
                >
                  {formatValue(normalized[key][row.field], row.format)}
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
