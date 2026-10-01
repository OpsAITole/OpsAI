import type {
  IncidentCategory,
  IncidentPriority,
  IncidentSeverity,
  IncidentStatus,
  UserRole,
} from "@/lib/api";

export const STATUS_LABELS: Record<IncidentStatus, string> = {
  NEW: "Nuevo",
  INVESTIGATING: "En investigación",
  WAITING: "En espera",
  RESOLVED: "Resuelto",
  CLOSED: "Cerrado",
};

export const PRIORITY_LABELS: Record<IncidentPriority, string> = {
  LOW: "Baja",
  MEDIUM: "Media",
  HIGH: "Alta",
  CRITICAL: "Crítica",
};

export const SEVERITY_LABELS: Record<IncidentSeverity, string> = {
  LOW: "Baja",
  MEDIUM: "Media",
  HIGH: "Alta",
  CRITICAL: "Crítica",
};

export const CATEGORY_LABELS: Record<IncidentCategory, string> = {
  NETWORK: "Red",
  WINDOWS: "Windows",
  LINUX: "Linux",
  DATABASE: "Base de datos",
  APPLICATION: "Aplicación",
  SECURITY: "Seguridad",
  VPN: "VPN",
  DNS: "DNS",
  CLOUD: "Nube",
  HARDWARE: "Hardware",
  OTHER: "Otros",
};

export const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Administrador",
  TECHNICIAN: "Técnico",
  VIEWER: "Observador",
};

export function statusLabel(value: string): string {
  return STATUS_LABELS[value as IncidentStatus] ?? value;
}

export function priorityLabel(value: string): string {
  return PRIORITY_LABELS[value as IncidentPriority] ?? value;
}

export function severityLabel(value: string): string {
  return SEVERITY_LABELS[value as IncidentSeverity] ?? value;
}

export function categoryLabel(value: string): string {
  return CATEGORY_LABELS[value as IncidentCategory] ?? value;
}

export function roleLabel(value: string): string {
  return ROLE_LABELS[value as UserRole] ?? value;
}

export function formatDateEs(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    return new Intl.DateTimeFormat("es-ES", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}
