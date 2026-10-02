"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

type VariantContextType = {
  variant: string;
  setVariant: (variant: string) => void;
};

const VariantContext = createContext<VariantContextType | undefined>(undefined);

export function VariantProvider({ children }: { children: React.ReactNode }) {
  const [variant, setVariant] = useState<string>("control");

  useEffect(() => {
    try {
      const storedVariant = localStorage.getItem("ab-variant");
      if (storedVariant) {
        setVariant(storedVariant);
      } else {
        const newVariant = Math.random() > 0.5 ? "experiment" : "control";
        setVariant(newVariant);
        localStorage.setItem("ab-variant", newVariant);
      }
    } catch (e) {
      setVariant("control");
    }
  }, []);

  return (
    <VariantContext.Provider value={{ variant, setVariant }}>
      {children}
    </VariantContext.Provider>
  );
}

export function useVariant() {
  const context = useContext(VariantContext);
  if (context === undefined) {
    throw new Error("useVariant must be used within a VariantProvider");
  }
  return context;
}
