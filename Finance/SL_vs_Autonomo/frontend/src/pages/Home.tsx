import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import PageMeta from '../components/PageMeta';

const icons = {
  briefcase: (
    <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 14.15v4.073a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V14.15M16.5 7.477V5.25A2.25 2.25 0 0014.25 3h-4.5A2.25 2.25 0 007.5 5.25v2.227M12 12.75v3m-6.75-6h13.5a2.25 2.25 0 012.25 2.25v1.5a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 13.5V12a2.25 2.25 0 012.25-2.25z" />
    </svg>
  ),
  user: (
    <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.25a8.25 8.25 0 0115 0" />
    </svg>
  ),
  building: (
    <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
    </svg>
  ),
  chart: (
    <svg className="h-8 w-8 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  rocket: (
    <svg className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.63 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.841m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
    </svg>
  ),
};

interface CalcCard {
  titleKey: string;
  descKey: string;
  to: string;
  icon: keyof typeof icons;
}

const cards: CalcCard[] = [
  { titleKey: 'home.card.employee.title', descKey: 'home.card.employee.desc', to: '/employee', icon: 'briefcase' },
  { titleKey: 'home.card.autonomo.title', descKey: 'home.card.autonomo.desc', to: '/autonomo', icon: 'user' },
  { titleKey: 'home.card.sl.title', descKey: 'home.card.sl.desc', to: '/sl', icon: 'building' },
  { titleKey: 'home.card.comparator.title', descKey: 'home.card.comparator.desc', to: '/comparador', icon: 'chart' },
  { titleKey: 'home.card.investment.title', descKey: 'home.card.investment.desc', to: '/simulador-inversion', icon: 'rocket' },
];

export default function Home() {
  const { t } = useTranslation();

  return (
    <>
      <PageMeta titleKey="meta.home.title" descriptionKey="meta.home.desc" />
      <div className="mx-auto max-w-3xl px-4 py-16">
        {/* Hero */}
        <header className="mb-16 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            {t('home.hero.title')}
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-gray-600">
            {t('home.hero.subtitle')}
          </p>
        </header>

        {/* Calculator cards */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {cards.map((card) => (
            <Link
              key={card.to}
              to={card.to}
              className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md"
            >
              <div className="mb-4">{icons[card.icon]}</div>
              <h2 className="text-lg font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">
                {t(card.titleKey)}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-gray-500">
                {t(card.descKey)}
              </p>
            </Link>
          ))}
        </div>

        {/* Bottom paragraph */}
        <p className="mt-16 text-center text-sm leading-relaxed text-gray-400">
          {t('home.footer')}
        </p>
      </div>
    </>
  );
}
