"use client";
import { createContext, useContext, useState, ReactNode } from "react";

type ToastType = "success" | "error" | "info";

interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

interface ToastContextType {
  toast: (title: string, message?: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used within ToastProvider");
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const toast = (title: string, message?: string, type: ToastType = "info") => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, title, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-[200] flex flex-col gap-3">
        {toasts.map((t) => (
          <div 
            key={t.id} 
            className={`min-w-[300px] flex items-start gap-3 p-4 rounded-xl shadow-xl border bg-surface transform transition-all duration-300 translate-y-0 opacity-100 ${
              t.type === "success" ? "border-emerald-200" :
              t.type === "error" ? "border-error/20" :
              "border-outline-variant/20"
            }`}
          >
            <span className={`material-symbols-outlined mt-0.5 ${
              t.type === "success" ? "text-emerald-500" :
              t.type === "error" ? "text-error" :
              "text-primary"
            }`}>
              {t.type === "success" ? "check_circle" : t.type === "error" ? "error" : "info"}
            </span>
            <div>
              <p className="font-bold text-sm text-on-surface">{t.title}</p>
              {t.message && <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">{t.message}</p>}
            </div>
            <button 
              onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))}
              className="ml-auto text-slate-400 hover:text-on-surface"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
