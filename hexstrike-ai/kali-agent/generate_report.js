/**
 * Pentest Report Generator — Professional .docx template
 * Generates a complete penetration test report from structured findings data.
 * 
 * Usage: node generate_report.js [findings.json] [output.docx]
 * 
 * AutoBoros.ai | 2026-03-27
 */

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageBreak, TableOfContents, PageNumber, LevelFormat,
  ExternalHyperlink,
} = require("docx");

// --- Colors ---
const COLORS = {
  primary: "1E293B",
  accent: "DC2626",
  critical: "DC2626",
  high: "F97316",
  medium: "EAB308",
  low: "3B82F6",
  info: "6B7280",
  headerBg: "0F172A",
  lightBg: "F1F5F9",
  border: "CBD5E1",
  text: "1E293B",
  textLight: "64748B",
};

const PAGE_WIDTH = 12240;       // US Letter
const MARGIN = 1440;            // 1 inch
const CONTENT_WIDTH = PAGE_WIDTH - MARGIN * 2;  // 9360

const thinBorder = { style: BorderStyle.SINGLE, size: 1, color: COLORS.border };
const borders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
const noBorders = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

function generateReport(data) {
  const {
    engagement = {},
    findings = [],
    attackPath = [],
    stats = {},
  } = data;

  const target = engagement.target || engagement.client || "Target";
  const engId = engagement.id || "ENG-XXXX";
  const tester = engagement.tester || "AutoBoros.ai";
  const dateRange = `${engagement.start_date || "N/A"} — ${engagement.end_date || "N/A"}`;

  // Sort findings by severity
  const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  const sortedFindings = [...findings].sort(
    (a, b) => (severityOrder[a.severity] || 4) - (severityOrder[b.severity] || 4)
  );

  const severityCounts = findings.reduce((acc, f) => {
    acc[f.severity] = (acc[f.severity] || 0) + 1;
    return acc;
  }, {});

  const overallRisk = severityCounts.critical ? "CRITICAL" :
    severityCounts.high ? "HIGH" : severityCounts.medium ? "MEDIUM" : "LOW";

  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: "Calibri", size: 22, color: COLORS.text } },
      },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 36, bold: true, font: "Calibri", color: COLORS.primary },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 28, bold: true, font: "Calibri", color: COLORS.primary },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: "Calibri", color: COLORS.text },
          paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: "\u2022",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          }],
        },
      ],
    },
    sections: [
      // === COVER PAGE ===
      coverPageSection(target, engId, tester, dateRange, overallRisk),

      // === TOC + BODY ===
      bodySection(target, engId, tester, dateRange, overallRisk, sortedFindings, severityCounts, attackPath, stats, engagement),
    ],
  });

  return doc;
}

function coverPageSection(target, engId, tester, dateRange, overallRisk) {
  const riskColor = COLORS[overallRisk.toLowerCase()] || COLORS.text;
  return {
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: 15840 },
        margin: { top: 2880, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    children: [
      spacer(4000),
      new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { after: 100 },
        children: [new TextRun({ text: "CONFIDENTIAL", font: "Calibri", size: 20, color: COLORS.accent, bold: true, allCaps: true })],
      }),
      new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { after: 200 },
        children: [new TextRun({ text: "PENETRATION TEST REPORT", font: "Calibri", size: 52, bold: true, color: COLORS.primary })],
      }),
      new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { after: 400 },
        children: [new TextRun({ text: target, font: "Calibri", size: 36, color: COLORS.accent })],
      }),
      rule(),
      spacer(200),
      infoPara("Engagement ID", engId),
      infoPara("Date Range", dateRange),
      infoPara("Assessor", tester),
      infoPara("Overall Risk", overallRisk, riskColor),
      spacer(200),
      new Paragraph({
        spacing: { before: 1200 },
        children: [new TextRun({ text: "AutoBoros.ai  |  Aurora AI Agency", font: "Calibri", size: 18, color: COLORS.textLight, italics: true })],
      }),
    ],
  };
}

