const SensitivityHeatmap = ({ data }: { data: Array<{ x: number; y: number; value: number }> }) => {
  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="text-sm text-slate-500">Heatmap placeholder</div>
      <div className="mt-2 grid grid-cols-6 gap-2">
        {data.slice(0, 36).map((cell, idx) => (
          <div key={idx} className="h-10 rounded bg-sky-100 text-xs text-slate-700">
            {Math.round(cell.value)}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SensitivityHeatmap;
