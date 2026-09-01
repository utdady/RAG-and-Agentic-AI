import { notFound } from "next/navigation";
import { DemoWorkspace } from "@/components/DemoWorkspace";
import { HubShell } from "@/components/HubShell";
import { DEMOS, demoBySlug } from "@/lib/demos";

export function generateStaticParams() {
  return DEMOS.map((d) => ({ slug: d.slug }));
}

export default async function DemoPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const demo = demoBySlug(slug);
  if (!demo) notFound();
  return (
    <HubShell active={demo.slug}>
      <DemoWorkspace demo={demo} />
    </HubShell>
  );
}
