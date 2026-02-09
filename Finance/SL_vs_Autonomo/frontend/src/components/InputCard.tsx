import { ReactNode, useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";

interface InputCardProps {
  title: string;
  children: ReactNode;
  expandable?: boolean;
  expandLabel?: string;
}

const InputCard = ({ title, children, expandable = false, expandLabel }: InputCardProps) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentHeight, setContentHeight] = useState(0);

  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight);
    }
  }, [children, expanded]);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>

      {expandable ? (
        <>
          <button
            className="mt-3 text-sm font-medium text-primary-700 hover:text-primary-800 transition-colors"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "−" : "+"}{" "}
            {expandLabel || t("input.advanced", "Opciones avanzadas")}
          </button>
          <div
            className="overflow-hidden transition-[max-height] duration-300 ease-in-out"
            style={{ maxHeight: expanded ? `${contentHeight}px` : "0px" }}
          >
            <div ref={contentRef} className="pt-4">
              {children}
            </div>
          </div>
        </>
      ) : (
        <div className="mt-4">{children}</div>
      )}
    </div>
  );
};

export default InputCard;
