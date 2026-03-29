import type { Metadata } from "next";
import { ClientLayout } from "@/components/ClientLayout";

export const metadata: Metadata = {
  title: "BRBPO Triage Portal | The Recruiter's Studio",
  description: "Enterprise recruitment intelligence platform — BRBPO",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="light">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#F5F7F6] text-on-surface antialiased leading-relaxed">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
