import { PropsWithChildren, ReactNode } from "react";

export function HudPage({
  title,
  subtitle,
  rightMeta,
  children
}: PropsWithChildren<{ title: string; subtitle: string; rightMeta?: ReactNode }>) {
  return (
    <div className="page hud-page">
      <div className="command-header">
        <div>
          <div className="brand-lock">{title}</div>
          <div className="subtle">{subtitle}</div>
        </div>
        <div className="system-meta">{rightMeta}</div>
      </div>
      {children}
    </div>
  );
}
