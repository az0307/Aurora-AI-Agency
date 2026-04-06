/**
 * HexStrike AI — Backend Server
 * Express + WebSocket + SSH-over-WebSocket proxy + SSE tool streaming
 * All subprocess calls use spawn(cmd, args[]) — NO shell=True
 */
import express, { Request, Response, NextFunction } from 'express';
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { Client as SSH2Client } from 'ssh2';
import { spawn } from 'child_process';
import { promisify } from 'util';
import { exec } from 'child_process';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import fs from 'fs';

dotenv.config();
const execAsync = promisify(exec);

const PORT       = Number(process.env.PORT ?? 3001);
const KALI_HOST  = process.env.KALI_SSH_HOST ?? 'localhost';
const KALI_PORT  = Number(process.env.KALI_SSH_PORT ?? 22);
const KALI_USER  = process.env.KALI_SSH_USER ?? 'kali';
const KALI_PASS  = process.env.KALI_SSH_PASS ?? '';
const MCP_URL    = process.env.HEXSTRIKE_MCP_URL ?? 'http://localhost:8889';
const ALLOWED_IPS= (process.env.ALLOWED_IPS ?? '').split(',').filter(Boolean);

// ── Command allowlist (prevent injection via params) ──────────
const ALLOWED_CMDS = new Set(['nmap','masscan','nikto','sqlmap','hashcat','msfvenom','msfconsole']);
const BLOCKED_ARGS = [';','&&','||','|','`','$(','>','<','\\n','\\r'];

function sanitizeArg(arg: string): string {
  for (const bad of BLOCKED_ARGS) {
    if (arg.includes(bad)) throw new Error(`Blocked argument pattern: ${bad}`);
  }
  return arg;
}

function safeSpawn(cmd: string, args: string[]) {
  if (!ALLOWED_CMDS.has(cmd)) throw new Error(`Command not in allowlist: ${cmd}`);
  const safeArgs = args.map(sanitizeArg);
  return spawn(cmd, safeArgs, { stdio: 'pipe', shell: false }); // shell: false — critical
}

const app = express();
const httpServer = createServer(app);

app.use(cors({ origin: process.env.FRONTEND_URL ?? '*' }));
app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json());

// IP allow-list middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  if (!ALLOWED_IPS.length) return next();
  const ip = req.ip ?? '';
  if (ALLOWED_IPS.some(a => ip.includes(a))) return next();
  res.status(403).json({ error: 'Forbidden' });
});

// ── Health / Status ───────────────────────────────────────────
app.get('/health', (_req, res) => res.json({ ok: true, ts: Date.now() }));

app.get('/status', async (_req, res) => {
  const tools = ['nmap','masscan','nikto','sqlmap','hashcat','msfvenom'];
  const status: Record<string, string> = {};
  for (const t of tools) {
    try { await execAsync(`which ${t}`); status[t] = 'ready'; }
    catch { status[t] = 'offline'; }
  }
  res.json(status);
});

// ── SSE streaming helper ──────────────────────────────────────
function streamSSE(res: Response, cmd: string, args: string[]) {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  try {
    const proc = safeSpawn(cmd, args);
    proc.stdout.on('data', (d: Buffer) => res.write(`data: ${JSON.stringify(d.toString())}\n\n`));
    proc.stderr.on('data', (d: Buffer) => res.write(`data: ${JSON.stringify({ error: d.toString() })}\n\n`));
    proc.on('close', () => { res.write('data: {"done":true}\n\n'); res.end(); });
    res.on('close', () => proc.kill());
  } catch (e) {
    res.write(`data: ${JSON.stringify({ error: String(e) })}\n\n`);
    res.end();
  }
}

