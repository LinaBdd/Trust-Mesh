import { useState } from "react";
import { triggerSimSwap, resetDemo } from "../api";

export default function Demo() {
  const [msg, setMsg] = useState("");
  const phone = "+213555000111";

  const attack = async () => {
    await triggerSimSwap({
      phone_number: phone,
      hours_since_swap: 2.0,
      real_country: "RU",
      device_id: "unknown-device",
    });
    setMsg("✅ Attaque SIM Swap activée — va sur Login et utilise country=RU");
  };

  const reset = async () => {
    await resetDemo(phone);
    setMsg("✅ Scénario réinitialisé");
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <h1 className="text-3xl font-bold mb-6">🎬 Demo — Simuler une attaque</h1>

      <div className="bg-white p-6 rounded-xl shadow max-w-2xl">
        <p className="mb-4 text-slate-600">
          Ce bouton simule un remplacement de SIM malveillant via l'API CAMARA SIM Swap.
          Ensuite, va sur Login avec <code>country=RU</code> et <code>device=unknown-device</code>.
        </p>

        <div className="flex gap-3">
          <button
            onClick={attack}
            className="bg-red-600 text-white px-6 py-3 rounded font-semibold hover:bg-red-700"
          >
            🔴 Simuler SIM Swap
          </button>
          <button
            onClick={reset}
            className="bg-slate-600 text-white px-6 py-3 rounded font-semibold hover:bg-slate-700"
          >
            ♻️ Reset
          </button>
        </div>

        {msg && <p className="mt-4 text-green-600">{msg}</p>}
      </div>
    </div>
  );
}