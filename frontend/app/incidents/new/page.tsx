import { AppShell } from "@/components/AppShell";
import { CreateIncidentForm } from "@/components/CreateIncidentForm";

export default function NewIncidentPage() {
  return (
    <AppShell title="Crear incidente">
      <CreateIncidentForm />
    </AppShell>
  );
}