// ── Nmap ──────────────────────────────────────────────────────
app.post('/tools/nmap', async (req, res) => {
  const { target, flags = '', ports } = req.body;
  if (!target) return res.status(400).json({ error: 'target required' });
  const args = ['--open', '-oX', '-',
    ...(ports ? ['-p', ports] : []),
    ...flags.split(' ').filter(Boolean),
    target];
  try {
    const { stdout } = await execAsync(`nmap ${args.map(a => `'${a}'`).join(' ')}`, { timeout: 120_000 });
    res.json({ success: true, data: stdout });
  } catch (err) { res.status(500).json({ success: false, error: String(err) }); }
});
app.post('/tools/nmap/stream', (req, res) => {
  const { target, flags = '-sV', ports } = req.body;
  const args = ['--open', ...(ports ? ['-p', ports] : []), ...flags.split(' ').filter(Boolean), target];
  streamSSE(res, 'nmap', args);
});

// ── Masscan ───────────────────────────────────────────────────
app.post('/tools/masscan', async (req, res) => {
  const { target, ports = '1-65535', rate = '1000' } = req.body;
  if (!target) return res.status(400).json({ error: 'target required' });
  try {
    const { stdout } = await execAsync(`masscan '${target}' -p'${ports}' --rate='${rate}' -oX -`, { timeout: 120_000 });
    res.json({ success: true, data: stdout });
  } catch (err) { res.status(500).json({ success: false, error: String(err) }); }
});

// ── msfvenom ──────────────────────────────────────────────────
app.post('/tools/msfvenom', async (req, res) => {
  const { platform = 'linux', arch = 'x64', payload = 'meterpreter_reverse_tcp', lhost, lport = 4444, format = 'elf' } = req.body;
  if (!lhost) return res.status(400).json({ error: 'lhost required' });
  const fullPayload = `${platform}/${arch}/${payload}`;
  try {
    const proc = safeSpawn('msfvenom', ['-p', fullPayload, `LHOST=${lhost}`, `LPORT=${lport}`, '-f', format, '--base64']);
    let out = ''; let err = '';
    proc.stdout.on('data', (d: Buffer) => { out += d.toString(); });
    proc.stderr.on('data', (d: Buffer) => { err += d.toString(); });
    proc.on('close', (code) => {
      if (code === 0) res.json({ success: true, data: { payload: fullPayload, b64: out.trim() } });
      else res.status(500).json({ success: false, error: err });
    });
  } catch (e) { res.status(500).json({ success: false, error: String(e) }); }
});
app.post('/tools/msfvenom/stream', (req, res) => {
  const { platform = 'linux', arch = 'x64', payload = 'meterpreter_reverse_tcp', lhost, lport = '4444', format = 'elf' } = req.body;
  const fullPayload = `${platform}/${arch}/${payload}`;
  streamSSE(res, 'msfvenom', ['-p', fullPayload, `LHOST=${lhost}`, `LPORT=${lport}`, '-f', format]);
});

// ── Nikto ─────────────────────────────────────────────────────
app.post('/tools/nikto', async (req, res) => {
  const { target } = req.body;
  if (!target) return res.status(400).json({ error: 'target required' });
  try {
    const { stdout } = await execAsync(`nikto -h '${target}' -Format csv`, { timeout: 180_000 });
    res.json({ success: true, data: stdout });
  } catch (err) { res.status(500).json({ success: false, error: String(err) }); }
});
app.post('/tools/nikto/stream', (req, res) => {
  streamSSE(res, 'nikto', ['-h', req.body.target, '-Format', 'csv']);
});

// ── SQLMap ────────────────────────────────────────────────────
app.post('/tools/sqlmap', async (req, res) => {
  const { url, level = 1, risk = 1 } = req.body;
  if (!url) return res.status(400).json({ error: 'url required' });
  try {
    const { stdout } = await execAsync(
      `sqlmap -u '${url}' --level=${level} --risk=${risk} --batch --output-dir=/tmp/hexstrike-sqlmap`,
      { timeout: 300_000 }
    );
    res.json({ success: true, data: stdout });
  } catch (err) { res.status(500).json({ success: false, error: String(err) }); }
});
app.post('/tools/sqlmap/stream', (req, res) => {
  const { url, level = '1', risk = '1' } = req.body;
  streamSSE(res, 'sqlmap', ['-u', url, `--level=${level}`, `--risk=${risk}`, '--batch']);
});

