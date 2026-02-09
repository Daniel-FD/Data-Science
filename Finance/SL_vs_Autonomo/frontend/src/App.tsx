import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import ErrorBoundary from "./components/ErrorBoundary";
import { lazy, Suspense } from "react";

const Home = lazy(() => import("./pages/Home"));
const Employee = lazy(() => import("./pages/Employee"));
const Autonomo = lazy(() => import("./pages/Autonomo"));
const SL = lazy(() => import("./pages/SL"));
const Comparator = lazy(() => import("./pages/Comparator"));
const InvestmentSimulator = lazy(() => import("./pages/InvestmentSimulator"));
const Formulas = lazy(() => import("./pages/Formulas"));
const Analysis = lazy(() => import("./pages/Analysis"));

const Loading = () => (
  <div className="flex items-center justify-center min-h-[60vh]">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
  </div>
);

const App = () => {
  return (
    <ErrorBoundary>
      <Layout>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/employee" element={<Employee />} />
            <Route path="/autonomo" element={<Autonomo />} />
            <Route path="/sl" element={<SL />} />
            <Route path="/comparador" element={<Comparator />} />
            <Route path="/simulador-inversion" element={<InvestmentSimulator />} />
            <Route path="/formulas" element={<Formulas />} />
            <Route path="/analisis" element={<Analysis />} />
          </Routes>
        </Suspense>
      </Layout>
    </ErrorBoundary>
  );
};

export default App;
