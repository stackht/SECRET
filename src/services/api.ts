/**
 * SECRET frontend API client (Phase 7).
 *
 * Thin typed wrapper over the FastAPI backend. Exposes the endpoints the frozen
 * UI consumes (auth, graph, criminals, cases) and centralizes the auth token.
 *
 * The backend base URL can be overridden via `VITE_API_URL` (defaults to the
 * local FastAPI dev server on :8000).
 */

export const API_BASE_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, `Backend unreachable at ${API_BASE_URL}`);
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* ignore */
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

// --- Types (mirror the backend Pydantic schemas) ----------------------------

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserRead {
  id: number;
  username: string;
  email: string;
  full_name?: string | null;
  role: string;
  status: string;
  created_at: string;
  last_login_at?: string | null;
}

export interface GraphNode {
  id: string;
  type: string;
  name: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface CriminalProfile {
  id: number;
  secret_id: string;
  profile_type: string;
  name: string;
  aliases: string[];
  risk_score: number;
  risk_level: string;
  confidence: number;
  status: string;
  attributes: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CriminalList {
  total: number;
  limit: number;
  offset: number;
  items: CriminalProfile[];
}

export interface CaseRead {
  id: number;
  case_number: string;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
  closed_at?: string | null;
}

export interface CaseList {
  total: number;
  limit: number;
  offset: number;
  items: CaseRead[];
}

// --- Auth -------------------------------------------------------------------

export async function apiLogin(username: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password } satisfies LoginRequest),
  });
}

export async function apiMe(): Promise<UserRead> {
  return request<UserRead>("/api/v1/auth/me");
}

// --- Graph ------------------------------------------------------------------

export async function apiGetNetwork(params: {
  node_types?: string[];
  rel_types?: string[];
  limit?: number;
} = {}): Promise<GraphResponse> {
  const search = new URLSearchParams();
  params.node_types?.forEach((t) => search.append("node_types", t));
  params.rel_types?.forEach((t) => search.append("rel_types", t));
  if (params.limit) search.append("limit", String(params.limit));
  const qs = search.toString();
  return request<GraphResponse>(`/api/v1/graph/network${qs ? `?${qs}` : ""}`);
}

export async function apiGetEntity(entityId: string): Promise<GraphNode> {
  return request<GraphNode>(`/api/v1/graph/entities/${encodeURIComponent(entityId)}`);
}

// --- Criminals --------------------------------------------------------------

export async function apiListCriminals(params: {
  q?: string;
  profile_type?: string;
  skip?: number;
  limit?: number;
} = {}): Promise<CriminalList> {
  const search = new URLSearchParams();
  if (params.q) search.append("q", params.q);
  if (params.profile_type) search.append("profile_type", params.profile_type);
  if (params.skip) search.append("skip", String(params.skip));
  if (params.limit) search.append("limit", String(params.limit));
  const qs = search.toString();
  return request<CriminalList>(`/api/v1/criminals${qs ? `?${qs}` : ""}`);
}

// --- Cases ------------------------------------------------------------------

export async function apiListCases(params: {
  q?: string;
  status?: string;
  priority?: string;
  limit?: number;
} = {}): Promise<CaseList> {
  const search = new URLSearchParams();
  if (params.q) search.append("q", params.q);
  if (params.status) search.append("status", params.status);
  if (params.priority) search.append("priority", params.priority);
  if (params.limit) search.append("limit", String(params.limit));
  const qs = search.toString();
  return request<CaseList>(`/api/v1/cases${qs ? `?${qs}` : ""}`);
}

export interface CaseCreateInput {
  title: string;
  case_number?: string;
  description?: string;
  status?: string;
  priority?: string;
}

export async function apiCreateCase(input: CaseCreateInput): Promise<CaseRead> {
  return request<CaseRead>("/api/v1/cases", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

// --- Analysis: temporal + location (Phase 9) --------------------------------

export interface TimeWindowResult {
  window_start: string;
  count: number;
  sources: string[];
}
export interface EventItem {
  record_id: string;
  timestamp: string;
  source: string;
  summary: string;
  location?: string | null;
}
export interface LocationActivityEntry {
  location: string;
  events: number;
  level: string;
}
export interface TemporalLocationResponse {
  windows: TimeWindowResult[];
  event_sequence: EventItem[];
  communication_bursts: { window_start: string; count: number }[];
  location_activity: LocationActivityEntry[];
  movement: EventItem[];
}

export async function apiTemporalLocation(params: { scenario?: string; entity_id?: string } = {}): Promise<TemporalLocationResponse> {
  const search = new URLSearchParams();
  if (params.scenario) search.append("scenario", params.scenario);
  if (params.entity_id) search.append("entity_id", params.entity_id);
  const qs = search.toString();
  return request<TemporalLocationResponse>(`/api/v1/analysis/temporal-location${qs ? `?${qs}` : ""}`);
}

// --- Investigation engine workflow (Phase 10) -------------------------------

export async function apiRunInvestigation(scenario = "NORMAL_NETWORK"): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/api/v1/analysis/investigation?scenario=${encodeURIComponent(scenario)}`, {
    method: "POST",
  });
}

// --- AI Assistant (Phase 11) ------------------------------------------------

export interface AssistantResponse {
  question: string;
  answer: string;
  source_ids: string[];
  found: boolean;
}

export async function apiAskAssistant(question: string): Promise<AssistantResponse> {
  return request<AssistantResponse>("/api/v1/analysis/assistant", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

// --- Audit (Phase 13) -------------------------------------------------------

export interface AuditEntry {
  id: number;
  user_id?: number | null;
  action: string;
  object_type?: string | null;
  object_id?: string | null;
  result: Record<string, unknown>;
  created_at: string;
}

export async function apiListAudit(limit = 50): Promise<AuditEntry[]> {
  return request<AuditEntry[]>(`/api/v1/audit?limit=${limit}`);
}

// --- Simulation / Demo mode (Phase 15) --------------------------------------

export interface SimulationStep {
  label: string;
  count: number;
  sample: string;
}
export interface SimulationResponse {
  scenario: string;
  steps: SimulationStep[];
  entities: number;
  relationships: number;
  nodes_written: number;
  insights: Record<string, unknown>;
  elapsed_seconds: number;
}

export async function apiRunSimulation(scenario = "NORMAL_NETWORK"): Promise<SimulationResponse> {
  return request<SimulationResponse>(`/api/v1/analysis/simulation?scenario=${encodeURIComponent(scenario)}`, {
    method: "POST",
  });
}
