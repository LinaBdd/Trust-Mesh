import { useState } from "react";
import { triggerSimSwap, resetDemo } from "../api";

export default function Demo() {
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const phone = "+213555000111";

  const attack = async () => {
    setBusy(true);
    try {
      await triggerSimSwap({
        phone_number: phone,
        hours_since_swap: 2.0,
        real_country: "RU",
        device_id: "unknown-device",
      });
      setMsg("success");
    } finally {
      setBusy(false);
    }
  };

  const reset = async () => {
    setBusy(true);
    try {
      await resetDemo(phone);
      setMsg("reset");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-white mb-1">Simulateur d'attaque</h1>
      <p className="text-slate-400 text-sm mb-8">
        Déclenche un scénario de fraude réel pour tester la détection en direct.
      </p>

      <div className="bg-[#111722] rounded-2xl p-6 glow-border">
        <div className="flex items-start gap-3 mb-6 p-4 bg-red-500/5 border border-red-500/20 rounded-xl">
          <span className="text-2xl">⚠️</span>
          <p className="text-sm text-slate-300 leading-relaxed">
            Ce scénario simule un remplacement de SIM malveillant détecté via l'API CAMARA SIM Swap.
            Après activation, va sur <span className="text-blue-400 font-medium">Login</span> avec
            le pays <span className="text-blue-400 font-medium">Russie</span> et le device ID{" "}
            <span className="text-blue-400 font-medium">unknown-device</span>.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={attack}
            disabled={busy}
            className="flex-1 bg-gradient-to-r from-red-500 to-red-700 text-white py-3 rounded-lg font-semibold text-sm hover:opacity-90 disabled:opacity-40 transition shadow-lg shadow-red-500/20"
          >
            🔴 Simuler l'attaque
          </button>
          <button
            onClick={reset}
            disabled={busy}
            className="px-6 bg-white/5 border border-white/10 text-slate-300 rounded-lg font-semibold text-sm hover:bg-white/10 disabled:opacity-40 transition"
          >
            ♻️ Reset
          </button>
        </div>

        {msg === "success" && (
          <p className="mt-4 text-sm text-emerald-400 animate-fade-in-up">
            ✅ Attaque activée — teste maintenant le Login.
          </p>
        )}
        {msg === "reset" && (
          <p className="mt-4 text-sm text-slate-400 animate-fade-in-up">
            ✅ Scénario réinitialisé.
          </p>
        )}
      </div>
    </div>
  );
}