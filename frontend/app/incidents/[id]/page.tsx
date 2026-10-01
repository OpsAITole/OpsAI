import { AppShell } from "@/components/AppShell";
import { IncidentDetailView } from "@/components/IncidentDetailView";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function IncidentDetailPage({ params }: PageProps) {
  const { id } = await params;
  return (
    <AppShell title="Incident detail">
      <IncidentDetailView incidentId={id} />
    </AppShell>
  );
}
