import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from '@clerk/nextjs'
import Script from 'next/script'
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
          <Script id="suppress-clerk-warning" strategy="beforeInteractive">
            {`
              const originalError = console.error;
              const originalWarn = console.warn;
              const originalLog = console.log;
              console.error = (...args) => {
                if (typeof args[0] === 'string' && args[0].includes('Clerk has been loaded with development keys')) return;
                originalError(...args);
              };
              console.warn = (...args) => {
                if (typeof args[0] === 'string' && args[0].includes('Clerk has been loaded with development keys')) return;
                originalWarn(...args);
              };
              console.log = (...args) => {
                if (typeof args[0] === 'string' && args[0].includes('Clerk has been loaded with development keys')) return;
                originalLog(...args);
              };
            `}
          </Script>
          <VariantProvider>
            <TooltipProvider>{children}</TooltipProvider>
          </VariantProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
