import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import NavBar from "@/components/layout/NavBar";
import Footer from "@/components/layout/Footer";
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
    <html lang="fr" className="dark">
      <body className={`${inter.className} bg-background text-foreground min-h-screen flex flex-col`}>
        <NodeProvider>
          <NavBar />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </NodeProvider>
      </body>
    </html>
  );
}
