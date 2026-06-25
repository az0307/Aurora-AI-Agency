# ─────────────────────────────────────────────────────────────
# Makefile — April 2026 Red Team Stack
# Single entry point for all operations
# Usage: make <target>
# ─────────────────────────────────────────────────────────────

.PHONY: help install install-all update start stop restart logs \
        health status clean new-mission report backup rotate-tokens \
        kali-shell hexstrike-status pentestgpt-config vulngpt-start \
        stride-ui grafana bench ctf osint

# ── Colors ───────────────────────────────────────────────────
RED    := \033[0;31m
GRN    := \033[0;32m
YLW    := \033[1;33m
BLU    := \033[0;34m
NC     := \033[0m

## ── DEFAULT ─────────────────────────────────────────────────
.DEFAULT_GOAL := help

help: ## Show this help menu
	@echo ""
	@echo "$(RED)═══════════════════════════════════════════════════$(NC)"
	@echo "$(RED)  APRIL 2026 RED TEAM STACK$(NC)"
	@echo "$(RED)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YLW)SETUP$(NC)"
	@grep -E '^(install|update)[a-z-]*:.*##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLU)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YLW)STACK$(NC)"
	@grep -E '^(start|stop|restart|logs|health|status)[a-z-]*:.*##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLU)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YLW)TOOLS$(NC)"
	@grep -E '^(kali|hexstrike|pentestgpt|vulngpt|stride|grafana|bench)[a-z-]*:.*##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLU)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YLW)MISSIONS$(NC)"
	@grep -E '^(new-mission|report|ctf|osint|backup)[a-z-]*:.*##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLU)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YLW)MAINTENANCE$(NC)"
	@grep -E '^(clean|rotate|update)[a-z-]*:.*##' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLU)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""

## ── SETUP ───────────────────────────────────────────────────
install: ## Install base stack (HexStrike + Kali MCP + PentestAgent)
	@./scripts/install.sh --full

install-all: ## Install everything including PentestGPT, VulnGPT, STRIDE-GPT, AutoGPT
	@./scripts/install.sh --full
	@./scripts/install-extended.sh
	@echo "$(GRN)[+] Full ecosystem installed$(NC)"

install-kali: ## Kali native install (apt install hexstrike-ai)
	@./scripts/install.sh --kali

update: ## Pull latest for all cloned repos
	@echo "$(BLU)[*] Updating all repos...$(NC)"
	@for repo in hexstrike-ai pentestagent pentestthinking pentestgpt vulngpt stride-gpt autogpt; do \
		if [ -d "$$repo" ]; then \
			echo "  Updating $$repo..."; \
			git -C "$$repo" pull origin main 2>/dev/null || git -C "$$repo" pull 2>/dev/null || echo "  $(YLW)Could not update $$repo$(NC)"; \
		fi; \
	done
	@docker compose pull 2>/dev/null || true
	@echo "$(GRN)[+] All repos updated$(NC)"

## ── STACK ───────────────────────────────────────────────────
start: ## Start all Docker services
	@echo "$(BLU)[*] Starting stack...$(NC)"
	@docker compose up -d
	@sleep 5
	@$(MAKE) health

stop: ## Stop all Docker services
	@docker compose down
	@echo "$(GRN)[+] Stack stopped$(NC)"

restart: ## Restart all Docker services
	@docker compose restart
	@$(MAKE) health

logs: ## Follow live logs from all services
	@docker compose logs -f

logs-hexstrike: ## Follow HexStrike logs only
	@docker compose logs -f hexstrike

logs-kali: ## Follow Kali MCP logs only
	@docker compose logs -f kali-mcp

health: ## Run full health check on all services
	@./scripts/healthcheck.sh

status: ## Quick status of all Docker containers
	@docker compose ps

## ── TOOLS ───────────────────────────────────────────────────
kali-shell: ## Open interactive shell on Kali MCP container
	@docker exec -it kali-mcp bash

hexstrike-status: ## Check HexStrike API status and tool count
	@echo "$(BLU)[*] HexStrike Status$(NC)"
	@curl -sf http://localhost:8888/health || echo "$(RED)Not responding$(NC)"
	@echo ""
	@curl -sf http://localhost:8888/api/version 2>/dev/null || true
	@echo ""
	@curl -sf http://localhost:8888/api/tools/list 2>/dev/null | python3 -c \
		"import sys,json; d=json.load(sys.stdin); print(f'Tools loaded: {len(d.get(\"tools\", []))}')" 2>/dev/null || true

pentestgpt-config: ## Configure PentestGPT for first use
	@cd pentestgpt && make config

vulngpt-start: ## Start VulnGPT v2 web server
	@docker compose up -d vulngpt
	@echo "$(GRN)[+] VulnGPT at http://localhost:8090$(NC)"

stride-ui: ## Open STRIDE-GPT threat modeling UI
	@docker compose up -d stride-gpt
	@echo "$(GRN)[+] STRIDE-GPT at http://localhost:8501$(NC)"
	@command -v xdg-open && xdg-open http://localhost:8501 2>/dev/null || \
		command -v open && open http://localhost:8501 2>/dev/null || \
		echo "Open: http://localhost:8501"

grafana: ## Open Grafana dashboard
	@echo "$(GRN)[+] Grafana at http://localhost:3000 (admin / see .env GRAFANA_PASSWORD)$(NC)"
	@command -v xdg-open && xdg-open http://localhost:3000 2>/dev/null || \
		command -v open && open http://localhost:3000 2>/dev/null || true

bench: ## Run PentestGPT XBOW benchmarks (first 10)
	@echo "$(YLW)[!] Running 10 XBOW benchmarks — estimated cost $8-12$(NC)"
	@read -p "Confirm [y/N]: " ans && [ "$$ans" = "y" ] || exit 1
	@cd pentestgpt/benchmark/standalone-xbow-benchmark-runner && \
		python3 run_benchmarks.py --range 1-10 --pattern-flag

## ── MISSIONS ────────────────────────────────────────────────
new-mission: ## Create new engagement (usage: make new-mission NAME=client TARGET=target.com TYPE=web)
	@./scripts/new-mission.sh "$(NAME)" "$(TARGET)" "$(TYPE)"

report: ## Generate pentest report from loot (usage: make report MISSION=client-name)
	@echo "$(BLU)[*] Generating report for: $(MISSION)$(NC)"
	@cp loot/REPORT_TEMPLATE.md loot/$(MISSION)/report.md
	@echo "$(GRN)[+] Template copied to loot/$(MISSION)/report.md$(NC)"
	@echo "$(YLW)[!] Run Claude Code to populate with findings$(NC)"

ctf: ## Start CTF session (usage: make ctf IP=10.10.11.234 NAME=machine-name)
	@./scripts/new-mission.sh "$(NAME)" "$(IP)" ctf
	@echo ""
	@echo "$(YLW)Prompt for Claude Code:$(NC)"
	@echo "Working on HTB/THM machine $(NAME) at $(IP). Authorized lab."
	@echo "Load playbooks/ctf-htb.md. Start PentestThinkingMCP planning."

osint: ## Start AutoGPT OSINT session (usage: make osint TARGET=company.com MISSION=name)
	@./scripts/new-mission.sh "$(MISSION)" "$(TARGET)" osint
	@echo ""
	@echo "$(YLW)Prompt for Claude Code:$(NC)"
	@echo "Run AutoGPT OSINT on $(TARGET). Load playbooks/autogpt-osint.md."
	@echo "Save to loot/$(MISSION)/osint/"

backup: ## Backup and encrypt loot directory
	@./scripts/backup.sh

## ── MAINTENANCE ─────────────────────────────────────────────
rotate-tokens: ## Rotate all API tokens (HexStrike + DB passwords)
	@./scripts/rotate-tokens.sh

clean: ## Clean Docker volumes and temp files (WARNING: destroys scan cache)
	@echo "$(RED)[!] This will destroy all Docker volumes including scan cache.$(NC)"
	@read -p "Confirm by typing 'destroy': " ans && [ "$$ans" = "destroy" ] || exit 1
	@docker compose down -v
	@docker system prune -f
	@echo "$(GRN)[+] Cleaned$(NC)"

clean-cache: ## Clear Redis scan cache only (keep DB)
	@docker exec rt-redis redis-cli FLUSHALL
	@echo "$(GRN)[+] Redis cache cleared$(NC)"

clean-loot: ## Securely delete loot directory (usage: make clean-loot MISSION=name)
	@echo "$(RED)[!] PERMANENTLY deleting loot/$(MISSION)/ with shred$(NC)"
	@read -p "Type mission name to confirm: " ans && [ "$$ans" = "$(MISSION)" ] || exit 1
	@find loot/$(MISSION)/ -type f -exec shred -u {} \;
	@rm -rf loot/$(MISSION)/
	@echo "$(GRN)[+] Loot securely deleted$(NC)"
