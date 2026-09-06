import type { Metadata } from "next";
import "./globals.css";
import "./workbench.css";

export const metadata: Metadata = {
  title: "DataMind — Ask better questions of your data",
  description: "A conversational data workspace for exploring, cleaning, visualizing, and explaining CSV datasets with Groq.",
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "32x32" },
    ],
    shortcut: "/favicon.ico",
    apple: "/apple-icon.png",
  },
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
