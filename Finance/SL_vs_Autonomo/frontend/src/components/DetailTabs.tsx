import { useState } from "react";
import { ScenarioResult } from "../api/simulator";

const DetailTabs = ({ data }: { data: Record<string, ScenarioResult | undefined> }) => {
  const [active, setActive] = useState(Object.keys(data)[0]);

  const result = data[active];

  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="flex flex-wrap gap-2">
        {Object.keys(data).map((key) => (
          <button
            key={key}
            onClick={() => setActive(key)}
            className={`rounded px-3 py-1 text-sm ${active === key ? "bg-sky-500 text-white" : "bg-slate-100"}`}
          >
            {key}
          </button>
        ))}
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2">Año</th>
              <th className="py-2">Aportación</th>
              <th className="py-2">Rentabilidad</th>
              <th className="py-2">Capital acumulado</th>
              <th className="py-2">Impuestos</th>
            </tr>
          </thead>
          <tbody>
            {result?.historial.map((r) => (
              <tr key={r.año} className="border-b">
                <td className="py-2">{r.año}</td>
                <td className="py-2">{Math.round(r.aportacion)}</td>
                <td className="py-2">{Math.round(r.rentabilidad)}</td>
                <td className="py-2">{Math.round(r.capital_acumulado)}</td>
                <td className="py-2">{Math.round(r.impuestos_pagados_año)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DetailTabs;
