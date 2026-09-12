export default function SignalBar({ signal }) {
  const pct = signal.score;
  const color =
    pct >= 70 ? "bg-green-500" :
    pct >= 40 ? "bg-orange-500" : "bg-red-500";

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="font-semibold uppercase">{signal.name}</span>
        <span>{pct}/100</span>
      </div>
      <div className="w-full bg-slate-200 rounded h-2 mb-1">
        <div className={`${color} h-2 rounded`} style={{ width: `${pct}%` }} />
      </div>
      <p className="text-xs text-slate-500">{signal.reason}</p>
    </div>
  );
}