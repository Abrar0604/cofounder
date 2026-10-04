import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from '@clerk/nextjs'
import { SuppressWarning } from "@/components/suppress-warning";
import { TooltipProvider } from "@/components/ui/tooltip";
import { VariantProvider } from "@/components/experiments/variant-provider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Swarn",
  description: "Swarn venture dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html
        lang="en"
        className={`${inter.variable} h-full antialiased font-sans`}
        style={{ "--font-sans": "var(--font-inter)" } as React.CSSProperties}
      >
        <body className="min-h-full flex flex-col font-sans">
          <SuppressWarning />
          <VariantProvider>
            <TooltipProvider>{children}</TooltipProvider>
          </VariantProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
