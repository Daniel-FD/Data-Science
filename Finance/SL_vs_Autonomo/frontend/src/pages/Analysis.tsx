import { useState, useEffect, useRef, useCallback } from "react";
import PageMeta from "../components/PageMeta";
import katex from "katex";
import "katex/dist/katex.min.css";
import { fetchInvestmentOptimizer } from "../api/client";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip,
  ResponsiveContainer, Legend, BarChart, Bar, LineChart, Line, ReferenceLine,
} from "recharts";

// ---------------------------------------------------------------------------
// KaTeX helpers
// ---------------------------------------------------------------------------
function Tex({ children, display = false }: { children: string; display?: boolean }) {
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (ref.current) {
      katex.render(children, ref.current, { displayMode: display, throwOnError: false });
    }
  }, [children, display]);
  return <span ref={ref} />;
}

function BlockTex({ children }: { children: string }) {
  return <div className="overflow-x-auto my-3"><Tex display>{children}</Tex></div>;
}

const fmtCur = (v: number) =>
  new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(v);
const fmtPct = (v: number) => `${(v * 100).toFixed(1)}%`;

// ---------------------------------------------------------------------------
// Section helpers
// ---------------------------------------------------------------------------
function Section({ id, num, title, children }: { id: string; num: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-24 mt-12">
      <h2 className="text-xl font-bold text-gray-900 mb-4 border-b pb-2">
        <span className="text-blue-600 mr-2">{num}</span>{title}
      </h2>
      {children}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Interactive analysis data generator
// ---------------------------------------------------------------------------
function useAnalysisData() {
  const [data, setData] = useState<any>(null);
  const [billings, setBillings] = useState<number[]>([]);

  useEffect(() => {
    async function fetchAll() {
      const bills = [40000, 60000, 80000, 100000, 120000, 150000, 200000, 250000, 300000];
      setBillings(bills);
      const results: any[] = [];
      for (const f of bills) {
        try {
          const r = await fetchInvestmentOptimizer({
            facturacion_anual: f,
            gastos_personales_mensuales: 2000,
            region: "Madrid",
            rentabilidad_anual: 0.07,
            anos: 20,
            capital_inicial: 0,
            gastos_deducibles_pct: 0.10,
            gastos_empresa: 2000,
            gastos_gestoria: 3000,
            tarifa_plana: false,
          });
          results.push({ facturacion: f, ...r });
        } catch {
          /* skip failed */
        }
      }
      setData(results);
    }
    fetchAll();
  }, []);

  return { data, billings };
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export default function Analysis() {
  const { data } = useAnalysisData();

  // Prepare chart data
  const crossoverData = data?.map((d: any) => ({
    facturacion: d.facturacion / 1000,
    autonomo: d.autonomo?.capital_final_neto ?? 0,
    sl_optimo: d.sl_key_scenarios?.optimo?.total_neto ?? 0,
    sl_dividendos: d.sl_key_scenarios?.todo_dividendos?.total_neto ?? 0,
    ventaja_sl: ((d.sl_key_scenarios?.optimo?.total_neto ?? 0) - (d.autonomo?.capital_final_neto ?? 0)),
  })) ?? [];

  const taxRateData = data?.map((d: any) => ({
    facturacion: d.facturacion / 1000,
    tipo_auto: d.autonomo?.detalle_fiscal?.tipo_efectivo ?? 0,
    tipo_sl: d.sl_key_scenarios?.optimo?.detalle_fiscal?.tipo_efectivo ?? 0,
    salario_optimo: d.optimal?.salario_optimo ?? d.facturacion,
  })) ?? [];

  const investmentSplitData = data?.map((d: any) => {
    const opt = d.sl_key_scenarios?.optimo;
    return {
      facturacion: d.facturacion / 1000,
      inv_personal: (opt?.inversion_personal_mensual ?? 0) * 12,
      inv_empresa: (opt?.inversion_empresa_mensual ?? 0) * 12,
      inv_auto: (d.autonomo?.inversion_mensual ?? 0) * 12,
    };
  }) ?? [];

  const rescueTaxData = data?.map((d: any) => {
    const opt = d.sl_key_scenarios?.optimo;
    return {
      facturacion: d.facturacion / 1000,
      imp_auto: d.autonomo?.impuestos_rescate ?? 0,
      imp_sl_personal: opt?.impuestos_personal ?? 0,
      imp_sl_empresa: opt?.impuestos_empresa ?? 0,
    };
  }) ?? [];

  const fireData = data?.map((d: any) => {
    const opt = d.sl_key_scenarios?.optimo;
    return {
      facturacion: d.facturacion / 1000,
      fire_auto: (d.autonomo?.rescate_fire?.renta_neta_mensual ?? 0),
      fire_sl: (opt?.rescate_fire?.renta_neta_mensual ?? 0),
    };
  }) ?? [];

  return (
    <>
      <PageMeta
        titleKey="Análisis: Autónomo vs SL"
        descriptionKey="Estudio comparativo sobre la optimalidad del régimen fiscal para autónomos y SL en España."
      />
      <article className="mx-auto max-w-4xl px-4 py-12 text-gray-700">

        {/* ============================================================ */}
        {/* TITLE / ABSTRACT */}
        {/* ============================================================ */}
        <header className="mb-10 border-b pb-8">
          <p className="text-sm text-blue-600 font-medium uppercase tracking-wide mb-2">Estudio Comparativo</p>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 leading-tight">
            Optimalidad del Régimen Fiscal para Trabajadores Independientes en España:
            Autónomo vs. Sociedad Limitada
          </h1>
          <p className="mt-4 text-sm text-gray-500">
            Un análisis cuantitativo de la acumulación patrimonial a largo plazo bajo diferentes estrategias fiscales,
            considerando la legislación vigente en 2025.
          </p>
        </header>

        {/* Abstract */}
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-6 mb-8">
          <h2 className="font-bold text-blue-800 mb-2">Resumen</h2>
          <p className="text-sm leading-relaxed text-blue-900">
            Este estudio analiza la decisión clave que enfrentan los trabajadores independientes en España:
            operar como autónomo (persona física) o constituir una Sociedad Limitada (SL).
            Mediante simulación numérica a 20 años con datos fiscales reales de 2025, evaluamos
            el patrimonio neto acumulado considerando: diferencias en tipos impositivos (IRPF vs IS),
            el efecto del <em>tax drag</em> corporativo sobre rendimientos de inversión, la doble imposición
            al distribuir dividendos, y la fiscalidad al rescate del patrimonio.
            Los resultados muestran que <strong>la SL con salario optimizado domina a partir de ~50-60K€ de facturación</strong>,
            con ventajas crecientes a mayor nivel de ingresos, pero que la ventaja real es menor de lo que
            sugiere la diferencia de tipos nominales debido a la doble imposición y el IS sobre rendimientos.
          </p>
        </div>

        {/* TOC */}
        <nav className="rounded-xl border border-gray-200 bg-gray-50 p-5 mb-8">
          <h2 className="font-semibold text-gray-800 mb-3">Índice</h2>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-700">
            {[
              ["introduccion", "Introducción y Motivación"],
              ["marco", "Marco Fiscal"],
              ["metodologia", "Metodología"],
              ["resultados", "Resultados"],
              ["crossover", "Punto de Crossover"],
              ["tax-drag", "Tax Drag Corporativo"],
              ["rescate", "Fiscalidad al Rescate"],
              ["fire", "Independencia Financiera (FIRE)"],
              ["recomendaciones", "Recomendaciones Prácticas"],
              ["limitaciones", "Limitaciones"],
            ].map(([id, label]) => (
              <li key={id}><a href={`#${id}`} className="hover:underline">{label}</a></li>
            ))}
          </ol>
        </nav>

        {/* ============================================================ */}
        {/* 1. INTRODUCTION */}
        {/* ============================================================ */}
        <Section id="introduccion" num="1" title="Introducción y Motivación">
          <p className="text-sm leading-relaxed mb-3">
            En España, un profesional independiente que factura a clientes tiene dos opciones principales
            para estructurar su actividad: darse de alta como <strong>autónomo</strong> (empresario individual) o constituir una
            <strong> Sociedad Limitada</strong> (SL). La elección tiene implicaciones profundas en la carga fiscal,
            la capacidad de ahorro, y la acumulación patrimonial a largo plazo.
          </p>
          <p className="text-sm leading-relaxed mb-3">
            La intuición habitual es simple: "el autónomo paga hasta el 47% de IRPF; la SL paga el 21-25% de Sociedades".
            Sin embargo, esta comparación es <strong>incompleta y engañosa</strong> por tres razones fundamentales:
          </p>
          <ol className="text-sm list-decimal pl-5 space-y-2 mb-3">
            <li>
              <strong>Doble imposición:</strong> El beneficio de la SL paga IS, y cuando se distribuye al socio como dividendos
              o salario, vuelve a tributar (IRPF ahorro o IRPF general). La carga combinada puede superar el 37%.
            </li>
            <li>
              <strong>Tax drag sobre inversiones:</strong> Los rendimientos de inversión dentro de la empresa pagan IS cada año,
              reduciendo la tasa de capitalización compuesta.
            </li>
            <li>
              <strong>Fiscalidad asimétrica al rescate:</strong> La inversión personal solo tributa sobre plusvalías;
              la inversión empresarial tributa sobre el capital total al distribuirse como dividendos.
            </li>
          </ol>
          <p className="text-sm leading-relaxed">
            Este análisis cuantifica estos tres efectos y determina bajo qué condiciones cada régimen es óptimo.
          </p>
        </Section>

        {/* ============================================================ */}
        {/* 2. MARCO FISCAL */}
        {/* ============================================================ */}
        <Section id="marco" num="2" title="Marco Fiscal (2025)">
          <p className="text-sm leading-relaxed mb-3">
            Resumimos las diferencias clave entre ambos regímenes:
          </p>

          <div className="overflow-x-auto my-4">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2 text-left">Concepto</th>
                  <th className="border px-3 py-2 text-center">Autónomo</th>
                  <th className="border px-3 py-2 text-center">SL + Administrador</th>
                </tr>
              </thead>
              <tbody className="text-xs">
                <tr><td className="border px-3 py-1.5 font-medium">Impuesto sobre beneficios</td><td className="border px-3 py-1.5 text-center">IRPF general (19-47%)</td><td className="border px-3 py-1.5 text-center">IS (21-22% micro)</td></tr>
                <tr><td className="border px-3 py-1.5 font-medium">Seguridad Social</td><td className="border px-3 py-1.5 text-center">Cuota fija por tramos (230-590€/mes)</td><td className="border px-3 py-1.5 text-center">SS empleado (~6,5%) + SS empresa (~30,6%)</td></tr>
                <tr><td className="border px-3 py-1.5 font-medium">Distribución de beneficios</td><td className="border px-3 py-1.5 text-center">Directa (ya tributó)</td><td className="border px-3 py-1.5 text-center">Dividendos: IRPF ahorro (19-30%)</td></tr>
                <tr><td className="border px-3 py-1.5 font-medium">Rendimientos de inversión</td><td className="border px-3 py-1.5 text-center">No tributan hasta venta</td><td className="border px-3 py-1.5 text-center">IS cada año sobre rendimientos</td></tr>
                <tr><td className="border px-3 py-1.5 font-medium">Rescate inversión</td><td className="border px-3 py-1.5 text-center">IRPF ahorro solo plusvalías</td><td className="border px-3 py-1.5 text-center">IRPF ahorro sobre todo (dividendos)</td></tr>
                <tr><td className="border px-3 py-1.5 font-medium">Deducciones trabajo</td><td className="border px-3 py-1.5 text-center">No (gastos deducibles propios)</td><td className="border px-3 py-1.5 text-center">2.000€ + reducción trabajo</td></tr>
                <tr><td className="border px-3 py-1.5 font-medium">Costes fijos</td><td className="border px-3 py-1.5 text-center">Mínimos</td><td className="border px-3 py-1.5 text-center">Gestoría (~3.000€/año) + gastos</td></tr>
              </tbody>
            </table>
          </div>
        </Section>

        {/* ============================================================ */}
        {/* 3. METODOLOGÍA */}
        {/* ============================================================ */}
        <Section id="metodologia" num="3" title="Metodología">
          <p className="text-sm leading-relaxed mb-3">
            Para cada nivel de facturación <Tex>{"F \\in [40\\text{K}, 300\\text{K}]"}</Tex>, simulamos:
          </p>
          <ol className="text-sm list-decimal pl-5 space-y-1 mb-3">
            <li>Cálculo del neto disponible después de impuestos y gastos personales (2.000€/mes).</li>
            <li>Inversión del excedente durante 20 años a una rentabilidad del 7% anual.</li>
            <li>Para la SL: optimización del salario del administrador mediante barrido (50 puntos) para maximizar el capital neto final.</li>
            <li>Cálculo de impuestos al rescate: plusvalías (personal) y dividendos (empresa).</li>
          </ol>

          <p className="text-sm leading-relaxed mb-3">Parámetros fijos:</p>
          <div className="overflow-x-auto my-3">
            <table className="text-sm border">
              <tbody>
                <tr><td className="border px-3 py-1">Gastos personales</td><td className="border px-3 py-1 font-mono">2.000 €/mes</td></tr>
                <tr><td className="border px-3 py-1">Gastos deducibles autónomo</td><td className="border px-3 py-1 font-mono">10%</td></tr>
                <tr><td className="border px-3 py-1">Gastos empresa SL</td><td className="border px-3 py-1 font-mono">2.000 €/año</td></tr>
                <tr><td className="border px-3 py-1">Gestoría SL</td><td className="border px-3 py-1 font-mono">3.000 €/año</td></tr>
                <tr><td className="border px-3 py-1">Rentabilidad</td><td className="border px-3 py-1 font-mono">7% anual</td></tr>
                <tr><td className="border px-3 py-1">Horizonte</td><td className="border px-3 py-1 font-mono">20 años</td></tr>
                <tr><td className="border px-3 py-1">Región</td><td className="border px-3 py-1 font-mono">Madrid</td></tr>
                <tr><td className="border px-3 py-1">Tipo empresa</td><td className="border px-3 py-1 font-mono">Micro (&lt;1M€)</td></tr>
              </tbody>
            </table>
          </div>
        </Section>

        {/* ============================================================ */}
        {/* 4. RESULTADOS */}
        {/* ============================================================ */}
        <Section id="resultados" num="4" title="Resultados Principales">
          {!data ? (
            <div className="flex items-center justify-center py-12">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
              <span className="ml-3 text-sm text-gray-500">Calculando escenarios...</span>
            </div>
          ) : (
            <>
              <p className="text-sm leading-relaxed mb-4">
                La siguiente gráfica muestra el <strong>capital neto acumulado</strong> (después de todos los impuestos, incluido el rescate)
                para cada nivel de facturación:
              </p>

              {/* Main crossover chart */}
              <div className="rounded-xl border p-4 bg-white mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Figura 1: Capital neto tras 20 años por nivel de facturación
                </h3>
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={crossoverData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="facturacion" tickFormatter={(v) => `${v}K`} label={{ value: "Facturación (K€)", position: "insideBottom", offset: -5 }} />
                    <YAxis tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
                    <RTooltip formatter={(v: number) => fmtCur(v)} labelFormatter={(l) => `Facturación: ${l}K€`} />
                    <Legend />
                    <Area type="monotone" dataKey="autonomo" name="Autónomo" stroke="#16a34a" fill="#bbf7d0" strokeWidth={2} />
                    <Area type="monotone" dataKey="sl_optimo" name="SL Óptimo" stroke="#7c3aed" fill="#ddd6fe" strokeWidth={2} />
                    <Area type="monotone" dataKey="sl_dividendos" name="SL Dividendos" stroke="#a855f7" fill="#f3e8ff" strokeWidth={1} strokeDasharray="5 5" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Advantage chart */}
              <div className="rounded-xl border p-4 bg-white mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Figura 2: Ventaja neta de SL óptimo vs Autónomo
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={crossoverData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="facturacion" tickFormatter={(v) => `${v}K`} />
                    <YAxis tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
                    <RTooltip formatter={(v: number) => fmtCur(v)} labelFormatter={(l) => `${l}K€`} />
                    <ReferenceLine y={0} stroke="#666" />
                    <Bar dataKey="ventaja_sl" name="Ventaja SL" fill="#7c3aed" />
                  </BarChart>
                </ResponsiveContainer>
                <p className="text-xs text-gray-500 mt-2">
                  Valores positivos = SL es mejor. Valores negativos = autónomo es mejor.
                </p>
              </div>

              {/* Numerical results table */}
              <div className="overflow-x-auto my-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Tabla 1: Resultados numéricos</h3>
                <table className="w-full text-xs border">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border px-2 py-1.5">Facturación</th>
                      <th className="border px-2 py-1.5 text-right">Auto Neto</th>
                      <th className="border px-2 py-1.5 text-right">SL Óptimo Neto</th>
                      <th className="border px-2 py-1.5 text-right">Salario Óptimo</th>
                      <th className="border px-2 py-1.5 text-right">Ventaja SL</th>
                      <th className="border px-2 py-1.5 text-center">Ganador</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.map((d: any) => {
                      const autoNeto = d.autonomo?.capital_final_neto ?? 0;
                      const slNeto = d.sl_key_scenarios?.optimo?.total_neto ?? 0;
                      const ventaja = slNeto - autoNeto;
                      return (
                        <tr key={d.facturacion}>
                          <td className="border px-2 py-1 font-mono">{fmtCur(d.facturacion)}</td>
                          <td className="border px-2 py-1 text-right font-mono">{fmtCur(autoNeto)}</td>
                          <td className="border px-2 py-1 text-right font-mono">{fmtCur(slNeto)}</td>
                          <td className="border px-2 py-1 text-right font-mono">{fmtCur(d.optimal?.salario_optimo ?? 0)}</td>
                          <td className={`border px-2 py-1 text-right font-mono ${ventaja >= 0 ? "text-green-700" : "text-red-600"}`}>
                            {ventaja >= 0 ? "+" : ""}{fmtCur(ventaja)}
                          </td>
                          <td className={`border px-2 py-1 text-center font-bold ${ventaja >= 0 ? "text-purple-700" : "text-green-700"}`}>
                            {ventaja >= 0 ? "SL" : "Auto"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </Section>

        {/* ============================================================ */}
        {/* 5. CROSSOVER */}
        {/* ============================================================ */}
        <Section id="crossover" num="5" title="Punto de Crossover">
          <p className="text-sm leading-relaxed mb-3">
            El <strong>punto de crossover</strong> es el nivel de facturación a partir del cual la SL supera al autónomo en patrimonio neto acumulado.
          </p>
          {data && (
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-5 mb-4">
              <p className="text-sm text-blue-900">
                Con los parámetros de referencia (Madrid, 10% gastos deducibles, 2.000€/mes gastos personales, 7% rentabilidad, 20 años),
                el crossover se sitúa aproximadamente en:
              </p>
              <p className="text-2xl font-bold text-blue-800 mt-2">
                {(() => {
                  const cross = crossoverData.find((d: any) => d.ventaja_sl > 0);
                  return cross ? `~${cross.facturacion}K€ de facturación anual` : "No encontrado en el rango analizado";
                })()}
              </p>
            </div>
          )}
          <p className="text-sm leading-relaxed mb-3">
            <strong>Factores que desplazan el crossover hacia la izquierda</strong> (SL favorable antes):
          </p>
          <ul className="text-sm list-disc pl-5 space-y-1 mb-3">
            <li>Comunidades con IRPF autonómico alto (Cataluña, Valencia).</li>
            <li>Menores gastos deducibles como autónomo.</li>
            <li>Mayor horizonte temporal (el diferimiento fiscal de la SL tiene más tiempo para componer).</li>
          </ul>
          <p className="text-sm leading-relaxed">
            <strong>Factores que desplazan el crossover hacia la derecha</strong> (autónomo favorable más tiempo):
          </p>
          <ul className="text-sm list-disc pl-5 space-y-1">
            <li>Comunidades con IRPF bajo (Madrid).</li>
            <li>Altos gastos deducibles como autónomo.</li>
            <li>Tarifa plana de nuevos autónomos.</li>
            <li>Altos costes de gestoría o empresa.</li>
          </ul>
        </Section>

        {/* ============================================================ */}
        {/* 6. TAX DRAG */}
        {/* ============================================================ */}
        <Section id="tax-drag" num="6" title="Tax Drag Corporativo">
          <p className="text-sm leading-relaxed mb-3">
            El <em>tax drag</em> es la penalización sobre la rentabilidad compuesta causada por tributar anualmente sobre los rendimientos.
            La inversión personal no sufre este efecto (los impuestos se difieren hasta la venta).
          </p>

          <BlockTex>{String.raw`r_{\text{efectiva}} = r \times (1 - t_{\text{IS}}) \approx 7\% \times (1 - 21\%) = 5{,}53\%`}</BlockTex>

          {data && investmentSplitData.length > 0 && (
            <div className="rounded-xl border p-4 bg-white mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Figura 3: Inversión anual por canal (SL Óptimo vs Autónomo)
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={investmentSplitData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="facturacion" tickFormatter={(v) => `${v}K`} />
                  <YAxis tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
                  <RTooltip formatter={(v: number) => fmtCur(v)} labelFormatter={(l) => `${l}K€`} />
                  <Legend />
                  <Bar dataKey="inv_auto" name="Autónomo (personal)" fill="#16a34a" />
                  <Bar dataKey="inv_personal" name="SL personal" fill="#3b82f6" />
                  <Bar dataKey="inv_empresa" name="SL empresa" fill="#7c3aed" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          <p className="text-sm leading-relaxed mb-3">
            A 20 años, el impacto acumulado del tax drag es significativo:
          </p>

          <div className="overflow-x-auto my-3">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2">Horizonte</th>
                  <th className="border px-3 py-2 text-right">Capital Personal (7%)</th>
                  <th className="border px-3 py-2 text-right">Capital Empresa (5,53%)</th>
                  <th className="border px-3 py-2 text-right">Pérdida por Tax Drag</th>
                </tr>
              </thead>
              <tbody>
                {[10, 15, 20, 25, 30].map((years) => {
                  // Simple FV calculation for 1000/month
                  const calcFV = (rate: number, n: number) => {
                    let c = 0;
                    for (let i = 0; i < n; i++) c = c * (1 + rate) + 12000;
                    return c;
                  };
                  const personal = calcFV(0.07, years);
                  const empresa = calcFV(0.0553, years);
                  return (
                    <tr key={years}>
                      <td className="border px-3 py-1.5 font-mono">{years} años</td>
                      <td className="border px-3 py-1.5 text-right font-mono">{fmtCur(personal)}</td>
                      <td className="border px-3 py-1.5 text-right font-mono">{fmtCur(empresa)}</td>
                      <td className="border px-3 py-1.5 text-right font-mono text-red-600">
                        -{fmtPct(1 - empresa / personal)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <p className="text-xs text-gray-500 mt-1">Basado en aportación constante de 1.000€/mes.</p>
          </div>
        </Section>

        {/* ============================================================ */}
        {/* 7. FISCALIDAD AL RESCATE */}
        {/* ============================================================ */}
        <Section id="rescate" num="7" title="Fiscalidad al Rescate">
          <p className="text-sm leading-relaxed mb-3">
            La <strong>asimetría fiscal al rescate</strong> es uno de los factores más subestimados en la comparativa.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="rounded-lg border border-green-200 bg-green-50 p-4">
              <h4 className="font-semibold text-green-800 text-sm mb-2">Inversión Personal</h4>
              <p className="text-xs text-green-900">
                Base imponible = <strong>solo plusvalías</strong><br />
                Si invertiste 200K y valen 500K, tributan 300K.
              </p>
              <BlockTex>{String.raw`\text{Tax} = T_{\text{ahorro}}(K - A_{\text{total}})`}</BlockTex>
            </div>
            <div className="rounded-lg border border-purple-200 bg-purple-50 p-4">
              <h4 className="font-semibold text-purple-800 text-sm mb-2">Inversión Empresa</h4>
              <p className="text-xs text-purple-900">
                Base imponible = <strong>capital total</strong> (dividendos)<br />
                Si la empresa tiene 400K, tributan los 400K completos.
              </p>
              <BlockTex>{String.raw`\text{Tax} = T_{\text{ahorro}}(K_{\text{empresa}})`}</BlockTex>
            </div>
          </div>

          {data && rescueTaxData.length > 0 && (
            <div className="rounded-xl border p-4 bg-white mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Figura 4: Impuestos al rescate por nivel de facturación
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={rescueTaxData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="facturacion" tickFormatter={(v) => `${v}K`} />
                  <YAxis tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
                  <RTooltip formatter={(v: number) => fmtCur(v)} labelFormatter={(l) => `${l}K€`} />
                  <Legend />
                  <Bar dataKey="imp_auto" name="Autónomo (plusvalías)" fill="#16a34a" />
                  <Bar dataKey="imp_sl_personal" name="SL personal (plusvalías)" fill="#3b82f6" />
                  <Bar dataKey="imp_sl_empresa" name="SL empresa (dividendos)" fill="#dc2626" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Section>

        {/* ============================================================ */}
        {/* 8. FIRE */}
        {/* ============================================================ */}
        <Section id="fire" num="8" title="Independencia Financiera (FIRE)">
          <p className="text-sm leading-relaxed mb-3">
            La regla del 4% permite calcular una renta mensual sostenible. El tratamiento fiscal del retiro
            gradual es más favorable que el rescate total, ya que las bases imponibles anuales son menores
            y se mantienen en tramos más bajos del IRPF del ahorro.
          </p>

          {data && fireData.length > 0 && (
            <div className="rounded-xl border p-4 bg-white mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Figura 5: Renta FIRE neta mensual por nivel de facturación
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={fireData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="facturacion" tickFormatter={(v) => `${v}K`} />
                  <YAxis tickFormatter={(v) => `${(v/1000).toFixed(1)}K`} />
                  <RTooltip formatter={(v: number) => fmtCur(v)} labelFormatter={(l) => `${l}K€`} />
                  <Legend />
                  <Line type="monotone" dataKey="fire_auto" name="Autónomo" stroke="#16a34a" strokeWidth={2} dot />
                  <Line type="monotone" dataKey="fire_sl" name="SL Óptimo" stroke="#7c3aed" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          <p className="text-sm leading-relaxed">
            La ventaja del retiro gradual es doble:
            (1) se mantiene la inversión generando rendimientos, y
            (2) la base imponible anual es mucho menor, beneficiándose de los tramos bajos del IRPF del ahorro (19% hasta 6K€).
          </p>
        </Section>

        {/* ============================================================ */}
        {/* 9. RECOMENDACIONES */}
        {/* ============================================================ */}
        <Section id="recomendaciones" num="9" title="Recomendaciones Prácticas">
          <div className="space-y-4">
            <div className="rounded-lg border-l-4 border-green-500 bg-green-50 p-4">
              <h4 className="font-semibold text-green-800 text-sm">Facturación &lt; 50K€</h4>
              <p className="text-xs text-green-900 mt-1">
                <strong>Recomendación: Autónomo.</strong> La SL no compensa por los costes fijos (gestoría, constitución)
                y la carga fiscal total es similar o menor como autónomo. Aprovecha la tarifa plana si eres nuevo.
              </p>
            </div>

            <div className="rounded-lg border-l-4 border-amber-500 bg-amber-50 p-4">
              <h4 className="font-semibold text-amber-800 text-sm">Facturación 50-80K€</h4>
              <p className="text-xs text-amber-900 mt-1">
                <strong>Recomendación: Analizar caso particular.</strong> La ventaja de la SL existe pero es moderada.
                Depende mucho de la región, gastos deducibles, y horizonte temporal. Usa el simulador con tus datos reales.
              </p>
            </div>

            <div className="rounded-lg border-l-4 border-purple-500 bg-purple-50 p-4">
              <h4 className="font-semibold text-purple-800 text-sm">Facturación &gt; 80K€</h4>
              <p className="text-xs text-purple-900 mt-1">
                <strong>Recomendación: SL con salario optimizado.</strong> La ventaja es clara y crece con la facturación.
                La clave es encontrar el salario óptimo: ni demasiado alto (IRPF excesivo) ni demasiado bajo
                (todo tributa como dividendos + IS sobre rendimientos). El simulador calcula este punto exacto.
              </p>
            </div>

            <div className="rounded-lg border-l-4 border-blue-500 bg-blue-50 p-4">
              <h4 className="font-semibold text-blue-800 text-sm">Optimización del salario del administrador</h4>
              <p className="text-xs text-blue-900 mt-1">
                El salario óptimo <strong>no es el mínimo</strong> (como muchos asesores sugieren). Un salario demasiado bajo
                significa que todo el excedente queda en la empresa, sufriendo IS anual sobre rendimientos de inversión y
                tributando como dividendos al rescate. El óptimo típicamente está en el rango donde el tipo marginal del
                IRPF se acerca al coste fiscal combinado de IS + IRPF ahorro.
              </p>
            </div>

            <div className="rounded-lg border-l-4 border-gray-500 bg-gray-50 p-4">
              <h4 className="font-semibold text-gray-800 text-sm">Estrategia de rescate</h4>
              <p className="text-xs text-gray-700 mt-1">
                Siempre que sea posible, prefiere el <strong>retiro gradual (regla del 4%)</strong> al rescate de golpe.
                Las bases imponibles anuales menores se mantienen en los tramos bajos del IRPF del ahorro,
                resultando en un tipo efectivo significativamente menor.
              </p>
            </div>
          </div>
        </Section>

        {/* ============================================================ */}
        {/* 10. LIMITACIONES */}
        {/* ============================================================ */}
        <Section id="limitaciones" num="10" title="Limitaciones del Análisis">
          <ul className="text-sm list-disc pl-5 space-y-2">
            <li>
              <strong>Legislación estática:</strong> Asumimos que la legislación fiscal de 2025 se mantiene constante durante todo el horizonte.
              En la realidad, los tipos impositivos cambian frecuentemente.
            </li>
            <li>
              <strong>Inflación no modelada:</strong> Los importes son nominales. La rentabilidad real sería ~4-5% ajustada por inflación.
            </li>
            <li>
              <strong>Rendimientos constantes:</strong> Asumimos una rentabilidad fija del 7% anual, cuando en la práctica hay volatilidad significativa.
            </li>
            <li>
              <strong>Gastos simplificados:</strong> Los gastos de la SL y del autónomo se modelan como valores fijos, pero en la práctica dependen de la actividad.
            </li>
            <li>
              <strong>Sin planificación fiscal avanzada:</strong> No se modelan estrategias como retribución en especie, planes de pensiones de empleo,
              reserva de capitalización, o compensación de pérdidas.
            </li>
            <li>
              <strong>Régimen general:</strong> No se consideran regímenes especiales (Canarias REF, País Vasco/Navarra foral, ZEC, etc.).
              Sin embargo, el simulador sí incluye los tramos autonómicos de cada comunidad, incluyendo los sistemas forales.
            </li>
            <li>
              <strong>Rescate simplificado:</strong> Asumimos rescate total como dividendos. En la práctica, existen alternativas (disolución y liquidación,
              reducción de capital) con tratamiento fiscal diferente.
            </li>
          </ul>
        </Section>

        {/* Footer */}
        <div className="mt-16 rounded-lg border border-gray-200 bg-gray-50 p-5 text-sm text-gray-500">
          <p>
            <strong>Nota:</strong> Este análisis es orientativo y no constituye asesoramiento fiscal profesional.
            Las circunstancias individuales pueden variar significativamente. Consulta con un asesor fiscal cualificado
            antes de tomar decisiones sobre tu estructura fiscal.
          </p>
          <p className="mt-2">
            <strong>Metodología reproducible:</strong> Todos los cálculos se realizan en tiempo real usando el motor fiscal del simulador.
            Las fórmulas exactas están documentadas en la{" "}
            <a href="/formulas" className="text-blue-600 hover:underline">página de fórmulas</a>.
          </p>
        </div>
      </article>
    </>
  );
}
