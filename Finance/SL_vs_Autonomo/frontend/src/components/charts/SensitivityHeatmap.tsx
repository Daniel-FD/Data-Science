import { useMemo } from "react";
import { useTranslation } from "react-i18next";

interface SensitivityHeatmapProps {
  matrix: number[][];
  title: string;
  returnRates?: number[];
  years?: number[];
}

const formatCompact = (v: number) =>
  v >= 1_000_000
    ? `${(v / 1_000_000).toFixed(1)}M`
    : v >= 1_000
      ? `${(v / 1_000).toFixed(0)}k`
      : v.toFixed(0);

const SensitivityHeatmap = ({
  matrix,
  title,
  returnRates = [3, 4, 5, 6, 7, 8, 9, 10, 11],
  years = [5, 10, 15, 20, 25, 30],
}: SensitivityHeatmapProps) => {
  const { t } = useTranslation();

  if (!matrix || matrix.length === 0 || !Array.isArray(matrix[0])) return null;

  const { minVal, maxVal } = useMemo(() => {
    const flat = matrix.flat();
    return { minVal: Math.min(...flat), maxVal: Math.max(...flat) };
  }, [matrix]);

  const getCellColor = (value: number) => {
    const ratio = maxVal === minVal ? 0.5 : (value - minVal) / (maxVal - minVal);
    // Green gradient from light to dark
    const lightness = 92 - ratio * 52; // 92% (very light) to 40% (dark green)
    return `hsl(152, 60%, ${lightness}%)`;
  };

  const getTextColor = (value: number) => {
    const ratio = maxVal === minVal ? 0.5 : (value - minVal) / (maxVal - minVal);
    return ratio > 0.6 ? "#ffffff" : "#1e293b";
  };

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-lg font-semibold">{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="px-2 py-2 text-left text-xs font-medium text-slate-500">
                {t("charts.returnRate", "Rentabilidad")}
              </th>
              {years.map((y) => (
                <th key={y} className="px-2 py-2 text-center text-xs font-medium text-slate-500">
                  {y} {t("charts.yrs", "años")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, ri) => (
              <tr key={ri}>
                <td className="px-2 py-1 text-xs font-medium text-slate-600">
                  {returnRates[ri] ?? ri}%
                </td>
                {row.map((val, ci) => (
                  <td key={ci} className="px-1 py-1">
                    <div
                      className="flex h-10 items-center justify-center rounded-md text-xs font-medium"
                      style={{
                        backgroundColor: getCellColor(val),
                        color: getTextColor(val),
                      }}
                    >
                      {formatCompact(val)} &euro;
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SensitivityHeatmap;
