const Explanations = () => {
  const items = [
    { title: "IRPF general vs ahorro", body: "El salario tributa en IRPF general, los dividendos y plusvalías en IRPF del ahorro." },
    { title: "Doble imposición", body: "Las sociedades pagan IS y luego el dividendo tributa en IRPF del ahorro." },
    { title: "Regla del 4%", body: "Estimación conservadora de renta anual sostenible sobre el capital." },
    { title: "Tarifa plana", body: "Cuota reducida para autónomos durante los primeros meses si se cumplen requisitos." },
    { title: "Tipo marginal vs efectivo", body: "El marginal aplica al último euro; el efectivo es el promedio real." }
  ];

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <details key={item.title} className="rounded border bg-white p-3">
          <summary className="cursor-pointer font-medium">{item.title}</summary>
          <p className="mt-2 text-sm text-slate-600">{item.body}</p>
        </details>
      ))}
    </div>
  );
};

export default Explanations;
