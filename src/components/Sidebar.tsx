import { useAppStore } from "../store";
import { Section } from "../types";
import { Shield, Radar, Users, MapPinned, Newspaper, TimerReset, Building2, ArrowLeftRight, MessagesSquare, Bell, FileText, Settings, PanelLeftClose, PanelLeftOpen, MessageCircle, Play, History, Upload } from "lucide-react";

const items: { id: Exclude<Section, "login">; label: string; icon: React.ReactNode }[] = [
  { id: "command-center", label: "Command Center", icon: <Shield size={18} /> },
  { id: "investigations", label: "Investigations", icon: <Radar size={18} /> },
  { id: "case-intake", label: "Case Intake", icon: <Upload size={18} /> },
  { id: "network", label: "Network Intelligence", icon: <Users size={18} /> },
  { id: "entities", label: "Entities", icon: <Building2 size={18} /> },
  { id: "timeline", label: "Timeline", icon: <TimerReset size={18} /> },
  { id: "locations", label: "Locations", icon: <MapPinned size={18} /> },
  { id: "transactions", label: "Transactions", icon: <ArrowLeftRight size={18} /> },
  { id: "communications", label: "Communications", icon: <MessagesSquare size={18} /> },
  { id: "alerts", label: "Alerts", icon: <Bell size={18} /> },
  { id: "reports", label: "Reports", icon: <FileText size={18} /> },
  { id: "settings", label: "Settings", icon: <Settings size={18} /> },
  { id: "assistant", label: "Assistant", icon: <MessageCircle size={18} /> },
  { id: "simulation", label: "Simulation", icon: <Play size={18} /> },
  { id: "audit", label: "Audit", icon: <History size={18} /> }
];

export function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { section, setSection } = useAppStore();
  return <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
    <div className="sidebar-top">
      <div className="sidebar-brandmark">
        <div className="brand">S</div>
        {!collapsed && <div className="subtle">SECRET</div>}
      </div>
      <button className="icon-button" onClick={onToggle}>{collapsed ? <PanelLeftOpen size={18}/> : <PanelLeftClose size={18}/>}</button>
    </div>
    <nav className="nav-list">
      {items.map((item) => (
        <button key={item.id} title={item.label} className={`nav-item ${section === item.id ? "active" : ""}`} onClick={() => setSection(item.id)}>
          <span className="nav-icon">{item.icon}</span>
          {!collapsed && <span>{item.label}</span>}
        </button>
      ))}
    </nav>
  </aside>;
}
