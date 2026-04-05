"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { api, PaperOutline, PaperSection } from "@/lib/api";
import katex from "katex";

const STATUS_COLORS: Record<string, string> = {
  outline: "#f59e0b",
  drafted: "#4a9eff",
  reviewed: "#8b5cf6",
  final: "#34d399",
};

export default function PaperEditor() {
  const [outline, setOutline] = useState<PaperOutline | null>(null);
  const [selectedSection, setSelectedSection] = useState<PaperSection | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [completeness, setCompleteness] = useState<{
    drafted_sections: number;
    total_sections: number;
  } | null>(null);

  useEffect(() => {
    api.paper
      .outline()
      .then((data) => {
        setOutline(data);
        if (data.sections.length > 0) setSelectedSection(data.sections[0]);
      })
      .catch(() => {
        setError("Could not load paper. Is the API running?");
        setOutline(buildFallbackOutline());
      });

    api.paper
      .completeness()
      .then((data) => {
        const d = data as { drafted_sections: number; total_sections: number };
        setCompleteness(d);
      })
      .catch(() => {});
  }, []);

  const downloadLatex = useCallback(async () => {
    setDownloading(true);
    try {
      const latex = await api.paper.fullLatex();
      const blob = new Blob([latex], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "thermodynamic_darwinism.tex";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Failed to download LaTeX");
    }
    setDownloading(false);
  }, []);

  const progressFraction = completeness
    ? completeness.drafted_sections / completeness.total_sections
    : outline
      ? outline.sections.filter((s) => s.status !== "outline").length /
        outline.sections.length
      : 0;

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      {/* Sidebar */}
      <div className="w-72 space-y-2 flex-shrink-0">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-[var(--text-secondary)]">
              Paper Progress
            </h3>
            <button
              onClick={downloadLatex}
              disabled={downloading}
              className="text-xs px-2 py-1 rounded bg-[var(--bg-tertiary)] hover:bg-[var(--border)] transition-colors"
            >
              {downloading ? "..." : "↓ LaTeX"}
            </button>
          </div>
          <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${progressFraction * 100}%`,
                background: "var(--accent-green)",
              }}
            />
          </div>
          <p className="text-xs text-[var(--text-secondary)] mt-1">
            {Math.round(progressFraction * 100)}% drafted
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
                className="inline-block w-2 h-2 rounded-full flex-shrink-0"
                style={{
                  background: STATUS_COLORS[section.status] || "#666",
                }}
              />
            </div>
          </button>
        ))}
      </div>

      {/* Main content */}
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
            Select a section to read.
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

      {section.body_latex ? (
        <LatexContent latex={section.body_latex} />
      ) : (
        <>
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
          <div className="p-8 rounded-lg border border-dashed border-[var(--border)] text-center text-[var(--text-secondary)] text-sm">
            No content yet. Run the Writer agent to draft this section.
          </div>
        </>
      )}
    </div>
  );
}

function LatexContent({ latex }: { latex: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const content = latex;
    const container = containerRef.current;
    container.innerHTML = "";

    const segments = splitLatex(content);

    for (const seg of segments) {
      if (seg.type === "display") {
        const div = document.createElement("div");
        div.className = "my-4 overflow-x-auto";
        try {
          katex.render(seg.content, div, {
            displayMode: true,
            throwOnError: false,
            trust: true,
            strict: false,
          });
        } catch {
          div.textContent = seg.content;
        }
        container.appendChild(div);
      } else if (seg.type === "inline") {
        const span = document.createElement("span");
        try {
          katex.render(seg.content, span, {
            displayMode: false,
            throwOnError: false,
            trust: true,
            strict: false,
          });
        } catch {
          span.textContent = seg.content;
        }
        container.appendChild(span);
      } else {
        const rendered = renderLatexText(seg.content);
        const span = document.createElement("span");
        span.innerHTML = rendered;
        container.appendChild(span);
      }
    }
  }, [latex]);

  return (
    <div
      ref={containerRef}
      className="paper-content leading-relaxed text-sm"
    />
  );
}

interface Segment {
  type: "text" | "display" | "inline";
  content: string;
}

function splitLatex(text: string): Segment[] {
  const segments: Segment[] = [];
  let rest = text;

  // Strip LaTeX environment wrappers that KaTeX doesn't handle
  rest = rest.replace(/\\begin\{itemize\}|\\end\{itemize\}/g, "");
  rest = rest.replace(/\\begin\{enumerate\}|\\end\{enumerate\}/g, "");
  rest = rest.replace(/\\begin\{trivlist\}|\\end\{trivlist\}/g, "");

  // Process display math: \begin{equation}...\end{equation} and \[...\]
  const displayPatterns = [
    /\\begin\{equation\}([\s\S]*?)\\end\{equation\}/g,
    /\\begin\{align\}([\s\S]*?)\\end\{align\}/g,
    /\\\[([\s\S]*?)\\\]/g,
  ];

  interface MathMatch {
    index: number;
    length: number;
    content: string;
    type: "display";
  }

  const matches: MathMatch[] = [];
  for (const pattern of displayPatterns) {
    let m;
    while ((m = pattern.exec(rest)) !== null) {
      matches.push({
        index: m.index,
        length: m[0].length,
        content: m[1].replace(/\\label\{[^}]*\}/g, "").trim(),
        type: "display",
      });
    }
  }

  matches.sort((a, b) => a.index - b.index);

  let cursor = 0;
  for (const match of matches) {
    if (match.index > cursor) {
      const textBefore = rest.slice(cursor, match.index);
      pushInlineSegments(segments, textBefore);
    }
    segments.push({ type: "display", content: match.content });
    cursor = match.index + match.length;
  }

  if (cursor < rest.length) {
    pushInlineSegments(segments, rest.slice(cursor));
  }

  return segments;
}

function pushInlineSegments(segments: Segment[], text: string) {
  const inlinePattern = /\$([^$]+)\$/g;
  let cursor = 0;
  let m;
  while ((m = inlinePattern.exec(text)) !== null) {
    if (m.index > cursor) {
      segments.push({ type: "text", content: text.slice(cursor, m.index) });
    }
    segments.push({ type: "inline", content: m[1] });
    cursor = m.index + m[0].length;
  }
  if (cursor < text.length) {
    segments.push({ type: "text", content: text.slice(cursor) });
  }
}

function renderLatexText(text: string): string {
  return text
    .replace(/%[^\n]*/g, "")
    .replace(/\\textbf\{([^}]*)\}/g, "<strong>$1</strong>")
    .replace(/\\textit\{([^}]*)\}/g, "<em>$1</em>")
    .replace(/\\emph\{([^}]*)\}/g, "<em>$1</em>")
    .replace(/\\cite\{([^}]*)\}/g, '<span class="text-[var(--accent-blue)]">[$1]</span>')
    .replace(/\\ref\{([^}]*)\}/g, '<span class="text-[var(--accent-blue)]">[ref:$1]</span>')
    .replace(/\\item\[([^\]]*)\]/g, '<div class="mt-3"><strong>$1</strong> ')
    .replace(/\\item/g, '<div class="mt-2">• ')
    .replace(/\\subsection\{([^}]*)\}/g, '<h3 class="text-base font-semibold mt-6 mb-2">$1</h3>')
    .replace(/\\subsubsection\{([^}]*)\}/g, '<h4 class="text-sm font-semibold mt-4 mb-1">$1</h4>')
    .replace(/\\paragraph\{([^}]*)\}/g, '<strong>$1</strong> ')
    .replace(/\\lipsum(\[[^\]]*\])?/g, "")
    .replace(/\\\\(\s|$)/g, "<br/>")
    .replace(/\n\n/g, "</p><p class='mt-2'>")
    .replace(/~/g, "&nbsp;");
}

function buildFallbackOutline(): PaperOutline {
  return {
    title: "Thermodynamic Darwinism: A Selection Principle for Quantum Histories",
    sections: [
      { number: "1", title: "Introduction", status: "outline", outline_points: ["MWI context", "Born rule problem", "Motivation"], body_latex: "" },
      { number: "2", title: "Background", status: "outline", outline_points: ["Quantum Darwinism", "Wick rotation", "Influence functional"], body_latex: "" },
      { number: "3", title: "The Framework", status: "outline", outline_points: ["Axioms A1-A8 (A3 falsified)"], body_latex: "" },
      { number: "4", title: "Derivations", status: "outline", outline_points: ["D1-D3 (broken by A3 falsification)"], body_latex: "" },
      { number: "5", title: "Initial Computational Results", status: "outline", outline_points: ["Simulations 1-3"], body_latex: "" },
      { number: "6", title: "Negative Results: Falsification of A3", status: "outline", outline_points: ["Influence functional analysis", "Sim5 Lindblad", "Sim6 HEOM"], body_latex: "" },
      { number: "7", title: "Discussion: What Survives", status: "outline", outline_points: ["Landauer bounds", "Bekenstein bounds", "SGD/Gibbs analogy"], body_latex: "" },
      { number: "8", title: "Conclusion", status: "outline", outline_points: ["Partial falsification", "Information-theoretic direction"], body_latex: "" },
    ],
  };
}
