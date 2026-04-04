"use client";

import { useState, useRef, useEffect } from "react";
import { api, AgentResponse, createAgentWebSocket } from "@/lib/api";

const AGENTS = [
  { id: "theorist", label: "Theorist", color: "#8b5cf6", desc: "Develops formal derivations" },
  { id: "critic", label: "Critic", color: "#ef4444", desc: "Finds weaknesses and gaps" },
  { id: "literature", label: "Literature", color: "#4a9eff", desc: "Searches and cites references" },
  { id: "simulator", label: "Simulator", color: "#34d399", desc: "Designs and runs experiments" },
  { id: "writer", label: "Writer", color: "#f59e0b", desc: "Drafts paper sections" },
];

const PHASES = ["formalize", "critique", "simulate", "write", "review"];

interface Message {
  role: "user" | "agent";
  agent?: string;
  content: string;
  timestamp: Date;
}

export default function AgentPanel() {
  const [selectedAgent, setSelectedAgent] = useState("theorist");
  const [phase, setPhase] = useState("formalize");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamContent]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.agents.run(selectedAgent, input, phase);
      const agentMsg: Message = {
        role: "agent",
        agent: res.agent,
        content: res.output,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "agent", agent: "system", content: "Error: could not reach API", timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const streamMessage = () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    const task = input;
    setInput("");
    setStreaming(true);
    setStreamContent("");

    const ws = createAgentWebSocket(
      (chunk) => setStreamContent((prev) => prev + chunk),
      (fullResponse) => {
        setMessages((prev) => [
          ...prev,
          { role: "agent", agent: selectedAgent, content: fullResponse, timestamp: new Date() },
        ]);
        setStreamContent("");
        setStreaming(false);
      },
      () => {
        setStreaming(false);
        setStreamContent("");
      },
    );

    ws.onopen = () => {
      ws.send(JSON.stringify({ agent: selectedAgent, task, phase }));
    };

    wsRef.current = ws;
  };

  const startPipeline = async () => {
    setLoading(true);
    try {
      await api.agents.startPipeline();
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          agent: "orchestrator",
          content: "Full pipeline started. Check status periodically.",
          timestamp: new Date(),
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "agent", agent: "system", content: "Failed to start pipeline", timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const agentInfo = AGENTS.find((a) => a.id === selectedAgent)!;

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      {/* Agent selector sidebar */}
      <div className="w-56 space-y-2">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-3">Agents</h3>
        {AGENTS.map((agent) => (
          <button
            key={agent.id}
            onClick={() => setSelectedAgent(agent.id)}
            className={`w-full text-left p-3 rounded-lg transition-all text-sm ${
              selectedAgent === agent.id
                ? "bg-[var(--bg-tertiary)] border border-[var(--border)]"
                : "hover:bg-[var(--bg-tertiary)]"
            }`}
          >
            <span className="flex items-center gap-2">
              <span
                className="inline-block w-2.5 h-2.5 rounded-full"
                style={{ background: agent.color }}
              />
              <span className="font-medium">{agent.label}</span>
            </span>
            <span className="text-xs text-[var(--text-secondary)] ml-5 block">
              {agent.desc}
            </span>
          </button>
        ))}

        <hr className="border-[var(--border)] my-3" />

        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">Phase</h3>
        <select
          value={phase}
          onChange={(e) => setPhase(e.target.value)}
          className="w-full p-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-sm"
        >
          {PHASES.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>

        <button onClick={startPipeline} disabled={loading} className="btn btn-ghost w-full mt-3">
          Run Full Pipeline
        </button>
      </div>

      {/* Chat area */}
      <div className="flex-1 card flex flex-col">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-[var(--border)]">
          <span
            className="inline-block w-3 h-3 rounded-full"
            style={{ background: agentInfo.color }}
          />
          <span className="font-semibold">{agentInfo.label}</span>
          <span className="text-xs text-[var(--text-secondary)]">
            {agentInfo.desc}
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 && (
            <p className="text-[var(--text-secondary)] text-sm">
              Send a task to the {agentInfo.label} agent, or run the full pipeline.
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`p-3 rounded-lg text-sm ${
                msg.role === "user"
                  ? "bg-[var(--bg-tertiary)] ml-12"
                  : "bg-[var(--bg-primary)] mr-12"
              }`}
            >
              <div className="text-xs text-[var(--text-secondary)] mb-1">
                {msg.role === "user" ? "You" : msg.agent || "Agent"}
              </div>
              <div className="agent-output whitespace-pre-wrap">{msg.content}</div>
            </div>
          ))}
          {streaming && streamContent && (
            <div className="p-3 rounded-lg text-sm bg-[var(--bg-primary)] mr-12">
              <div className="text-xs text-[var(--text-secondary)] mb-1">
                {selectedAgent} <span className="loading-pulse">typing...</span>
              </div>
              <div className="agent-output whitespace-pre-wrap">{streamContent}</div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder={`Task for ${agentInfo.label}...`}
            className="flex-1 p-3 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--accent-blue)]"
          />
          <button onClick={sendMessage} disabled={loading} className="btn btn-primary">
            Send
          </button>
          <button onClick={streamMessage} disabled={streaming} className="btn btn-ghost">
            Stream
          </button>
        </div>
      </div>
    </div>
  );
}
