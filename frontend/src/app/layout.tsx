import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { NodeProvider } from "@/lib/contexts/NodeContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Daznode - Lightning Node Dashboard",
  description: "Application de monitoring pour nœuds Lightning Network",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${inter.className} bg-[#0F0F14] text-white`}>
        <NodeProvider>
          {children}
        </NodeProvider>
      </body>
    </html>
  );
}