function bodySection(target, engId, tester, dateRange, overallRisk, findings, severityCounts, attackPath, stats, engagement) {
  const children = [];

  // Table of Contents
  children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Table of Contents")] }),
    new TableOfContents("TOC", { hyperlink: true, headingStyleRange: "1-3" }),
    new Paragraph({ children: [new PageBreak()] }),
  );

  // 1. Executive Summary
  children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Executive Summary")] }),
    bodyPara(`This report presents the findings from a penetration test conducted against ${target} during the period ${dateRange}. The assessment was performed by ${tester} under engagement ${engId}.`),
    spacer(100),
    bodyPara(`Overall Risk Rating: ${overallRisk}`, true),
    spacer(100),
  );

  // Severity summary table
  children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Finding Summary")] }),
    severityTable(severityCounts),
    spacer(200),
  );

  // Key findings
  const criticals = findings.filter((f) => f.severity === "critical");
  const highs = findings.filter((f) => f.severity === "high");
  if (criticals.length || highs.length) {
    children.push(
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 Key Findings")] }),
    );
    [...criticals, ...highs].slice(0, 5).forEach((f) => {
      children.push(
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [
            new TextRun({ text: `[${f.severity.toUpperCase()}] `, bold: true, color: COLORS[f.severity] }),
            new TextRun({ text: `${f.title}` }),
            f.cve ? new TextRun({ text: ` (${f.cve})`, color: COLORS.textLight }) : new TextRun(""),
          ],
        }),
      );
    });
    children.push(spacer(200));
  }

  children.push(new Paragraph({ children: [new PageBreak()] }));

  // 2. Methodology
  children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Methodology")] }),
    bodyPara(`The assessment followed the ${engagement.methodology || "PTES (Penetration Testing Execution Standard)"} methodology, covering reconnaissance, vulnerability analysis, exploitation, post-exploitation, and reporting phases.`),
    spacer(100),
    new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Scope")] }),
    bodyPara(`Target: ${target}`),
    bodyPara(`Type: ${engagement.type || "External penetration test"}`),
    spacer(200),
    new Paragraph({ children: [new PageBreak()] }),
  );

  // 3. Detailed Findings
  children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Detailed Findings")] }),
  );

  if (!findings.length) {
    children.push(bodyPara("No vulnerabilities were identified during this assessment."));
  } else {
    findings.forEach((f, i) => {
      children.push(findingSection(f, i + 1));
      if (i < findings.length - 1) children.push(spacer(200));
    });
  }

  children.push(new Paragraph({ children: [new PageBreak()] }));

  // 4. Attack Path
  if (attackPath.length) {
    children.push(
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Attack Path")] }),
      bodyPara("The following attack path was identified during the engagement:"),
      spacer(100),
    );
    attackPath.forEach((step, i) => {
      children.push(
        new Paragraph({
          spacing: { after: 80 },
          children: [
            new TextRun({ text: `${i + 1}. `, bold: true, color: COLORS.accent }),
            new TextRun({ text: step }),
          ],
        }),
      );
    });
    children.push(new Paragraph({ children: [new PageBreak()] }));
  }

  // 5. Remediation Roadmap
  children.push(
    new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(`${attackPath.length ? "5" : "4"}. Remediation Roadmap`)] }),
    bodyPara("The following remediation timeline is recommended based on finding severity:"),
    spacer(100),
    remediationTable(findings),
    spacer(200),
  );

  return {
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: 15840 },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: `${engId} | CONFIDENTIAL`, font: "Calibri", size: 16, color: COLORS.textLight })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", font: "Calibri", size: 16, color: COLORS.textLight }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Calibri", size: 16, color: COLORS.textLight }),
          ],
        })],
      }),
    },
    children,
  };
}

// --- Component builders ---

