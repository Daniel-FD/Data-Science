import { useMemo, useState } from "react";

const entries = [
  { term: "Base imponible", def: "Magnitud sobre la que se aplica un tipo impositivo." },
  { term: "Tipo marginal", def: "Tipo aplicado al último euro de base." },
  { term: "Tipo efectivo", def: "Tipo medio real pagado." },
  { term: "Plusvalía", def: "Beneficio generado por la inversión." },
  { term: "Dividendo", def: "Distribución de beneficios de una empresa." },
  { term: "Gestoría", def: "Servicio de gestión contable y fiscal." }
];

const Glossary = () => {
  const [query, setQuery] = useState("");
  const filtered = useMemo(
    () => entries.filter((e) => e.term.toLowerCase().includes(query.toLowerCase())),
    [query]
  );

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Glosario</h1>
      <input
        className="w-full rounded border px-3 py-2"
        placeholder="Buscar término"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="space-y-2">
        {filtered.map((entry) => (
          <div key={entry.term} className="rounded border bg-white p-3">
            <div className="font-medium">{entry.term}</div>
            <div className="text-sm text-slate-600">{entry.def}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Glossary;
