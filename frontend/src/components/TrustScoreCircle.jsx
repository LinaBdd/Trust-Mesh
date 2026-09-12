export default function TrustScoreCircle({ score, risk }) {
  const config = {
    LOW: { ring: "#10b981", glow: "shadow-emerald-500/30", label: "Risque faible" },
    MEDIUM: { ring: "#f59e0b", glow: "shadow-amber-500/30", label: "Risque moyen" },
    HIGH: { ring: "#ef4444", glow: "shadow-red-500/30", label: "Risque élevé" },
  }[risk] || { ring: "#64748b", glow: "", label: "" };

  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className={`relative w-36 h-36 ${config.glow} rounded-full shadow-xl`}>
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="54" fill="none" stroke="#1e293b" strokeWidth="8" />
          <circle
            cx="60" cy="60" r="54" fill="none"
            stroke={config.ring} strokeWidth="8" strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold text-white">{Math.round(score)}</span>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider">/ 100</span>
        </div>
      </div>
      <span className="text-xs font-medium mt-3 uppercase tracking-wide" style={{ color: config.ring }}>
        {config.label}
      </span>
    </div>
  );
}