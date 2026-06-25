/**
 * Pentest Proposal Generator
 * Takes client intake JSON and generates a professional .docx proposal.
 * 
 * Usage: node generate_proposal.js intake.json [output.docx]
 * 
 * AutoBoros.ai / Aurora AI Agency | 2026
 */

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageBreak, PageNumber, LevelFormat,
} = require("docx");

const W = 12240, M = 1440, CW = W - M * 2;
const bdr = { style: BorderStyle.SINGLE, size: 1, color: "CBD5E1" };
const borders = { top: bdr, bottom: bdr, left: bdr, right: bdr };

const PRICING = {
  external: { base: 8000, perDay: 1200, days: 7 },
  webapp: { base: 6000, perDay: 1000, days: 5 },
  internal: { base: 12000, perDay: 1500, days: 7 },
  redteam: { base: 25000, perDay: 2000, days: 15 },
  wireless: { base: 4000, perDay: 800, days: 3 },
  cloud: { base: 8000, perDay: 1200, days: 5 },
};

const TYPE_LABELS = {
  external: "External Network Penetration Test",
  webapp: "Web Application Security Assessment",
  internal: "Internal Network Penetration Test",
  redteam: "Red Team Engagement",
  wireless: "Wireless Security Assessment",
  cloud: "Cloud Security Configuration Review",
};

const METHODOLOGY_LABELS = {
  ptes: "Penetration Testing Execution Standard (PTES)",
  owasp: "OWASP Testing Guide v4.2",
  nist: "NIST SP 800-115",
  mitre: "MITRE ATT&CK Framework",
};

