"use client";

import Link from "next/link";

interface RecentCandidatesTableProps {
  candidates: any[];
  initialLoad: boolean;
  onSelect: (candidate: any) => void;
}

export function RecentCandidatesTable({ candidates, initialLoad, onSelect }: RecentCandidatesTableProps) {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-black text-[#191c1c] tracking-tight">Candidatos Recentes</h2>
        <Link href="/talent" className="text-sm font-bold text-primary hover:underline flex items-center gap-1">
          Ver todos <span className="material-symbols-outlined text-sm">arrow_forward</span>
        </Link>
      </div>
      
      <div className="bg-white rounded-lg shadow-[0_1px_3px_rgba(47,93,82,0.08)] overflow-hidden border border-outline-variant/10">
         <table className="w-full text-left border-collapse">
          <thead className="bg-surface-container-low border-b border-outline-variant/10">
            <tr>
              <th className="px-6 py-4 text-[11px] font-black uppercase tracking-widest text-outline">Nome</th>
              <th className="px-6 py-4 text-[11px] font-black uppercase tracking-widest text-outline">Vaga</th>
              <th className="px-6 py-4 text-[11px] font-black uppercase tracking-widest text-outline">Score</th>
              <th className="px-6 py-4 text-[11px] font-black uppercase tracking-widest text-outline text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/10 text-sm">
            {candidates.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-outline/50 italic">
                  {initialLoad ? "Carregando dados..." : "Nenhum candidato triado ainda."}
                </td>
              </tr>
            ) : (
              candidates.map((c, i) => (
                <tr 
                   key={i} 
                   onClick={() => onSelect(c)}
                   className="hover:bg-surface-container-low/50 transition-colors group cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-secondary-container flex items-center justify-center text-primary font-black text-[10px]">
                        {c.candidate_name?.split(" ").map((n: string) => n[0]).join("").slice(0, 2) || "??"}
                      </div>
                      <div>
                        <p className="font-bold text-on-surface">{c.candidate_name}</p>
                        <p className="text-[10px] text-outline">{c.date ? new Date(c.date).toLocaleDateString("pt-BR") : "—"}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-medium text-on-surface-variant">{c.job_title}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 ${Number(c.score) >= 8 ? "bg-[#E8F2EF] text-primary" : "bg-surface-container text-outline"} text-[10px] font-black rounded`}>
                      {c.score?.toFixed(1) || "0.0"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                     <button 
                       onClick={(e) => {
                         e.stopPropagation();
                         onSelect(c);
                       }}
                       className="material-symbols-outlined text-outline hover:text-primary transition-colors text-lg"
                     >
                       more_vert
                     </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
         </table>
      </div>
    </section>
  );
}
