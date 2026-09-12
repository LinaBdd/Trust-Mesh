import { useState } from "react";
import { login } from "../api";
import TrustScoreCircle from "../components/TrustScoreCircle";
import SignalBar from "../components/SignalBar";
import ProfileMaturity from "../components/ProfileMaturity";
import AgentReasoning from "../components/AgentReasoning";

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
      const data = await login({ ...form, timestamp: new Date().toISOString() });
      setResult(data.trust_score);
    } catch (e) {
      alert("Erreur : " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Simulateur de connexion</h1>
        <p className="text-slate-400 text-sm mt-1">
          Teste le moteur de confiance en simulant différents scénarios de connexion.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Formulaire */}
        <div className="bg-[#111722] rounded-2xl p-6 glow-border w-full min-w-0 h-fit">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-5">
            Paramètres de connexion
          </h2>

          <label className="block mb-4 w-full">
            <span className="block text-xs text-slate-400 mb-1.5">Numéro de téléphone</span>
            <input
              className="w-full box-border bg-[#0a0e14] border border-white/10 rounded-lg p-2.5 text-slate-100 text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition"
              value={form.phone_number}
              onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
            />
          </label>

          <label className="block mb-4 w-full">
            <span className="block text-xs text-slate-400 mb-1.5">Device ID</span>
            <input
              className="w-full box-border bg-[#0a0e14] border border-white/10 rounded-lg p-2.5 text-slate-100 text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition"
              value={form.device_id}
              onChange={(e) => setForm({ ...form, device_id: e.target.value })}
            />
          </label>

          <label className="block mb-6 w-full">
            <span className="block text-xs text-slate-400 mb-1.5">Pays déclaré</span>
            <select
              className="w-full box-border bg-[#0a0e14] border border-white/10 rounded-lg p-2.5 text-slate-100 text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition"
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
            className="w-full bg-gradient-to-r from-blue-500 to-violet-600 text-white py-3 rounded-lg font-semibold text-sm hover:opacity-90 disabled:opacity-40 transition shadow-lg shadow-blue-500/20"
          >
            {loading ? "Analyse en cours..." : "Se connecter"}
          </button>
        </div>

        {/* Résultat */}
        {result ? (
          <div className="bg-[#111722] rounded-2xl p-6 glow-border w-full min-w-0 animate-fade-in-up">
            <TrustScoreCircle score={result.final_score} risk={result.risk_level} />

            <p className="text-center mt-4">
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${
                result.decision === "ALLOW" ? "bg-emerald-500/15 text-emerald-400" :
                result.decision === "REQUIRE_MFA" ? "bg-amber-500/15 text-amber-400" :
                "bg-red-500/15 text-red-400"
              }`}>
                {result.decision.replace(/_/g, " ")}
              </span>
            </p>

            {result.session_count !== undefined && (
              <div className="mt-5">
                <ProfileMaturity sessionCount={result.session_count} />
              </div>
            )}

            <div className="mt-5 space-y-3">
              {result.signals.map((s) => (
                <SignalBar key={s.name} signal={s} />
              ))}
            </div>
            
            <AgentReasoning reasoning={result.agent_reasoning} toolsCalled={result.tools_called} />
            <div className="mt-5 p-4 bg-blue-500/5 border border-blue-500/20 rounded-xl">
              <p className="text-xs font-semibold mb-1.5 text-blue-400 flex items-center gap-1.5">
                🤖 AI Security Copilot
              </p>
              <p className="text-sm text-slate-300 leading-relaxed">{result.explanation}</p>
            </div>
          </div>
        ) : (
          <div className="bg-[#111722]/50 border border-dashed border-white/10 rounded-2xl p-6 flex items-center justify-center text-slate-500 text-sm min-h-[300px]">
            Les résultats de l'analyse apparaîtront ici
          </div>
        )}
      </div>
    </div>
  );
}