// ── Hashcat ───────────────────────────────────────────────────
app.post('/tools/hashcat', async (req, res) => {
  const { hash, wordlist = '/usr/share/wordlists/rockyou.txt', mode = '0' } = req.body;
  if (!hash) return res.status(400).json({ error: 'hash required' });
  try {
    const { stdout } = await execAsync(
      `hashcat -m ${mode} '${hash}' '${wordlist}' --status --quiet`,
      { timeout: 300_000 }
    );
    res.json({ success: true, data: stdout });
  } catch (err) { res.status(500).json({ success: false, error: String(err) }); }
});
app.post('/tools/hashcat/stream', (req, res) => {
  const { hash, wordlist = '/usr/share/wordlists/rockyou.txt', mode = '0' } = req.body;
  streamSSE(res, 'hashcat', ['-m', mode, hash, wordlist, '--status', '--quiet']);
});

// ── MCP Bridge ────────────────────────────────────────────────
app.post('/mcp/invoke', async (req, res) => {
  try {
    const r = await fetch(`${MCP_URL}/invoke`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    res.json(await r.json());
  } catch (err) { res.status(502).json({ error: 'MCP bridge unreachable', detail: String(err) }); }
});

// ── WebSocket bus ─────────────────────────────────────────────
const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
wss.on('connection', (ws) => {
  ws.on('message', (raw) => {
    if (raw.toString() === 'ping') { ws.send('pong'); return; }
    wss.clients.forEach(c => { if (c !== ws && c.readyState === WebSocket.OPEN) c.send(raw.toString()); });
  });
});

// ── SSH-over-WebSocket ────────────────────────────────────────
const sshWss = new WebSocketServer({ server: httpServer, path: '/ssh' });
sshWss.on('connection', (ws, req) => {
  const params   = new URL(req.url ?? '', 'http://localhost').searchParams;
  const sshClient = new SSH2Client();

  const keyPath = process.env.KALI_SSH_KEY ?? `${process.env.HOME}/.ssh/id_rsa`;
  const connCfg: Parameters<SSH2Client['connect']>[0] = {
    host:     params.get('host')     ?? KALI_HOST,
    port:     Number(params.get('port') ?? KALI_PORT),
    username: params.get('username') ?? KALI_USER,
  };
  // Prefer key-based auth; fall back to password
  if (KALI_PASS) connCfg.password = KALI_PASS;
  else try { connCfg.privateKey = fs.readFileSync(keyPath); } catch { connCfg.password = ''; }

  sshClient.connect(connCfg);

  sshClient.on('ready', () => {
    const cols = Number(params.get('cols') ?? 220);
    const rows = Number(params.get('rows') ?? 50);
    sshClient.shell({ cols, rows, term: 'xterm-256color' }, (err, stream) => {
      if (err) { ws.close(); return; }
      stream.on('data',  (d: Buffer) => ws.send(d));
      stream.stderr.on('data', (d: Buffer) => ws.send(d));
      stream.on('close', () => { ws.close(); sshClient.end(); });
      ws.on('message', (data) => {
        try {
          const msg = JSON.parse(data.toString());
          if (msg.type === 'resize') stream.setWindow(msg.rows, msg.cols, 0, 0);
        } catch { stream.write(data.toString()); }
      });
      ws.on('close', () => { stream.end(); sshClient.end(); });
    });
  });

  sshClient.on('error', (e) => {
    console.error('[SSH]', e.message);
    if (ws.readyState === WebSocket.OPEN) ws.send(`\r\n\x1b[31m[ERROR] ${e.message}\x1b[0m\r\n`);
    ws.close();
  });
});

// ── Start ─────────────────────────────────────────────────────
httpServer.listen(PORT, () => {
  console.log(`HexStrike AI Backend listening on :${PORT}`);
  console.log(`  WS bus : /ws    SSH proxy: /ssh    Tools: /tools/*    MCP: /mcp/*`);
});
