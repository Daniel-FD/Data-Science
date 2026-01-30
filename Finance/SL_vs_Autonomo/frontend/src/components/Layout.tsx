import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

const Layout = ({ children }: { children: ReactNode }) => {
  const { t, i18n } = useTranslation();
  const { pathname } = useLocation();

  const isActive = (path: string) => (pathname === path ? "text-sky-600" : "text-slate-700");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-sky-500" />
            <span className="text-lg font-semibold">{t("app.title")}</span>
          </div>
          <nav className="flex items-center gap-6 text-sm font-medium">
            <Link className={isActive("/")} to="/">
              {t("nav.simulator")}
            </Link>
            <Link className={isActive("/how-it-works")} to="/how-it-works">
              {t("nav.how")}
            </Link>
            <Link className={isActive("/glossary")} to="/glossary">
              {t("nav.glossary")}
            </Link>
          </nav>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-500">{t("nav.language")}</span>
            <button
              className={`rounded px-2 py-1 ${i18n.language === "es" ? "bg-sky-500 text-white" : "bg-slate-100"}`}
              onClick={() => i18n.changeLanguage("es")}
            >
              ES
            </button>
            <button
              className={`rounded px-2 py-1 ${i18n.language === "en" ? "bg-sky-500 text-white" : "bg-slate-100"}`}
              onClick={() => i18n.changeLanguage("en")}
            >
              EN
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  );
};

export default Layout;