function findingSection(finding, index) {
  const sevColor = COLORS[finding.severity] || COLORS.text;
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [2200, CONTENT_WIDTH - 2200],
    rows: [
      // Header row
      new TableRow({
        children: [
          new TableCell({
            borders, columnSpan: 2,
            shading: { fill: sevColor, type: ShadingType.CLEAR },
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
            width: { size: CONTENT_WIDTH, type: WidthType.DXA },
            children: [new Paragraph({
              children: [
                new TextRun({ text: `${finding.id || `VULN-${String(index).padStart(3, "0")}`}  `, bold: true, color: "FFFFFF", font: "Calibri", size: 22 }),
                new TextRun({ text: finding.title || "Untitled Finding", bold: true, color: "FFFFFF", font: "Calibri", size: 22 }),
              ],
            })],
          }),
        ],
      }),
      findingRow("Severity", `${(finding.severity || "unknown").toUpperCase()}${finding.cvss ? ` (CVSS ${finding.cvss})` : ""}`, sevColor),
      finding.cve ? findingRow("CVE", finding.cve) : null,
      findingRow("Affected Asset", finding.affected_asset || finding.asset || "N/A"),
      findingRow("Tool", finding.tool || "Manual"),
      finding.description ? findingRow("Description", finding.description) : null,
      finding.evidence ? findingRow("Evidence", finding.evidence) : null,
      finding.remediation ? findingRow("Remediation", finding.remediation) : null,
      finding.cwe ? findingRow("CWE", finding.cwe) : null,
    ].filter(Boolean),
  });
}

function findingRow(label, value, valueColor) {
  return new TableRow({
    children: [
      new TableCell({
        borders,
        width: { size: 2200, type: WidthType.DXA },
        shading: { fill: COLORS.lightBg, type: ShadingType.CLEAR },
        margins: { top: 40, bottom: 40, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, font: "Calibri", size: 20, color: COLORS.textLight })] })],
      }),
      new TableCell({
        borders,
        width: { size: CONTENT_WIDTH - 2200, type: WidthType.DXA },
        margins: { top: 40, bottom: 40, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: String(value), font: "Calibri", size: 20, color: valueColor || COLORS.text })],
        })],
      }),
    ],
  });
}

function severityTable(counts) {
  const severities = ["critical", "high", "medium", "low", "info"];
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: severities.map(() => Math.floor(CONTENT_WIDTH / severities.length)),
    rows: [
      new TableRow({
        children: severities.map((sev) => new TableCell({
          borders,
          width: { size: Math.floor(CONTENT_WIDTH / severities.length), type: WidthType.DXA },
          shading: { fill: COLORS[sev], type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 60, right: 60 },
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: sev.toUpperCase(), bold: true, color: "FFFFFF", font: "Calibri", size: 18 })],
          })],
        })),
      }),
      new TableRow({
        children: severities.map((sev) => new TableCell({
          borders,
          width: { size: Math.floor(CONTENT_WIDTH / severities.length), type: WidthType.DXA },
          margins: { top: 60, bottom: 60, left: 60, right: 60 },
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: String(counts[sev] || 0), bold: true, font: "Calibri", size: 28, color: COLORS[sev] })],
          })],
        })),
      }),
    ],
  });
}

function remediationTable(findings) {
  const timeframes = [
    { label: "Immediate (0-48 hours)", severities: ["critical"], color: COLORS.critical },
    { label: "Short-term (1-2 weeks)", severities: ["high"], color: COLORS.high },
    { label: "Medium-term (1-3 months)", severities: ["medium"], color: COLORS.medium },
    { label: "Long-term (3-6 months)", severities: ["low", "info"], color: COLORS.low },
  ];

  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: [3000, 3000, 3360],
    rows: [
      // Header
      new TableRow({
        children: ["Timeframe", "Severity", "Count"].map((h, i) => new TableCell({
          borders,
          width: { size: [3000, 3000, 3360][i], type: WidthType.DXA },
          shading: { fill: COLORS.headerBg, type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF", font: "Calibri", size: 20 })] })],
        })),
      }),
      // Data rows
      ...timeframes.map((tf) => {
        const count = findings.filter((f) => tf.severities.includes(f.severity)).length;
        return new TableRow({
          children: [
            new TableCell({
              borders, width: { size: 3000, type: WidthType.DXA },
              margins: { top: 40, bottom: 40, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: tf.label, font: "Calibri", size: 20 })] })],
            }),
            new TableCell({
              borders, width: { size: 3000, type: WidthType.DXA },
              margins: { top: 40, bottom: 40, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: tf.severities.join(", ").toUpperCase(), font: "Calibri", size: 20, color: tf.color, bold: true })] })],
            }),
            new TableCell({
              borders, width: { size: 3360, type: WidthType.DXA },
              margins: { top: 40, bottom: 40, left: 120, right: 120 },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: String(count), font: "Calibri", size: 20 })] })],
            }),
          ],
        });
      }),
    ],
  });
}

