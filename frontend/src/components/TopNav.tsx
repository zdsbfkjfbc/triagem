"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";
import { useToast } from "@/components/ui/Toast";

export function TopNav() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [query, setQuery] = useState(searchParams.get("q") || "");

  // Sync with URL changes
  useEffect(() => {
    setQuery(searchParams.get("q") || "");
  }, [searchParams]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams);
    if (query) {
      params.set("q", query);
      toast("Buscando...", `Filtrando resultados por "${query}"`, "info");
    } else {
      params.delete("q");
    }
    router.push(`?${params.toString()}`);
  };

  return (
    <header className="fixed top-0 right-0 w-[calc(100%-16rem)] z-40 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex justify-between items-center px-8 h-16 ml-64 font-['Inter'] text-sm tracking-wide border-b border-outline-variant/10">
      <form onSubmit={handleSearch} className="flex items-center bg-surface-container-low rounded-full px-4 py-2 w-96 focus-within:ring-2 focus-within:ring-primary/10 transition-all border border-transparent focus-within:border-outline-variant/30">
        <span className="material-symbols-outlined text-outline text-lg">search</span>
        <input 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-outline/60 px-2" 
          placeholder="Buscar candidatos, vagas ou eventos..." 
          type="text" 
        />
      </form>
      
      <div className="flex items-center gap-4">
        <button 
          onClick={() => toast("Notificações", "Você não possui novos alertas de triagem.", "info")}
          className="hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full p-2 transition-all relative text-primary dark:text-emerald-400 flex items-center justify-center"
        >
          <span className="material-symbols-outlined">notifications</span>
          <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border-2 border-white"></span>
        </button>
        <button 
          onClick={() => toast("Suporte BRBPO", "Como podemos ajudar hoje? Central de ajuda em breve.", "info")}
          className="hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full p-2 transition-all text-slate-400 flex items-center justify-center"
        >
          <span className="material-symbols-outlined">help_outline</span>
        </button>
        
        <div className="h-8 w-[1px] bg-outline-variant/30 mx-2"></div>
        
        <div className="flex items-center gap-2">
          <span className="font-bold text-primary">Dashboard</span>
        </div>
      </div>
    </header>
  );
}
