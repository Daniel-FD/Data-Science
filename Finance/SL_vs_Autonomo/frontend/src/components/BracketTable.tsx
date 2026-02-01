import { useTranslation } from 'react-i18next';

const fmtEur = (n: number) =>
  new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n);

const fmtPct = (n: number) => `${(n * 100).toFixed(1)}%`;

interface Bracket {
  from: number;
  to: number;
  rate: number;
  taxable: number;
  tax: number;
}

interface BracketTableProps {
  brackets: Bracket[];
  total: number;
  effectiveRate: number;
}

const COLORS = [
  'bg-blue-100', 'bg-blue-200', 'bg-blue-300', 'bg-blue-400',
  'bg-blue-500', 'bg-blue-600', 'bg-blue-700', 'bg-blue-800',
];

export default function BracketTable({ brackets, total, effectiveRate }: BracketTableProps) {
  const { t } = useTranslation();
  const maxTax = Math.max(...brackets.map((b) => b.tax), 1);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left">
            <th className="py-2 pr-3 font-medium text-gray-500">{t('brackets.range')}</th>
            <th className="py-2 px-3 font-medium text-gray-500 text-right">{t('brackets.rate')}</th>
            <th className="py-2 px-3 font-medium text-gray-500 text-right">{t('brackets.base')}</th>
            <th className="py-2 px-3 font-medium text-gray-500 text-right">{t('brackets.tax')}</th>
            <th className="py-2 pl-3 font-medium text-gray-500 w-32"></th>
          </tr>
        </thead>
        <tbody>
          {brackets.map((b, i) => {
            const colorIdx = Math.min(i, COLORS.length - 1);
            const barWidth = total > 0 ? (b.tax / maxTax) * 100 : 0;
            return (
              <tr key={i} className="border-b">
                <td className="py-2 pr-3 text-gray-700">
                  {fmtEur(b.from)} &ndash; {fmtEur(b.to)}
                </td>
                <td className="py-2 px-3 text-right font-medium text-gray-800">
                  {fmtPct(b.rate)}
                </td>
                <td className="py-2 px-3 text-right text-gray-600">
                  {fmtEur(b.taxable)}
                </td>
                <td className="py-2 px-3 text-right font-medium text-gray-800">
                  {fmtEur(b.tax)}
                </td>
                <td className="py-2 pl-3">
                  <div className="h-3 w-full rounded-full bg-gray-100">
                    <div
                      className={`h-3 rounded-full ${COLORS[colorIdx]}`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-gray-300">
            <td colSpan={3} className="py-3 pr-3 font-semibold text-gray-900">
              {t('brackets.total')}
            </td>
            <td className="py-3 px-3 text-right font-bold text-blue-700 text-base">
              {fmtEur(total)}
            </td>
            <td className="py-3 pl-3 text-right text-xs text-gray-500">
              {t('brackets.effective')}: {fmtPct(effectiveRate)}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
