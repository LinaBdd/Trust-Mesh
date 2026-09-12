export default function ProfileMaturity({ sessionCount, threshold = 10 }) {
  const pct = Math.min(100, Math.round((sessionCount / threshold) * 100));
  const isMature = sessionCount >= threshold;

  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="font-medium text-slate-400 uppercase tracking-wide">
          Maturité du profil
        </span>
        <span className="font-mono text-slate-500">{sessionCount} / {threshold}</span>
      </div>
      <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ${
            isMature ? "bg-gradient-to-r from-blue-500 to-violet-500" : "bg-slate-500"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-slate-500 mt-1">
        {isMature ? "✅ Profil mature — comportement bien connu" : "🧠 Profil en apprentissage"}
      </p>
    </div>
  );
}