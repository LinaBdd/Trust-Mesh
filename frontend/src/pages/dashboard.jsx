import { useEffect, useState } from "react";
import { getLogs } from "../api";

export default function Dashboard() {
  const [logs, setLogs] = useState([]);
  const [userId, setUserId] = useState("");

  const load = async () => {
    if (!userId) return;
    const data = await getLogs(userId);
    setLogs(data);
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-3xl font-bold mb-6">📊 Dashboard Admin</h1>

      <div className="flex gap-2 mb-6">
        <input
          className="border rounded p-2 flex-1 max-w-md"
          placeholder="User ID (récupère-le depuis un login)"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        <button onClick={load} className="bg-blue-600 text-white px-4 rounded">
          Charger
        </button>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-100">
            <tr>
              <th className="text-left p-3">Heure</th>
              <th className="text-left p-3">Score</th>
              <th className="text-left p-3">Risque</th>
              <th className="text-left p-3">Décision</th>
              <th className="text-left p-3">Explication</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.session_id} className="border-t">
                <td className="p-3 text-sm">{new Date(log.computed_at).toLocaleString()}</td>
                <td className="p-3 font-bold">{log.score}</td>
                <td className="p-3">{log.risk_level}</td>
                <td className="p-3">{log.decision}</td>
                <td className="p-3 text-xs text-slate-600 max-w-md">{log.explanation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}