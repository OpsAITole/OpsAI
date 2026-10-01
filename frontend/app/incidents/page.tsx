import { AppShell } from "@/components/AppShell";
import { IncidentsBoard } from "@/components/IncidentsBoard";

export default function IncidentsPage() {
  return (
    <AppShell title="Incidentes">
      <IncidentsBoard />
    </AppShell>
  );
}
