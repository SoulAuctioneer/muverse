"use client";

import { useState } from "react";
import TheoryGraphView from "@/components/theory-graph/TheoryGraphView";
import MathExplorer from "@/components/math-explorer/MathExplorer";
import AgentPanel from "@/components/agent-panel/AgentPanel";
import SimulationLab from "@/components/simulation-lab/SimulationLab";
import PaperEditor from "@/components/paper-editor/PaperEditor";

type Tab = "theory" | "math" | "simulations" | "paper" | "agents";

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("theory");

  const tabs: { id: Tab; label: string; desc: string }[] = [
    { id: "theory", label: "Theory Graph", desc: "Axioms, derivations, predictions" },
    { id: "math", label: "Math", desc: "Derivation chain with equations" },
    { id: "simulations", label: "Simulations", desc: "Branch ensemble, NN analog, Langevin" },
    { id: "paper", label: "Paper", desc: "Full rendered paper with LaTeX" },
    { id: "agents", label: "Agents", desc: "Theorist, Critic, Simulator, Writer" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-[var(--border)] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Muverse</h1>
            <p className="text-sm text-[var(--text-secondary)]">
              Thermodynamic Darwinism — Agentic Theory Development
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge badge-derived">v0.1</span>
          </div>
        </div>
        <nav className="flex gap-6 mt-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "tab-active"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="flex-1 p-6">
        {activeTab === "theory" && <TheoryGraphView />}
        {activeTab === "math" && <MathExplorer />}
        {activeTab === "simulations" && <SimulationLab />}
        {activeTab === "paper" && <PaperEditor />}
        {activeTab === "agents" && <AgentPanel />}
      </main>
    </div>
  );
}
