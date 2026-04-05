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
  if (simId === "sim5") return <Sim5Chart data={data} />;
  if (simId === "sim6") return <Sim6Chart data={data} />;
  if (simId === "sim7") return <Sim7Chart data={data} />;
  if (simId === "sim8") return <Sim8Chart data={data} />;
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

function Sim5Chart({ data }: { data: SimResults }) {
  const energies = data.energies as number[];
  const wkbActions = data.wkb_actions as number[];
  const barrierTop = data.barrier_top as number;
  const temps = data.bath_temps as number[];
  const lindbladPops = data.lindblad_pops as number[][];
  const gibbsEPops = data.gibbs_energy_pops as number[][];
  const gibbsSPops = data.gibbs_action_pops as number[][];
  const bornPops = data.born_pops as number[];
  const resLE = data.residual_lindblad_vs_gibbs_e as number[];
  const resES = data.residual_gibbs_e_vs_gibbs_s as number[];
  const traceTimes = data.trace_times as number[];
  const tracePops = data.trace_pops as number[][];
  const traceTempIdx = data.trace_temp_idx as number;

  const [selTemp, setSelTemp] = useState(0);

  if (!temps || !lindbladPops) {
    return <div className="text-sm text-[var(--text-secondary)]">No chart data available</div>;
  }

  const nLevels = energies?.length ?? 0;
  const maxResLE = Math.max(...(resLE ?? [0]));
  const maxGap = Math.max(...(resES ?? [0]));
  const maxGapT = temps[(resES ?? []).indexOf(maxGap)];

  const comparisonData = energies
    ? energies.map((_, i) => ({
        level: `|${i}⟩`,
        "Lindblad SS": lindbladPops[selTemp]?.[i] ?? 0,
        "Gibbs(E) — Std QM": gibbsEPops[selTemp]?.[i] ?? 0,
        "Gibbs(S_E) — TD": gibbsSPops[selTemp]?.[i] ?? 0,
      }))
    : [];

  const residualData = temps.map((t, i) => ({
    temperature: t,
    "Lindblad vs Gibbs(E)": resLE[i],
    "Gibbs(E) vs Gibbs(S_E)": resES[i],
  }));

  const levelData = energies
    ? energies.map((e, i) => ({
        level: `|${i}⟩`,
        Energy: e,
        "WKB Action": wkbActions[i],
        subBarrier: e < barrierTop,
      }))
    : [];

  const traceData =
    traceTimes && tracePops
      ? traceTimes.map((t, ti) => {
          const row: Record<string, number> = { time: t };
          for (let n = 0; n < Math.min(nLevels, 6); n++) {
            row[`|${n}⟩`] = tracePops[ti]?.[n] ?? 0;
          }
          return row;
        })
      : [];

  const traceColors = ["#4a9eff", "#34d399", "#f59e0b", "#c084fc", "#f87171", "#94a3b8"];

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg border border-emerald-800/30 bg-emerald-900/10 text-sm">
        <div className="font-semibold text-emerald-400 mb-1">
          The Small Provable Step
        </div>
        <p className="text-[var(--text-secondary)]">
          This simulation solves the <strong>Lindblad master equation</strong> for
          a double-well potential coupled to a thermal bath — the standard framework
          for open quantum systems. It compares the <em>exact</em> steady-state
          populations to three predictions: Born rule, Gibbs over energies (standard QM),
          and Gibbs over WKB actions (Thermodynamic Darwinism). The Lindblad equation
          satisfies detailed balance, so its steady state is guaranteed to be Gibbs(E).
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          label="‖Lindblad − Gibbs(E)‖ (max)"
          value={maxResLE < 1e-6 ? "< 10⁻⁶" : maxResLE.toExponential(2)}
          accent="#34d399"
        />
        <MetricCard
          label="‖Gibbs(E) − Gibbs(S_E)‖ (max)"
          value={maxGap.toFixed(3)}
          accent="#f59e0b"
        />
        <MetricCard
          label="Max gap at T ="
          value={maxGapT?.toFixed(2) ?? "—"}
          accent="#c084fc"
        />
      </div>

      {/* Temperature selector + comparison chart */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <h3 className="text-sm font-semibold">
            Population Comparison at T = {temps[selTemp]?.toFixed(2)}
          </h3>
          <input
            type="range"
            min={0}
            max={temps.length - 1}
            value={selTemp}
            onChange={(e) => setSelTemp(parseInt(e.target.value))}
            className="flex-1 max-w-48"
          />
        </div>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          Lindblad steady state (green) matches Gibbs(E) (blue) exactly.
          Gibbs(S_E) (orange) predicts a measurably different distribution —
          it favours above-barrier states because they have zero tunneling action.
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
              formatter={fmtTooltip}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Bar dataKey="Lindblad SS" fill="#34d399" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Gibbs(E) — Std QM" fill="#4a9eff" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Gibbs(S_E) — TD" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Residual chart */}
      <div>
        <h3 className="text-sm font-semibold mb-3">
          Residuals vs Temperature
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          Green line (Lindblad vs Gibbs(E)) is zero at all temperatures — confirming
          the steady state IS the thermal Gibbs state. Orange line shows the gap
          between standard QM and the TD prediction — large and distinguishable.
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={residualData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="temperature"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "Bath temperature", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              label={{ value: "‖Residual‖₂", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `T = ${Number(label).toFixed(2)}`}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="Lindblad vs Gibbs(E)" stroke="#34d399" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="Gibbs(E) vs Gibbs(S_E)" stroke="#f59e0b" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Time-evolution trace */}
      {traceData.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">
            Time Evolution at T = {temps[traceTempIdx]?.toFixed(2)}
          </h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">
            Initial asymmetric superposition relaxes toward the Gibbs thermal state.
            Each line is the population of one energy eigenstate.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={traceData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="time"
                label={{ value: "Time (ℏ/E)", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
                tick={{ fill: "#888", fontSize: 11 }}
              />
              <YAxis
                label={{ value: "Population ρ_nn", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
                tick={{ fill: "#888", fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
                labelStyle={{ color: "#ccc" }}
                formatter={fmtTooltip}
              />
              <Legend wrapperStyle={{ paddingTop: 16 }} />
              {Array.from({ length: Math.min(nLevels, 6) }, (_, n) => (
                <Line
                  key={n}
                  type="monotone"
                  dataKey={`|${n}⟩`}
                  stroke={traceColors[n]}
                  strokeWidth={1.5}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Level structure */}
      {levelData.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-3">
            Energy Levels and WKB Tunneling Actions
          </h3>
          <p className="text-xs text-[var(--text-secondary)] mb-4">
            Below the barrier (dashed line at E = {barrierTop.toFixed(1)}),
            the WKB action decreases with energy — so Gibbs(E) and Gibbs(S_E)
            predict <em>opposite</em> orderings.
            Above the barrier, S_E = 0 (no tunneling region).
          </p>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={levelData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="level" tick={{ fill: "#888", fontSize: 11 }} />
              <YAxis tick={{ fill: "#888", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
                formatter={fmtTooltip}
              />
              <Legend wrapperStyle={{ paddingTop: 8 }} />
              <Bar dataKey="Energy" fill="#4a9eff" radius={[4, 4, 0, 0]} />
              <Bar dataKey="WKB Action" fill="#c084fc" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Scientific verdict */}
      <div className="p-4 rounded-lg border border-blue-800/30 bg-blue-900/10 text-sm space-y-2">
        <div className="font-semibold text-blue-400">Scientific Verdict</div>
        <p className="text-[var(--text-secondary)]">
          The Lindblad master equation produces the Gibbs state over <em>energies</em>,
          matching standard QM with residual {"<"} 10⁻⁶ at all temperatures. The TD
          prediction (Gibbs over WKB actions) deviates by up to {maxGap.toFixed(2)} in
          L₂ norm — large enough to be distinguishable.
        </p>
        <p className="text-[var(--text-secondary)]">
          <strong>Conclusion:</strong> Within the Born-Markov approximation (which the
          Lindblad equation assumes), standard QM wins decisively. The TD hypothesis
          would need non-Markovian dynamics or strong system-bath coupling to be viable.
        </p>
      </div>
    </div>
  );
}

function Sim6Chart({ data }: { data: SimResults }) {
  const energies = data.energies as number[];
  const wkbActions = data.wkb_actions as number[];
  const couplings = data.coupling_strengths as number[];
  const heomPops = data.heom_pops as number[][];
  const gibbsEPops = data.gibbs_energy_pops as number[];
  const gibbsSPops = data.gibbs_action_pops as number[];
  const resHE = data.residual_heom_vs_gibbs_e as number[];
  const resHS = data.residual_heom_vs_gibbs_s as number[];
  const dirCos = data.direction_cosine as number[];
  const bathTemp = data.bath_temp as number;

  const [selCoupling, setSelCoupling] = useState(0);

  if (!couplings || !heomPops) {
    return <div className="text-sm text-[var(--text-secondary)]">No chart data available</div>;
  }

  const nLevels = energies?.length ?? 0;

  const comparisonData = energies
    ? energies.map((_, i) => ({
        level: `|${i}⟩`,
        "HEOM Steady State": heomPops[selCoupling]?.[i] ?? 0,
        "Bare Gibbs(E)": gibbsEPops[i] ?? 0,
        "Gibbs(S_E) — TD": gibbsSPops[i] ?? 0,
      }))
    : [];

  const sweepData = couplings.map((lam, i) => ({
    lambda: lam,
    "HEOM vs Gibbs(E)": resHE[i],
    "HEOM vs Gibbs(S_E)": resHS[i],
  }));

  const directionData = couplings.map((lam, i) => ({
    lambda: lam,
    "Direction cosine": dirCos[i],
  }));

  const meanDirCos = dirCos.reduce((a, b) => a + b, 0) / dirCos.length;
  const maxDeviation = Math.max(...resHE);
  const maxDevLam = couplings[resHE.indexOf(maxDeviation)];

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg border border-violet-800/30 bg-violet-900/10 text-sm">
        <div className="font-semibold text-violet-400 mb-1">
          Beyond Lindblad: Non-Markovian Dynamics
        </div>
        <p className="text-[var(--text-secondary)]">
          Sim5 showed Lindblad (weak coupling) produces Gibbs(E). This simulation
          uses the <strong>HEOM solver</strong> — numerically exact for a
          Drude-Lorentz bath — to test what happens at <em>strong</em> coupling
          where the Lindblad approximation breaks down. The steady state is the
          mean-force Gibbs state, which deviates from bare Gibbs(E). The key
          question: does the deviation point toward Gibbs(S_E)?
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          label="Mean direction cosine"
          value={meanDirCos.toFixed(3)}
          accent={meanDirCos > 0.2 ? "#34d399" : meanDirCos < -0.2 ? "#f87171" : "#94a3b8"}
        />
        <MetricCard
          label="Max ‖HEOM − Gibbs(E)‖"
          value={maxDeviation.toFixed(4)}
          accent="#c084fc"
        />
        <MetricCard
          label="Max deviation at λ ="
          value={maxDevLam.toFixed(2)}
          accent="#f59e0b"
        />
      </div>

      {/* Coupling strength selector + comparison chart */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <h3 className="text-sm font-semibold">
            Population Comparison at λ = {couplings[selCoupling]?.toFixed(2)}
          </h3>
          <input
            type="range"
            min={0}
            max={couplings.length - 1}
            value={selCoupling}
            onChange={(e) => setSelCoupling(parseInt(e.target.value))}
            className="flex-1 max-w-48"
          />
        </div>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          Purple = HEOM exact steady state. Blue = bare Gibbs(E). Orange = TD
          prediction. Slide to increase coupling strength and observe how the
          HEOM state deviates from Gibbs(E).
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
              formatter={fmtTooltip}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Bar dataKey="HEOM Steady State" fill="#c084fc" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Bare Gibbs(E)" fill="#4a9eff" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Gibbs(S_E) — TD" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Residual sweep */}
      <div>
        <h3 className="text-sm font-semibold mb-3">
          Residuals vs Coupling Strength
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          As coupling increases, the HEOM steady state deviates from Gibbs(E)
          (purple line rises). But the deviation from Gibbs(S_E) (orange line)
          also increases — the strong-coupling correction moves AWAY from the
          TD prediction.
        </p>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={sweepData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="lambda"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "Coupling strength λ", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              label={{ value: "‖Residual‖₂", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `λ = ${Number(label).toFixed(3)}`}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="HEOM vs Gibbs(E)" stroke="#c084fc" strokeWidth={2} dot />
            <Line type="monotone" dataKey="HEOM vs Gibbs(S_E)" stroke="#f59e0b" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Direction cosine */}
      <div>
        <h3 className="text-sm font-semibold mb-3">
          Direction Cosine: Does Strong Coupling Support TD?
        </h3>
        <p className="text-xs text-[var(--text-secondary)] mb-4">
          cos(θ) measures whether the HEOM deviation from Gibbs(E) points toward
          (+1) or away from (−1) the TD prediction. A value near 0 means the
          deviation is orthogonal (unrelated to TD). Negative values mean the
          strong-coupling correction opposes the TD hypothesis.
        </p>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={directionData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="lambda"
              scale="log"
              domain={["auto", "auto"]}
              label={{ value: "Coupling strength λ", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              domain={[-1, 1]}
              label={{ value: "cos(θ)", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
              ticks={[-1, -0.5, 0, 0.5, 1]}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `λ = ${Number(label).toFixed(3)}`}
            />
            <Line type="monotone" dataKey="Direction cosine" stroke="#f87171" strokeWidth={2.5} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Scientific verdict */}
      <div className="p-4 rounded-lg border border-red-800/30 bg-red-900/10 text-sm space-y-2">
        <div className="font-semibold text-red-400">Scientific Verdict</div>
        <p className="text-[var(--text-secondary)]">
          The HEOM steady state deviates from bare Gibbs(E) at strong coupling (max
          deviation: {maxDeviation.toFixed(3)} at λ = {maxDevLam}). But the
          direction cosine is <strong>{meanDirCos < -0.2 ? "consistently negative" :
          meanDirCos > 0.2 ? "positive" : "near zero"}</strong> (mean = {meanDirCos.toFixed(3)}),
          meaning the deviation {meanDirCos < -0.2 ? "moves AWAY from" :
          meanDirCos > 0.2 ? "aligns with" : "is unrelated to"} the TD prediction.
        </p>
        <p className="text-[var(--text-secondary)]">
          <strong>Conclusion:</strong> The influence functional formalism confirms that
          bath-induced corrections to the steady state are controlled by the spectral
          density J(ω) and coupling operator, not by WKB tunneling actions. The Wick
          rotation analogy (Axiom A3) has no support from either Markovian or
          non-Markovian dynamics.
        </p>
      </div>
    </div>
  );
}

function Sim7Chart({ data }: { data: SimResults }) {
  const envSizes = (data.env_sizes as number[]) || [];
  const bornProbs = (data.born_probs as number[]) || [];
  const infoProbs = (data.info_probs as number[]) || [];
  const klBorn = (data.kl_born_per_env as number[]) || [];
  const klInfo = (data.kl_info_per_env as number[]) || [];
  const landauerEff = (data.landauer_efficiency as number[]) || [];
  const redundancy = (data.redundancy_per_env as number[]) || [];
  const pointerBits = (data.pointer_info_bits as number[]) || [];

  const klData = envSizes.map((sz, i) => ({
    "Env size": sz,
    "KL(obs || Born)": klBorn[i] || 0,
    "KL(obs || Info)": klInfo[i] || 0,
  }));

  const effData = envSizes.map((sz, i) => ({
    "Env size": sz,
    "Landauer efficiency η": landauerEff[i] || 0,
    "Redundancy": redundancy[i] || 0,
  }));

  const compLabels = bornProbs.map((_, i) => `State ${i}`);
  const compData = compLabels.map((label, i) => ({
    name: label,
    "Born |ψ|²": bornProbs[i] || 0,
    "Info 1/Iᵢ": infoProbs[i] || 0,
    "Info bits Iᵢ": pointerBits[i] || 0,
  }));

  const maxKlBorn = Math.max(...klBorn.filter(Number.isFinite), 0);
  const maxKlInfo = Math.max(...klInfo.filter(Number.isFinite), 0);
  const meanEff = landauerEff.length > 0
    ? landauerEff.reduce((a, b) => a + b, 0) / landauerEff.length : 0;

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border)] text-sm space-y-2">
        <div className="font-semibold text-emerald-400">Phase A: Information-Theoretic Selection (Non-Circular)</div>
        <p className="text-[var(--text-secondary)]">
          Tests whether Landauer-cost constraints on pointer-state redundancy produce
          selection effects distinguishable from the Born rule. A {(data.d_system as number) || 4}-level
          system is coupled to environments of varying size. The info-budget prediction
          P<sub>i</sub><sup>info</sup> = (1/I<sub>i</sub>) / &Sigma;(1/I<sub>j</sub>) weights
          states by inverse Hamiltonian-determined encoding cost
          I<sub>i</sub> = S(&rho;<sub>E<sub>k</sub>|i</sub>), computed from the actual
          system-environment dynamics &mdash; no Born probabilities assumed.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard label="Max KL(obs || Born)" value={maxKlBorn.toFixed(4)} accent="#4a9eff" />
        <MetricCard label="Max KL(obs || Info)" value={maxKlInfo.toFixed(4)} accent="#34d399" />
        <MetricCard label="Mean Landauer η" value={meanEff.toFixed(3)} accent="#f59e0b" />
      </div>

      {/* Born vs Info-Budget comparison */}
      <div className="p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]">
        <h3 className="text-sm font-semibold mb-3">Probability Comparison: Born vs Info-Budget (Hamiltonian)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={compData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="name" tick={{ fill: "#888", fontSize: 11 }} />
            <YAxis tick={{ fill: "#888", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Born |ψ|²" fill="#4a9eff" />
            <Bar dataKey="Info 1/Iᵢ" fill="#34d399" />
          </BarChart>
        </ResponsiveContainer>
        <p className="text-xs text-[var(--text-secondary)] mt-2">
          Born rule (blue) weights by |&psi;|&sup2;. Information budget (green) weights
          inversely by I<sub>i</sub> = S(&rho;<sub>E|i</sub>), the Hamiltonian-determined
          encoding cost &mdash; no Born probabilities assumed.
        </p>
      </div>

      {/* KL divergence vs environment size */}
      <div className="p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]">
        <h3 className="text-sm font-semibold mb-3">KL Divergence vs Environment Size</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={klData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="Env size"
              label={{ value: "n_env (qubits)", position: "insideBottom", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis tick={{ fill: "#888", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `n_env = ${label}`}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="KL(obs || Born)" stroke="#4a9eff" strokeWidth={2} dot />
            <Line type="monotone" dataKey="KL(obs || Info)" stroke="#34d399" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-xs text-[var(--text-secondary)] mt-2">
          As the environment grows, observed pointer-state statistics should converge
          to Born (blue → 0). For small environments, information constraints may
          pull statistics toward the info-budget prediction (green lower than blue).
        </p>
      </div>

      {/* Landauer efficiency */}
      <div className="p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]">
        <h3 className="text-sm font-semibold mb-3">Landauer Efficiency &amp; Redundancy</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={effData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="Env size"
              label={{ value: "n_env (qubits)", position: "insideBottom", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis tick={{ fill: "#888", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `n_env = ${label}`}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="Landauer efficiency η" stroke="#f59e0b" strokeWidth={2} dot />
            <Line type="monotone" dataKey="Redundancy" stroke="#c084fc" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-xs text-[var(--text-secondary)] mt-2">
          Landauer efficiency (yellow): ratio of minimum thermodynamic cost to actual
          dissipation. When &eta; &rarr; 1, the Landauer bound is tight. Redundancy
          (purple): number of environment fragments carrying the system state.
        </p>
      </div>

      {/* Scientific verdict */}
      <div className="p-4 rounded-lg border border-emerald-800/30 bg-emerald-900/10 text-sm space-y-2">
        <div className="font-semibold text-emerald-400">Scientific Assessment</div>
        <p className="text-[var(--text-secondary)]">
          {meanEff > 0.8
            ? "Landauer efficiency is high — information bounds are tight and genuinely constrain pointer selection in this regime."
            : meanEff > 0.5
            ? "Landauer efficiency is moderate — information bounds are relevant but not yet the dominant constraint."
            : "Landauer efficiency is low — the system dissipates well above the Landauer minimum, so information bounds are not yet the binding constraint."}
        </p>
        <p className="text-[var(--text-secondary)]">
          <strong>Key question:</strong> As the environment shrinks, do observed statistics
          deviate from Born toward the Hamiltonian-determined info-budget prediction? If
          KL(obs || Info) decreases while KL(obs || Born) increases at small n_env, this
          would be evidence for information-theoretic selection. I<sub>i</sub> is now
          computed from S(&rho;<sub>E|i</sub>) &mdash; no circularity.
        </p>
      </div>
    </div>
  );
}

function Sim8Chart({ data }: { data: SimResults }) {
  const gammas = (data.dissipation_rates as number[]) || [];
  const dsDist = (data.ds_distance as number[]) || [];
  const jRatio = (data.jarzynski_ratio as number[]) || [];
  const rowDev = (data.row_sum_dev as number[]) || [];
  const colDev = (data.col_sum_dev as number[]) || [];
  const a4Unitary = data.a4_verified_unitary as boolean;
  const a4Broken = data.a4_broken_dissipative as boolean;

  const dsData = gammas.map((g, i) => ({
    gamma: g,
    "DS distance": dsDist[i] || 0,
    "Row-sum deviation": rowDev[i] || 0,
    "Col-sum deviation": colDev[i] || 0,
  }));

  const jData = gammas.map((g, i) => ({
    gamma: g,
    "Jarzynski ratio": jRatio[i] || 0,
  }));

  const unitaryDS = dsDist.length > 0 ? dsDist[0] : NaN;
  const maxDS = Math.max(...dsDist.filter(Number.isFinite), 0);
  const unitaryJ = jRatio.length > 0 ? jRatio[0] : NaN;

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg border border-amber-800/30 bg-amber-900/10 text-sm">
        <div className="font-semibold text-amber-400 mb-1">
          Axiom A4: Jarzynski Double Stochasticity
        </div>
        <p className="text-[var(--text-secondary)]">
          A4 claims: (a) unitary branching preserves double stochasticity, (b)
          dissipative branching breaks it, (c) Jarzynski-violating branches are
          suppressed. Claims (a) and (b) are established physics. Claim (c)
          depends on falsified A3. This simulation sweeps dissipation rate
          &gamma; from 0 (unitary) to large values to quantify the transition.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          label="Unitary DS distance"
          value={unitaryDS < 0.001 ? "< 10\u207B\u00B3" : unitaryDS.toFixed(4)}
          accent={unitaryDS < 0.01 ? "#34d399" : "#f87171"}
        />
        <MetricCard
          label="Max DS distance"
          value={maxDS.toFixed(4)}
          accent="#f59e0b"
        />
        <MetricCard
          label="Unitary Jarzynski"
          value={unitaryJ.toFixed(4)}
          accent={Math.abs(unitaryJ - 1.0) < 0.01 ? "#34d399" : "#f87171"}
        />
      </div>

      <div className="p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]">
        <h3 className="text-sm font-semibold mb-3">
          Double Stochasticity Distance vs Dissipation Rate
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dsData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="gamma"
              label={{ value: "Dissipation rate \u03B3", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              label={{ value: "Distance", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `\u03B3 = ${label}`}
            />
            <Legend wrapperStyle={{ paddingTop: 16 }} />
            <Line type="monotone" dataKey="DS distance" stroke="#f59e0b" strokeWidth={2.5} dot />
            <Line type="monotone" dataKey="Row-sum deviation" stroke="#c084fc" strokeWidth={1.5} dot strokeDasharray="5 3" />
            <Line type="monotone" dataKey="Col-sum deviation" stroke="#94a3b8" strokeWidth={1.5} dot strokeDasharray="5 3" />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-xs text-[var(--text-secondary)] mt-2">
          At &gamma; = 0 (unitary), DS distance is near zero (doubly stochastic
          by Birkhoff&apos;s theorem). As dissipation increases, row sums deviate
          from 1 &mdash; probability flows preferentially toward the ground
          state, breaking double stochasticity.
        </p>
      </div>

      <div className="p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]">
        <h3 className="text-sm font-semibold mb-3">
          Jarzynski Ratio vs Dissipation Rate
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={jData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="gamma"
              label={{ value: "Dissipation rate \u03B3", position: "insideBottom", offset: -10, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <YAxis
              domain={[0, "auto"]}
              label={{ value: "\u27E8e^{\u2212\u03B2W}\u27E9", angle: -90, position: "insideLeft", offset: -5, style: { fill: "#999", fontSize: 12 } }}
              tick={{ fill: "#888", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{ background: "#1e1e2e", border: "1px solid #333", borderRadius: 8 }}
              labelStyle={{ color: "#ccc" }}
              formatter={fmtTooltip}
              labelFormatter={(label) => `\u03B3 = ${label}`}
            />
            <Line type="monotone" dataKey="Jarzynski ratio" stroke="#4a9eff" strokeWidth={2.5} dot />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-xs text-[var(--text-secondary)] mt-2">
          The Jarzynski equality predicts this ratio = 1.0 for doubly stochastic
          processes. Deviation from 1.0 quantifies how strongly the Jarzynski
          equality is violated by dissipation.
        </p>
      </div>

      <div className={`p-4 rounded-lg border text-sm space-y-2 ${
        a4Unitary && a4Broken
          ? "border-emerald-800/30 bg-emerald-900/10"
          : "border-amber-800/30 bg-amber-900/10"
      }`}>
        <div className={`font-semibold ${
          a4Unitary && a4Broken ? "text-emerald-400" : "text-amber-400"
        }`}>
          Axiom A4 Verdict
        </div>
        <p className="text-[var(--text-secondary)]">
          <strong>(a) Unitary preserves DS:</strong>{" "}
          {a4Unitary ? "VERIFIED" : "NOT VERIFIED"} &mdash; DS distance at
          &gamma;=0 is {unitaryDS < 0.01 ? "< 0.01" : unitaryDS.toFixed(4)}
          {a4Unitary ? " (consistent with Birkhoff's theorem)" : ""}.
        </p>
        <p className="text-[var(--text-secondary)]">
          <strong>(b) Dissipation breaks DS:</strong>{" "}
          {a4Broken ? "VERIFIED" : "NOT VERIFIED"} &mdash; DS distance rises to{" "}
          {maxDS.toFixed(4)} at max dissipation.
        </p>
        <p className="text-[var(--text-secondary)]">
          <strong>(c) Suppression via Gibbs(S_E):</strong> UNTESTABLE &mdash;
          this claim depends on the Euclidean action weighting from falsified A3.
          The suppression mechanism needs reformulation.
        </p>
        <p className="text-[var(--text-secondary)]">
          <strong>Overall:</strong> A4 is <em>partially verified</em>. Its
          established claims (a) and (b) hold numerically. Its novel claim (c)
          is broken along with A3. Status: CONTESTED.
        </p>
      </div>
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
