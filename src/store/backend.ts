/**
 * Backend connection + graph state (Phase 7).
 *
 * Manages whether the app is talking to the live FastAPI backend or falling back
 * to synthetic mock data. The frozen UI always has data either way, so a demo
 * never looks broken even when the backend is not running.
 */
import { create } from "zustand";
import {
  apiGetNetwork,
  apiLogin,
  setAccessToken,
  type GraphResponse,
} from "../services/api";
import { mockGraph } from "../data/graphMock";

export type BackendMode = "checking" | "backend" | "mock";

// Demo credentials; used only to obtain a token for the dev backend.
const DEMO_USERNAME = "admin";
const DEMO_PASSWORD = "admin-secret";

interface BackendState {
  mode: BackendMode;
  connected: boolean;
  graph: GraphResponse;
  lastError: string | null;

  connect: () => Promise<BackendMode>;
  refreshGraph: () => Promise<void>;
  isBackend: () => boolean;
  setGraph: (graph: GraphResponse) => void;
}

export const useBackendStore = create<BackendState>((set, get) => ({
  mode: "checking",
  connected: false,
  graph: mockGraph,
  lastError: null,

  isBackend: () => get().mode === "backend",

  connect: async () => {
    set({ mode: "checking", lastError: null });
    try {
      const tokens = await apiLogin(DEMO_USERNAME, DEMO_PASSWORD);
      setAccessToken(tokens.access_token);
      const network = await apiGetNetwork({ limit: 500 });
      set({ graph: network, mode: "backend", connected: true, lastError: null });
      return "backend";
    } catch (err) {
      setAccessToken(null);
      set({
        mode: "mock",
        connected: false,
        graph: mockGraph,
        lastError: err instanceof Error ? err.message : "Backend unavailable",
      });
      return "mock";
    }
  },

  refreshGraph: async () => {
    if (get().mode !== "backend") return;
    try {
      const network = await apiGetNetwork({ limit: 500 });
      set({ graph: network, lastError: null });
    } catch (err) {
      // Do not drop the UI to mock just because one refresh failed.
      set({ lastError: err instanceof Error ? err.message : "Refresh failed" });
    }
  },

  setGraph: (graph) => set({ graph }),
}));
