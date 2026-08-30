import { useCallback, useEffect, useState } from "react";
import { useBackendStore } from "../store/backend";
import { apiListCases, type CaseRead } from "./api";

/**
 * Shared "select a case" state for analysis pages. Falls back to null when the
 * backend is offline so pages can render their demo/synthetic view.
 */
export function useCaseSelection() {
  const backend = useBackendStore((s) => s.mode);
  const [cases, setCases] = useState<CaseRead[]>([]);
  const [caseKey, setCaseKey] = useState<string>("");

  const reload = useCallback(() => {
    if (backend !== "backend") {
      setCases([]);
      setCaseKey("");
      return;
    }
    apiListCases({ limit: 100 })
      .then((res) => {
        setCases(res.items);
        setCaseKey((prev) => prev || res.items[0]?.case_number || "");
      })
      .catch(() => setCases([]));
  }, [backend]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { backend, cases, caseKey, setCaseKey, reload };
}