import { useAppStore } from "../store";
import { Section } from "../types";
import { Bell, Building2, FileText, MapPinned, MessagesSquare, Radar, Settings, Shield, TimerReset, Users, ArrowLeftRight } from "lucide-react";

const items: { id: Exclude<Section, "login">; label: string; icon: React.ReactNode }[] = [
  { id: "command-center", label: "Command", icon: <Shield size={14} /> },
  { id: "investigations", label: "Cases", icon: <Radar size={14} /> },
  { id: "network", label: "Network", icon: <Users size={14} /> },
  { id: "entities", label: "Entities", icon: <Building2 size={14} /> },
  { id: "timeline", label: "Timeline", icon: <TimerReset size={14} /> },
  { id: "locations", label: "Locations", icon: <MapPinned size={14} /> },
  { id: "transactions", label: "Transactions", icon: <ArrowLeftRight size={14} /> },
  { id: "communications", label: "Comms", icon: <MessagesSquare size={14} /> },
  { id: "alerts", label: "Alerts", icon: <Bell size={14} /> },
  { id: "reports", label: "Reports", icon: <FileText size={14} /> },
  { id: "settings", label: "Settings", icon: <Settings size={14} /> }
];

export function TopNav() {
  const { section, setSection } = useAppStore();
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
        {items.map((item) => (
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
      </nav>
    </header>
  );
}
