/**
 * Kali Agent — Playbook Execution Engine
 * Wires Agent Workspace security steps to HexStrike MCP on localhost:8888
 * 
 * Drop into agent-workspace-v2 or import as module.
 * AutoBoros.ai | 2026-03-27
 */

const HEXSTRIKE_BASE = "http://localhost:8888";
const HEXSTRIKE_MCP = "http://localhost:8889";

// ============================================================
// HEXSTRIKE CONNECTION
// ============================================================

export async function checkHexstrikeHealth() {
  try {
    const res = await fetch(`${HEXSTRIKE_BASE}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    return res.ok ? "online" : "error";
  } catch {
    return "offline";
  }
}

async function callHexstrikeTool(toolName, args, timeout = 300000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(`${HEXSTRIKE_MCP}/mcp/tools/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: toolName, arguments: args }),
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!res.ok) {
      const errText = await res.text();
      return { status: "error", message: `HexStrike returned ${res.status}: ${errText}` };
    }
    return await res.json();
  } catch (err) {
    clearTimeout(timer);
    if (err.name === "AbortError") {
      return { status: "error", message: `Tool ${toolName} timed out after ${timeout / 1000}s` };
    }
    return { status: "error", message: `HexStrike unreachable: ${err.message}` };
  }
}

// ============================================================
// SKILL → TOOL MAPPING
// ============================================================

const SKILL_TOOL_MAP = {
  "scope-guard": {
    init_engagement: (params) => callHexstrikeTool("init_engagement", {
      scope_config: JSON.stringify(params.scope_config),
    }),
    revalidate_scope: (params) => callHexstrikeTool("check_scope", {
      target: params.target,
    }),
  },
  "recon-osint": {
    passive_recon: (params) => callHexstrikeTool("recon_target", {
      target: params.target,
      mode: "passive",
    }),
    active_recon: (params) => callHexstrikeTool("recon_target", {
      target: params.target,
      mode: "active",
    }),
    full_recon: (params) => callHexstrikeTool("recon_target", {
      target: params.target,
      mode: "active",
    }),
    web_recon: (params) => callHexstrikeTool("recon_target", {
      target: params.target,
      mode: "passive",
    }),
  },
  "vuln-analysis": {
    automated_scan: (params) => callHexstrikeTool("vuln_scan", {
      target: params.target,
      templates: params.templates || "cves,exposures,misconfiguration",
    }),
    web_scan: (params) => callHexstrikeTool("vuln_scan", {
      target: params.target,
      templates: "cves,exposures,xss",
    }),
    full_scan: (params) => callHexstrikeTool("vuln_scan", {
      target: params.target,
      templates: "cves,exposures,misconfiguration,default-logins",
    }),
  },
  "web-app-security": {
    owasp_testing: (params) => callHexstrikeTool("web_enum", {
      target: params.target,
      wordlist: params.wordlist || "/usr/share/wordlists/dirb/common.txt",
    }),
    full_owasp: (params) => callHexstrikeTool("web_enum", {
      target: params.target,
    }),
  },
  "exploit-dev": {
    research_exploits: (params) => callHexstrikeTool("exploit_search", {
      query: params.query || params.target,
    }),
    auto_exploit: (params) => callHexstrikeTool("exploit_search", {
      query: params.target,
    }),
    web_exploits: (params) => callHexstrikeTool("exploit_search", {
      query: params.target,
    }),
  },
  "red-team-report": {
    generate_report: (params) => callHexstrikeTool("generate_report", {
      target: params.target,
      format: params.format || "markdown",
    }),
    webapp_report: (params) => callHexstrikeTool("generate_report", {
      target: params.target,
      format: "markdown",
    }),
    ctf_writeup: (params) => callHexstrikeTool("generate_report", {
      target: params.target,
      format: "markdown",
    }),
  },
};

// Skills that don't have HexStrike tool calls — handle via Claude/Sonnet
const AI_ONLY_SKILLS = new Set([
  "threat-intel",
  "audit-logger",
  "tool-output-sanitizer",
  "credential-attack",
  "active-directory",
  "post-exploit",
  "payload-craft",
  "wireless-recon",
  "network-forensics",
]);

// ============================================================
// PLAYBOOK EXECUTOR
// ============================================================

/**
 * Execute a complete pentest playbook.
 * 
 * @param {Object} playbook - Playbook from kali_playbook_template.json
 * @param {Object} engagementConfig - Scope config from KaliTargetPanel
 * @param {Function} onStepStart - Callback(step) when a step begins
 * @param {Function} onStepComplete - Callback(step, result) when a step finishes
 * @param {Function} onApprovalNeeded - Callback(step) → Promise<boolean> for operator gates
 * @returns {Object} Complete execution results
 */
