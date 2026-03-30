"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useToast } from "@/components/ui/Toast";

const SIDE_LINKS = [
  { href: "/", label: "Dashboard", icon: "dashboard" },
  { href: "/talent", label: "Candidatos", icon: "group" },
  { href: "/jobs", label: "Vagas", icon: "work" },
  { href: "/triage", label: "Nova Triagem", icon: "upload_file" },
  // { href: "#", label: "Calendário", icon: "calendar_today" },
  // { href: "#", label: "Relatórios", icon: "bar_chart" },
];

export function SideNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { toast } = useToast();
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    window.dispatchEvent(new Event("auth-changed"));
    setShowProfileMenu(false);
    toast("Sessão Encerrada", "Você foi desconectado com segurança do Arquivo BRBPO.", "success");
    router.push("/login");
  };

  return (
    <aside className="h-screen w-64 fixed left-0 top-0 bg-white dark:bg-slate-900 shadow-[4px_0_24px_rgba(47,93,82,0.04)] shadow-xl dark:shadow-none z-50 flex flex-col py-4 font-['Inter'] antialiased text-sm font-medium">
      <div className="text-2xl font-black tracking-tighter text-primary dark:text-emerald-500 px-6 py-8">
        BRBPO
        <div className="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-400 mt-1">Recruitment Engine</div>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 py-6">
        {SIDE_LINKS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                isActive 
                  ? "bg-primary text-white shadow-lg shadow-primary/10" 
                  : "text-outline hover:bg-surface-container-low hover:text-primary"
              }`}
            >
              <span className={`material-symbols-outlined text-[20px] ${isActive ? "" : "group-hover:scale-110 transition-transform"}`}>
                {item.icon}
              </span>
              <span className="text-xs font-bold tracking-wide">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-outline-variant/10 relative">
        {showProfileMenu && (
          <div className="absolute bottom-full left-4 right-4 mb-2 bg-white rounded-2xl shadow-2xl border border-outline-variant/10 overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-200 z-50">
            <button 
              onClick={() => {
                setShowProfileMenu(false);
                toast("Configurações", "O módulo de ajustes do Gestor será liberado na V7.", "info");
              }}
              className="w-full px-4 py-3 flex items-center gap-3 text-xs font-bold text-outline hover:bg-surface-container-low transition-colors"
            >
              <span className="material-symbols-outlined text-lg">settings</span> Configurações
            </button>
            <button 
              onClick={handleLogout}
              className="w-full px-4 py-3 flex items-center gap-3 text-xs font-bold text-error border-t border-outline-variant/5 hover:bg-error/5 transition-colors"
            >
              <span className="material-symbols-outlined text-lg">logout</span> Sair do Sistema
            </button>
          </div>
        )}
        <div 
          onClick={() => setShowProfileMenu(!showProfileMenu)}
          className="flex items-center gap-3 p-3 rounded-2xl bg-surface-container-low/50 group hover:bg-surface-container-low transition-colors cursor-pointer"
        >
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-black text-xs shadow-md shadow-primary/5 group-hover:scale-105 transition-transform">
             SA
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[11px] font-black text-on-surface truncate">Gestor BRBPO</p>
            <p className="text-[10px] text-outline font-medium truncate uppercase tracking-tighter">System Admin</p>
          </div>
          <span className={`material-symbols-outlined text-outline text-lg transition-transform ${showProfileMenu ? "rotate-180" : ""}`}>keyboard_arrow_up</span>
        </div>
      </div>
    </aside>
  );
}
