"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";

type VariantContextType = {
  assignments: Record<string, string>;
  loading: boolean;
};

const VariantContext = createContext<VariantContextType | undefined>(undefined);

export function VariantProvider({ children }: { children: React.ReactNode }) {
  const [assignments, setAssignments] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const { user, isLoaded } = useUser();

  useEffect(() => {
    async function fetchAssignments() {
      if (!isLoaded) return;
      
      const userId = user?.id || "anonymous_" + Math.random().toString(36).substring(7);
      
      try {
        const response = await fetch(`http://localhost:8000/v1/experiments/assignments?user_id=${userId}`);
        if (response.ok) {
          const data = await response.json();
          setAssignments(data);
        } else {
          console.error("Failed to fetch experiment assignments");
        }
      } catch (e) {
        console.error("Error fetching experiment assignments:", e);
      } finally {
        setLoading(false);
      }
    }
    
    fetchAssignments();
  }, [isLoaded, user?.id]);

  return (
    <VariantContext.Provider value={{ assignments, loading }}>
      {children}
    </VariantContext.Provider>
  );
}

export function useExperiment(experimentId: string, defaultVariant: string = "control") {
  const context = useContext(VariantContext);
  if (context === undefined) {
    throw new Error("useExperiment must be used within a VariantProvider");
  }
  
  if (context.loading) {
    return defaultVariant;
  }
  
  return context.assignments[experimentId] || defaultVariant;
}
