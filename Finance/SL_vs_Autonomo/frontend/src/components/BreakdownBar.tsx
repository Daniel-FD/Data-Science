interface BreakdownItem {
  label: string;
  amount: number;
  color: string;
}

interface BreakdownBarProps {
  items: BreakdownItem[];
  total: number;
}

const fmt = (v: number): string =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v);

const pct = (amount: number, total: number): string =>
  total > 0 ? `${((amount / total) * 100).toFixed(1)}%` : "0%";

const BreakdownBar = ({ items, total }: BreakdownBarProps) => {
  return (
    <div>
      {/* Stacked bar */}
      <div className="flex h-8 w-full overflow-hidden rounded-lg">
        {items.map((item, i) => {
          const width = total > 0 ? (item.amount / total) * 100 : 0;
          return (
            <div
              key={i}
              className="transition-all duration-300"
              style={{ width: `${width}%`, backgroundColor: item.color }}
              title={`${item.label}: ${fmt(item.amount)} (${pct(item.amount, total)})`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm text-gray-700">
        {items.map((item, i) => (
          <div key={i} className="flex items-center gap-2">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{ backgroundColor: item.color }}
            />
            <span>
              {item.label}: {fmt(item.amount)} ({pct(item.amount, total)})
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BreakdownBar;
