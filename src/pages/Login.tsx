import { motion } from "framer-motion";
import { useAppStore } from "../store";
import { ShieldCheck, Network, LockKeyhole, ArrowRight } from "lucide-react";

export function LoginScreen() {
  const enterApp = useAppStore((s) => s.enterApp);
  return (
    <div className="login">
      <div className="login-card">
        <div className="row" style={{ justifyContent: "space-between" }}>
          <div className="glass-strip">SECRET / Secure Intelligence Workspace</div>
          <div className="glass-strip">System Online</div>
        </div>
        <div className="login-grid">
          <div className="stack">
            <h1 className="title">Smart Entity &amp; Criminal Relationship Exploration Tool</h1>
            <p className="headline">A premium intelligence-analysis workspace for network discovery, entity profiling, and operational awareness.</p>
            <div className="status"><span>SECURE ENVIRONMENT</span><span>SYSTEM ONLINE</span></div>
            <button className="cta" onClick={enterApp}>ACCESS INTELLIGENCE CONSOLE <ArrowRight size={16} style={{ display: "inline", marginLeft: 8 }} /></button>
          </div>
          <motion.div initial={{ opacity: 0.6, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1.2 }} className="panel mini">
            <div className="row" style={{ justifyContent: "space-between" }}><h3 style={{ margin: 0 }}>Operational Mesh</h3><Network size={18} color="var(--blue)" /></div>
            <p className="meta">Subtle network background placeholder with restrained depth, motion, and classified tone.</p>
            <div className="grid" style={{ gridTemplateColumns: "repeat(3,1fr)", marginTop: 16 }}>
              {Array.from({ length: 9 }).map((_, i) => <div key={i} style={{ height: 36 + (i % 3) * 24, borderRadius: 999, background: `linear-gradient(180deg, rgba(77,141,255,${0.14 + i * 0.01}), rgba(77,141,255,0.02))`, border: "1px solid rgba(255,255,255,.06)" }} />)}
            </div>
            <div className="row" style={{ marginTop: 14 }}>
              <ShieldCheck size={16} color="var(--green)" />
              <span className="meta">Verified secure runtime</span>
              <LockKeyhole size={16} color="var(--muted)" />
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
