export type ApiStatus = {
  service: string;
  status: string;
  version: string;
  environment: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getApiBaseUrl(): string {
  return API_URL.replace(/\/$/, "");
}

export async function fetchApiStatus(): Promise<ApiStatus> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/status`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Status request failed (${response.status})`);
  }

  return response.json() as Promise<ApiStatus>;
}