function generateProposal(intake) {
  const eng = intake.engagement || intake;
  const scope = intake.scope || {};
  const company = eng.client || "Client";
  const type = eng.type || "external";
  const pricing = PRICING[type] || PRICING.external;
  const days = parseInt(eng.duration) || pricing.days;
  const total = pricing.base + (Math.max(0, days - pricing.days) * pricing.perDay);
  const today = new Date().toISOString().slice(0, 10);

  const doc = new Document({
    styles: {
      default: { document: { run: { font: "Calibri", size: 22, color: "1E293B" } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 36, bold: true, font: "Calibri", color: "1E293B" },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 28, bold: true, font: "Calibri", color: "334155" },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      ],
    },
    numbering: {
      config: [{
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
      }],
    },
    sections: [
      // Cover
      {
        properties: { page: { size: { width: W, height: 15840 }, margin: { top: 2880, right: M, bottom: M, left: M } } },
        children: [
          sp(3600),
          p("SECURITY ASSESSMENT PROPOSAL", { size: 48, bold: true, color: "DC2626" }),
          sp(200),
          p(company, { size: 36, bold: true }),
          sp(100),
          p(TYPE_LABELS[type] || type, { size: 24, color: "64748B" }),
          sp(600),
          rule(),
          sp(200),
          meta("Prepared by", "Aurora AI Agency / AutoBoros.ai"),
          meta("Date", today),
          meta("Proposal ID", `PROP-${today.replace(/-/g, "")}`),
          meta("Validity", "30 days from date of issue"),
          sp(2400),
          p("CONFIDENTIAL — For intended recipient only", { size: 16, color: "DC2626", italics: true }),
        ],
      },
      // Body
      {
        properties: { page: { size: { width: W, height: 15840 }, margin: { top: M, right: M, bottom: M, left: M } } },
        headers: { default: new Header({ children: [
          new Paragraph({ alignment: AlignmentType.RIGHT, children: [
            new TextRun({ text: `${company} — Security Proposal`, size: 16, color: "94A3B8", font: "Calibri" })
          ] })
        ] }) },
        footers: { default: new Footer({ children: [
          new Paragraph({ alignment: AlignmentType.CENTER, children: [
            new TextRun({ text: "Page ", size: 16, color: "94A3B8" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "94A3B8" }),
          ] })
        ] }) },
        children: [
          h1("1. Executive Summary"),
          body(`Aurora AI Agency is pleased to submit this proposal for a ${(TYPE_LABELS[type] || type).toLowerCase()} of ${company}'s infrastructure. This assessment will identify security vulnerabilities, evaluate the effectiveness of existing controls, and provide actionable remediation guidance.`),
          body(`The engagement will be conducted over ${days} business days using the ${METHODOLOGY_LABELS[eng.methodology] || "PTES"} methodology, ensuring thorough coverage and industry-standard reporting.`),
          sp(100),

          h1("2. Scope of Work"),
          h2("2.1 Engagement Type"),
          body(`${TYPE_LABELS[type] || type}`),
          sp(50),

          h2("2.2 In-Scope Assets"),
          ...(scope.in_scope?.targets || []).map(t =>
            bullet(t)
          ),
          sp(100),

          ...(scope.out_of_scope?.targets?.length ? [
            h2("2.3 Excluded Assets"),
            ...(scope.out_of_scope.targets.map(t => bullet(t))),
            sp(100),
          ] : []),

          h2(`2.${scope.out_of_scope?.targets?.length ? "4" : "3"} Rules of Engagement`),
          ...(scope.rules_of_engagement || [
            "No denial-of-service testing",
            "Stop testing if production impact detected",
            "Report critical findings within 24 hours",
          ]).map(r => bullet(r)),
          sp(100),

          new Paragraph({ children: [new PageBreak()] }),

          h1("3. Methodology"),
          body(`The assessment will follow the ${METHODOLOGY_LABELS[eng.methodology] || "PTES"} framework, covering the following phases:`),
          sp(50),
          phasesTable(type),
          sp(200),

          h1("4. Deliverables"),
          bullet("Executive Summary — non-technical overview for leadership"),
          bullet("Technical Report — detailed findings with evidence and remediation steps"),
          bullet("Remediation Roadmap — prioritised timeline (immediate / short / medium / long term)"),
          bullet("Findings Export — CSV, Jira, or Linear-compatible format for ticket creation"),
          bullet("Debrief Presentation — walk-through of key findings with your team"),
          sp(200),

          h1("5. Timeline & Pricing"),
          sp(50),
          pricingTable(days, total, eng.time_window || "Business hours", eng.start_date),
          sp(100),
          body("Payment terms: 50% upon engagement commencement, 50% upon report delivery. Prices are in AUD and exclusive of GST."),
          sp(200),

          h1("6. About Aurora AI Agency"),
          body("Aurora AI Agency specialises in AI-augmented cybersecurity services, combining human expertise with advanced AI-driven tooling for comprehensive security assessments. Our Kali Agent platform enables thorough, auditable, and efficient penetration testing with full compliance trails."),
          sp(100),
          bullet("Certified ethical hackers with commercial pentest experience"),
          bullet("AI-augmented methodology for comprehensive coverage"),
          bullet("Full audit trail and compliance documentation"),
          bullet("Findings exported to your ticketing system (Jira, Linear, Notion)"),
          sp(300),

          h1("7. Acceptance"),
          body("To proceed with this engagement, please sign below and return this document. A signed Statement of Work with detailed scope will follow."),
          sp(400),
          sigLine("Client Representative"),
          sp(200),
          sigLine("Aurora AI Agency"),
        ],
      },
    ],
  });
  return doc;
}

// Helpers
function p(text, opts = {}) { return new Paragraph({ spacing: { after: opts.after || 100 }, alignment: opts.align, children: [new TextRun({ text, font: "Calibri", ...opts })] }); }
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function body(t) { return new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: t, font: "Calibri", size: 22 })] }); }
function bullet(t) { return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: t, font: "Calibri", size: 22 })] }); }
function sp(t) { return new Paragraph({ spacing: { before: t } }); }
function rule() { return new Paragraph({ spacing: { before: 100, after: 100 }, border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "DC2626" } } }); }
function meta(l, v) { return new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: `${l}: `, size: 22, color: "64748B" }), new TextRun({ text: v, size: 22, bold: true })] }); }

