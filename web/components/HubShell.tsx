import type { ReactNode } from "react";
import { DemoShell } from "@/components/DemoShell";

export function HubShell({
  children,
  active,
}: {
  children: ReactNode;
  active?: string;
}) {
  if (active) {
    return <DemoShell active={active}>{children}</DemoShell>;
  }

  return <div className="min-h-screen">{children}</div>;
}
