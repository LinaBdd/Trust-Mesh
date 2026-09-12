import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Demo from "./pages/Demo";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="bg-slate-900 text-white p-4 flex gap-6">
        <Link to="/" className="font-bold">🔐 Trust Mesh</Link>
        <Link to="/dashboard">📊 Dashboard</Link>
        <Link to="/demo">🎬 Demo SIM Swap</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/demo" element={<Demo />} />
      </Routes>
    </BrowserRouter>
  );
}