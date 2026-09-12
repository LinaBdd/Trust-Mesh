import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Login from "./pages/login";
import Dashboard from "./pages/dashboard";
import Demo from "./pages/demo";

function Nav() {
  const location = useLocation();

  const linkClass = (path) =>
    `px-4 py-2 rounded-lg text-sm font-medium transition-all ${
      location.pathname === path
        ? "bg-blue-500/15 text-blue-400 border border-blue-500/30"
        : "text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent"
    }`;

  return (
    <nav className="border-b border-white/10 bg-[#0d1117]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg text-white">
          <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-sm">
            🔐
          </span>
          Trust Mesh
        </Link>
        <div className="flex gap-2">
          <Link to="/" className={linkClass("/")}>Login</Link>
          <Link to="/dashboard" className={linkClass("/dashboard")}>Dashboard</Link>
          <Link to="/demo" className={linkClass("/demo")}>Demo</Link>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0a0e14]">
        <Nav />
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/demo" element={<Demo />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}