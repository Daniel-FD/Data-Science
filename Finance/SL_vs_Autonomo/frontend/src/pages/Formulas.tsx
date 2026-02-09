import { useEffect, useRef } from "react";
import PageMeta from "../components/PageMeta";
import katex from "katex";
import "katex/dist/katex.min.css";

// ---------------------------------------------------------------------------
// Helper: render LaTeX string into a span
// ---------------------------------------------------------------------------
function Tex({ children, display = false }: { children: string; display?: boolean }) {
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (ref.current) {
      katex.render(children, ref.current, {
        displayMode: display,
        throwOnError: false,
      });
    }
  }, [children, display]);
  return <span ref={ref} />;
}

function BlockTex({ children }: { children: string }) {
  return (
    <div className="overflow-x-auto my-4">
      <Tex display>{children}</Tex>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section component
// ---------------------------------------------------------------------------
function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-24">
      <h2 className="text-xl font-bold text-gray-900 mt-10 mb-4 border-b pb-2">{title}</h2>
      {children}
    </section>
  );
}

function SubSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-6 mb-4">
      <h3 className="text-base font-semibold text-gray-800 mb-2">{title}</h3>
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function Formulas() {
  return (
    <>
      <PageMeta titleKey="Fórmulas y Metodología" descriptionKey="Documentación completa de las fórmulas fiscales utilizadas en el simulador." />
      <article className="mx-auto max-w-4xl px-4 py-12 text-gray-700">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Fórmulas y Metodología de Cálculo
          </h1>
          <p className="mt-4 leading-relaxed text-gray-600">
            Documentación completa de todas las fórmulas fiscales y financieras utilizadas en el simulador.
            Todos los datos corresponden a la <strong>legislación fiscal española vigente en 2025</strong>.
          </p>
        </header>

        {/* Table of contents */}
        <nav className="rounded-xl border border-gray-200 bg-gray-50 p-5 mb-8">
          <h2 className="font-semibold text-gray-800 mb-3">Índice</h2>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-700">
            {[
              ["irpf-ahorro", "IRPF del Ahorro"],
              ["irpf-general", "IRPF General (Renta del Trabajo)"],
              ["ss-empleado", "Seguridad Social — Empleado"],
              ["ss-empresa", "Seguridad Social — Empresa"],
              ["ss-autonomo", "Cuota de Autónomos"],
              ["is", "Impuesto de Sociedades"],
              ["autonomo", "Cálculo Autónomo"],
              ["sl", "Cálculo SL"],
              ["inversion-personal", "Simulación de Inversión Personal"],
              ["inversion-empresa", "Simulación de Inversión Empresa"],
              ["rescate", "Impuestos al Rescate"],
              ["fire", "Regla del 4% (FIRE)"],
            ].map(([id, label]) => (
              <li key={id}><a href={`#${id}`} className="hover:underline">{label}</a></li>
            ))}
          </ol>
        </nav>

        {/* ============================================================ */}
        {/* 1. IRPF AHORRO */}
        {/* ============================================================ */}
        <Section id="irpf-ahorro" title="1. IRPF del Ahorro (Rentas del Ahorro)">
          <p className="text-sm leading-relaxed mb-2">
            Se aplica a dividendos, plusvalías por venta de activos e intereses. Es un impuesto <strong>nacional</strong> (sin variación autonómica).
            Se calcula por tramos progresivos sobre la base imponible del ahorro.
          </p>

          <div className="overflow-x-auto my-4">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2 text-left">Tramo</th>
                  <th className="border px-3 py-2 text-right">Tipo (%)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["0 — 6.000 €", "19%"],
                  ["6.000 — 50.000 €", "21%"],
                  ["50.000 — 200.000 €", "23%"],
                  ["200.000 — 300.000 €", "27%"],
                  ["> 300.000 €", "30%"],
                ].map(([tramo, tipo]) => (
                  <tr key={tramo}>
                    <td className="border px-3 py-1.5">{tramo}</td>
                    <td className="border px-3 py-1.5 text-right font-mono">{tipo}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <BlockTex>{String.raw`T_{\text{ahorro}}(B) = \sum_{i=1}^{n} \min\!\bigl(\max(B - L_{i-1},\; 0),\; L_i - L_{i-1}\bigr) \times t_i`}</BlockTex>

          <p className="text-xs text-gray-500">
            donde <Tex>{"L_i"}</Tex> es el límite superior del tramo <Tex>{"i"}</Tex> y <Tex>{"t_i"}</Tex> su tipo impositivo.
          </p>
        </Section>

        {/* ============================================================ */}
        {/* 2. IRPF GENERAL */}
        {/* ============================================================ */}
        <Section id="irpf-general" title="2. IRPF General (Rentas del Trabajo y Actividades Económicas)">
          <p className="text-sm leading-relaxed mb-2">
            Se compone de la <strong>cuota estatal</strong> + <strong>cuota autonómica</strong>. Cada comunidad tiene sus propios tramos autonómicos.
            Se aplica el <strong>mínimo personal</strong> (5.550 €) como crédito fiscal.
          </p>

          <SubSection title="2.1 Tramos estatales (2025)">
            <div className="overflow-x-auto my-3">
              <table className="w-full text-sm border">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border px-3 py-2 text-left">Tramo</th>
                    <th className="border px-3 py-2 text-right">Tipo estatal (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["0 — 12.450 €", "9,50%"],
                    ["12.450 — 20.200 €", "12,00%"],
                    ["20.200 — 35.200 €", "15,00%"],
                    ["35.200 — 60.000 €", "18,50%"],
                    ["60.000 — 300.000 €", "22,50%"],
                    ["> 300.000 €", "24,50%"],
                  ].map(([tramo, tipo]) => (
                    <tr key={tramo}>
                      <td className="border px-3 py-1.5">{tramo}</td>
                      <td className="border px-3 py-1.5 text-right font-mono">{tipo}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SubSection>

          <SubSection title="2.2 Fórmula con mínimo personal">
            <BlockTex>{String.raw`\text{IRPF}_{\text{general}}(B, R) = T_{\text{estatal+auton.}}(B) - T_{\text{estatal+auton.}}(M_p)`}</BlockTex>
            <p className="text-xs text-gray-500">
              donde <Tex>{"M_p = 5.550"}</Tex> € es el mínimo personal y <Tex>{"R"}</Tex> la comunidad autónoma.
              El mínimo personal se aplica como <em>crédito fiscal</em>: se calcula el impuesto que correspondería al mínimo y se resta.
            </p>
          </SubSection>

          <SubSection title="2.3 Base liquidable para rentas del trabajo (asalariados y administradores SL)">
            <BlockTex>{String.raw`B_{\text{trabajo}} = \max\!\bigl(0,\; S_b - \text{SS}_{\text{emp}} - 2.000 - \text{Red}_{\text{trabajo}}\bigr)`}</BlockTex>
            <p className="text-sm leading-relaxed mb-2">Donde:</p>
            <ul className="text-sm list-disc pl-5 space-y-1">
              <li><Tex>{"S_b"}</Tex>: salario bruto anual</li>
              <li><Tex>{String.raw`\text{SS}_{\text{emp}}`}</Tex>: cotización del empleado a la Seguridad Social</li>
              <li>2.000 €: gastos deducibles del trabajador (art. 19.2f LIRPF)</li>
              <li><Tex>{String.raw`\text{Red}_{\text{trabajo}}`}</Tex>: reducción por rendimientos del trabajo (art. 20 LIRPF)</li>
            </ul>

            <BlockTex>{String.raw`\text{Red}_{\text{trabajo}} = \begin{cases} 7.302 & \text{si } R_n \leq 14.852 \\ \max(0,\; 7.302 - 1{,}4929 \times (R_n - 14.852)) & \text{si } R_n > 14.852 \end{cases}`}</BlockTex>
            <p className="text-xs text-gray-500">
              donde <Tex>{"R_n = S_b - \\text{SS}_{\\text{emp}} - 2.000"}</Tex> (rendimiento neto del trabajo).
              Esta reducción solo aplica a rendimientos del trabajo, <strong>no a autónomos</strong>.
            </p>
          </SubSection>
        </Section>

        {/* ============================================================ */}
        {/* 3. SS EMPLEADO */}
        {/* ============================================================ */}
        <Section id="ss-empleado" title="3. Seguridad Social — Empleado">
          <p className="text-sm leading-relaxed mb-2">
            El trabajador cotiza sobre su base de cotización (salario mensual, acotado entre base mínima y máxima).
          </p>
          <BlockTex>{String.raw`\text{SS}_{\text{emp}} = \text{Base}_{\text{cotiz}} \times 6{,}47\%`}</BlockTex>
          <BlockTex>{String.raw`\text{Base}_{\text{cotiz}} = \text{clip}\!\left(\frac{S_b}{12},\; 1.381{,}20,\; 4.909{,}50\right) \times 12`}</BlockTex>

          <div className="overflow-x-auto my-4">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2 text-left">Concepto</th>
                  <th className="border px-3 py-2 text-right">Tipo (%)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Contingencias comunes", "4,70%"],
                  ["Desempleo", "1,55%"],
                  ["Formación profesional", "0,10%"],
                  ["MEI", "0,12%"],
                  ["Total empleado", "6,47%"],
                ].map(([c, t]) => (
                  <tr key={c}>
                    <td className="border px-3 py-1.5">{c}</td>
                    <td className="border px-3 py-1.5 text-right font-mono">{t}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        {/* ============================================================ */}
        {/* 4. SS EMPRESA */}
        {/* ============================================================ */}
        <Section id="ss-empresa" title="4. Seguridad Social — Empresa (Cotización Patronal)">
          <BlockTex>{String.raw`\text{SS}_{\text{empresa}} = \text{Base}_{\text{cotiz}} \times 30{,}57\% \;+\; \text{Solidaridad}(S_b)`}</BlockTex>

          <div className="overflow-x-auto my-4">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2 text-left">Concepto</th>
                  <th className="border px-3 py-2 text-right">Tipo (%)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Contingencias comunes", "23,60%"],
                  ["Desempleo", "5,50%"],
                  ["FOGASA", "0,20%"],
                  ["Formación profesional", "0,60%"],
                  ["MEI", "0,67%"],
                  ["Total empresa", "30,57%"],
                ].map(([c, t]) => (
                  <tr key={c}>
                    <td className="border px-3 py-1.5">{c}</td>
                    <td className="border px-3 py-1.5 text-right font-mono">{t}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <SubSection title="4.1 Cotización de solidaridad (2025)">
            <p className="text-sm leading-relaxed mb-2">
              Nueva cotización progresiva sobre salario que exceda la base máxima anual (58.914 €):
            </p>
            <div className="overflow-x-auto my-3">
              <table className="w-full text-sm border">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="border px-3 py-2 text-left">Exceso sobre base máxima</th>
                    <th className="border px-3 py-2 text-right">Tipo (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["0-10% (0 — 5.891 €)", "0,92%"],
                    ["10-50% (5.891 — 29.457 €)", "1,00%"],
                    ["> 50% (> 29.457 €)", "1,17%"],
                  ].map(([t, r]) => (
                    <tr key={t}>
                      <td className="border px-3 py-1.5">{t}</td>
                      <td className="border px-3 py-1.5 text-right font-mono">{r}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SubSection>
        </Section>

        {/* ============================================================ */}
        {/* 5. CUOTA AUTONOMOS */}
        {/* ============================================================ */}
        <Section id="ss-autonomo" title="5. Cuota de Autónomos (RETA 2025)">
          <p className="text-sm leading-relaxed mb-2">
            Sistema de cotización por tramos de rendimiento neto mensual. La cuota varía entre 230 € y 590 €/mes.
          </p>

          <div className="overflow-x-auto my-4">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2 text-left">Rendimiento neto mensual</th>
                  <th className="border px-3 py-2 text-right">Cuota (€/mes)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["≤ 670 €", "230"],
                  ["670 — 900 €", "260"],
                  ["900 — 1.166,70 €", "290"],
                  ["1.166,70 — 1.300 €", "320"],
                  ["1.300 — 1.500 €", "350"],
                  ["1.500 — 1.700 €", "370"],
                  ["1.700 — 1.850 €", "390"],
                  ["1.850 — 2.030 €", "400"],
                  ["2.030 — 2.330 €", "410"],
                  ["2.330 — 2.760 €", "450"],
                  ["2.760 — 3.190 €", "480"],
                  ["3.190 — 3.620 €", "510"],
                  ["3.620 — 4.050 €", "540"],
                  ["4.050 — 6.000 €", "590"],
                  ["> 6.000 €", "590"],
                ].map(([r, c]) => (
                  <tr key={r}>
                    <td className="border px-3 py-1.5">{r}</td>
                    <td className="border px-3 py-1.5 text-right font-mono">{c} €</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-sm">
            <strong>Tarifa plana:</strong> 87 €/mes durante los primeros 12 meses como nuevo autónomo.
            Ampliable a 24 meses si los ingresos no superan el SMI (15.876 €/año).
          </p>

          <BlockTex>{String.raw`\text{Cuota}_{\text{anual}} = \begin{cases} 87 \times m_{\text{plana}} + C_{\text{normal}} \times m_{\text{rest}} & \text{si tarifa plana} \\ C_{\text{normal}} \times 12 & \text{en caso contrario} \end{cases}`}</BlockTex>
        </Section>

        {/* ============================================================ */}
        {/* 6. IS */}
        {/* ============================================================ */}
        <Section id="is" title="6. Impuesto de Sociedades (2025)">
          <div className="overflow-x-auto my-4">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-3 py-2 text-left">Tipo de empresa</th>
                  <th className="border px-3 py-2 text-right">Tipo (%)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Startup (primeros 2 años con beneficios)", "15%"],
                  ["Microempresa (< 1M€ facturación): primeros 50.000 €", "21%"],
                  ["Microempresa: resto", "22%"],
                  ["PYME (1M — 10M€ facturación)", "24%"],
                  ["General", "25%"],
                ].map(([t, r]) => (
                  <tr key={t}>
                    <td className="border px-3 py-1.5">{t}</td>
                    <td className="border px-3 py-1.5 text-right font-mono">{r}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <BlockTex>{String.raw`\text{IS}_{\text{micro}}(P) = \min(P, 50.000) \times 0{,}21 + \max(0, P - 50.000) \times 0{,}22`}</BlockTex>
        </Section>

        {/* ============================================================ */}
        {/* 7. AUTONOMO */}
        {/* ============================================================ */}
        <Section id="autonomo" title="7. Cálculo Completo: Autónomo">
          <p className="text-sm leading-relaxed mb-3">
            Flujo de cálculo desde facturación hasta neto:
          </p>

          <div className="bg-gray-50 rounded-lg p-4 space-y-2 font-mono text-sm">
            <BlockTex>{String.raw`R_n = F - G_d \qquad \text{(rendimiento neto = facturación - gastos deducibles)}`}</BlockTex>
            <BlockTex>{String.raw`C_a = f_{\text{cuota}}(R_n) \qquad \text{(cuota autónomos según tramo)}`}</BlockTex>
            <BlockTex>{String.raw`B_{\text{IRPF}} = R_n - C_a \qquad \text{(base imponible IRPF)}`}</BlockTex>
            <BlockTex>{String.raw`\text{IRPF} = T_{\text{general}}(B_{\text{IRPF}}, \text{región}) - T_{\text{general}}(M_p, \text{región})`}</BlockTex>
            <BlockTex>{String.raw`\boxed{\text{Neto}_{\text{autónomo}} = R_n - C_a - \text{IRPF}}`}</BlockTex>
          </div>

          <p className="text-xs text-gray-500 mt-2">
            Nota: el autónomo <strong>no</strong> se beneficia de los 2.000 € de gastos deducibles del trabajador ni de la reducción por rendimientos del trabajo.
            Esas deducciones son exclusivas de rentas del trabajo por cuenta ajena (art. 19.2f y art. 20 LIRPF).
          </p>
        </Section>

        {/* ============================================================ */}
        {/* 8. SL */}
        {/* ============================================================ */}
        <Section id="sl" title="8. Cálculo Completo: Sociedad Limitada">
          <p className="text-sm leading-relaxed mb-3">
            La SL tiene dos flujos: el societario (empresa) y el personal (administrador).
          </p>

          <SubSection title="8.1 Flujo societario">
            <BlockTex>{String.raw`\text{Gastos}_{\text{total}} = S_b + \text{SS}_{\text{empresa}}(S_b) + G_e + G_g`}</BlockTex>
            <BlockTex>{String.raw`P = \max(0,\; F - \text{Gastos}_{\text{total}}) \qquad \text{(beneficio antes IS)}`}</BlockTex>
            <BlockTex>{String.raw`\text{IS} = \text{IS}_{\text{micro}}(P)`}</BlockTex>
            <BlockTex>{String.raw`P_n = P - \text{IS} \qquad \text{(beneficio neto = beneficio retenido)}`}</BlockTex>
          </SubSection>

          <SubSection title="8.2 Flujo personal (salario del administrador)">
            <BlockTex>{String.raw`\text{SS}_{\text{emp}} = \text{clip}(S_b/12,\; 1.381{,}20,\; 4.909{,}50) \times 12 \times 6{,}47\%`}</BlockTex>
            <BlockTex>{String.raw`B_{\text{trabajo}} = \max(0,\; S_b - \text{SS}_{\text{emp}} - 2.000 - \text{Red}_{\text{trabajo}})`}</BlockTex>
            <BlockTex>{String.raw`\text{IRPF}_{\text{sal}} = T_{\text{general}}(B_{\text{trabajo}}, R) - T_{\text{general}}(M_p, R)`}</BlockTex>
            <BlockTex>{String.raw`\boxed{S_n = S_b - \text{SS}_{\text{emp}} - \text{IRPF}_{\text{sal}}}`}</BlockTex>
          </SubSection>

          <SubSection title="8.3 Dividendos (si se distribuyen)">
            <BlockTex>{String.raw`D_b = P_n \times \text{pct}_{\text{div}}`}</BlockTex>
            <BlockTex>{String.raw`\text{IRPF}_{\text{div}} = T_{\text{ahorro}}(D_b)`}</BlockTex>
            <BlockTex>{String.raw`\boxed{\text{Neto}_{\text{total}} = S_n + D_b - \text{IRPF}_{\text{div}}}`}</BlockTex>
          </SubSection>
        </Section>

        {/* ============================================================ */}
        {/* 9. INVERSION PERSONAL */}
        {/* ============================================================ */}
        <Section id="inversion-personal" title="9. Simulación de Inversión Personal">
          <p className="text-sm leading-relaxed mb-3">
            Modelo de interés compuesto con aportaciones mensuales constantes. Los rendimientos <strong>no tributan hasta la venta</strong>.
          </p>

          <BlockTex>{String.raw`K_t = K_{t-1} \times (1 + r) + A \times 12`}</BlockTex>
          <BlockTex>{String.raw`A_{\text{total},t} = A_{\text{total},t-1} + A \times 12`}</BlockTex>
          <BlockTex>{String.raw`\text{Plusvalías}_t = K_t - A_{\text{total},t}`}</BlockTex>

          <p className="text-xs text-gray-500">
            donde <Tex>{"K_t"}</Tex> es el capital al final del año <Tex>{"t"}</Tex>, <Tex>{"r"}</Tex> la rentabilidad anual, y <Tex>{"A"}</Tex> la aportación mensual.
          </p>
        </Section>

        {/* ============================================================ */}
        {/* 10. INVERSION EMPRESA */}
        {/* ============================================================ */}
        <Section id="inversion-empresa" title="10. Simulación de Inversión Empresa (SL)">
          <p className="text-sm leading-relaxed mb-3">
            La empresa paga <strong>Impuesto de Sociedades sobre los rendimientos cada año</strong>, lo que reduce la rentabilidad compuesta efectiva.
          </p>

          <BlockTex>{String.raw`R_t = K_{t-1} \times r \qquad \text{(rentabilidad bruta del año)}`}</BlockTex>
          <BlockTex>{String.raw`\text{IS}_t = \text{IS}_{\text{micro}}(R_t)`}</BlockTex>
          <BlockTex>{String.raw`K_t = K_{t-1} + A \times 12 + R_t - \text{IS}_t`}</BlockTex>

          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 mt-4 text-sm">
            <strong>Impacto del IS anual:</strong> Con una rentabilidad bruta del 7% y un IS del 21%, la rentabilidad neta efectiva es
            aproximadamente <Tex>{"r_{\\text{neta}} \\approx 0{,}07 \\times (1 - 0{,}21) = 5{,}53\\%"}</Tex>.
            A 20 años, esto supone ~15% menos de capital acumulado respecto a la inversión personal.
          </div>
        </Section>

        {/* ============================================================ */}
        {/* 11. RESCATE */}
        {/* ============================================================ */}
        <Section id="rescate" title="11. Impuestos al Rescate (Liquidación)">
          <SubSection title="11.1 Inversión personal — Plusvalías">
            <p className="text-sm leading-relaxed mb-2">
              Solo tributan las <strong>plusvalías</strong> (ganancias patrimoniales). Las aportaciones originales ya tributaron como renta.
            </p>
            <BlockTex>{String.raw`\text{IRPF}_{\text{rescate}} = T_{\text{ahorro}}(K - A_{\text{total}}) = T_{\text{ahorro}}(\text{Plusvalías})`}</BlockTex>
            <BlockTex>{String.raw`\boxed{K_{\text{neto}} = K - \text{IRPF}_{\text{rescate}}}`}</BlockTex>
          </SubSection>

          <SubSection title="11.2 Inversión empresa — Dividendos">
            <p className="text-sm leading-relaxed mb-2">
              Al distribuir el capital de la empresa como dividendos, tributa el <strong>capital íntegro</strong>,
              no solo las ganancias. Todo el capital retenido es beneficio que nunca tributó como renta personal.
            </p>
            <BlockTex>{String.raw`\text{IRPF}_{\text{dividendos}} = T_{\text{ahorro}}(K_{\text{empresa}})`}</BlockTex>
            <BlockTex>{String.raw`\boxed{K_{\text{empresa,neto}} = K_{\text{empresa}} - T_{\text{ahorro}}(K_{\text{empresa}})}`}</BlockTex>

            <div className="rounded-lg border border-red-200 bg-red-50 p-4 mt-4 text-sm">
              <strong>Doble imposición:</strong> El beneficio de la SL primero paga IS (~21%), y cuando se distribuye como dividendos,
              paga además IRPF del ahorro (19-30%). Sobre 100 € de beneficio bruto:
              <BlockTex>{String.raw`100 \xrightarrow{\text{IS 21\%}} 79 \xrightarrow{\text{IRPF 19-21\%}} \approx 63\text{-}64 \text{ € netos}`}</BlockTex>
              Carga fiscal combinada: ~36-37%.
            </div>
          </SubSection>

          <SubSection title="11.3 Combinación SL (personal + empresa)">
            <BlockTex>{String.raw`K_{\text{total,neto}} = \underbrace{(K_p - T_{\text{ahorro}}(\text{Plusvalías}_p))}_{\text{personal neto}} + \underbrace{(K_e - T_{\text{ahorro}}(K_e))}_{\text{empresa neto}}`}</BlockTex>
          </SubSection>
        </Section>

        {/* ============================================================ */}
        {/* 12. FIRE */}
        {/* ============================================================ */}
        <Section id="fire" title="12. Regla del 4% — Retiro Gradual (FIRE)">
          <p className="text-sm leading-relaxed mb-3">
            La regla del 4% establece que puedes retirar un 4% anual de tu capital sin agotarlo (basada en el <em>Trinity Study</em>).
            El tratamiento fiscal del retiro depende del origen del capital.
          </p>

          <SubSection title="12.1 Inversión personal — FIRE">
            <p className="text-sm leading-relaxed mb-2">
              Al retirar un 4%, solo la parte proporcional correspondiente a plusvalías es gravable:
            </p>
            <BlockTex>{String.raw`W = K \times 0{,}04 \qquad \text{(retiro anual bruto)}`}</BlockTex>
            <BlockTex>{String.raw`\gamma = \frac{\text{Plusvalías}}{K} \qquad \text{(ratio de ganancias)}`}</BlockTex>
            <BlockTex>{String.raw`\text{IRPF}_{\text{FIRE}} = T_{\text{ahorro}}(W \times \gamma)`}</BlockTex>
            <BlockTex>{String.raw`\boxed{W_{\text{neto}} = W - \text{IRPF}_{\text{FIRE}}}`}</BlockTex>
          </SubSection>

          <SubSection title="12.2 Combinación SL — FIRE">
            <p className="text-sm leading-relaxed mb-2">
              El retiro se reparte proporcionalmente entre el patrimonio personal y empresarial.
              Se <strong>combinan las bases imponibles</strong> en una sola liquidación de IRPF del ahorro para aplicar correctamente los tramos progresivos:
            </p>
            <BlockTex>{String.raw`W = (K_p + K_e) \times 0{,}04`}</BlockTex>
            <BlockTex>{String.raw`W_p = \frac{K_p}{K_p + K_e} \times W \qquad W_e = \frac{K_e}{K_p + K_e} \times W`}</BlockTex>
            <BlockTex>{String.raw`\text{Base}_{\text{gravable}} = \underbrace{W_p \times \gamma_p}_{\text{plusvalías personal}} + \underbrace{W_e}_{\text{dividendos (100\%)}}`}</BlockTex>
            <BlockTex>{String.raw`\boxed{\text{IRPF}_{\text{FIRE}} = T_{\text{ahorro}}\!\left(\text{Base}_{\text{gravable}}\right)}`}</BlockTex>

            <p className="text-xs text-gray-500 mt-2">
              Nota: se usa una <strong>única llamada</strong> a los tramos del IRPF del ahorro para que los tramos progresivos se apliquen correctamente
              sobre la base combinada, evitando subestimar el impuesto por calcular cada parte por separado.
            </p>
          </SubSection>

          <SubSection title="12.3 Tipo efectivo">
            <BlockTex>{String.raw`\tau_{\text{efectivo}} = \frac{\text{IRPF}_{\text{FIRE}}}{W} \qquad \text{(sobre el retiro total)}`}</BlockTex>
            <p className="text-sm text-gray-600 mt-2">
              Este tipo efectivo mide qué porcentaje del dinero que retiras se va en impuestos. Es la métrica relevante para el usuario.
              Es diferente (y menor) que el tipo sobre la base imponible, ya que parte del retiro no es gravable.
            </p>
          </SubSection>
        </Section>

        {/* ============================================================ */}
        {/* Footer */}
        {/* ============================================================ */}
        <div className="mt-16 rounded-lg border border-gray-200 bg-gray-50 p-5 text-sm text-gray-500">
          <p>
            <strong>Fuentes legales:</strong> Ley 35/2006 del IRPF (arts. 19, 20, 25, 57, 63-66), Ley 27/2014 del Impuesto sobre Sociedades,
            Real Decreto-ley 13/2022 (sistema de cotización autónomos), Ley General de la Seguridad Social,
            Presupuestos Generales del Estado 2025.
          </p>
          <p className="mt-2">
            Los tramos autonómicos del IRPF se obtienen de la legislación fiscal de cada comunidad autónoma.
            Los tipos del Impuesto de Sociedades para microempresas reflejan la reforma fiscal 2025 (Ley 7/2024).
          </p>
        </div>
      </article>
    </>
  );
}
