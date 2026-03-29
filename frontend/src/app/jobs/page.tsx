"use client";
import { useEffect, useState } from "react";
import { fetchJobs, createJob } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { Drawer } from "@/components/ui/Drawer";
import { useSearchParams } from "next/navigation";

export default function JobsPage() {
  const { toast } = useToast();
  const searchParams = useSearchParams();
  const globalQuery = searchParams.get("q") || "";
  const [jobs, setJobs] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [initialLoad, setInitialLoad] = useState(true);

  async function loadJobs() { 
    try { setJobs(await fetchJobs()); } 
    catch { toast("Erro ao buscar vagas", "A API pode estar offline.", "error"); }
    finally { setInitialLoad(false); }
  }
  useEffect(() => { loadJobs(); }, []);

  async function handleDelete(jobId: number) {
    if (!confirm("Deseja realmente excluir esta vaga?")) return;
    try {
      await import("@/lib/api").then(api => api.deleteJob(jobId));
      toast("Vaga Excluída", "A vaga foi removida do sistema.", "success");
      await loadJobs();
    } catch {
      toast("Falha ao Excluir", "Não foi possível remover a vaga.", "error");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title || !description) return;
    setLoading(true);
    try { 
      await createJob(title, description); 
      setTitle(""); 
      setDescription(""); 
      setShowForm(false); 
      await loadJobs(); 
      toast("Vaga Criada", "A oportunidade foi publicada com sucesso.", "success");
    }
    catch (err: any) { 
      toast("Falha ao criar", err.message || "Não foi possível cadastrar a vaga.", "error"); 
    }
    finally { setLoading(false); }
  }

  const filteredJobs = jobs.filter(j => 
    j.title?.toLowerCase().includes(globalQuery.toLowerCase()) ||
    j.description?.toLowerCase().includes(globalQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* HEADER SECTION */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-primary tracking-tight">Gestão de Vagas</h1>
          <p className="text-sm text-outline font-medium">Cadastre e gerencie as oportunidades ativas da BRBPO.</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm shadow-lg transition-all active:scale-95 duration-200 ${
            showForm ? "bg-white text-primary border border-outline-variant/30 hover:bg-surface-container-low shadow-none" : "bg-primary text-white hover:bg-primary-container shadow-primary/10"
          }`}
        >
          <span className="material-symbols-outlined text-lg">{showForm ? "close" : "add"}</span> 
          {showForm ? "Fechar Formulário" : "Nova Vaga"}
        </button>
      </section>

      {/* NEW JOB FORM */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-outline-variant/10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 animate-in slide-in-from-top-4 duration-300">
          <div className="flex items-center gap-3 mb-8 pb-4 border-b border-outline-variant/5">
             <div className="bg-[#E8F2EF] p-2 rounded-lg text-primary">
                <span className="material-symbols-outlined">post_add</span>
             </div>
             <h2 className="text-lg font-black text-primary">Detalhes da Oportunidade</h2>
          </div>
          
          <div className="space-y-6 max-w-3xl">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-outline ml-1">Título da Vaga</label>
              <input 
                value={title} 
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-5 py-3.5 bg-surface-container-low border border-transparent focus:border-outline-variant/30 rounded-xl text-sm font-medium focus:ring-0 transition-all placeholder:text-outline/40"
                placeholder="Ex: Engenheiro de Dados Sênior" 
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-outline ml-1">Descrição & Requisitos</label>
              <textarea 
                value={description} 
                onChange={(e) => setDescription(e.target.value)} 
                rows={6}
                className="w-full px-5 py-3.5 bg-surface-container-low border border-transparent focus:border-outline-variant/30 rounded-xl text-sm font-medium focus:ring-0 transition-all placeholder:text-outline/40 resize-none"
                placeholder="Descreva as responsabilidades, stacks necessárias e diferenciais..." 
                required
              />
            </div>
            
            <div className="flex gap-4 pt-4">
              <button 
                type="submit" 
                disabled={loading}
                className="flex items-center gap-2 bg-primary text-white px-8 py-3.5 rounded-xl font-bold text-sm shadow-xl shadow-primary/10 hover:bg-primary-container transition-all disabled:opacity-40 active:scale-[0.98]"
              >
                {loading ? (
                  <span className="material-symbols-outlined animate-spin">sync</span>
                ) : (
                  <span className="material-symbols-outlined text-lg">check_circle</span>
                )}
                {loading ? "Publicando..." : "Publicar Vaga"}
              </button>
              <button 
                type="button" 
                onClick={() => setShowForm(false)} 
                className="px-6 py-3.5 text-sm font-bold text-outline hover:text-primary transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        </form>
      )}

      {/* METRICS & LIST */}
      <section className="space-y-6">
        <div className="bg-white rounded-2xl border border-outline-variant/10 shadow-[0_1px_3px_rgba(47,93,82,0.06)] overflow-hidden">
          <div className="px-8 py-6 flex items-center justify-between border-b border-outline-variant/5 bg-surface-container-low/20">
            <div className="flex items-center gap-4">
              <h2 className="text-sm font-black text-primary uppercase tracking-widest">Painel de Vagas</h2>
              <div className="px-2.5 py-1 bg-[#E8F2EF] text-primary text-[10px] font-black rounded-md border border-outline-variant/10">
                {jobs.length} VAGAS ATIVAS
              </div>
            </div>
          </div>

          {jobs.length === 0 ? (
            <div className="py-24 text-center">
              <div className="flex flex-col items-center gap-4 max-w-xs mx-auto">
                <div className="w-16 h-16 bg-surface-container-low rounded-full flex items-center justify-center text-outline/30">
                  <span className="material-symbols-outlined text-4xl">work</span>
                </div>
                <p className="text-sm font-bold text-outline">Nenhuma vaga encontrada</p>
                <p className="text-xs text-outline/50 leading-relaxed italic">Cadastre sua primeira oportunidade para começar a triar currículos com IA.</p>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-surface-container-low/50">
                    <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-outline">Oportunidade</th>
                    <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-outline">Sumário</th>
                    <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-outline">Status</th>
                    <th className="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-outline text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10 text-sm">
                  {jobs.map((job: any) => (
                    <tr key={job.id} className="hover:bg-surface-container-low/30 transition-all group cursor-pointer" onClick={() => setSelectedJob(job)}>
                      <td className="px-8 py-6">
                        <div className="flex items-center gap-4">
                          <div className="w-11 h-11 bg-secondary-container rounded-xl flex items-center justify-center text-primary font-black text-sm shadow-sm">
                            {job.title?.charAt(0).toUpperCase() || "V"}
                          </div>
                          <p className="font-bold text-on-surface group-hover:text-primary transition-colors">{job.title}</p>
                        </div>
                      </td>
                      <td className="px-8 py-6 max-w-sm">
                        <p className="text-xs text-outline font-medium line-clamp-2 leading-relaxed">
                          {job.description}
                        </p>
                      </td>
                      <td className="px-8 py-6">
                        <span className="px-2.5 py-1 bg-[#E8F2EF] text-primary text-[9px] font-black rounded-md border border-outline-variant/10 uppercase tracking-widest">
                          Aberta
                        </span>
                      </td>
                      <td className="px-8 py-6 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={(e) => { e.stopPropagation(); handleDelete(job.id); }}
                            className="w-10 h-10 flex items-center justify-center rounded-full text-outline hover:bg-error/5 hover:text-error transition-all opacity-0 group-hover:opacity-100"
                            title="Excluir Vaga"
                          >
                             <span className="material-symbols-outlined text-[20px]">delete</span>
                          </button>
                          <button className="w-10 h-10 flex items-center justify-center rounded-full text-outline group-hover:bg-primary/5 group-hover:text-primary transition-all opacity-0 group-hover:opacity-100">
                             <span className="material-symbols-outlined">chevron_right</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* DRAWER SECTION */}
      <Drawer 
        isOpen={!!selectedJob} 
        onClose={() => setSelectedJob(null)} 
        title="Especificação da Vaga"
      >
        {selectedJob && (
          <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
            <header className="flex flex-col gap-5 border-b border-outline-variant/10 pb-8">
              <div className="w-20 h-20 bg-secondary-container rounded-3xl flex items-center justify-center text-primary font-black text-3xl shadow-lg shadow-primary/5">
                {selectedJob.title?.charAt(0).toUpperCase() || "V"}
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-black text-primary leading-tight">{selectedJob.title}</h3>
                <div className="flex gap-2">
                  <span className="px-2 py-0.5 bg-[#E8F2EF] text-primary text-[9px] font-black rounded uppercase border border-outline-variant/10">Vaga Ativa</span>
                  <span className="px-2 py-0.5 bg-surface-container-low text-outline text-[9px] font-black rounded uppercase border border-outline-variant/10">Prioridade Alta</span>
                </div>
              </div>
            </header>
            
            <section className="bg-surface-container-low/40 p-6 rounded-2xl border border-outline-variant/10 space-y-4">
              <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-outline">Requisitos & Escopo</h4>
              <p className="text-sm text-on-surface-variant leading-relaxed whitespace-pre-wrap italic">
                &quot;{selectedJob.description}&quot;
              </p>
            </section>

            <button 
              onClick={() => {
                toast("Redirecionando", "Iniciando nova esteira de triagem...", "info");
                setSelectedJob(null);
              }}
              className="w-full flex items-center justify-center gap-3 py-4 bg-primary text-white rounded-2xl font-black text-xs shadow-xl shadow-primary/10 hover:bg-primary-container transition-all active:scale-[0.98] uppercase tracking-widest"
            >
              <span className="material-symbols-outlined text-lg">rocket_launch</span>
              Iniciar Triagem IA
            </button>
          </div>
        )}
      </Drawer>
    </div>
  );
}
