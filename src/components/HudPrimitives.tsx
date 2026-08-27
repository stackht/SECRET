export function HudCard({
  label,
  title,
  children,
  className = ""
}: {
  label: string;
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`hud-card ${className}`.trim()}>
      <div className="hud-label">{label}</div>
      <span className="hud-corner hud-corner-tl" />
      <span className="hud-corner hud-corner-tr" />
      <span className="hud-corner hud-corner-bl" />
      <span className="hud-corner hud-corner-br" />
      {title ? <h3>{title}</h3> : null}
      {children}
    </div>
  );
}

export function StatRow({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="stat-row">
      <span className="stat-label">{label}</span>
      <span className={`stat-value ${accent ?? ""}`}>{value}</span>
    </div>
  );
}

export function HoloList({ items }: { items: { label: string; value: string; accent?: string }[] }) {
  return (
    <div className="mini-list">
      {items.map((item) => (
        <StatRow key={item.label} label={item.label} value={item.value} accent={item.accent} />
      ))}
    </div>
  );
}
