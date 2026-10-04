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
      
      let userId = user?.id;
      if (!userId) {
        userId = localStorage.getItem("ab-anon-id");
        if (!userId) {
          userId = "anonymous_" + Math.random().toString(36).substring(7);
          localStorage.setItem("ab-anon-id", userId);
        }
      }
      
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${baseUrl}/v1/experiments/assignments?user_id=${encodeURIComponent(userId as string)}`);
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
