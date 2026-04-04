"use client";

import { useState, useEffect, useRef } from "react";
import { api, DerivationStep } from "@/lib/api";
import katex from "katex";

function RenderedLatex({
  latex,
  displayMode = true,
}: {
  latex: string;
  displayMode?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    try {
      katex.render(latex, ref.current, {
        displayMode,
        throwOnError: false,
        trust: true,
        strict: false,
      });
    } catch {
      ref.current.textContent = latex;
    }
  }, [latex, displayMode]);

  return <div ref={ref} />;
}

const STEP_COLORS = [
  "#4a9eff",
  "#c084fc",
  "#f59e0b",
  "#34d399",
  "#f87171",
  "#38bdf8",
  "#fb923c",
  "#a78bfa",
];

const STEP_ICONS = ["∫", "τ", "Z", "∂", "∇", "ψ", "Δ", "⚡"];

export default function MathExplorer() {
  const [steps, setSteps] = useState<DerivationStep[]>([]);
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.math
      .derivations()
      .then((data) => {
        setSteps(data.steps);
        if (data.steps.length > 0) setActiveStep(data.steps[0].id);
        setLoading(false);
      })
      .catch((e) => {
        setError("Could not load derivations. Is the API running?");
        setLoading(false);
      });
  }, []);

  const currentStep = steps.find((s) => s.id === activeStep);
  const currentIdx = steps.findIndex((s) => s.id === activeStep);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-160px)]">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-[var(--accent-blue)] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-[var(--text-secondary)] text-sm">
            Loading derivation chain...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      {/* Chain navigation */}
      <div className="w-72 flex-shrink-0">
        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-4">
          Derivation Chain
        </h3>
        <div className="relative">
          {/* Connecting line */}
          <div
            className="absolute left-5 top-8 bottom-8 w-px"
            style={{ background: "var(--border)" }}
          />

          <div className="space-y-1">
            {steps.map((step, i) => (
              <button
                key={step.id}
                onClick={() => setActiveStep(step.id)}
                className={`w-full text-left p-3 rounded-lg transition-all relative ${
                  activeStep === step.id
                    ? "bg-[var(--bg-tertiary)] border border-[var(--border)]"
                    : "hover:bg-[var(--bg-tertiary)]"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold flex-shrink-0 relative z-10"
                    style={{
                      background:
                        activeStep === step.id
                          ? STEP_COLORS[i]
                          : "var(--bg-primary)",
                      color:
                        activeStep === step.id ? "#fff" : STEP_COLORS[i],
                      border: `2px solid ${STEP_COLORS[i]}`,
                    }}
                  >
                    {STEP_ICONS[i]}
                  </div>
                  <div>
                    <div className="font-medium text-sm">{step.title}</div>
                    <div className="text-xs text-[var(--text-secondary)]">
                      {step.subtitle}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 card overflow-y-auto">
        {error && (
          <div className="p-3 rounded-lg bg-amber-900/20 border border-amber-800/30 text-amber-400 text-sm mb-4">
            {error}
          </div>
        )}

        {currentStep && (
          <div className="space-y-6">
            {/* Step header */}
            <div className="flex items-center gap-4 pb-4 border-b border-[var(--border)]">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold"
                style={{
                  background: STEP_COLORS[currentIdx] + "20",
                  color: STEP_COLORS[currentIdx],
                }}
              >
                {STEP_ICONS[currentIdx]}
              </div>
              <div>
                <div className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wide">
                  Step {currentIdx + 1} of {steps.length}
                </div>
                <h2 className="text-xl font-semibold">{currentStep.title}</h2>
                <p className="text-sm text-[var(--text-secondary)]">
                  {currentStep.subtitle}
                </p>
              </div>
            </div>

            {/* Description */}
            <div className="text-sm leading-relaxed text-[var(--text-secondary)]">
              {currentStep.description}
            </div>

            {/* Equations */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold">Key Equations</h3>
              {currentStep.equations.map((eq, i) => (
                <div
                  key={i}
                  className="p-4 rounded-lg bg-[var(--bg-primary)] border border-[var(--border)]"
                >
                  <div className="text-xs text-[var(--text-secondary)] mb-2 font-medium">
                    {eq.label}
                  </div>
                  <div className="overflow-x-auto py-2">
                    <RenderedLatex latex={eq.latex} />
                  </div>
                </div>
              ))}
            </div>

            {/* Navigation arrows */}
            {currentIdx < steps.length - 1 && (
              <div className="pt-4 border-t border-[var(--border)]">
                <button
                  onClick={() => setActiveStep(steps[currentIdx + 1].id)}
                  className="flex items-center gap-2 text-sm font-medium hover:opacity-80 transition-opacity"
                  style={{ color: STEP_COLORS[(currentIdx + 1) % STEP_COLORS.length] }}
                >
                  Next: {steps[currentIdx + 1].title} →
                </button>
              </div>
            )}

            {currentIdx === steps.length - 1 && (
              <div className="p-4 rounded-lg border border-dashed border-[var(--border)] text-center text-sm text-[var(--text-secondary)]">
                    End of the derivation chain. Path integrals → Wick rotation →
                    partition functions → Fokker-Planck → SGD → WKB derivation →
                    temperature prediction → branch suppression. The Born rule
                    is derived from WKB + thermodynamics, with testable deviations.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
