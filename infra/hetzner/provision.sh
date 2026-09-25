# hetzner/provision.sh — the Hetzner Cloud part of ../bootstrap.sh (sourced, not run).
# Needs HCLOUD_TOKEN. Sets IP, PRICE_LINE and READY_CMD for bootstrap.sh.
# Knobs: SERVER_TYPE=cpx31 LOCATION=sin IMAGE=ubuntu-24.04 EUR_AUD=1.75 IPV4_EUR=0.60

SERVER_TYPE="${SERVER_TYPE:-cpx31}"
LOCATION="${LOCATION:-sin}"
IMAGE="${IMAGE:-ubuntu-24.04}"
# Conservative EUR→AUD rate so the budget check errs on the side of refusing.
EUR_AUD="${EUR_AUD:-1.75}"
# Hetzner bills a primary IPv4 separately from the server type (~€0.50–0.60/mo).
IPV4_EUR="${IPV4_EUR:-0.60}"
API="${HCLOUD_API:-https://api.hetzner.cloud/v1}"

provision_hetzner() {
  export HCLOUD_TOKEN="${HCLOUD_TOKEN:-${HETZNER_API_TOKEN:-}}"
  [ -n "$HCLOUD_TOKEN" ] || die "HCLOUD_TOKEN is not set (put it in infra/secrets.env or your environment)"

  # --- 1. Preflight (read-only) ---------------------------------------------------------
  say "Preflight"
  SERVER_TYPE="$SERVER_TYPE" LOCATION="$LOCATION" SSH_KEY="$SSH_KEY" bash "$DIR/hetzner/preflight.sh"

  api() { # api METHOD PATH [JSON]
    local m="$1" p="$2" body="${3:-}"
    if [ -n "$body" ]; then
      curl -sS -X "$m" -H "Authorization: Bearer $HCLOUD_TOKEN" -H 'Content-Type: application/json' \
        --data "$body" "$API$p"
    else
      curl -sS -X "$m" -H "Authorization: Bearer $HCLOUD_TOKEN" "$API$p"
    fi
  }
  api_ok() { # fail loudly on a Hetzner error object
    local out="$1"
    if echo "$out" | jq -e '.error' >/dev/null 2>&1; then
      die "Hetzner API: $(echo "$out" | jq -r '.error.code + ": " + .error.message')"
    fi
  }

  # --- 2. Budget guard --------------------------------------------------------------------
  say "Budget check (cap: AUD \$${BUDGET_AUD}/mo)"
  st="$(api GET "/server_types?name=$SERVER_TYPE")"; api_ok "$st"
  eur="$(echo "$st" | jq -r --arg l "$LOCATION" \
    '.server_types[0].prices[]|select(.location==$l)|.price_monthly.gross' | head -1)"
  [ -n "$eur" ] && [ "$eur" != null ] || die "no price for $SERVER_TYPE in $LOCATION"
  aud="$(awk -v e="$eur" -v ip="$IPV4_EUR" -v r="$EUR_AUD" 'BEGIN{printf "%.2f",(e+ip)*r}')"
  echo "  $SERVER_TYPE in $LOCATION: €${eur} + IPv4 €${IPV4_EUR} ≈ AUD \$${aud}/mo (at ${EUR_AUD} AUD/EUR)"
  awk -v a="$aud" -v b="$BUDGET_AUD" 'BEGIN{exit !(a<=b)}' \
    || die "≈AUD \$${aud}/mo is over the AUD \$${BUDGET_AUD} cap. Pick a smaller SERVER_TYPE or raise BUDGET_AUD."

  # --- 3. Render cloud-init with your public key ----------------------------------------
  USER_DATA="$(<"$DIR/hetzner/cloud-init.yaml")"
  USER_DATA="${USER_DATA//"<YOUR_SSH_PUBLIC_KEY>"/$PUBKEY}"
  grep -q '<YOUR_SSH_PUBLIC_KEY>' <<<"$USER_DATA" && die "failed to substitute SSH key into cloud-init"

  existing="$(api GET "/servers?name=$NAME")"; api_ok "$existing"
  SERVER_ID="$(echo "$existing" | jq -r '.servers[0].id // empty')"

  if [ "$DRY_RUN" = 1 ]; then
    say "Dry run complete. Would $( [ -n "$SERVER_ID" ] && echo "REUSE existing server $NAME (#$SERVER_ID)" || echo "CREATE $NAME ($SERVER_TYPE, $LOCATION, $IMAGE)")."
    echo "  Nothing was created or changed."
    exit 0
  fi

  if [ -z "$SERVER_ID" ] && [ "$ASSUME_YES" != 1 ]; then
    read -r -p "Create $NAME ($SERVER_TYPE in $LOCATION) for ≈AUD \$${aud}/mo? This starts billing. [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] || die "aborted — nothing was created"
  fi

  # --- 4. SSH key, firewall, server (create or reuse) -----------------------------------
  say "SSH key"
  keys="$(api GET "/ssh_keys?per_page=50")"; api_ok "$keys"
  key_body="$(awk '{print $1" "$2}' <<<"$PUBKEY")"
  KEY_ID="$(echo "$keys" | jq -r --arg k "$key_body" \
    '.ssh_keys[]|select((.public_key|split(" ")[0:2]|join(" "))==$k)|.id' | head -1)"
  if [ -z "$KEY_ID" ]; then
    out="$(api POST /ssh_keys "$(jq -n --arg n "$NAME-key" --arg k "$PUBKEY" '{name:$n,public_key:$k}')")"
    api_ok "$out"; KEY_ID="$(echo "$out" | jq -r '.ssh_key.id')"
    echo "  uploaded (#$KEY_ID)"
  else
    echo "  reusing (#$KEY_ID)"
  fi

  say "Cloud firewall (inbound SSH only — Docker-published ports can bypass ufw, this can't be bypassed)"
  fw="$(api GET "/firewalls?name=$NAME-fw")"; api_ok "$fw"
  FW_ID="$(echo "$fw" | jq -r '.firewalls[0].id // empty')"
  if [ -z "$FW_ID" ]; then
    out="$(api POST /firewalls "$(jq -n --arg n "$NAME-fw" '{name:$n, rules:[
      {direction:"in",protocol:"tcp",port:"22",source_ips:["0.0.0.0/0","::/0"],description:"ssh"},
      {direction:"in",protocol:"icmp",source_ips:["0.0.0.0/0","::/0"],description:"ping"}]}')")"
    api_ok "$out"; FW_ID="$(echo "$out" | jq -r '.firewall.id')"
    echo "  created (#$FW_ID)"
  else
    echo "  reusing (#$FW_ID)"
  fi

  if [ -z "$SERVER_ID" ]; then
    say "Creating server $NAME"
    body="$(jq -n --arg n "$NAME" --arg t "$SERVER_TYPE" --arg l "$LOCATION" --arg i "$IMAGE" \
      --arg ud "$USER_DATA" --argjson k "$KEY_ID" --argjson f "$FW_ID" \
      '{name:$n,server_type:$t,location:$l,image:$i,ssh_keys:[$k],user_data:$ud,
        firewalls:[{firewall:$f}],labels:{"managed-by":"aurora-bootstrap"},
        public_net:{enable_ipv4:true,enable_ipv6:true},start_after_create:true}')"
    out="$(api POST /servers "$body")"; api_ok "$out"
    SERVER_ID="$(echo "$out" | jq -r '.server.id')"
  else
    say "Reusing existing server $NAME (#$SERVER_ID)"
  fi

  for _ in $(seq 1 60); do
    s="$(api GET "/servers/$SERVER_ID")"; api_ok "$s"
    [ "$(echo "$s" | jq -r '.server.status')" = running ] && break
    sleep 5
  done
  IP="$(echo "$s" | jq -r '.server.public_net.ipv4.ip')"
  [ -n "$IP" ] && [ "$IP" != null ] || die "server has no IPv4 yet"
  echo "  running at $IP"

  PRICE_LINE="≈AUD \$${aud}/mo ($SERVER_TYPE, $LOCATION)"
  READY_CMD='sudo cloud-init status --wait >/dev/null || true'
}
