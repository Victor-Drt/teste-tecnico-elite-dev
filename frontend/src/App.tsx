import HomePage from "./pages/HomePage";
import { BrowserRouter, Route, Routes } from "react-router";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import PrivateRoute from "./components/PrivateRoute";
import AppLayout from "./layout/AppLayout";
import VitrinePage from "./pages/VitrinePage";
import PainelLeiloeiroPage from "./pages/PainleLeiloeiroPage";
import RoleRoute from "./components/RoleRoute";

function AppShell() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/cadastro" element={<RegisterPage />} />
      <Route element={<PrivateRoute />}>
        <Route element={<AppLayout />}>
          <Route element={<RoleRoute role="licitante" redirectTo="/painel-leiloeiro" />}>
            <Route path="/vitrine" element={<VitrinePage />} />
          </Route>
          <Route element={<RoleRoute role="leiloeiro" redirectTo="/vitrine" />}>
            <Route path="/painel-leiloeiro" element={<PainelLeiloeiroPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}

export default App;
