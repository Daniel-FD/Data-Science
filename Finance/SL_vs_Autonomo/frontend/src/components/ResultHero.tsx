import { useState, useEffect, useRef } from 'react';

interface ResultHeroProps {
  value: number;
  label: string;
  subtitle: string;
  formatAsCurrency?: boolean;
}

function useAnimatedNumber(target: number, duration = 400) {
  const [display, setDisplay] = useState(target);
  const prevRef = useRef(target);
  const frameRef = useRef(0);

  useEffect(() => {
    const start = prevRef.current;
    const diff = target - start;
    if (Math.abs(diff) < 0.5) { setDisplay(target); prevRef.current = target; return; }

    const startTime = performance.now();
    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(start + diff * eased);
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      } else {
        prevRef.current = target;
      }
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => { cancelAnimationFrame(frameRef.current); prevRef.current = target; };
  }, [target, duration]);

  return display;
}

const formatCurrency = (value: number): string =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);

const formatNumber = (value: number): string =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);

const ResultHero = ({ value, label, subtitle, formatAsCurrency = true }: ResultHeroProps) => {
  const safeValue = typeof value === "number" && !Number.isNaN(value) ? value : 0;
  const animatedValue = useAnimatedNumber(safeValue);
  const displayed = formatAsCurrency ? formatCurrency(animatedValue) : formatNumber(animatedValue);

  return (
    <div className="rounded-xl border border-accent-200 border-l-4 border-l-accent-600 bg-accent-50 p-6">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-4xl font-bold text-accent-700">{displayed}</p>
      <p className="mt-2 text-sm text-gray-600">{subtitle}</p>
    </div>
  );
};

export default ResultHero;
