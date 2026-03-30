"use client";
import { useEffect, useState, useRef } from "react";
import { fetchJobs, runTriage, getTriageStatus, getTriageErrors } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export default function TriagePage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<number | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("google/gemini-2.0-flash-lite-preview-02-05:free");
  const [files, setFiles] = useState<File[]>([]);
  const [status, setStatus] = useState<"idle" | "processing" | "done" | "error">("idle");
  const [progress, setProgress] = useState<{ total: number; processed: number; percent: number; status?: string } | null>(null);
  const [errors, setErrors] = useState<any[]>([]);
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollInFlightRef = useRef(false);

  useEffect(() => { 
    fetchJobs()
      .then(setJobs)
      .catch(() => toast("Erro de Conexão", "Não foi possível carregar as vagas.", "error")); 

    return () => {
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, []);

  async function startPolling(jobId: number) {
    if (pollingRef.current) clearInterval(pollingRef.current);
    
    let errorCount = 0;
    const MAX_ERRORS = 3;

    pollingRef.current = setInterval(async () => {
      if (pollInFlightRef.current) return;
      pollInFlightRef.current = true;
      try {
        const statusData = await getTriageStatus(jobId);
        errorCount = 0; // Reset errors on success
        
        setProgress({ total: statusData.total, processed: statusData.processed, percent: statusData.percent });
        
        if (statusData.status === "completed" || statusData.status === "failed") {
          if (pollingRef.current) clearInterval(pollingRef.current);
          setStatus(statusData.status === "completed" ? "done" : "error");
          
          const errorData = await getTriageErrors(jobId);
          setErrors(errorData);
          
          if (statusData.status === "completed") {
            toast("Finalizado", "Processamento em lote concluído com sucesso.", "success");
          } else {
            toast("Lote com Falhas", "Alguns arquivos não puderam ser processados.", "error");
          }
        }
      } catch (e: any) {
        errorCount++;
        // Só interrompe se os erros persistirem por várias tentativas (ex: falha de rede real)
        if (errorCount >= MAX_ERRORS) {
          console.error("Polling failure:", e);
          if (pollingRef.current) clearInterval(pollingRef.current);
          setStatus("error");
          toast("Erro de Monitoramento", "Não foi possível sincronizar o progresso.", "error");
        }
      } finally {
        pollInFlightRef.current = false;
      }
    }, 5000);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith(".pdf") || f.name.endsWith(".txt"));
    setFiles(prev => [...prev, ...dropped]);
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files) setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
  }

  async function handleSubmit() {
    if (!apiKey || !selectedJob || files.length === 0) return;
    setStatus("processing");
    setErrors([]);
    setProgress({ total: files.length, processed: 0, percent: 0 });
    
    try { 
      await runTriage(apiKey, model, selectedJob, files); 
      // Iniciamos o monitoramento em tempo real (HUD)
      startPolling(selectedJob);
    }
    catch (err: any) { 
      setStatus("error"); 
      // Extrai a mensagem de erro real do backend (passada via Error.message em lib/api.ts)
      const msg = err.message || "Ocorreu um erro desconhecido no processamento.";
      toast("Falha na Triagem", msg, "error");
    }
  }

  const AI_MODELS = [
    { id: "z-ai/glm-4.5-air:free", name: "GLM 4.5 Air (Free)", provider: "Z.ai" },
    { id: "google/gemini-2.0-flash-lite-preview-02-05:free", name: "Gemini 2.0 Flash Lite (Free)", provider: "Google" },
    { id: "meta-llama/llama-3.3-70b-instruct:free", name: "Llama 3.3 70B Instruct (Free)", provider: "Meta" },
    { id: "deepseek/deepseek-r1:free", name: "DeepSeek R1 (Free)", provider: "DeepSeek" },
    { id: "qwen/qwen-2.5-72b-instruct:free", name: "Qwen 2.5 72B (Free)", provider: "Alibaba" },
    { id: "google/gemma-3-27b-it:free", name: "Gemma 3 27B (Free)", provider: "Google" },
    { id: "google/gemma-3-12b-it:free", name: "Gemma 3 12B (Free)", provider: "Google" },
    { id: "google/gemma-3-4b-it:free", name: "Gemma 3 4B (Free)", provider: "Google" },
    { id: "google/gemma-3n-e4b-it:free", name: "Gemma 3n 4B (Free)", provider: "Google" },
    { id: "google/gemma-3n-e2b-it:free", name: "Gemma 3n 2B (Free)", provider: "Google" },
    { id: "mistralai/mistral-7b-instruct:free", name: "Mistral 7B (Free)", provider: "Mistral" },
    { id: "microsoft/phi-3-medium-128k-instruct:free", name: "Phi-3 Medium (Free)", provider: "Microsoft" },
    { id: "nvidia/nemotron-3-super-120b-a12b:free", name: "Nemotron 3 Super (Free)", provider: "Nvidia" },
    { id: "nvidia/nemotron-3-nano-30b-a3b:free", name: "Nemotron 3 Nano 30B (Free)", provider: "Nvidia" },
    { id: "nvidia/nemotron-nano-12b-v2-vl:free", name: "Nemotron Nano 12B VL (Free)", provider: "Nvidia" },
    { id: "nvidia/nemotron-nano-9b-v2:free", name: "Nemotron Nano 9B V2 (Free)", provider: "Nvidia" },
    { id: "nvidia/llama-nemotron-embed-vl-1b-v2:free", name: "Llama Nemotron Embed 1B (Free)", provider: "Nvidia" },
    { id: "google/learnlm-1.5-pro-experimental:free", name: "LearnLM 1.5 Pro (Free)", provider: "Google" },
    { id: "liquid/lfm-2.5-1.2b:free", name: "Liquid LFM-2.5 (Free)", provider: "Liquid" },
    { id: "liquid/lfm-2.5-1.2b-thinking:free", name: "Liquid LFM-2.5 Thinking (Free)", provider: "Liquid" },
    { id: "liquid/lfm-2.5-1.2b-instruct:free", name: "Liquid LFM-2.5 Instruct (Free)", provider: "Liquid" },
    { id: "stepfun/step-3.5-flash:free", name: "Step 3.5 Flash (Free)", provider: "StepFun" },
    { id: "arcee-ai/trinity-large-preview:free", name: "Trinity Large Preview (Free)", provider: "Arcee AI" },
    { id: "arcee-ai/trinity-mini:free", name: "Trinity Mini (Free)", provider: "Arcee AI" },
    { id: "minimax/minimax-m2.5:free", name: "MiniMax M2.5 (Free)", provider: "MiniMax" },
    { id: "qwen/qwen3-coder:free", name: "Qwen 3 Coder 480B (Free)", provider: "Qwen" },
    { id: "qwen/qwen3-next-80b-a3b-instruct:free", name: "Qwen 3 Next 80B Instruct (Free)", provider: "Qwen" },
    { id: "openai/gpt-oss-120b:free", name: "GPT OSS 120B (Free)", provider: "OpenAI" },
    { id: "openai/gpt-oss-20b:free", name: "GPT OSS 20B (Free)", provider: "OpenAI" },
    { id: "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", name: "Venice Uncensored (Free)", provider: "Cognitive Computations" },
    { id: "nousresearch/hermes-3-llama-3.1-405b:free", name: "Hermes 3 405B Instruct (Free)", provider: "NousResearch" },
    { id: "meta-llama/llama-3.2-3b-instruct:free", name: "Llama 3.2 3B Instruct (Free)", provider: "Meta" },
    { id: "openrouter/free", name: "Auto-Selection (Router)", provider: "OpenRouter" },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-20">
      {/* HEADER */}
      <section className="space-y-1">
        <h1 className="text-3xl font-black text-primary tracking-tight">Motor de Triagem IA (HUD V3.3)</h1>
        <p className="text-sm text-outline font-medium">Acompanhe o processamento inteligente em tempo real.</p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* CONFIGURATION SIDEBAR */}
        <aside className="lg:col-span-4 space-y-6">
          <div className="bg-white p-8 rounded-2xl border border-outline-variant/10 shadow-sm">
            <div className="flex items-center gap-3 mb-8 pb-4 border-b border-outline-variant/5 text-primary">
               <span className="material-symbols-outlined text-xl">settings_input_composite</span>
               <h2 className="text-sm font-black uppercase tracking-widest">Configuração</h2>
            </div>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-outline ml-1">Chave OpenRouter</label>
                <div className="relative group">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-outline">key</span>
                  <input 
                    type="password" 
                    value={apiKey} 
                    onChange={(e) => setApiKey(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-surface-container-low border border-transparent focus:border-outline-variant/30 rounded-xl text-xs font-medium focus:ring-0 transition-all placeholder:text-outline/40"
                    placeholder="sk-or-..." 
                  />
                </div>
              </div>

              {/* Novo Seletor de Inteligência IA */}
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-outline ml-1">Cérebro IA (Model)</label>
                <div className="relative group">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-outline">psychology</span>
                  <select 
                    value={model} 
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-surface-container-low border border-transparent focus:border-outline-variant/30 rounded-xl text-xs font-bold text-primary focus:ring-0 transition-all appearance-none cursor-pointer"
                  >
                    {AI_MODELS.map((m) => (
                        <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-outline ml-1">Vaga de Referência</label>
                <div className="relative group">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-outline">work</span>
                  <select 
                    value={selectedJob ?? ""} 
                    onChange={(e) => setSelectedJob(Number(e.target.value))}
                    className="w-full pl-10 pr-4 py-3 bg-surface-container-low border border-transparent focus:border-outline-variant/30 rounded-xl text-xs font-bold text-primary focus:ring-0 transition-all appearance-none cursor-pointer"
                  >
                    <option value="" disabled>Selecione a vaga alvo...</option>
                    {jobs.map((j: any) => <option key={j.id} value={j.id}>{j.title}</option>)}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {files.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-outline-variant/10">
              <div className="flex items-center justify-between mb-4 border-b border-outline-variant/5 pb-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-outline">Conteúdo do Lote</p>
                <button onClick={() => setFiles([])} className="text-[10px] font-bold text-error uppercase hover:underline">Limpar</button>
              </div>
              <div className="space-y-2 max-h-56 overflow-y-auto pr-2 custom-scrollbar text-[11px] font-bold text-on-surface">
                {files.map((file, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2.5 bg-surface-container-low rounded-xl border border-transparent">
                    <span className="material-symbols-outlined text-lg text-primary">description</span>
                    <span className="truncate flex-1">{file.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* UPLOAD & PROCESSING ZONE */}
        <div className="lg:col-span-8 space-y-8">
          {status !== "processing" ? (
             <div
             onDrop={handleDrop}
             onDragOver={(e) => e.preventDefault()}
             onClick={() => fileInputRef.current?.click()}
             className={`bg-white rounded-[2rem] border-2 border-dashed p-16 text-center cursor-pointer transition-all duration-300 group shadow-sm ${
               files.length > 0 ? "border-primary/40 bg-[#E8F2EF]/20" : "border-outline-variant/30 hover:border-primary hover:bg-[#E8F2EF]/10"
             }`}
           >
             <input ref={fileInputRef} type="file" multiple accept=".pdf,.txt" onChange={handleFileSelect} className="hidden" />
             <div className="w-20 h-20 bg-[#E8F2EF] rounded-full flex items-center justify-center text-primary mx-auto mb-6 group-hover:scale-110 transition-transform duration-500 shadow-lg shadow-primary/5">
                <span className="material-symbols-outlined text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>cloud_upload</span>
             </div>
             <h3 className="text-xl font-black text-primary mb-2 tracking-tight">Deposite os Currículos</h3>
             <p className="text-sm font-medium text-outline max-w-xs mx-auto mb-2">PDF ou TXT para análise imediata em segundo plano.</p>
           </div>
          ) : (
            /* HUD DE PROGRESSO REAL (Ciclo 3) */
            <div className="bg-white rounded-[2rem] border border-outline-variant/10 p-12 text-center shadow-xl animate-in zoom-in duration-500">
               <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center text-primary mx-auto mb-8 relative">
                  <span className="material-symbols-outlined text-5xl animate-spin">sync</span>
                  <div className="absolute -bottom-1 -right-1 bg-primary text-white text-[10px] font-black w-8 h-8 rounded-full flex items-center justify-center shadow-lg">
                    {progress?.percent}%
                  </div>
               </div>
               <h3 className="text-2xl font-black text-primary mb-4 tracking-tight">Processando Inteligência</h3>
               
               <div className="max-w-md mx-auto space-y-4">
                  <div className="h-4 bg-surface-container-low rounded-full overflow-hidden border border-outline-variant/5">
                    <div 
                      className="h-full bg-primary transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(47,93,82,0.3)]"
                      style={{ width: `${progress?.percent}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] font-black uppercase tracking-widest text-outline">
                    <span>{progress?.processed} de {progress?.total} arquivos</span>
                    <span>{progress?.status === 'running' ? 'Executando...' : 'Finalizando...'}</span>
                  </div>
               </div>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={status === "processing" || !apiKey || !selectedJob || files.length === 0}
            className="w-full py-5 bg-primary text-white rounded-2xl font-black text-sm uppercase tracking-[0.2em] shadow-lg hover:bg-primary-container disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-[0.98] flex items-center justify-center gap-3"
          >
            {status === "processing" ? (
              <span className="material-symbols-outlined animate-spin">sync</span>
            ) : (
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>bolt</span>
            )}
            {status === "processing" ? "Ocultando em Background..." : `Iniciar Triagem Resiliente`}
          </button>

          {/* RELATÓRIO DE ERROS (Ciclo 3) */}
          {errors.length > 0 && (
            <div className="bg-red-50 rounded-2xl p-8 border border-red-200 animate-in slide-in-from-top-4 duration-500">
              <div className="flex items-center gap-3 mb-6 text-error">
                <span className="material-symbols-outlined">warning</span>
                <h4 className="font-black uppercase text-xs tracking-widest">Relatório de Erros de Processamento</h4>
              </div>
              <div className="space-y-3">
                {errors.map((err, i) => (
                  <div key={i} className="flex gap-4 p-4 bg-white/60 rounded-xl border border-red-100 text-xs">
                    <span className="font-black text-error whitespace-nowrap">[{err.file_name}]</span>
                    <span className="font-medium text-error/80">{err.error}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {status === "done" && (
            <div className="bg-[#E8F2EF] rounded-2xl p-8 border border-primary/20 animate-in zoom-in duration-500 shadow-lg">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center text-primary shadow-sm border border-primary/10">
                   <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>task_alt</span>
                </div>
                <div>
                  <h4 className="font-black text-primary uppercase text-xs tracking-widest">Triagem Lote Concluída</h4>
                  <p className="text-sm font-medium text-primary/70">O processamento foi finalizado. Confira os resultados no Talent Pool.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