export async function executePlaybook(
  playbook,
  engagementConfig,
  { onStepStart, onStepComplete, onApprovalNeeded, onError } = {}
) {
  const results = {
    engagement_id: engagementConfig.engagement?.id || "unknown",
    started_at: new Date().toISOString(),
    completed_at: null,
    steps: [],
    status: "running",
  };

  const target = engagementConfig.scope?.in_scope?.domains?.[0]
    || engagementConfig.scope?.in_scope?.ip_ranges?.[0]
    || "unknown";

  // Check HexStrike availability
  const hexStatus = await checkHexstrikeHealth();
  if (hexStatus !== "online") {
    results.status = "error";
    results.error = "HexStrike is offline — start it with: python hexstrike_mcp.py";
    return results;
  }

  const phases = playbook.phases || [];

  for (const step of phases) {
    const stepResult = {
      step: step.step,
      skill: step.skill,
      action: step.action,
      description: step.description || "",
      started_at: new Date().toISOString(),
      status: "pending",
      result: null,
    };

    // Notify step start
    onStepStart?.(step);

    // Check conditions
    if (step.condition) {
      // Simple condition evaluation — extend as needed
      const condMet = evaluateCondition(step.condition, results);
      if (!condMet) {
        stepResult.status = "skipped";
        stepResult.result = { reason: `Condition not met: ${step.condition}` };
        results.steps.push(stepResult);
        onStepComplete?.(step, stepResult);
        continue;
      }
    }

    // Operator approval gate
    if (step.requires_approval) {
      const approved = onApprovalNeeded
        ? await onApprovalNeeded(step)
        : false;
      if (!approved) {
        stepResult.status = "skipped";
        stepResult.result = { reason: "Operator did not approve" };
        results.steps.push(stepResult);
        onStepComplete?.(step, stepResult);

        if (step.blocking) {
          results.status = "halted";
          results.halt_reason = `Operator declined step ${step.step}: ${step.action}`;
          break;
        }
        continue;
      }
    }

    // Execute the step
    try {
      const skillMap = SKILL_TOOL_MAP[step.skill];
      const toolFn = skillMap?.[step.action];

      if (toolFn) {
        // HexStrike tool call
        stepResult.result = await toolFn({
          target,
          scope_config: engagementConfig,
          ...step.params,
        });
        stepResult.status = stepResult.result?.status === "blocked"
          ? "blocked"
          : "success";
      } else if (AI_ONLY_SKILLS.has(step.skill)) {
        // AI-only skill — return params for Claude/Sonnet to process
        stepResult.status = "ai_pending";
        stepResult.result = {
          message: `Skill '${step.skill}' action '${step.action}' requires AI processing`,
          skill: step.skill,
          params: { target, ...step.params },
        };
      } else {
        stepResult.status = "no_handler";
        stepResult.result = { message: `No tool mapping for ${step.skill}.${step.action}` };
      }
    } catch (err) {
      stepResult.status = "error";
      stepResult.result = { error: err.message };
      onError?.(step, err);
    }

    stepResult.completed_at = new Date().toISOString();
    results.steps.push(stepResult);
    onStepComplete?.(step, stepResult);

    // Halt on blocking failure
    if (step.blocking && stepResult.status !== "success" && stepResult.status !== "ai_pending") {
      results.status = "halted";
      results.halt_reason = `Blocking step ${step.step} failed: ${stepResult.status}`;
      break;
    }
  }

  if (results.status === "running") {
    results.status = "completed";
  }
  results.completed_at = new Date().toISOString();
  return results;
}

// ============================================================
// HELPERS
// ============================================================

function evaluateCondition(condition, results) {
  // Simple condition parser — extend as needed
  if (condition.includes("exploitation_successful")) {
    return results.steps.some(
      (s) => s.skill === "exploit-dev" && s.status === "success"
    );
  }
  if (condition.includes("hashes_collected")) {
    return results.steps.some(
      (s) => s.skill === "post-exploit" && s.status === "success"
    );
  }
  if (condition.includes("ad_detected")) {
    return results.steps.some(
      (s) => s.result?.output?.includes("Active Directory") ||
             s.result?.output?.includes("Domain Controller")
    );
  }
  // Default: condition met
  return true;
}

/**
 * Get a summary of playbook execution for display.
 */
export function getPlaybookSummary(results) {
  const total = results.steps.length;
  const completed = results.steps.filter((s) => s.status === "success").length;
  const blocked = results.steps.filter((s) => s.status === "blocked").length;
  const skipped = results.steps.filter((s) => s.status === "skipped").length;
  const errors = results.steps.filter((s) => s.status === "error").length;
  const pending = results.steps.filter((s) => s.status === "ai_pending").length;

  return {
    engagement_id: results.engagement_id,
    status: results.status,
    total_steps: total,
    completed,
    blocked,
    skipped,
    errors,
    ai_pending: pending,
    duration_ms: results.completed_at
      ? new Date(results.completed_at) - new Date(results.started_at)
      : null,
  };
}
