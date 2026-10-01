import { AppShell } from "@/components/AppShell";
import { CreateIncidentForm } from "@/components/CreateIncidentForm";

export default function NewIncidentPage() {
  return (
    <AppShell title="Create incident">
      <CreateIncidentForm />
    </AppShell>
  );
}
