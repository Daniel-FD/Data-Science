const HowItWorks = () => {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Cómo funciona</h1>
      <p className="text-slate-600">
        Explicación paso a paso de cada escenario, cómo leer los resultados y cuándo considerar el cambio de estructura.
      </p>
      <div className="rounded-xl border bg-white p-4">
        <ol className="list-decimal space-y-2 pl-4 text-sm text-slate-600">
          <li>Se calcula el rendimiento neto y los impuestos correspondientes.</li>
          <li>Se simula la inversión anual con la rentabilidad esperada.</li>
          <li>Se calcula el rescate y la renta anual neta estimada.</li>
        </ol>
      </div>
    </div>
  );
};

export default HowItWorks;
