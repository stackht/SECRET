import { PropsWithChildren } from "react";
import { TopNav } from "./TopNav";
import { GlobeScene } from "./GlobeScene";

export function Layout({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <div className="app-background-globe" aria-hidden="true">
        <GlobeScene />
      </div>
      <TopNav />
      <main className="app-main">{children}</main>
    </div>
  );
}
