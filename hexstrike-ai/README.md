# HexStrike AI 🐉

> AI-native red team platform — Live Kali integration, real exploit chains, SSH-over-WebSocket, 14 tool connectors.

Part of the AutoBoros.ai / Aurora AI Agency ecosystem.

## Quick links
- Full platform code: `hexstrike-ai/` subdirectory
- Backend: Express + WebSocket + SSH proxy → runs on Kali
- Frontend: React + xterm.js → deploys to Vercel
- Tools wired: Nmap, Metasploit, SQLMap, Hashcat, Shodan, VirusTotal, GreyNoise, GitHub

## Architecture
```
Browser → Vercel → Frontend (React/Vite/xterm.js)
                  ↓ WSS
            Nginx Proxy (Kali)
                  ↓
         HexStrike API :3001 (Express + ssh2 + SSE)
                  ↓                    ↓
         Kali Linux tools         FastMCP :8889
         (14 connectors)         (hexstrike_mcp.py)
```

## Deploy backend on Kali
```bash
sudo bash hexstrike-ai/scripts/setup-kali.sh
```

## Deploy frontend
```bash
cd hexstrike-ai/frontend
npm install && npm run build
vercel deploy --prod
```

See `hexstrike-ai/docs/ARCHITECTURE.md` for full docs.

---
AutoBoros.ai · az0307 · 2026