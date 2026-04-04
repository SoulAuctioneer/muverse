"use client";

import { useState, useEffect } from "react";
import { api, PaperOutline, PaperSection } from "@/lib/api";

const STATUS_COLORS: Record<string, string> = {
  outline: "#f59e0b",
  drafted: "#4a9eff",
  reviewed: "#8b5cf6",
  final: "#34d399",
};

export default function PaperEditor() {
  const [outline, setOutline] = useState<PaperOutline | null>(null);
  const [selectedSection, setSelectedSection] = useState<PaperSection | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.paper
      .outline()
      .then((data) => {
        setOutline(data);
        if (data.sections.length > 0) setSelectedSection(data.sections[0]);
      })
      .catch(() => {
        setError("Could not load paper outline. Is the API running?");
        setOutline(buildFallbackOutline());
      });
  }, []);

  const completeness = outline
    ? outline.sections.filter((s) => s.status === "final").length /
      outline.sections.length
    : 0;

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      <div className="w-72 space-y-2">
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
            Paper Progress
          </h3>
          <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${completeness * 100}%`,
                background: "var(--accent-green)",
              }}
            />
          </div>
          <p className="text-xs text-[var(--text-secondary)] mt-1">
            {Math.round(completeness * 100)}% complete
          </p>
        </div>

        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
          Sections
        </h3>
        {outline?.sections.map((section) => (
          <button
            key={section.number}
            onClick={() => setSelectedSection(section)}
            className={`w-full text-left p-3 rounded-lg transition-all text-sm ${
              selectedSection?.number === section.number
                ? "bg-[var(--bg-tertiary)] border border-[var(--border)]"
                : "hover:bg-[var(--bg-tertiary)]"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium">
                {section.number}. {section.title}
              </span>
              <span
                className="inline-block w-2 h-2 rounded-full"
                style={{ background: STATUS_COLORS[section.status] || "#666" }}
              />
            </div>
          </button>
        ))}
      </div>

      <div className="flex-1 card overflow-y-auto">
        {error && (
          <div className="p-3 rounded-lg bg-amber-900/20 border border-amber-800/30 text-amber-400 text-sm mb-4">
            {error}
          </div>
        )}

        {selectedSection ? (
          <SectionView section={selectedSection} />
        ) : (
          <p className="text-[var(--text-secondary)] text-sm">
            Select a section to view details.
          </p>
        )}
      </div>
    </div>
  );
}

function SectionView({ section }: { section: PaperSection }) {
  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h2 className="text-xl font-semibold">
            {section.number}. {section.title}
          </h2>
          <span
            className="badge"
            style={{
              background: `${STATUS_COLORS[section.status]}20`,
              color: STATUS_COLORS[section.status],
            }}
          >
            {section.status}
          </span>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
          Outline Points
        </h3>
        <ul className="space-y-1.5">
          {section.outline_points.map((point, i) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              <span className="text-[var(--accent-blue)] mt-0.5">-</span>
              {point}
            </li>
          ))}
        </ul>
      </div>

      {section.body_latex && (
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
            LaTeX Content
          </h3>
          <pre className="p-4 rounded-lg bg-[var(--bg-primary)] text-xs mono overflow-x-auto max-h-96 whitespace-pre-wrap">
            {section.body_latex}
          </pre>
        </div>
      )}

      {!section.body_latex && (
        <div className="p-8 rounded-lg border border-dashed border-[var(--border)] text-center text-[var(--text-secondary)] text-sm">
          No content yet. Run the Writer agent to draft this section.
        </div>
      )}
    </div>
  );
}

function buildFallbackOutline(): PaperOutline {
  return {
    title: "Thermodynamic Darwinism: Born Rule as Emergent Gibbs Weighting",
    sections: [
      { number: "1", title: "Introduction", status: "outline", outline_points: ["MWI context", "Born rule problem", "Motivation"], body_latex: "" },
      { number: "2", title: "Background", status: "outline", outline_points: ["Quantum Darwinism", "Wick rotation", "FEP"], body_latex: "" },
      { number: "3", title: "The Framework", status: "outline", outline_points: ["Axioms A1-A8"], body_latex: "" },
      { number: "4", title: "Derivations", status: "outline", outline_points: ["D1-D3"], body_latex: "" },
      { number: "5", title: "Predictions", status: "outline", outline_points: ["P1-P3"], body_latex: "" },
      { number: "6", title: "Computational Results", status: "outline", outline_points: ["Simulations 1-3"], body_latex: "" },
      { number: "7", title: "Discussion", status: "outline", outline_points: ["Limitations", "Open problems"], body_latex: "" },
      { number: "8", title: "Conclusion", status: "outline", outline_points: ["Summary", "Future work"], body_latex: "" },
    ],
  };
}
