import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface PageMetaProps {
  titleKey: string;
  descriptionKey: string;
}

export default function PageMeta({ titleKey, descriptionKey }: PageMetaProps) {
  const { t } = useTranslation();

  useEffect(() => {
    const title = t(titleKey);
    const siteName = t('app.title');
    document.title = `${title} — ${siteName}`;

    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) metaDesc.setAttribute('content', t(descriptionKey));

    // OG tags
    let ogTitle = document.querySelector('meta[property="og:title"]');
    if (!ogTitle) { ogTitle = document.createElement('meta'); ogTitle.setAttribute('property', 'og:title'); document.head.appendChild(ogTitle); }
    ogTitle.setAttribute('content', `${title} — ${siteName}`);

    let ogDesc = document.querySelector('meta[property="og:description"]');
    if (!ogDesc) { ogDesc = document.createElement('meta'); ogDesc.setAttribute('property', 'og:description'); document.head.appendChild(ogDesc); }
    ogDesc.setAttribute('content', t(descriptionKey));
  }, [t, titleKey, descriptionKey]);

  return null;
}
