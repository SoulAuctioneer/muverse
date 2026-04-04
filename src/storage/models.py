"""PostgreSQL DDL for the muverse database.

These SQL statements create the schema for persisting theory state,
simulation results, literature, and agent conversation history.
Executed by database.init_schema() on application startup.
"""

SCHEMA_SQL = """
-- Theory versions: snapshots of the full theory state
CREATE TABLE IF NOT EXISTS theory_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version INTEGER NOT NULL,
    name TEXT NOT NULL DEFAULT 'Thermodynamic Darwinism',
    state_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_theory_versions_version ON theory_versions(version DESC);

-- Individual axioms (denormalized for fast queries)
CREATE TABLE IF NOT EXISTS axioms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL UNIQUE,
    statement TEXT NOT NULL,
    formal_expression TEXT,
    status TEXT NOT NULL DEFAULT 'postulated',
    source_document TEXT,
    tags TEXT[] DEFAULT '{}',
    theory_version_id UUID REFERENCES theory_versions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Derivations
CREATE TABLE IF NOT EXISTS derivations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL UNIQUE,
    premises TEXT[] NOT NULL,
    conclusion TEXT NOT NULL,
    steps_json JSONB NOT NULL DEFAULT '[]',
    verification_status TEXT NOT NULL DEFAULT 'unverified',
    agent_notes TEXT,
    theory_version_id UUID REFERENCES theory_versions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL UNIQUE,
    derived_from TEXT[] DEFAULT '{}',
    statement TEXT NOT NULL,
    quantitative_formula TEXT,
    testable BOOLEAN DEFAULT true,
    experimental_design TEXT,
    discriminating_power TEXT,
    theory_version_id UUID REFERENCES theory_versions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Critiques
CREATE TABLE IF NOT EXISTS critiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_label TEXT NOT NULL,
    critique_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium',
    description TEXT NOT NULL,
    counter_argument TEXT,
    resolution_status TEXT NOT NULL DEFAULT 'open',
    resolution_notes TEXT,
    theory_version_id UUID REFERENCES theory_versions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Simulation configs and results
CREATE TABLE IF NOT EXISTS simulation_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_name TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS simulation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES simulation_configs(id),
    status TEXT NOT NULL DEFAULT 'pending',
    metrics JSONB DEFAULT '{}',
    figures TEXT[] DEFAULT '{}',
    raw_data JSONB,
    analysis_notes TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

-- Literature / citations
CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bibtex_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    authors TEXT[] DEFAULT '{}',
    year INTEGER,
    journal TEXT,
    url TEXT,
    bibtex TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Agent conversation history
CREATE TABLE IF NOT EXISTS agent_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    task TEXT,
    input_summary TEXT,
    output_text TEXT NOT NULL,
    theory_version INTEGER,
    iteration INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_history_agent ON agent_history(agent_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_history_phase ON agent_history(phase);

-- Paper sections
CREATE TABLE IF NOT EXISTS paper_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section_number TEXT,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'outline',
    outline_points TEXT[] DEFAULT '{}',
    body_latex TEXT DEFAULT '',
    related_axioms TEXT[] DEFAULT '{}',
    related_derivations TEXT[] DEFAULT '{}',
    related_simulations TEXT[] DEFAULT '{}',
    citations_used TEXT[] DEFAULT '{}',
    review_notes TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""
