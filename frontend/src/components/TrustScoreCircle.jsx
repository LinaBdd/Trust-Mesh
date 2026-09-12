export default function TrustScoreCircle({ score, risk }) {
  const color =
    risk === "LOW" ? "text-green-500" :
    risk === "MEDIUM" ? "text-orange-500" : "text-red-500";
  const bg =
    risk === "LOW" ? "bg-green-100" :
    risk === "MEDIUM" ? "bg-orange-100" : "bg-red-100";

  return (
    <div className={`${bg} rounded-full w-40 h-40 mx-auto flex flex-col items-center justify-center`}>
      <span className={`text-5xl font-bold ${color}`}>{Math.round(score)}</span>
      <span className="text-xs text-slate-500 mt-1">/ 100</span>
    </div>
  );
}