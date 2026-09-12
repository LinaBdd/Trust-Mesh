import { useState } from "react";
import { getLogs } from "../api";

export default function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState(false);

  const load = async () => {
    if (!userId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getLogs(userId.trim());
      setLogs(data);
      setSearched(true);
    } catch (e) {
      setError("Impossible de charger les logs — vérifie le User ID.");
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") load();
  };

  const riskColor = (risk) =>
    risk === "LOW" ? "text-emerald-400 bg-emerald-500/10" :
    risk === "MEDIUM" ? "text-amber-400 bg-amber-500/10" :
    "text-red-400 bg-red-500/10";

  const scoreColor = (score) =>
    score >= 70 ? "#10b981" : score >= 40 ? "#f59e0b" : "#ef4444";

  const decisionColor = (decision) =>
    decision === "ALLOW" ? "text-emerald-400" :
    decision === "REQUIRE_MFA" ? "text-amber-400" :
    "text-red-400";

  // Statistiques agrégées
  const stats = logs.length > 0 ? {
    avgScore: Math.round(logs.reduce((sum, l) => sum + l.score, 0) / logs.length),
    allowCount: logs.filter((l) => l.decision === "ALLOW").length,
    blockedCount: logs.filter((l) => l.decision === "BLOCK" || l.decision === "REQUIRE_ADMIN_APPROVAL").length,
    mfaCount: logs.filter((l) => l.decision === "REQUIRE_MFA").length,
  } : null;

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-white mb-1">Dashboard Admin</h1>
      <p className="text-slate-400 text-sm mb-8">
        Historique et analyse des tentatives de connexion.
      </p>

      {/* Barre de recherche */}
      <div className="flex gap-3 mb-6">
        <input
          className="flex-1 max-w-md bg-[#111722] border border-white/10 rounded-lg p-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition"
          placeholder="User ID (récupéré depuis un login)"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={load}
          disabled={loading || !userId.trim()}
          className="bg-gradient-to-r from-blue-500 to-violet-600 text-white px-5 rounded-lg text-sm font-semibold hover:opacity-90 disabled:opacity-40 transition min-w-[100px]"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Chargement
            </span>
          ) : (
            "Charger"
          )}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400">
          ⚠️ {error}
        </div>
      )}

      {/* Cartes de synthèse */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 animate-fade-in-up">
          <div className="bg-[#111722] glow-border rounded-xl p-4">
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Score moyen</p>
            <p className="text-2xl font-bold" style={{ color: scoreColor(stats.avgScore) }}>
              {stats.avgScore}
              <span className="text-xs text-slate-500 font-normal"> /100</span>
            </p>
          </div>
          <div className="bg-[#111722] glow-border rounded-xl p-4">
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Sessions</p>
            <p className="text-2xl font-bold text-white">{logs.length}</p>
          </div>
          <div className="bg-[#111722] glow-border rounded-xl p-4">
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Autorisées</p>
            <p className="text-2xl font-bold text-emerald-400">{stats.allowCount}</p>
          </div>
          <div className="bg-[#111722] glow-border rounded-xl p-4">
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Bloquées / MFA</p>
            <p className="text-2xl font-bold text-red-400">
              {stats.blockedCount}
              <span className="text-sm text-amber-400 font-normal"> + {stats.mfaCount}</span>
            </p>
          </div>
        </div>
      )}

      {/* Tableau */}
      <div className="bg-[#111722] rounded-2xl glow-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 text-slate-400 text-xs uppercase tracking-wide">
              <th className="text-left p-4 font-medium">Heure</th>
              <th className="text-left p-4 font-medium">Score</th>
              <th className="text-left p-4 font-medium">Risque</th>
              <th className="text-left p-4 font-medium">Décision</th>
              <th className="text-left p-4 font-medium">Explication</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <tr key={i} className="border-t border-white/5">
                  {Array.from({ length: 5 }).map((__, j) => (
                    <td key={j} className="p-4">
                      <div className="h-3 bg-white/5 rounded animate-pulse" style={{ width: `${60 + j * 5}%` }} />
                    </td>
                  ))}
                </tr>
              ))
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-10 text-center">
                  <p className="text-slate-500 text-sm">
                    {searched
                      ? "Aucune session trouvée pour ce User ID."
                      : "Entre un User ID et clique sur \"Charger\" pour voir l'historique."}
                  </p>
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.session_id} className="border-t border-white/5 hover:bg-white/[0.02] transition">
                  <td className="p-4 text-slate-400 text-xs whitespace-nowrap">
                    {new Date(log.computed_at).toLocaleString()}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white w-8">{log.score}</span>
                      <div className="w-16 bg-white/5 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="h-1.5 rounded-full"
                          style={{ width: `${Math.max(log.score, 4)}%`, backgroundColor: scoreColor(log.score) }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-0.5 rounded-md text-xs font-semibold ${riskColor(log.risk_level)}`}>
                      {log.risk_level}
                    </span>
                  </td>
                  <td className={`p-4 text-xs font-medium ${decisionColor(log.decision)}`}>
                    {log.decision.replace(/_/g, " ")}
                  </td>
                  <td className="p-4 text-xs text-slate-500 max-w-md">{log.explanation}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}