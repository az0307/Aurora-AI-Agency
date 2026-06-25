-- ─────────────────────────────────────────────────────────────
-- init.sql — Red Team Stack PostgreSQL Schema
-- Created at container startup
-- ─────────────────────────────────────────────────────────────

-- Engagements
CREATE TABLE IF NOT EXISTS engagements (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    target      TEXT,
    type        VARCHAR(50) DEFAULT 'web',  -- web|network|ad|ctf|bugbounty
    status      VARCHAR(50) DEFAULT 'active',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Hosts discovered per engagement
CREATE TABLE IF NOT EXISTS hosts (
    id              SERIAL PRIMARY KEY,
    engagement_id   INTEGER REFERENCES engagements(id) ON DELETE CASCADE,
    ip_address      INET,
    hostname        VARCHAR(255),
    os              VARCHAR(255),
    status          VARCHAR(50) DEFAULT 'up',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Services found on hosts
CREATE TABLE IF NOT EXISTS services (
    id          SERIAL PRIMARY KEY,
    host_id     INTEGER REFERENCES hosts(id) ON DELETE CASCADE,
    port        INTEGER NOT NULL,
    protocol    VARCHAR(10) DEFAULT 'tcp',
    service     VARCHAR(100),
    version     VARCHAR(255),
    banner      TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Vulnerability findings
CREATE TABLE IF NOT EXISTS findings (
    id              SERIAL PRIMARY KEY,
    engagement_id   INTEGER REFERENCES engagements(id) ON DELETE CASCADE,
    host_id         INTEGER REFERENCES hosts(id),
    title           VARCHAR(500) NOT NULL,
    severity        VARCHAR(20) NOT NULL CHECK (severity IN ('critical','high','medium','low','info')),
    cvss_score      DECIMAL(3,1),
    cve             VARCHAR(50),
    cwe             VARCHAR(50),
    description     TEXT,
    evidence        TEXT,
    poc             TEXT,
    remediation     TEXT,
    status          VARCHAR(50) DEFAULT 'open',  -- open|verified|false_positive|fixed
    tool            VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Raw tool scan outputs
CREATE TABLE IF NOT EXISTS scans (
    id              SERIAL PRIMARY KEY,
    engagement_id   INTEGER REFERENCES engagements(id) ON DELETE CASCADE,
    tool            VARCHAR(100) NOT NULL,
    target          TEXT,
    command         TEXT,
    output          TEXT,
    exit_code       INTEGER,
    duration_secs   INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Captured credentials
CREATE TABLE IF NOT EXISTS credentials (
    id              SERIAL PRIMARY KEY,
    engagement_id   INTEGER REFERENCES engagements(id) ON DELETE CASCADE,
    host_id         INTEGER REFERENCES hosts(id),
    service         VARCHAR(100),
    username        VARCHAR(255),
    password_hash   TEXT,  -- Store hashed, not plaintext
    source          TEXT,
    cracked         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tool execution telemetry (for Grafana)
CREATE TABLE IF NOT EXISTS telemetry (
    id              SERIAL PRIMARY KEY,
    tool            VARCHAR(100) NOT NULL,
    duration_ms     INTEGER,
    success         BOOLEAN,
    error           TEXT,
    cached          BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_findings_severity     ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_engagement   ON findings(engagement_id);
CREATE INDEX IF NOT EXISTS idx_hosts_engagement      ON hosts(engagement_id);
CREATE INDEX IF NOT EXISTS idx_scans_tool            ON scans(tool);
CREATE INDEX IF NOT EXISTS idx_telemetry_tool        ON telemetry(tool);
CREATE INDEX IF NOT EXISTS idx_telemetry_created     ON telemetry(created_at);

-- ── Views ─────────────────────────────────────────────────────
CREATE OR REPLACE VIEW findings_summary AS
    SELECT
        e.name AS engagement,
        f.severity,
        COUNT(*) AS count,
        AVG(f.cvss_score) AS avg_cvss
    FROM findings f
    JOIN engagements e ON f.engagement_id = e.id
    GROUP BY e.name, f.severity
    ORDER BY e.name, CASE f.severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        ELSE 5
    END;

CREATE OR REPLACE VIEW tool_performance AS
    SELECT
        tool,
        COUNT(*) AS total_runs,
        AVG(duration_ms) AS avg_duration_ms,
        SUM(CASE WHEN success THEN 1 ELSE 0 END) AS successes,
        SUM(CASE WHEN cached THEN 1 ELSE 0 END) AS cache_hits,
        ROUND(100.0 * SUM(CASE WHEN cached THEN 1 ELSE 0 END) / COUNT(*), 1) AS cache_hit_pct
    FROM telemetry
    WHERE created_at > NOW() - INTERVAL '7 days'
    GROUP BY tool
    ORDER BY total_runs DESC;

-- Seed data: example engagement (remove for production)
-- INSERT INTO engagements (name, target, type) VALUES ('example', 'localhost', 'ctf');

COMMENT ON TABLE findings IS 'Vulnerability findings from penetration tests';
COMMENT ON TABLE scans IS 'Raw tool output from HexStrike and Kali MCP';
COMMENT ON TABLE telemetry IS 'Tool performance data for Grafana dashboards';
