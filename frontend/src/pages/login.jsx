import { useState } from "react";
import { login } from "../api";
import TrustScoreCircle from "../components/TrustScoreCircle";
import SignalBar from "../components/SignalBar";

export default function Login() {
  const [form, setForm] = useState({
    phone_number: "+213555000111",
    device_id: "device-abc",
    claimed_country: "DZ",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const data = await login({
        ...form,
        timestamp: new Date().toISOString(),
      });
      setResult(data.trust_score);
    } catch (e) {
      alert("Erreur : " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-3xl font-bold mb-6">🔐 Trust Mesh — Login</h1>

      <div className="grid grid-cols-2 gap-8 max-w-6xl">
        {/* Formulaire */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-semibold mb-4">Connexion simulée</h2>

          <label className="block mb-3">
            <span className="text-sm text-slate-600">Téléphone</span>
            <input
              className="w-full border rounded p-2 mt-1"
              value={form.phone_number}
              onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
            />
          </label>

          <label className="block mb-3">
            <span className="text-sm text-slate-600">Device ID</span>
            <input
              className="w-full border rounded p-2 mt-1"
              value={form.device_id}
              onChange={(e) => setForm({ ...form, device_id: e.target.value })}
            />
          </label>

          <label className="block mb-4">
            <span className="text-sm text-slate-600">Pays déclaré</span>
            <select
              className="w-full border rounded p-2 mt-1"
              value={form.claimed_country}
              onChange={(e) => setForm({ ...form, claimed_country: e.target.value })}
            >
              <option value="DZ">🇩🇿 Algérie</option>
              <option value="RU">🇷🇺 Russie</option>
              <option value="FR">🇫🇷 France</option>
              <option value="US">🇺🇸 USA</option>
            </select>
          </label>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Analyse..." : "Se connecter"}
          </button>
        </div>

        {/* Résultat */}
        {result && (
          <div className="bg-white p-6 rounded-xl shadow">
            <TrustScoreCircle score={result.final_score} risk={result.risk_level} />
            <p className="text-center mt-4 text-lg font-bold">
              Décision : {result.decision}
            </p>
            <div className="mt-6 space-y-2">
              {result.signals.map((s) => (
                <SignalBar key={s.name} signal={s} />
              ))}
            </div>
            <div className="mt-6 p-4 bg-slate-100 rounded">
              <p className="text-sm font-semibold mb-1">🤖 AI Security Copilot :</p>
              <p className="text-sm text-slate-700">{result.explanation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}