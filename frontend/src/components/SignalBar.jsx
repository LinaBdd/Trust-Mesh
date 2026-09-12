export default function SignalBar({ signal }) {
  const pct = signal.score;
  const color = pct >= 70 ? "#10b981" : pct >= 40 ? "#f59e0b" : "#ef4444";
  const icons = { sim: "📶", device: "📱", location: "📍", behaviour: "🧠" };

  return (
    <div>
      <div className="flex justify-between items-center text-xs mb-1.5">
        <span className="font-medium text-slate-300 flex items-center gap-1.5">
          <span>{icons[signal.name] || "•"}</span>
          <span className="uppercase tracking-wide">{signal.name}</span>
        </span>
        <span className="font-mono text-slate-400">{pct}/100</span>
      </div>
      <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
        <div
          className="h-1.5 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <p className="text-xs text-slate-500 mt-1">{signal.reason}</p>
    </div>
  );
}