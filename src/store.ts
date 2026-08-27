import { create } from "zustand";
import { Section, Entity } from "./types";
import { entities } from "./data/mock";

type State = {
  section: Section;
  selectedEntity: Entity | null;
  sidebarCollapsed: boolean;
  loginComplete: boolean;
  alertFilter: "ALL" | "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  setSection: (section: Section) => void;
  setSelectedEntity: (entity: Entity | null) => void;
  toggleSidebar: () => void;
  enterApp: () => void;
  setAlertFilter: (filter: State["alertFilter"]) => void;
};

export const useAppStore = create<State>((set) => ({
  section: "login",
  selectedEntity: entities[0],
  sidebarCollapsed: true,
  loginComplete: false,
  alertFilter: "ALL",
  setSection: (section) => set({ section }),
  setSelectedEntity: (selectedEntity) => set({ selectedEntity }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  enterApp: () => set({ section: "command-center", loginComplete: true }),
  setAlertFilter: (alertFilter) => set({ alertFilter })
}));
