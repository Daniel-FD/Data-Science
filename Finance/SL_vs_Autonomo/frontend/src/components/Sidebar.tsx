import { useTranslation } from "react-i18next";

export type SidebarValues = {
  region: string;
  facturacion: number;
  gastos_deducibles: number;
  gastos_personales: number;
  salario_administrador: number;
  gastos_gestoria: number;
  capital_inicial: number;
  rentabilidad: number;
  años: number;
  tarifa_plana: boolean;
  company_age: number;
  turnover: number;
  is_startup: boolean;
  aportacion_plan_pensiones: number;
};

type Preset = { label: string; facturacion: number; gastos_deducibles: number; gastos_personales: number };

type Props = {
  values: SidebarValues;
  regions: string[];
  presets: Preset[];
  onChange: (values: SidebarValues) => void;
  onPreset: (preset: Preset) => void;
  onSimulate: () => void;
};

const Sidebar = ({ values, regions, presets, onChange, onPreset, onSimulate }: Props) => {
  const { t } = useTranslation();

  const update = (patch: Partial<SidebarValues>) => onChange({ ...values, ...patch });

  return (
    <aside className="w-full rounded-xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">{t("sidebar.title")}</h2>

      <div className="mt-4 space-y-4">
        <div>
          <label className="text-sm font-medium">{t("sidebar.region")}</label>
          <select
            className="mt-1 w-full rounded border px-3 py-2"
            value={values.region}
            onChange={(e) => update({ region: e.target.value })}
          >
            {regions.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-sm font-medium">{t("sidebar.presets")}</label>
          <div className="mt-2 flex flex-wrap gap-2">
            {presets.map((p) => (
              <button
                key={p.label}
                className="rounded bg-slate-100 px-3 py-1 text-sm"
                onClick={() => onPreset(p)}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold">{t("sidebar.income")}</h3>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.facturacion}
              onChange={(e) => update({ facturacion: Number(e.target.value) })}
              placeholder="Facturación"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.gastos_deducibles}
              onChange={(e) => update({ gastos_deducibles: Number(e.target.value) })}
              placeholder="Gastos deducibles"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.gastos_personales}
              onChange={(e) => update({ gastos_personales: Number(e.target.value) })}
              placeholder="Gastos personales"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.aportacion_plan_pensiones}
              onChange={(e) => update({ aportacion_plan_pensiones: Number(e.target.value) })}
              placeholder="Plan de pensiones"
            />
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold">{t("sidebar.company")}</h3>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.salario_administrador}
              onChange={(e) => update({ salario_administrador: Number(e.target.value) })}
              placeholder="Salario administrador"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.gastos_gestoria}
              onChange={(e) => update({ gastos_gestoria: Number(e.target.value) })}
              placeholder="Gestoría"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.turnover}
              onChange={(e) => update({ turnover: Number(e.target.value) })}
              placeholder="Turnover"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.company_age}
              onChange={(e) => update({ company_age: Number(e.target.value) })}
              placeholder="Años empresa"
            />
          </div>
          <div className="mt-3 flex items-center gap-2">
            <input
              type="checkbox"
              checked={values.is_startup}
              onChange={(e) => update({ is_startup: e.target.checked })}
            />
            <span className="text-sm">Startup</span>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold">{t("sidebar.investment")}</h3>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.capital_inicial}
              onChange={(e) => update({ capital_inicial: Number(e.target.value) })}
              placeholder="Capital inicial"
            />
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.rentabilidad}
              onChange={(e) => update({ rentabilidad: Number(e.target.value) })}
              placeholder="Rentabilidad (0-1)"
            />
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold">{t("sidebar.horizon")}</h3>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <input
              className="rounded border px-3 py-2"
              type="number"
              value={values.años}
              onChange={(e) => update({ años: Number(e.target.value) })}
              placeholder="Años"
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={values.tarifa_plana}
                onChange={(e) => update({ tarifa_plana: e.target.checked })}
              />
              Tarifa plana
            </label>
          </div>
        </div>

        <button
          className="mt-2 w-full rounded bg-sky-500 px-4 py-2 text-white"
          onClick={onSimulate}
        >
          {t("sidebar.simulate")}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
