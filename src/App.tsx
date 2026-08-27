import { useMemo } from "react";
import { useAppStore } from "./store";
import { Section } from "./types";
import { Layout } from "./components/Layout";
import { LoginScreen } from "./pages/Login";
import { CommandCenter } from "./pages/CommandCenter";
import { Investigation } from "./pages/Investigation";
import { NetworkIntel } from "./pages/NetworkIntel";
import { EntityExplorer } from "./pages/EntityExplorer";
import { TimelinePage } from "./pages/TimelinePage";
import { AlertsPage } from "./pages/AlertsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { ErrorBoundary } from "./components/ErrorBoundary";

const pages: Record<Exclude<Section, "login">, JSX.Element> = {
  "command-center": <CommandCenter />,
  investigations: <Investigation />,
  network: <NetworkIntel />,
  entities: <EntityExplorer />,
  timeline: <TimelinePage />,
  locations: <PlaceholderPage title="LOCATION INTELLIGENCE" subtitle="Stylized mock map, activity clusters, and movement paths." />,
  transactions: <PlaceholderPage title="TRANSACTION ANALYSIS" subtitle="Mock financial flows, suspicious transfers, and volume charts." />,
  communications: <PlaceholderPage title="COMMUNICATION ANALYSIS" subtitle="Call and message cluster relationships with temporal patterns." />,
  alerts: <AlertsPage />,
  reports: <ReportsPage />,
  settings: <SettingsPage />
};

export function App() {
  const { section } = useAppStore();
  const content = useMemo(() => (section === "login" ? <LoginScreen /> : pages[section]), [section]);
  return section === "login" ? content : <Layout><ErrorBoundary fallback={<div className="panel"><h3>Command Center unavailable</h3><div className="meta">The visualization layer failed to load, but the app shell is still running.</div></div>}>{content}</ErrorBoundary></Layout>;
}
