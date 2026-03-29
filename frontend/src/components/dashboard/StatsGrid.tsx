"use client";

interface StatsGridProps {
  initialLoad: boolean;
  jobCount: string;
  candidateCount: string;
  avgScore: string;
}

export function StatsGrid({ initialLoad, jobCount, candidateCount, avgScore }: StatsGridProps) {
  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Total Candidatos */}
      <div className="bg-white p-6 rounded-lg shadow-[0_1px_3px_rgba(47,93,82,0.08)] flex items-start justify-between">
        <div>
          <p className="text-[10px] font-black text-outline uppercase tracking-widest mb-2">Total de Candidatos</p>
          {initialLoad ? (
            <div className="h-9 w-16 bg-surface-container mt-1 mb-2 rounded skeleton-pulse" />
          ) : (
            <h3 className="text-3xl font-black text-primary">{candidateCount}</h3>
          )}
          <div className="flex items-center mt-2 text-emerald-600 text-[10px] font-bold">
            <span className="material-symbols-outlined text-sm mr-1" style={{ fontVariationSettings: "'FILL' 1" }}>trending_up</span>
            +12% este mês
          </div>
        </div>
        <div className="bg-[#E8F2EF] p-3 rounded-full text-primary">
          <span className="material-symbols-outlined">group</span>
        </div>
      </div>

      {/* Vagas Abertas */}
      <div className="bg-white p-6 rounded-lg shadow-[0_1px_3px_rgba(47,93,82,0.08)] flex items-start justify-between">
        <div>
          <p className="text-[10px] font-black text-outline uppercase tracking-widest mb-2">Vagas Abertas</p>
          {initialLoad ? (
            <div className="h-9 w-16 bg-surface-container mt-1 mb-2 rounded skeleton-pulse" />
          ) : (
            <h3 className="text-3xl font-black text-primary">{jobCount}</h3>
          )}
          <div className="flex items-center mt-2 text-primary/60 text-[10px] font-bold">Ativas no momento</div>
        </div>
        <div className="bg-[#E8F2EF] p-3 rounded-full text-primary">
          <span className="material-symbols-outlined">work</span>
        </div>
      </div>

      {/* Score Médio */}
      <div className="bg-white p-6 rounded-lg shadow-[0_1px_3px_rgba(47,93,82,0.08)] flex items-start justify-between">
        <div>
          <p className="text-[10px] font-black text-outline uppercase tracking-widest mb-2">Score Médio IA</p>
          {initialLoad ? (
            <div className="h-9 w-16 bg-surface-container mt-1 mb-2 rounded skeleton-pulse" />
          ) : (
            <h4 className="text-3xl font-black text-primary">{avgScore}</h4>
          )}
          <div className="flex items-center mt-2 text-emerald-600 text-[10px] font-bold">Match de Alta Performance</div>
        </div>
        <div className="bg-[#E8F2EF] p-3 rounded-full text-primary">
          <span className="material-symbols-outlined">psychology</span>
        </div>
      </div>
    </section>
  );
}