// --- Helpers ---

function bodyPara(text, bold = false) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, font: "Calibri", size: 22, bold })],
  });
}

function infoPara(label, value, valueColor) {
  return new Paragraph({
    spacing: { after: 80 },
    children: [
      new TextRun({ text: `${label}: `, font: "Calibri", size: 22, color: COLORS.textLight }),
      new TextRun({ text: value, font: "Calibri", size: 22, bold: true, color: valueColor || COLORS.text }),
    ],
  });
}

function spacer(twips) {
  return new Paragraph({ spacing: { before: twips } });
}

function rule() {
  return new Paragraph({
    spacing: { before: 100, after: 100 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: COLORS.accent } },
  });
}

// --- Main ---
async function main() {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3] || "/mnt/user-data/outputs/pentest_report.docx";

  let data;
  if (inputPath && fs.existsSync(inputPath)) {
    data = JSON.parse(fs.readFileSync(inputPath, "utf8"));
  } else {
    // Demo data
    data = {
      engagement: {
        id: "ENG-2026-DEMO",
        client: "Example Corp",
        target: "example.com",
        type: "External Penetration Test",
        tester: "Az / AutoBoros.ai / Aurora AI Agency",
        start_date: "2026-04-01",
        end_date: "2026-04-14",
        methodology: "PTES",
      },
      findings: [
        { id: "VULN-001", severity: "critical", cvss: 9.8, cve: "CVE-2024-12345", title: "Remote Code Execution in WordPress Plugin", affected_asset: "blog.example.com", tool: "nuclei + sqlmap", description: "Unauthenticated RCE via file upload in vulnerable plugin version 2.1", evidence: "Nuclei template match confirmed; sqlmap demonstrated database access", remediation: "Update plugin to version 2.3 or remove entirely", cwe: "CWE-94" },
        { id: "VULN-002", severity: "high", cvss: 7.5, title: "SQL Injection in Search Parameter", affected_asset: "app.example.com/search", tool: "sqlmap", description: "Boolean-based blind SQL injection in the 'q' parameter", remediation: "Use parameterized queries / prepared statements", cwe: "CWE-89" },
        { id: "VULN-003", severity: "medium", cvss: 5.3, title: "Missing Security Headers", affected_asset: "*.example.com", tool: "nuclei", description: "Content-Security-Policy, X-Frame-Options, and Strict-Transport-Security headers are missing", remediation: "Configure web server to return appropriate security headers", cwe: "CWE-693" },
        { id: "VULN-004", severity: "low", cvss: 3.1, title: "Information Disclosure via Server Banner", affected_asset: "example.com", tool: "whatweb", description: "Server version disclosed in HTTP headers: nginx/1.24.0", remediation: "Configure server to suppress version information" },
        { id: "VULN-005", severity: "info", title: "TLS 1.0 Deprecated but Still Accepted", affected_asset: "example.com:443", tool: "testssl.sh", description: "Server accepts TLS 1.0 connections which is deprecated", remediation: "Disable TLS 1.0 and 1.1, require TLS 1.2+" },
      ],
      attackPath: [
        "Internet access to blog.example.com (public WordPress site)",
        "Identified vulnerable plugin via nuclei CVE scan",
        "Exploited file upload RCE to gain www-data shell on web01",
        "Escalated to root via SUID binary misconfiguration",
        "Discovered SSH key reuse — pivoted to db01",
        "Accessed production database containing customer PII",
      ],
      stats: { toolCalls: 47, scopeChecks: 23, findings: 5, hostsCompromised: 2 },
    };
    console.log("Using demo data (pass a JSON file as argument for real data)");
  }

  const doc = generateReport(data);
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Report generated: ${outputPath}`);
}

main().catch(console.error);
