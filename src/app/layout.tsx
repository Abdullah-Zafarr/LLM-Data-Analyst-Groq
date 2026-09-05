import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataMind — Ask better questions of your data",
  description: "A conversational data workspace for exploring, cleaning, visualizing, and explaining CSV datasets with Groq.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
