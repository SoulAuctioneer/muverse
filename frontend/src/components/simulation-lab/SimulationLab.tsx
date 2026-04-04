"use client";

import { useState, useEffect, useCallback } from "react";
import { api, SimStatus } from "@/lib/api";

interface SimInfo {
  name: string;
  description: string;
  status: string;
}

export default function SimulationLab() {
  const [simulations, setSimulations] = useState<Record<string, SimInfo>>({});
  const [selectedSim, setSelectedSim] = useState<string>("sim1");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.simulations
      .list()
      .then((data) => setSimulations(data as Record<string, SimInfo>))
      .catch(() =>
        setSimulations({
          sim1: {
            name: "Branch Ensemble under Boltzmann Constraint",
            description: "Tests whether Gibbs weighting recovers Born rule statistics",
            status: "not_started",
          },
          sim2: {
            name: "Neural Network Analog Model",
            description: "Tests SGD-Gibbs equivalence at different effective temperatures",
            status: "not_started",
          },
          sim3: {
            name: "Quantum Langevin Dynamics",
            description: "Tests temperature-dependent branch probabilities",
            status: "not_started",
          },
        }),
      );
  }, []);

  const runSimulation = async (simId: string) => {
    setLoading(true);
    setError(null);
    try {
      await api.simulations.run(simId);
      pollStatus(simId);
    } catch (e) {
      setError("Failed to start simulation. Is the API running?");
      setLoading(false);
    }
  };

  const pollStatus = useCallback(async (simId: string) => {
    const poll = async () => {
      try {
        const status = await api.simulations.status(simId);
        if (status.status === "completed") {
          setResults(status.metrics as Record<string, unknown>);
          setSimulations((prev) => ({
            ...prev,
            [simId]: { ...prev[simId], status: "completed" },
          }));
          setLoading(false);
        } else if (status.status === "failed") {
          setError(status.error || "Simulation failed");
          setLoading(false);
        } else {
          setTimeout(poll, 2000);
        }
      } catch {
        setTimeout(poll, 3000);
      }
    };
    poll();
  }, []);

  const fetchResults = async (simId: string) => {
    try {
      const data = await api.simulations.results(simId);
      setResults((data as { metrics: Record<string, unknown> }).metrics || data as Record<string, unknown>);
    } catch {
      setError("Could not fetch results");
    }
  };

  const simKeys = Object.keys(simulations);

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      <div className="w-72 space-y-3">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-3">
          Simulations
        </h3>
        {simKeys.map((key) => {
          const sim = simulations[key];
          return (
            <button
              key={key}
              onClick={() => {
                setSelectedSim(key);
                setResults(null);
                if (sim.status === "completed") fetchResults(key);
              }}
              className={`w-full text-left p-4 rounded-lg transition-all ${
                selectedSim === key
                  ? "bg-[var(--bg-tertiary)] border border-[var(--border)]"
                  : "hover:bg-[var(--bg-tertiary)]"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-sm">{key.toUpperCase()}</span>
                <StatusBadge status={sim.status} />
              </div>
              <div className="text-xs text-[var(--text-secondary)]">{sim.name}</div>
            </button>
          );
        })}
      </div>

      <div className="flex-1 card flex flex-col">
        {selectedSim && simulations[selectedSim] && (
          <>
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border)]">
              <div>
                <h2 className="text-lg font-semibold">
                  {simulations[selectedSim].name}
                </h2>
                <p className="text-sm text-[var(--text-secondary)]">
                  {simulations[selectedSim].description}
                </p>
              </div>
              <button
                onClick={() => runSimulation(selectedSim)}
                disabled={loading}
                className="btn btn-primary"
              >
                {loading ? "Running..." : "Run Simulation"}
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-900/20 border border-red-800/30 text-red-400 text-sm mb-4">
                {error}
              </div>
            )}

            {loading && (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-8 h-8 border-2 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-[var(--text-secondary)] text-sm">
                    Running {selectedSim}...
                  </p>
                </div>
              </div>
            )}

            {results && !loading && (
              <div className="flex-1 overflow-y-auto">
                <h3 className="text-sm font-semibold mb-3">Results</h3>
                <div className="grid grid-cols-2 gap-3 mb-6">
                  {Object.entries(results)
                    .filter(([, v]) => typeof v === "number")
                    .map(([key, value]) => (
                      <div key={key} className="p-3 rounded-lg bg-[var(--bg-primary)]">
                        <div className="text-xs text-[var(--text-secondary)]">{key}</div>
                        <div className="text-lg font-mono font-semibold">
                          {typeof value === "number" ? value.toFixed(6) : String(value)}
                        </div>
                      </div>
                    ))}
                </div>

                <h3 className="text-sm font-semibold mb-3">Raw Data</h3>
                <pre className="p-4 rounded-lg bg-[var(--bg-primary)] text-xs mono overflow-x-auto max-h-96">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            )}

            {!results && !loading && (
              <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)] text-sm">
                Click "Run Simulation" to execute {selectedSim}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    not_started: "badge-unverified",
    running: "badge-postulated",
    completed: "badge-derived",
    failed: "badge-critical",
  };
  return <span className={`badge ${styles[status] || ""}`}>{status}</span>;
}
