import { DemoBrand, DemoNav } from "@/components/DemoNav";

export function Sidebar({ active }: { active?: string }) {
  return (
    <aside className="hidden shrink-0 flex-col border-r border-[var(--line)] bg-[var(--bg2)] lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-64 xl:w-72">
      <DemoBrand />
      <DemoNav active={active} className="flex min-h-0 flex-1 flex-col" />
    </aside>
  );
}
