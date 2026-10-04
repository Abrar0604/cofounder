"use client";

import { useEffect } from "react";

export function SuppressWarning() {
  useEffect(() => {
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
  }, []);

  return null;
}
