import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Simulator from "./pages/Simulator";
import HowItWorks from "./pages/HowItWorks";
import Glossary from "./pages/Glossary";

const App = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Simulator />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/glossary" element={<Glossary />} />
      </Routes>
    </Layout>
  );
};

export default App;