function sigLine(label) {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [CW / 2, CW / 2],
    rows: [new TableRow({ children: [
      cell("Signed: ____________________________", CW / 2),
      cell("Date: ____________________________", CW / 2),
    ] }), new TableRow({ children: [
      cell(`Name: ____________________________`, CW / 2),
      cell(`Title: ____________________________`, CW / 2),
    ] }), new TableRow({ children: [
      new TableCell({ borders: { top: bdr, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, columnSpan: 2, width: { size: CW, type: WidthType.DXA }, children: [new Paragraph({ spacing: { before: 40 }, children: [new TextRun({ text: label, size: 18, color: "64748B", italics: true })] })] }),
    ] })],
  });
}

function cell(t, w) {
  return new TableCell({
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
    width: { size: w, type: WidthType.DXA }, margins: { top: 40, bottom: 40 },
    children: [new Paragraph({ children: [new TextRun({ text: t, size: 20, color: "334155" })] })],
  });
}

function phasesTable(type) {
  const phases = [
    ["Reconnaissance", "Passive and active intelligence gathering, subdomain enumeration, port scanning"],
    ["Vulnerability Analysis", "Automated and manual vulnerability scanning, CVE correlation, finding triage"],
    type !== "wireless" ? ["Exploitation", "Controlled exploitation of confirmed vulnerabilities with operator oversight"] : null,
    type !== "wireless" ? ["Post-Exploitation", "Privilege escalation, lateral movement assessment, impact demonstration"] : null,
    type === "wireless" ? ["Wireless Testing", "WiFi enumeration, handshake capture, encryption analysis"] : null,
    ["Reporting", "Executive summary, technical findings, remediation roadmap, debrief"],
  ].filter(Boolean);

  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [2800, CW - 2800],
    rows: [
      hRow(["Phase", "Description"]),
      ...phases.map(([ph, desc]) => new TableRow({ children: [
        tCell(ph, 2800, true), tCell(desc, CW - 2800),
      ] })),
    ],
  });
}

function pricingTable(days, total, window, startDate) {
  const rows = [
    ["Duration", `${days} business days`],
    ["Testing Window", window],
    ["Start Date", startDate || "To be confirmed"],
    ["Investment", `$${total.toLocaleString()} AUD + GST`],
  ];
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [3500, CW - 3500],
    rows: [
      hRow(["Item", "Details"]),
      ...rows.map(([l, v]) => new TableRow({ children: [tCell(l, 3500, true), tCell(v, CW - 3500)] })),
    ],
  });
}

function hRow(cells) {
  return new TableRow({ children: cells.map((t, i) => new TableCell({
    borders, width: { size: i === 0 ? 3500 : CW - 3500, type: WidthType.DXA },
    shading: { fill: "0F172A", type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text: t, bold: true, color: "FFFFFF", size: 20 })] })],
  })) });
}

function tCell(t, w, bold) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    margins: { top: 40, bottom: 40, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text: t, size: 20, bold: !!bold })] })],
  });
}

async function main() {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3] || "/mnt/user-data/outputs/pentest_proposal.docx";

  let intake;
  if (inputPath && fs.existsSync(inputPath)) {
    intake = JSON.parse(fs.readFileSync(inputPath, "utf8"));
  } else {
    intake = {
      engagement: { client: "Acme Corp Pty Ltd", type: "external", methodology: "ptes", duration: "7", start_date: "2026-04-14", time_window: "Business hours" },
      scope: {
        in_scope: { targets: ["*.acme.com.au", "203.0.113.0/24", "https://app.acme.com.au"] },
        out_of_scope: { targets: ["mail.acme.com.au", "production-db.acme.com.au"] },
        rules_of_engagement: ["No denial-of-service testing", "No social engineering without separate approval", "Stop testing if production impact detected", "Report critical findings within 24 hours"],
      },
    };
    console.log("Using demo intake data");
  }

  const doc = generateProposal(intake);
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buf);
  console.log(`Proposal generated: ${outputPath}`);
}

main().catch(console.error);
