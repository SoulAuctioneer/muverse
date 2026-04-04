"use client";

import { useState, useEffect, useCallback } from "react";
import { api, SimStatus } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import type {
  ValueType,
  NameType,
  Payload,
} from "recharts/types/component/DefaultTooltipContent";

type TooltipEntry = Payload<ValueType, NameType>;
const fmtTooltip = (value: ValueType | undefined, _name: NameType | undefined, _item: TooltipEntry) =>
  typeof value === "number" ? value.toExponential(4) : String(value ?? "");

interface SimInfo {
  name: string;
  description: string;
  status: string;
  configurable_params?: Record<
    string,
    { default: number; type: string; label: string }
  >;
}

type SimResults = Record<string, unknown>;

export default function SimulationLab() {
  const [simulations, setSimulations] = useState<Record<string, SimInfo>>({});
  const [selectedSim, setSelectedSim] = useState<string>("sim1");
  const [results, setResults] = useState<SimResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<Record<string, number>>({});

  useEffect(() => {
    api.simulations
      .list()
      .then((data) => {
        const d = data as Record<string, SimInfo>;
        setSimulations(d);
        if (d[selectedSim]?.configurable_params) {
          const defaults: Record<string, number> = {};
          for (const [k, v] of Object.entries(
            d[selectedSim].configurable_params!,
          )) {
            defaults[k] = v.default;
          }
          setParams(defaults);
        }
      })
      .catch(() => {});
  }, []);

  const selectSim = (key: string) => {
    setSelectedSim(key);
    setResults(null);
    setError(null);
    const sim = simulations[key];
    if (sim?.configurable_params) {
      const defaults: Record<string, number> = {};
      for (const [k, v] of Object.entries(sim.configurable_params)) {
        defaults[k] = v.default;
      }
      setParams(defaults);
    } else {
      setParams({});
    }
    if (sim?.status === "completed") fetchResults(key);
  };

  const runSimulation = async (simId: string) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setSimulations((prev) => ({
      ...prev,
      [simId]: { ...prev[simId], status: "running" },
    }));
    try {
      await api.simulations.run(simId, params);
      pollStatus(simId);
    } catch {
      setError("Failed to start simulation. Is the API running?");
      setLoading(false);
    }
  };

  const pollStatus = useCallback(async (simId: string) => {
    const poll = async () => {
      try {
        const status = await api.simulations.status(simId);
        if (status.status === "completed") {
          setResults(status.metrics as SimResults);
          setSimulations((prev) => ({
            ...prev,
            [simId]: { ...prev[simId], status: "completed" },
          }));
          setLoading(false);
        } else if (status.status === "failed") {
          setError(status.error || "Simulation failed");
          setSimulations((prev) => ({
            ...prev,
            [simId]: { ...prev[simId], status: "failed" },
          }));
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
      const d = data as { metrics?: SimResults };
      setResults(d.metrics || (data as SimResults));
    } catch {
      setError("Could not fetch results");
    }
  };

  const simKeys = Object.keys(simulations);
  const currentSim = simulations[selectedSim];

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      {/* Sidebar */}
      <div className="w-72 space-y-3 flex-shrink-0">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-3">
          Simulations
        </h3>
        {simKeys.map((key) => {
          const sim = simulations[key];
          return (
            <button
              key={key}
              onClick={() => selectSim(key)}
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
              <div className="text-xs text-[var(--text-secondary)]">
                {sim.name}
              </div>
            </button>
          );
        })}
      </div>

      {/* Main panel */}
      <div className="flex-1 card flex flex-col overflow-hidden">
        {currentSim && (
          <>
            {/* Header */}
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border)]">
              <div>
                <h2 className="text-lg font-semibold">{currentSim.name}</h2>
                <p className="text-sm text-[var(--text-secondary)]">
                  {currentSim.description}
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

            {/* Parameter controls */}
            {currentSim.configurable_params && (
              <div className="flex flex-wrap gap-3 mb-4 pb-3 border-b border-[var(--border)]">
                {Object.entries(currentSim.configurable_params).map(
                  ([key, meta]) => (
                    <div key={key} className="flex flex-col">
                      <label className="text-xs text-[var(--text-secondary)] mb-1">
                        {meta.label}
                      </label>
                      <input
                        type="number"
                        value={params[key] ?? meta.default}
                        step={meta.type === "float" ? 0.01 : 1}
                        onChange={(e) =>
                          setParams((p) => ({
                            ...p,
                            [key]: parseFloat(e.target.value) || 0,
                          }))
                        }
                        className="w-28 px-2 py-1 rounded bg-[var(--bg-primary)] border border-[var(--border)] text-sm font-mono"
                      />
                    </div>
                  ),
                )}
              </div>
            )}

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
                <SimChart simId={selectedSim} data={results} />
              </div>
            )}

            {!results && !loading && (
              <div className="flex-1 flex items-center justify-center text-[var(--text-secondary)] text-sm">
                Click &quot;Run Simulation&quot; to execute {selectedSim}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function SimChart({ simId, data }: { simId: string; data: SimResults }) {
  if (simId === "sim1") return <Sim1Chart data={data} />;
  if (simId === "sim2") return <Sim2Chart data={data} />;
  if (simId === "sim3") return <Sim3Chart data={data} />;
  if (simId === "sim4") return <Sim4Chart data={data} />;
  return <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>;
}

function Sim1Chart({ data }: { data: SimResults }) {
  const betas = data.betas as number[];
  const klC = data.kl_constrained as number[];
  const klU = data.kl_unconstrained as number[];

  if (!betas || !klC || !klU) {
    return <div className="text-sm text-[var(--text-secondary)]">No chart data available</div>;
  }

  const chartData = betas.map((b, i) => ({
    beta: b,
    "Gibbs (constrained)": klC[i],
    "Uniform (unconstrained)": klU[i],
  }));

  const bestKLC = Math.min(...klC);
  const bestKLU = Math.min(...klU);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="Best KL (Gibbs)" value={bestKLC.toExponential(3)} accent="var(--accent-blue)" />
        <MetricCard label="Best KL (Uniform)" value={bestKLU.toExponential(3)} accent="var(--accent-purple)" />
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-3">
          KL Divergence vs Inverse Temperature (β)
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          The Gibbs-weighted model converges to the Born rule at high β (low T),
          while uniform weighting retains large divergence.
        </p>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="beta"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "β (inverse temperature)", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "KL divergence (bits)", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="Gibbs (constrained)" stroke="#4a9eff" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="Uniform (unconstrained)" stroke="#c084fc" strokeWidth={2} dot={false} strokeDasharray="5 5" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Sim2Chart({ data }: { data: SimResults }) {
  const temps = data.temperatures as number[];
  const klBorn = data.kl_from_born as number[];
  const klGibbs = data.kl_from_gibbs as number[];

  if (!temps || !klBorn || !klGibbs) {
    return <div className="text-sm text-[var(--text-secondary)]">No chart data available</div>;
  }

  const chartData = temps.map((t, i) => ({
    temperature: t,
    "KL from Born": klBorn[i],
    "KL from Gibbs": klGibbs[i],
  }));

  const crossoverIdx = klBorn.findIndex((b, i) => klGibbs[i] < b);
  const crossoverT = crossoverIdx >= 0 ? temps[crossoverIdx] : null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3">
        <MetricCard label="Min KL (Born)" value={Math.min(...klBorn).toExponential(3)} accent="var(--accent-green)" />
        <MetricCard label="Min KL (Gibbs)" value={Math.min(...klGibbs).toExponential(3)} accent="var(--accent-blue)" />
        {crossoverT && (
          <MetricCard label="Crossover T" value={crossoverT.toFixed(3)} accent="var(--accent-yellow)" />
        )}
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-3">
          KL Divergence vs Effective Temperature
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          At low T, the Gibbs distribution becomes a better fit than the Born rule --
          confirming the SGD-thermodynamics analogy.
        </p>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="temperature"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "T_eff (effective temperature)", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "KL divergence", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="KL from Born" stroke="#34d399" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="KL from Gibbs" stroke="#4a9eff" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Sim3Chart({ data }: { data: SimResults }) {
  const temps = data.temperatures as number[];
  const klGibbs = data.kl_from_gibbs as number[];
  const klBorn = data.kl_from_born as number[];
  const convergenceTimes = data.convergence_times as number[];
  const energies = data.energies as number[];

  if (!temps || !klGibbs) {
    return <div className="text-sm text-[var(--text-secondary)]">No chart data available</div>;
  }

  const klChartData = temps.map((t, i) => ({
    temperature: t,
    "KL from Gibbs": klGibbs[i],
    ...(klBorn ? { "KL from Born": klBorn[i] } : {}),
  }));

  const barData = energies
    ? energies.map((e, i) => ({
        level: `E${i}`,
        energy: e,
      }))
    : [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        <MetricCard label="Min KL (Gibbs)" value={Math.min(...klGibbs).toExponential(3)} accent="var(--accent-blue)" />
        {convergenceTimes && (
          <MetricCard
            label="Avg convergence"
            value={`${(convergenceTimes.reduce((a, b) => a + b, 0) / convergenceTimes.length).toFixed(1)} steps`}
            accent="var(--accent-purple)"
          />
        )}
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-3">
          KL Divergence vs Bath Temperature
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          The steady-state populations follow Boltzmann statistics --
          confirming the thermal selection mechanism.
        </p>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={klChartData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="temperature"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "Temperature", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              label={{ value: "KL divergence", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="KL from Gibbs" stroke="#4a9eff" strokeWidth={2} dot={false} />
            {klBorn && (
              <Line type="monotone" dataKey="KL from Born" stroke="#34d399" strokeWidth={2} dot={false} />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {barData.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Energy Level Spectrum</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="level" tick={{ fill: "#888", fontSize: 11 }} />
              <YAxis
                label={{ value: "Energy", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
                tick={{ fill: "#888", fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              />
              <Bar dataKey="energy" radius={[4, 4, 0, 0]}>
                {barData.map((_, i) => (
                  <Cell key={i} fill={`hsl(${210 + i * 20}, 70%, 55%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function Sim4Chart({ data }: { data: SimResults }) {
  const temps = data.temperatures as number[];
  const bornProbs = data.born_probs as number[];
  const residualNorm = data.residual_norm as number[];
  const tdBornResidual = data.td_born_residual_norm as number[] | undefined;
  const energies = data.energies as number[];
  const actions = data.euclidean_actions as number[];
  const thermalProbs = data.thermal_state_probs as number[][];
  const tdProbs = data.td_probs as number[][];

  if (!temps || !residualNorm) {
    return <div className="text-sm text-[var(--text-secondary)]">No chart data available</div>;
  }

  const residualChartData = temps.map((t, i) => ({
    temperature: parseFloat(t.toPrecision(4)),
    "TD vs Thermal": residualNorm[i],
    ...(tdBornResidual ? { "TD vs Born": tdBornResidual[i] } : {}),
  }));

  const compIdx = Math.min(Math.floor(temps.length * 0.75), temps.length - 1);
  const compTemp = temps[compIdx];

  const comparisonData = bornProbs
    ? bornProbs.map((b, i) => ({
        level: `|${i}⟩`,
        "Born rule": b,
        "Thermal (QM)": thermalProbs?.[compIdx]?.[i] ?? 0,
        "TD prediction": tdProbs?.[compIdx]?.[i] ?? 0,
      }))
    : [];

  const maxResidual = Math.max(...residualNorm);
  const peakIdx = residualNorm.indexOf(maxResidual);

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg border border-amber-800/30 bg-amber-900/10 text-sm">
        <div className="font-semibold text-amber-400 mb-1">Distinguishing Prediction (P1)</div>
        <p className="text-[var(--text-secondary)]">
          Three competing frameworks predict different measurement probabilities
          for the same quantum system: <strong>Born</strong> (amplitudes from
          initial state), <strong>Thermal QM</strong> (Gibbs over energies),
          and <strong>TD</strong> (Gibbs over Euclidean actions, S_E ∝ E^3/2
          from WKB). The residual between Thermal and TD is nonzero because
          they weight by different physical quantities — energy vs. action.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard label="Peak residual" value={maxResidual.toExponential(3)} accent="#f59e0b" />
        <MetricCard label="Peak T" value={temps[peakIdx].toFixed(3)} accent="#c084fc" />
        <MetricCard
          label="High-T residual"
          value={residualNorm[residualNorm.length - 1].toExponential(3)}
          accent="#34d399"
        />
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-3">
          Residual ‖P_TD − P_thermal‖ vs Temperature
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          Nonzero residual = distinguishable predictions. Both TD and thermal
          favor the ground state at low T, so they partially agree. At
          intermediate T, they diverge maximally because TD weights by
          Euclidean action (S_E ∝ E^1.5) while thermal weights by energy (E) —
          a genuinely different physical mechanism.
        </p>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={residualChartData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="temperature"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "Temperature", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
              tickFormatter={(v: number) => Number(v.toPrecision(3)).toString()}
            />
            <YAxis
              label={{ value: "‖Residual‖₂", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
              tickFormatter={(v: number) => v === 0 ? "0" : v < 0.01 ? v.toExponential(1) : v.toFixed(2)}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `T = ${Number(label).toPrecision(3)}`}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="TD vs Thermal" stroke="#f59e0b" strokeWidth={2} dot={false} />
            {tdBornResidual && (
              <Line type="monotone" dataKey="TD vs Born" stroke="#c084fc" strokeWidth={2} dot={false} strokeDasharray="5 3" />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {comparisonData.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">
            Probability Comparison at T = {compTemp.toFixed(2)}
          </h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">
            All three predictions for each energy level.
            &ldquo;Born rule&rdquo; is temperature-independent.
            &ldquo;Thermal (QM)&rdquo; thermalizes the state.
            &ldquo;TD prediction&rdquo; modifies the probability rule itself.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="level" tick={{ fill: "#888", fontSize: 11 }} />
              <YAxis
                label={{ value: "Probability", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
                tick={{ fill: "#888", fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              />
              <Legend wrapperStyle={{ paddingTop: 16 }} />
              <Bar dataKey="Born rule" fill="#4a9eff" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Thermal (QM)" fill="#34d399" radius={[4, 4, 0, 0]} />
              <Bar dataKey="TD prediction" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {energies && actions && (
        <div>
          <h3 className="text-sm font-semibold mb-3">Level Structure</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={energies.map((e, i) => ({
                level: `|${i}⟩`,
                Energy: e,
                "S_E": actions[i],
              }))}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="level" tick={{ fill: "#888", fontSize: 11 }} />
              <YAxis tick={{ fill: "#888", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              />
              <Legend wrapperStyle={{ paddingTop: 8 }} />
              <Bar dataKey="Energy" fill="#4a9eff" radius={[4, 4, 0, 0]} />
              <Bar dataKey="S_E" fill="#c084fc" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div className="p-3 rounded-lg bg-[var(--bg-primary)] border-l-2" style={{ borderColor: accent }}>
      <div className="text-xs text-[var(--text-secondary)]">{label}</div>
      <div className="text-lg font-mono font-semibold">{value}</div>
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
