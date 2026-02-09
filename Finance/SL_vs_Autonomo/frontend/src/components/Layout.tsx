import { ReactNode, useState } from "react";
import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

interface LayoutProps {
  children: ReactNode;
}

const navLinks = [
  { to: "/", labelKey: "nav.home" },
  { to: "/employee", labelKey: "nav.employee" },
  { to: "/autonomo", labelKey: "nav.autonomo" },
  { to: "/sl", labelKey: "nav.sl" },
  { to: "/comparador", labelKey: "nav.comparator" },
  { to: "/simulador-inversion", labelKey: "nav.investment_sim" },
];

const Layout = ({ children }: LayoutProps) => {
  const { t, i18n } = useTranslation();
  const [menuOpen, setMenuOpen] = useState(false);

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `transition-colors ${isActive ? "text-primary-700 font-semibold" : "text-gray-600 hover:text-primary-700"}`;

  return (
    <div className="min-h-screen flex flex-col bg-white font-sans text-gray-900">
      {/* Sticky nav */}
      <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          {/* Logo */}
          <NavLink to="/" className="text-lg font-bold tracking-tight text-primary-700">
            {t("app.title", "Simulador Fiscal")}
          </NavLink>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-5 text-sm md:flex">
            {navLinks.map((link) => (
              <NavLink key={link.to} to={link.to} className={linkClass}>
                {t(link.labelKey, link.labelKey)}
              </NavLink>
            ))}
          </nav>

          {/* Language toggle + hamburger */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 text-xs">
              <button
                className={`rounded px-2 py-1 transition-colors ${i18n.language === "es" ? "bg-primary-700 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
                onClick={() => i18n.changeLanguage("es")}
              >
                ES
              </button>
              <button
                className={`rounded px-2 py-1 transition-colors ${i18n.language === "en" ? "bg-primary-700 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
                onClick={() => i18n.changeLanguage("en")}
              >
                EN
              </button>
            </div>

            {/* Hamburger */}
            <button
              className="flex flex-col gap-1 md:hidden"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Toggle menu"
            >
              <span className={`block h-0.5 w-5 bg-gray-600 transition-transform ${menuOpen ? "translate-y-1.5 rotate-45" : ""}`} />
              <span className={`block h-0.5 w-5 bg-gray-600 transition-opacity ${menuOpen ? "opacity-0" : ""}`} />
              <span className={`block h-0.5 w-5 bg-gray-600 transition-transform ${menuOpen ? "-translate-y-1.5 -rotate-45" : ""}`} />
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <nav className="border-t border-gray-100 bg-white px-4 pb-4 md:hidden">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `block py-2 text-sm ${isActive ? "text-primary-700 font-semibold" : "text-gray-600"}`
                }
                onClick={() => setMenuOpen(false)}
              >
                {t(link.labelKey, link.labelKey)}
              </NavLink>
            ))}
          </nav>
        )}
      </header>

      {/* Main content */}
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8">{children}</main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50">
        <div className="mx-auto max-w-4xl px-4 py-6 text-center text-xs text-gray-500">
          <p>{t("disclaimer", "Simulador orientativo. Consulta con un asesor fiscal profesional.")}</p>
          <div className="mt-2 flex items-center justify-center gap-3">
            <NavLink to="/formulas" className="text-blue-600 hover:underline">Fórmulas y Metodología</NavLink>
            <span>&middot;</span>
            <NavLink to="/analisis" className="text-blue-600 hover:underline">Análisis: Autónomo vs SL</NavLink>
          </div>
          <p className="mt-2">{t("footer.datos", "Datos fiscales 2025")} &middot; &copy; {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
