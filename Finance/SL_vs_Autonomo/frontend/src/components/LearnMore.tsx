import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";

interface LearnMoreProps {
  titleKey: string;
  contentKey: string;
}

const LearnMore = ({ titleKey, contentKey }: LearnMoreProps) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (contentRef.current) {
      setHeight(contentRef.current.scrollHeight);
    }
  }, [open]);

  const lines = t(contentKey, "").split("\n");

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50">
      <button
        className="flex w-full items-center justify-between px-5 py-4 text-left text-sm font-medium text-gray-800 hover:text-primary-700 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <span>{t(titleKey)}</span>
        <span
          className={`ml-2 text-gray-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        >
          &#9662;
        </span>
      </button>

      <div
        className="overflow-hidden transition-[max-height] duration-300 ease-in-out"
        style={{ maxHeight: open ? `${height}px` : "0px" }}
      >
        <div ref={contentRef} className="px-5 pb-4 text-sm leading-relaxed text-gray-600">
          {lines.map((line, i) => (
            <p key={i} className={i > 0 ? "mt-2" : ""}>
              {line}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LearnMore;
