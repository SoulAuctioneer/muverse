const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 300_000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
    if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export interface TheoryNode {
  id: string;
  type: "axiom" | "derivation" | "prediction" | "critique";
  label: string;
  statement?: string;
  status?: string;
  severity?: string;
  testable?: boolean;
}

export interface TheoryEdge {
  source: string;
  target: string;
  type: string;
}

export interface TheoryGraph {
  nodes: TheoryNode[];
  edges: TheoryEdge[];
}

export interface AgentResponse {
  agent: string;
  output: string;
  phase: string;
  iteration: number;
}

export interface SimStatus {
  simulation: string;
  status: string;
  metrics: Record<string, unknown>;
  error: string | null;
}

export interface PaperSection {
  number: string;
  title: string;
  status: string;
  outline_points: string[];
  body_latex: string;
}

export interface PaperOutline {
  title: string;
  sections: PaperSection[];
}

export const api = {
  theory: {
    get: () => fetchJSON("/api/theory/"),
    graph: () => fetchJSON<TheoryGraph>("/api/theory/graph"),
    seed: () => fetchJSON("/api/theory/seed", { method: "POST" }),
    labels: () => fetchJSON("/api/theory/labels"),
  },

  agents: {
    run: (agent: string, task: string, phase = "formalize") =>
      fetchJSON<AgentResponse>("/api/agents/run", {
        method: "POST",
        body: JSON.stringify({ agent, task, phase }),
      }),
    startPipeline: () =>
      fetchJSON("/api/agents/pipeline/start", { method: "POST" }),
    pipelineStatus: () => fetchJSON("/api/agents/pipeline/status"),
  },

  simulations: {
    list: () => fetchJSON("/api/simulations/list"),
    run: (simulation: string, parameters = {}) =>
      fetchJSON<SimStatus>("/api/simulations/run", {
        method: "POST",
        body: JSON.stringify({ simulation, parameters }),
      }),
    status: (simulation: string) =>
      fetchJSON<SimStatus>(`/api/simulations/status/${simulation}`),
    results: (simulation: string) =>
      fetchJSON(`/api/simulations/results/${simulation}`),
  },

  paper: {
    outline: () => fetchJSON<PaperOutline>("/api/paper/outline"),
    sections: () => fetchJSON<PaperSection[]>("/api/paper/sections"),
    completeness: () => fetchJSON("/api/paper/completeness"),
  },
};

export function createAgentWebSocket(
  onChunk: (chunk: string) => void,
  onDone: (fullResponse: string) => void,
  onError?: (error: Event) => void,
): WebSocket {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = API_BASE
    ? new URL(API_BASE).host
    : window.location.host;
  const ws = new WebSocket(`${protocol}//${host}/ws/agent-stream`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "chunk") {
      onChunk(data.content);
    } else if (data.type === "done") {
      onDone(data.full_response);
    }
  };

  ws.onerror = (event) => onError?.(event);

  return ws;
}
