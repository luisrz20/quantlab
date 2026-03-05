import { Routes, Route, Navigate } from "react-router-dom";
import SimulatePage from "@/pages/SimulatePage";
import ResultsPage from "@/pages/ResultsPage";
import ComparePage from "@/pages/ComparePage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/simulate" replace />} />
      <Route path="/simulate" element={<SimulatePage />} />
      <Route path="/results/:id" element={<ResultsPage />} />
      <Route path="/compare" element={<ComparePage />} />
    </Routes>
  );
}
