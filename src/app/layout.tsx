import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataMind AI — Autonomous Conversational Data Analyst",
  description: "Autonomous data analyst translating natural language queries to sandboxed execution containers powered by Groq LPU inference.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-cyan-500/20 selection:text-cyan-300">
        {children}
      </body>
    </html>
  );
}
