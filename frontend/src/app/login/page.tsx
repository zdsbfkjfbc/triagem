"use client";
import { useState } from "react";
import { login } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/Toast";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username, password);
      window.dispatchEvent(new Event("auth-changed"));
      toast("Acesso Permitido", "Bem-vindo ao Portal de Recrutamento BRBPO.", "success");
      router.push("/triage");
    } catch (err: any) {
      toast("Falha na Identificação", err.message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#F4F7F6] text-[#15453B] flex items-center justify-center p-6 selection:bg-[#15453B] selection:text-white font-['Inter']">
      <div className="w-full max-w-[480px] bg-white rounded-[2rem] border border-slate-200/50 p-12 shadow-[0_32px_64px_-12px_rgba(21,69,59,0.08)] animate-in fade-in slide-in-from-bottom-4 duration-1000">
        
        {/* Logo Oficial do Dashboard */}
        <div className="mb-12 text-center">
            <div className="text-4xl font-black tracking-tighter text-[#15453B]">
                BRBPO
                <div className="text-[10px] uppercase tracking-[0.3em] font-bold text-slate-400 mt-1">Recruitment Engine</div>
            </div>
        </div>

        <div className="mb-10 text-center">
          <h1 className="text-2xl font-black tracking-tight mb-2">Login Recrutador</h1>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest leading-relaxed">
            Identificação de Segurança / V3.5
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 ml-1">Usuário</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-lg text-slate-300 group-focus-within:text-[#15453B] transition-colors">person</span>
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ex: admin"
                className="w-full pl-12 pr-4 py-4 bg-[#F8FAFB] border border-transparent focus:border-[#15453B]/20 rounded-2xl text-sm font-bold placeholder:text-slate-300 focus:outline-none focus:ring-4 focus:ring-[#15453B]/5 transition-all"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 ml-1">Senha</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-lg text-slate-300 group-focus-within:text-[#15453B] transition-colors">lock</span>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-12 pr-4 py-4 bg-[#F8FAFB] border border-transparent focus:border-[#15453B]/20 rounded-2xl text-sm font-bold placeholder:text-slate-300 focus:outline-none focus:ring-4 focus:ring-[#15453B]/5 transition-all"
                required
              />
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-5 bg-[#15453B] text-white rounded-2xl font-black text-sm uppercase tracking-[0.2em] shadow-[0_12px_24px_-8px_rgba(21,69,59,0.3)] hover:bg-[#1A5448] hover:scale-[1.01] transition-all disabled:opacity-30 disabled:scale-100 flex items-center justify-center gap-3 active:scale-[0.98]"
            >
              {loading ? (
                <span className="material-symbols-outlined animate-spin">sync</span>
              ) : (
                <>
                    <span>Entrar no Sistema</span>
                    <span className="material-symbols-outlined text-xl">login</span>
                </>
              )}
            </button>
          </div>
        </form>

        <div className="mt-12 pt-8 border-t border-slate-100 text-center">
            <p className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">
                Proteção por Arquitetura JWT & Resiliência IA<br/>
                BRBPO Business Intelligence &middot; 2026
            </p>
        </div>
      </div>
    </div>
  );
}
