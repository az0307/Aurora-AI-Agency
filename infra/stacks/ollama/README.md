# Ollama — self-hosted open-weight models (the future path)

> **This is documented, not our default.** Aurora runs on **hosted APIs** on a cheap CPU box
> (see [`../../README.md`](../../README.md) and [`../../AGENTS.md`](../../AGENTS.md)). Ollama is
> the path for when you *want* to run open-weight models yourself — Nous **Hermes**, **Qwen**,
> **Kimi** weights, Llama, Mistral — for offline/air-gapped work, data-residency, or to stop
> paying per token. Stand it up deliberately, not by default.

## What runs
- **`ollama`** — the inference server. Exposes an **OpenAI-compatible** API on
  `127.0.0.1:11434` (loopback only; reach it via Cloudflare Tunnel + Access, never publicly).
- **`open-webui`** *(profile `ui`, off by default)* — a browser chat UI over the same API.

## Start it
```sh
cd infra/stacks/ollama
cp .env.example .env && $EDITOR .env
docker compose up -d
docker compose exec ollama ollama pull hermes3:8b     # or qwen2.5:7b, llama3.1:8b, etc.
docker compose exec ollama ollama list                # confirm it's there
# optional chat UI:
docker compose --profile ui up -d                     # http://127.0.0.1:3080 behind Access
```

## CPU-only reality (what this cheap box can and can't do)
CPU inference **works** but is slow, and quality tracks model size:

| Model class | Example | Runs on CPU? | Honest expectation |
|---|---|---|---|
| Tiny / heavily quantized | `qwen2.5:0.5b`, `llama3.2:1b`, `*:3b-q4` | **Yes** | usable for classify/extract/route; single-digit → low-tens tokens/sec |
| Small (7–8B, 4-bit) | `hermes3:8b`, `qwen2.5:7b` (Q4) | Marginal | works but slow (a few tok/s on a small VPS); fine for async/batch, painful for chat |
| Mid (13–34B) | — | Not really | needs lots of RAM and is too slow to be pleasant on CPU |
| Large (70B+) | — | **No** | GPU (often multi-GPU) territory |

Rules of thumb: budget **~RAM ≥ model file size + a couple of GB**; prefer **`q4`/`q5`
quantized** tags; keep `OLLAMA_MAX_LOADED_MODELS=1` and a short `OLLAMA_KEEP_ALIVE` so a small
box reclaims RAM between jobs (same rotate-to-save-RAM discipline as the on-demand pool).

## When you actually need a GPU (and the cost, honestly)
For interactive speed, mid/large models, or any real throughput, you need an **NVIDIA GPU** +
the **NVIDIA Container Toolkit** on the host, then uncomment the `deploy:` GPU block in
`docker-compose.yml`.

Be honest about the bill: a standard Hetzner **CX/CPX VPS has no GPU** — this is a **materially
more expensive tier**, not a config flag. Realistic options:
- A GPU/dedicated host (Hetzner's dedicated GPU line where available, or a rented GPU box from
  a GPU-focused provider). Expect a large multiple of the €4–9/mo CPU-box cost.
- Do **not** overstate Hetzner here: its cheap cloud line is CPU-only; GPU means a different,
  pricier product (and possibly a different provider/region entirely). Price it before committing.

For most Aurora work the math still favours **hosted APIs** — you pay per token instead of
renting a GPU 24/7. Reach for local GPU only when offline/residency/volume economics flip.

## Point the agent CLIs / apps at it
Ollama speaks the OpenAI API, so most tools just need a base URL + a throwaway key:

```sh
# generic OpenAI-compatible clients (Aider, scripts, SDKs):
export OPENAI_BASE_URL=http://127.0.0.1:11434/v1      # or http://<ollama-host>:11434/v1
export OPENAI_API_KEY=ollama                          # any non-empty string; Ollama ignores it
# example: chat completion against a pulled model
curl http://127.0.0.1:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"hermes3:8b","messages":[{"role":"user","content":"ping"}]}'
```

- **Same box:** use `http://127.0.0.1:11434`.
- **Another box / an agent container:** use `http://<ollama-host>:11434` over the private
  network or a Cloudflare Access-fronted hostname — never the raw public internet.
- **n8n / Activepieces:** point their OpenAI/HTTP nodes at the same `…:11434/v1` base URL.

Native Ollama API (`/api/generate`, `/api/chat`) is also available on the same port for tools
that speak it directly.

## Notes
- First `pull` downloads several GB into the `ollama_models` volume — size the disk accordingly.
- Pin `ollama/ollama` and `open-webui` to a reviewed version + `@sha256` for production
  (see [`../../STACK.md`](../../STACK.md)).
