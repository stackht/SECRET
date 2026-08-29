import { PropsWithChildren } from "react";
import { TopNav } from "./TopNav";

export function Layout({ children }: PropsWithChildren) {
  return (
    <div className="app-shell">
      <TopNav />
      <main className="app-main">{children}</main>
    </div>
  );
}
