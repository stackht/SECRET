import { useAppStore } from "../store";
import { Section } from "../types";
import { Bell, Building2, FileText, MapPinned, MessagesSquare, Radar, Settings, Shield, TimerReset, Users, ArrowLeftRight, MessageCircle, Play, History, Upload } from "lucide-react";

type NavGroup = "OPERATIONS" | "ANALYZE" | "INTELLIGENCE" | "OUTPUT" | "ASSISTANT";

const items: { id: Exclude<Section, "login">; label: string; icon: React.ReactNode; group: NavGroup }[] = [
  { id: "command-center", label: "Command", icon: <Shield size={14} />, group: "OPERATIONS" },
  { id: "investigations", label: "Cases", icon: <Radar size={14} />, group: "OPERATIONS" },
  { id: "case-intake", label: "Intake", icon: <Upload size={14} />, group: "OPERATIONS" },
  { id: "network", label: "Network", icon: <Users size={14} />, group: "ANALYZE" },
  { id: "entities", label: "Entities", icon: <Building2 size={14} />, group: "ANALYZE" },
  { id: "timeline", label: "Timeline", icon: <TimerReset size={14} />, group: "ANALYZE" },
  { id: "locations", label: "Locations", icon: <MapPinned size={14} />, group: "ANALYZE" },
  { id: "communications", label: "Comms", icon: <MessagesSquare size={14} />, group: "ANALYZE" },
  { id: "transactions", label: "Transactions", icon: <ArrowLeftRight size={14} />, group: "ANALYZE" },
  { id: "alerts", label: "Alerts", icon: <Bell size={14} />, group: "INTELLIGENCE" },
  { id: "simulation", label: "Simulation", icon: <Play size={14} />, group: "INTELLIGENCE" },
  { id: "reports", label: "Reports", icon: <FileText size={14} />, group: "OUTPUT" },
  { id: "audit", label: "Audit", icon: <History size={14} />, group: "OUTPUT" },
  { id: "assistant", label: "Assistant", icon: <MessageCircle size={14} />, group: "ASSISTANT" },
  { id: "settings", label: "Settings", icon: <Settings size={14} />, group: "OUTPUT" }
];

const GROUP_ORDER: NavGroup[] = ["OPERATIONS", "ANALYZE", "INTELLIGENCE", "OUTPUT", "ASSISTANT"];

export function TopNav() {
  const { section, setSection } = useAppStore();
  const grouped = GROUP_ORDER.map((g) => ({ group: g, items: items.filter((i) => i.group === g) }))
    .filter((g) => g.items.length > 0);
  return (
    <header className="top-nav">
      <div className="top-nav-brand">
        <span className="brand-mark">S</span>
        <div>
          <div className="top-nav-title">SECRET</div>
          <div className="top-nav-subtitle">Smart Entity &amp; Criminal Relationship Exploration Tool</div>
        </div>
      </div>
      <nav className="top-nav-links" aria-label="Primary">
        {grouped.map((g) => (
          <div className="top-nav-group" key={g.group}>
            <span className="top-nav-group-label">{g.group}</span>
            {g.items.map((item) => (
              <button
                key={item.id}
                className={`top-nav-item ${section === item.id ? "active" : ""}`}
                onClick={() => setSection(item.id)}
                title={item.label}
              >
                <span className="nav-icon">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>
    </header>
  );
}
