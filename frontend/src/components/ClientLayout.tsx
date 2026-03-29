"use client";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { TopNav } from "@/components/TopNav";
import { SideNav } from "@/components/Sidebar";
import { ToastProvider } from "@/components/ui/Toast";
import "./../app/globals.css";

function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const checkAuth = () => {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      if (!token && pathname !== "/login") {
        setAuthorized(false);
        router.push("/login");
      } else {
        setAuthorized(true);
      }
    };

    checkAuth();
    window.addEventListener("auth-changed", checkAuth);
    window.addEventListener("storage", (e) => {
        if (e.key === "access_token") checkAuth();
    });
    
    return () => {
        window.removeEventListener("auth-changed", checkAuth);
    };
  }, [pathname, router]);

  if (!authorized && pathname !== "/login") return (
    <div className="min-h-screen bg-[#F9F9F7] flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-1000">
        <div className="w-16 h-1 bg-black mb-8 animate-pulse"></div>
        <div className="font-black tracking-[0.4em] text-[10px] uppercase text-black/40">
            Arquivo BRBPO / Verificando Acreditação
        </div>
    </div>
  );
  
  return <>{children}</>;
}

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  return (
    <ToastProvider>
      <AuthGuard>
        {!isLoginPage && <TopNav />}
        {!isLoginPage && <SideNav />}
        <main id="main-content" className={`${isLoginPage ? "" : "ml-64 pt-24 px-8 pb-12"} min-h-screen bg-[#F5F7F6] transition-all duration-500`}>
          {children}
        </main>
        {!isLoginPage && (
          <Link 
            href="/triage" 
            aria-label="Nova Triagem" 
            className="fixed bottom-8 right-8 w-14 h-14 bg-primary text-white rounded-full shadow-[0_10px_30px_rgba(21,69,59,0.3)] flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-50 group border border-white/10"
          >
            <span className="material-symbols-outlined text-2xl group-hover:rotate-12 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>bolt</span>
          </Link>
        )}
      </AuthGuard>
    </ToastProvider>
  );
}
