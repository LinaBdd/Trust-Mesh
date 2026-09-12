const TOOL_LABELS = {
  sim_swap: { icon: "📶", label: "SIM Swap" },
  device_status: { icon: "📱", label: "Device Status" },
  location_verification: { icon: "📍", label: "Location Verification" },
};

export default function AgentReasoning({ reasoning, toolsCalled }) {
  if (!reasoning && (!toolsCalled || toolsCalled.length === 0)) return null;

  return (
    <div className="mt-5 p-4 bg-violet-500/5 border border-violet-500/20 rounded-xl">
      <p className="text-xs font-semibold mb-2 text-violet-400 flex items-center gap-1.5">
        🧠 Raisonnement de l'agent IA
      </p>

      {toolsCalled && toolsCalled.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {toolsCalled.map((tool) => {
            const meta = TOOL_LABELS[tool] || { icon: "🔧", label: tool };
            return (
              <span
                key={tool}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-violet-500/10 border border-violet-500/20 rounded-full text-xs text-violet-300"
              >
                <span>{meta.icon}</span>
                {meta.label}
              </span>
            );
          })}
        </div>
      )}

      {reasoning && (
        <p className="text-xs text-slate-400 leading-relaxed italic">
          "{reasoning}"
        </p>
      )}
    </div>
  );
}