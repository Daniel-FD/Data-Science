import { useState, useRef, useEffect } from "react";

interface TooltipProps {
  text: string;
  children?: React.ReactNode;
}

/**
 * Info icon (ⓘ) with hover tooltip. Inline, minimal footprint.
 * If children provided, wraps them; otherwise renders ⓘ icon.
 */
export default function Tooltip({ text, children }: TooltipProps) {
  const [show, setShow] = useState(false);
  const [position, setPosition] = useState<"top" | "bottom">("top");
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (show && ref.current) {
      const rect = ref.current.getBoundingClientRect();
      setPosition(rect.top < 80 ? "bottom" : "top");
    }
  }, [show]);

  return (
    <span
      ref={ref}
      className="relative inline-flex items-center"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children ?? (
        <svg
          className="h-3.5 w-3.5 text-gray-400 hover:text-gray-600 cursor-help ml-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 16v-4M12 8h.01" />
        </svg>
      )}
      {show && (
        <span
          className={`absolute z-50 w-64 rounded-lg bg-gray-800 px-3 py-2 text-xs leading-relaxed text-white shadow-lg ${
            position === "top"
              ? "bottom-full mb-2 left-1/2 -translate-x-1/2"
              : "top-full mt-2 left-1/2 -translate-x-1/2"
          }`}
        >
          {text}
          <span
            className={`absolute left-1/2 -translate-x-1/2 border-4 border-transparent ${
              position === "top"
                ? "top-full border-t-gray-800"
                : "bottom-full border-b-gray-800"
            }`}
          />
        </span>
      )}
    </span>
  );
}
