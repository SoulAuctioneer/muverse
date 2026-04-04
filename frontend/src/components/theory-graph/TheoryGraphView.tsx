"use client";

import { useEffect, useRef, useState } from "react";
import { api, TheoryGraph, TheoryNode, TheoryEdge } from "@/lib/api";

const NODE_COLORS: Record<string, string> = {
  axiom: "#8b5cf6",
  derivation: "#4a9eff",
  prediction: "#34d399",
  critique: "#ef4444",
};

const STATUS_BADGES: Record<string, string> = {
  postulated: "badge-postulated",
  derived: "badge-derived",
  contested: "badge-contested",
  unverified: "badge-unverified",
  symbolically_verified: "badge-verified",
  numerically_confirmed: "badge-verified",
  open: "badge-critical",
  resolved: "badge-derived",
};

export default function TheoryGraphView() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graph, setGraph] = useState<TheoryGraph | null>(null);
  const [selected, setSelected] = useState<TheoryNode | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.theory
      .graph()
      .then(setGraph)
      .catch(() => setError("Could not load theory graph. Is the API running?"));
  }, []);

  useEffect(() => {
    if (!graph || !svgRef.current) return;
    renderGraph(svgRef.current, graph, setSelected);
  }, [graph]);

  if (error) {
    return <FallbackView error={error} />;
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-160px)]">
      <div className="flex-1 card overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Theory Structure</h2>
          <div className="flex gap-3 text-xs">
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <span key={type} className="flex items-center gap-1">
                <span
                  className="inline-block w-3 h-3 rounded-full"
                  style={{ background: color }}
                />
                {type}
              </span>
            ))}
          </div>
        </div>
        <svg
          ref={svgRef}
          className="w-full h-full"
          style={{ minHeight: "500px" }}
        />
      </div>

      <div className="w-96 card overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">Details</h2>
        {selected ? (
          <NodeDetail node={selected} />
        ) : (
          <p className="text-[var(--text-secondary)] text-sm">
            Click a node in the graph to view its details.
          </p>
        )}
      </div>
    </div>
  );
}

function NodeDetail({ node }: { node: TheoryNode }) {
  const badgeClass =
    STATUS_BADGES[node.status || ""] || STATUS_BADGES[node.severity || ""] || "";

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span
          className="inline-block w-4 h-4 rounded"
          style={{ background: NODE_COLORS[node.type] }}
        />
        <span className="font-mono font-bold">{node.label}</span>
        <span className={`badge ${badgeClass}`}>
          {node.status || node.severity || node.type}
        </span>
      </div>
      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
        {node.statement || `${node.type} node`}
      </p>
      {node.testable !== undefined && (
        <p className="text-xs">
          Testable: {node.testable ? "Yes" : "No"}
        </p>
      )}
    </div>
  );
}

function FallbackView({ error }: { error: string }) {
  const staticNodes = [
    { id: "A1", type: "axiom", label: "A1 — Unitary Evolution" },
    { id: "A2", type: "axiom", label: "A2 — Finite Action" },
    { id: "A3", type: "axiom", label: "A3 — Wick Rotation" },
    { id: "A4", type: "axiom", label: "A4 — Jarzynski" },
    { id: "A5", type: "axiom", label: "A5 — Born Rule" },
    { id: "D1", type: "derivation", label: "D1 — Born from Gibbs" },
    { id: "P1", type: "prediction", label: "P1 — Temp-Dependent Born" },
  ];

  return (
    <div className="card">
      <p className="text-[var(--text-secondary)] text-sm mb-4">{error}</p>
      <h3 className="font-semibold mb-3">Theory Structure (static)</h3>
      <div className="flex flex-wrap gap-2">
        {staticNodes.map((n) => (
          <span
            key={n.id}
            className="badge text-sm px-3 py-1"
            style={{
              background: `${NODE_COLORS[n.type]}20`,
              color: NODE_COLORS[n.type],
              border: `1px solid ${NODE_COLORS[n.type]}40`,
            }}
          >
            {n.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function renderGraph(
  svg: SVGSVGElement,
  graph: TheoryGraph,
  onSelect: (n: TheoryNode) => void,
) {
  const width = svg.clientWidth || 800;
  const height = svg.clientHeight || 500;
  svg.innerHTML = "";
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const nodeMap = new Map(graph.nodes.map((n) => [n.id, n]));

  const typeGroups: Record<string, TheoryNode[]> = {};
  graph.nodes.forEach((n) => {
    (typeGroups[n.type] ||= []).push(n);
  });

  const positions: Record<string, { x: number; y: number }> = {};
  const typeOrder = ["axiom", "derivation", "prediction", "critique"];
  typeOrder.forEach((type, row) => {
    const nodes = typeGroups[type] || [];
    const y = 80 + row * 110;
    nodes.forEach((n, col) => {
      const x = (width / (nodes.length + 1)) * (col + 1);
      positions[n.id] = { x, y };
    });
  });

  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  const marker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
  marker.setAttribute("id", "arrow");
  marker.setAttribute("viewBox", "0 0 10 10");
  marker.setAttribute("refX", "10");
  marker.setAttribute("refY", "5");
  marker.setAttribute("markerWidth", "6");
  marker.setAttribute("markerHeight", "6");
  marker.setAttribute("orient", "auto-start-reverse");
  const arrowPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
  arrowPath.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
  arrowPath.setAttribute("fill", "#4a4a60");
  marker.appendChild(arrowPath);
  defs.appendChild(marker);
  svg.appendChild(defs);

  graph.edges.forEach((e) => {
    const src = positions[e.source];
    const tgt = positions[e.target];
    if (!src || !tgt) return;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", String(src.x));
    line.setAttribute("y1", String(src.y));
    line.setAttribute("x2", String(tgt.x));
    line.setAttribute("y2", String(tgt.y));
    line.setAttribute("stroke", "#3a3a50");
    line.setAttribute("stroke-width", "1.5");
    line.setAttribute("marker-end", "url(#arrow)");
    svg.appendChild(line);
  });

  graph.nodes.forEach((n) => {
    const pos = positions[n.id];
    if (!pos) return;
    const color = NODE_COLORS[n.type] || "#888";

    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("cursor", "pointer");
    g.addEventListener("click", () => onSelect(n));

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", String(pos.x));
    circle.setAttribute("cy", String(pos.y));
    circle.setAttribute("r", "20");
    circle.setAttribute("fill", `${color}30`);
    circle.setAttribute("stroke", color);
    circle.setAttribute("stroke-width", "2");
    g.appendChild(circle);

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", String(pos.x));
    text.setAttribute("y", String(pos.y + 5));
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("fill", color);
    text.setAttribute("font-size", "11");
    text.setAttribute("font-weight", "600");
    text.setAttribute("font-family", "monospace");
    text.textContent = n.label;
    g.appendChild(text);

    svg.appendChild(g);
  });
}
