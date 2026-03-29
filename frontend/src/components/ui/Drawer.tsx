"use client";
import { useEffect } from "react";

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Drawer({ isOpen, onClose, title, children }: DrawerProps) {
  useEffect(() => {
    if (isOpen) { document.body.style.overflow = "hidden"; }
    else { document.body.style.overflow = "unset"; }
    return () => { document.body.style.overflow = "unset"; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-[100] transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />
      <div 
        className="fixed inset-y-0 right-0 w-full max-w-md bg-surface shadow-2xl z-[101] transform transition-transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-surface-container">
          <h2 id="drawer-title" className="text-lg font-bold text-on-surface">{title}</h2>
          <button 
            onClick={onClose}
            aria-label="Fechar painel de detalhes"
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container-low transition-colors text-slate-500 hover:text-error"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>
      </div>
    </>
  );
}
