"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchJobs, fetchTalentPool, deleteTalentResult } from "@/lib/api";
import { Drawer } from "@/components/ui/Drawer";
import { useToast } from "@/components/ui/Toast";
import { parseAnalysisData, formatAnalysisList } from "@/lib/utils";
import { StatsGrid } from "@/components/dashboard/StatsGrid";
import { RecentCandidatesTable } from "@/components/dashboard/RecentCandidatesTable";

export default function Dashboard() {
  const [jobCount, setJobCount] = useState("—");
  const [candidateCount, setCandidateCount] = useState("—");
  const [avgScore, setAvgScore] = useState("—");
  const [recentCandidates, setRecentCandidates] = useState<any[]>([]);
  const [initialLoad, setInitialLoad] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const { toast } = useToast();

  useEffect(() => {
    async function load() {
      try {
        const [jobs, talent] = await Promise.all([fetchJobs(), fetchTalentPool()]);
        setJobCount(String(jobs.length));
        setCandidateCount(String(talent.length));
        
        const avg = talent.length > 0
          ? (talent.reduce((s: number, t: any) => s + (t.score || 0), 0) / talent.length).toFixed(1)
          : "0";
        setAvgScore(avg);
        
        const sorted = [...talent].sort((a: any, b: any) => 
          new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime()
        ).slice(0, 5);
        setRecentCandidates(sorted);
        
      } catch (err) {
        console.error("Dashboard load error:", err);
      } finally {
        setInitialLoad(false);
      }
    }
    load();
  }, []);

  const analysis = selectedCandidate ? parseAnalysisData(selectedCandidate.analysis) : null;

  return (
    <div className="space-y-10">
      <StatsGrid 
        initialLoad={initialLoad} 
        jobCount={jobCount} 
        candidateCount={candidateCount} 
        avgScore={avgScore} 
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-12 space-y-8">
          <RecentCandidatesTable 
            candidates={recentCandidates} 
            initialLoad={initialLoad} 
            onSelect={setSelectedCandidate} 
          />

          <section className="bg-white p-6 rounded-lg shadow-[0_1px_3px_rgba(47,93,82,0.08)] border border-outline-variant/10">
            <h2 className="text-sm font-black text-[#191c1c] uppercase tracking-widest mb-6 pb-2 border-b border-outline-variant/10">Comandos Expressos</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link href="/jobs" className="flex items-center gap-3 p-4 rounded-xl bg-surface-container-low hover:bg-[#E8F2EF] group transition-all duration-200">
                <span className="material-symbols-outlined text-primary p-2 bg-white rounded-lg shadow-sm">add_task</span>
                <span className="text-xs font-bold text-on-surface-variant">Nova Vaga</span>
              </Link>
              <Link href="/triage" className="flex items-center gap-3 p-4 rounded-xl bg-surface-container-low hover:bg-[#E8F2EF] group transition-all duration-200">
                <span className="material-symbols-outlined text-primary p-2 bg-white rounded-lg shadow-sm">rocket_launch</span>
                <span className="text-xs font-bold text-on-surface-variant">Triagem IA</span>
              </Link>
              <Link href="/talent" className="flex items-center gap-3 p-4 rounded-xl bg-surface-container-low hover:bg-[#E8F2EF] group transition-all duration-200">
                <span className="material-symbols-outlined text-primary p-2 bg-white rounded-lg shadow-sm">database</span>
                <span className="text-xs font-bold text-on-surface-variant">Talent Pool</span>
              </Link>
            </div>
          </section>
        </div>
      </div>

      <Drawer 
        isOpen={!!selectedCandidate} 
        onClose={() => setSelectedCandidate(null)} 
        title="Perfil do Talento"
      >
        {selectedCandidate && (
          <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300 pb-20">
            <header className="flex items-center gap-5 border-b border-outline-variant/10 pb-8">
              <div className="w-20 h-20 bg-secondary-container rounded-3xl flex items-center justify-center text-primary font-black text-3xl shadow-lg shadow-primary/5">
                {selectedCandidate.candidate_name?.split(" ").map((n: string) => n[0]).join("").slice(0, 2) || "??"}
              </div>
              <div className="space-y-1">
                <h3 className="text-2xl font-black text-primary leading-tight">{selectedCandidate.candidate_name}</h3>
                <p className="text-sm font-bold text-outline flex items-center gap-2">
                   <span className="material-symbols-outlined text-base">work</span>
                   {selectedCandidate.job_title}
                </p>
              </div>
            </header>
            
            <section className="bg-surface-container-low/40 p-6 rounded-2xl border border-outline-variant/10 space-y-6">
              <div className="flex items-center justify-between">
                 <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-outline">Análise do Match IA</h4>
                 <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>psychology</span>
              </div>
              
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                   <span className="text-sm font-bold text-on-surface">Compatibilidade Técnica</span>
                   <span className="text-xl font-black text-primary">{(selectedCandidate.score * 10).toFixed(0)}%</span>
                </div>
                <div className="w-full h-2.5 bg-white rounded-full overflow-hidden border border-outline-variant/10">
                   <div className="h-full bg-primary rounded-full" style={{ width: `${selectedCandidate.score * 10}%` }}></div>
                </div>
              </div>

              <div className="space-y-4">
                <p className="text-xs font-black text-outline uppercase tracking-widest">Parecer Detalhado do Sistema</p>
                <div className="text-sm text-on-surface-variant leading-relaxed space-y-3">
                  {!analysis || (!analysis.verdict && !analysis.strengths && !analysis.gaps && !analysis.interviewQuestion) ? (
                    <p className="text-outline/60 italic">Este candidato ainda não possui uma análise detalhada estruturada.</p>
                  ) : (
                    <>
                      <p className="font-bold text-primary italic">"{analysis.verdict}"</p>
                      
                      {analysis.strengths && (
                        <div className="pt-2">
                          <p className="font-black text-[10px] uppercase text-emerald-600 tracking-wider">Pontos Fortes:</p>
                          <ul className="list-disc list-inside space-y-1 mt-1">
                            {formatAnalysisList(analysis.strengths).map((item, i) => (
                              <li key={i} className="text-on-surface-variant font-medium leading-relaxed">{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {analysis.gaps && (
                        <div className="pt-2">
                          <p className="font-black text-[10px] uppercase text-amber-600 tracking-wider">Lacunas Técnicas:</p>
                          <ul className="list-disc list-inside space-y-1 mt-1">
                            {formatAnalysisList(analysis.gaps).map((item, i) => (
                              <li key={i} className="text-on-surface-variant font-medium leading-relaxed">{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {analysis.interviewQuestion && (
                        <div className="pt-4 p-4 bg-primary/5 rounded-xl border border-primary/10">
                          <p className="font-black text-[10px] uppercase text-primary tracking-widest mb-2 flex items-center gap-2">
                            <span className="material-symbols-outlined text-xs">quiz</span> Sugestão de Pergunta
                          </p>
                          <p className="text-sm font-bold text-primary leading-relaxed italic">
                            "{Array.isArray(analysis.interviewQuestion) ? analysis.interviewQuestion[0] : analysis.interviewQuestion}"
                          </p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-outline">Dados do Currículo (Texto Original)</h4>
                <span className="material-symbols-outlined text-outline/40">description</span>
              </div>
              <div className="bg-surface-container-low/20 p-4 rounded-xl border border-outline-variant/10 max-h-64 overflow-y-auto custom-scrollbar">
                 <pre className="text-[11px] text-on-surface-variant whitespace-pre-wrap font-sans leading-relaxed">
                   {selectedCandidate.original_text || "Texto indisponível."}
                 </pre>
              </div>
            </section>

            <div className="grid grid-cols-2 gap-4">
              <button 
                onClick={() => toast("Abrindo Currículo", "Visualizando documento original...", "info")}
                className="flex flex-col items-center gap-3 p-5 border-2 border-outline-variant/20 rounded-2xl hover:border-primary/30 hover:bg-surface-container-low transition-all group"
              >
                <span className="material-symbols-outlined text-outline group-hover:text-primary transition-colors">description</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-outline group-hover:text-primary">Ver Currículo</span>
              </button>
              <button 
                onClick={() => toast("Contato", "Iniciando fluxo de contato...", "success")}
                className="flex flex-col items-center gap-3 p-5 bg-primary rounded-2xl shadow-lg shadow-primary/10 hover:bg-primary-container transition-all"
              >
                <span className="material-symbols-outlined text-white">mail</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-white">Enviar E-mail</span>
              </button>
            </div>
            
            <div className="pt-4 border-t border-red-500/10 mt-4">
              <button 
                onClick={async () => {
                  try {
                    await deleteTalentResult(selectedCandidate.id);
                    toast("Candidato Excluído", "Registro removido com sucesso.", "success");
                    setSelectedCandidate(null);
                    setTimeout(() => window.location.reload(), 500); 
                  } catch(e) {
                     toast("Erro", "Não foi possível excluir o resultado.", "error");
                  }
                }}
                className="w-full flex items-center justify-center gap-3 p-4 border-2 border-red-500/20 bg-red-50/50 rounded-2xl hover:bg-red-50 transition-all group"
              >
                <span className="material-symbols-outlined text-red-500 group-hover:text-red-700 transition-colors">delete</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-red-500 group-hover:text-red-700">Excluir Resultado</span>
              </button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
