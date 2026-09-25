# hostinger/provision.sh — the Hostinger part of ../bootstrap.sh (sourced, not run).
#
# Uses the official Hostinger API (https://developers.hostinger.com, spec v1.54) with
# HOSTINGER_API_TOKEN (make one at https://hpanel.hostinger.com/profile/api). It finds or
# gets you a VPS in one of four ways, in this order:
#
#   reuse    a VPS whose hostname is $NAME (or HOSTINGER_VM_ID) that's already running
#   setup    a VPS you bought in hPanel that isn't set up yet (state "initial"): installs
#            Ubuntu 24.04 with our post-install script and your SSH key. No charge.
#   buy      no VPS yet: buys HOSTINGER_PLAN for HOSTINGER_TERM months, if the price
#            passes the budget check, and only after you type "buy"
#   adopt    HOSTINGER_VM_ID points at a running VPS set up some other way: attaches your
#            key, then runs the post-install script over SSH as root (asks first)
#
# Then it puts the VPS behind a Hostinger firewall (SSH + Tailscale only) and hands back
# IP / PRICE_LINE / READY_CMD to bootstrap.sh, which ships infra/ + secrets.
#
# Knobs (env or secrets.env):
#   HOSTINGER_PLAN="KVM 2"      KVM 1 | KVM 2 | KVM 4 | KVM 8
#   HOSTINGER_TERM=24           months to prepay: 1, 12, 24 or 48 (Hostinger charges it all up front)
#   HOSTINGER_DC_PREFER="ID MY IN"   country codes, first available wins (no AU/SG VPS locations)
#   HOSTINGER_DC_ID / HOSTINGER_TEMPLATE_ID / HOSTINGER_VM_ID   pin exact ids
#   FX_TO_AUD (auto per currency) · TAX_RATE=0.10 (GST) · ALLOW_RENEWAL_OVER_CAP=0

HAPI="${HOSTINGER_API:-https://developers.hostinger.com}"
HOSTINGER_PLAN="${HOSTINGER_PLAN:-KVM 2}"
HOSTINGER_TERM="${HOSTINGER_TERM:-24}"
HOSTINGER_DC_PREFER="${HOSTINGER_DC_PREFER:-ID MY IN}"
TAX_RATE="${TAX_RATE:-0.10}"
ALLOW_RENEWAL_OVER_CAP="${ALLOW_RENEWAL_OVER_CAP:-0}"
PI_NAME="${PI_NAME:-aurora-post-install}"
# Written when a purchase comes back "payment processing": blocks a second purchase until
# the VPS shows up (or you delete the file after checking hPanel).
PENDING="${HOSTINGER_PENDING_FILE:-$HOME/.aurora-hostinger-order-pending}"

# h_call METHOD PATH [JSON] → sets H_CODE and H_BODY (no subshell, so both survive).
h_call() {
  local m="$1" p="$2" body="${3:-}" tmp try
  tmp="$(mktemp)"
  for try in 1 2 3 4 5; do
    if [ -n "$body" ]; then
      H_CODE="$(curl -sS -o "$tmp" -w '%{http_code}' -X "$m" -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
        -H 'Accept: application/json' -H 'Content-Type: application/json' --data "$body" "$HAPI$p")" || H_CODE=000
    else
      H_CODE="$(curl -sS -o "$tmp" -w '%{http_code}' -X "$m" -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
        -H 'Accept: application/json' "$HAPI$p")" || H_CODE=000
    fi
    case "$H_CODE" in 429|000|502|503) sleep $((try * 6)) ;; *) break ;; esac
  done
  H_BODY="$(cat "$tmp")"; rm -f "$tmp"
}
h_ok() { # h_ok "what we were doing" → die with Hostinger's message unless 2xx
  case "$H_CODE" in 2??) return 0 ;; esac
  local msg; msg="$(printf '%s' "$H_BODY" | jq -r '[.message // empty, (.errors // {} | to_entries[] | "\(.key): \(.value|join(" "))")] | join(" · ")' 2>/dev/null)"
  case "$H_CODE" in
    401) die "Hostinger API: token rejected (401). Make a new one at https://hpanel.hostinger.com/profile/api" ;;
    *)   die "Hostinger API, $1: HTTP $H_CODE ${msg:-$(printf '%s' "$H_BODY" | head -c 300)}" ;;
  esac
}
h_list() { # h_list PATH → H_BODY = JSON array of every page's .data
  local all='[]' page=1 n
  while [ $page -le 20 ]; do
    h_call GET "$1?page=$page"; h_ok "listing $1"
    n="$(printf '%s' "$H_BODY" | jq '.data | length')"
    all="$(jq -n --argjson a "$all" --argjson b "$(printf '%s' "$H_BODY" | jq '.data')" '$a + $b')"
    [ "$n" -gt 0 ] || break
    [ "$(printf '%s' "$H_BODY" | jq '(.meta.current_page // 1) * (.meta.per_page // 1000) >= (.meta.total // 0)')" = true ] && break
    page=$((page + 1))
  done
  H_BODY="$all"
}
h_vm() { h_call GET "/api/vps/v1/virtual-machines/$1"; h_ok "reading VPS $1"; VM="$H_BODY"; }

provision_hostinger() {
  [ -n "${HOSTINGER_API_TOKEN:-}" ] || die "HOSTINGER_API_TOKEN is not set: make one at https://hpanel.hostinger.com/profile/api and put it in infra/secrets.env"
  local vms mode="" vm_id="" state dcs dc_id dc_label tpls tpl_id tpl_name

  # --- Which VPS? ------------------------------------------------------------------------
  say "Looking at your Hostinger VPSes"
  h_call GET /api/vps/v1/virtual-machines; h_ok "listing VPSes"; vms="$H_BODY"
  printf '%s' "$vms" | jq -r '.[] | "  #\(.id)  \(.hostname)  \(.plan // "?")  \(.state)  \([.ipv4[]?.address] | join(","))"'
  if [ -n "${HOSTINGER_VM_ID:-}" ]; then
    vm_id="$HOSTINGER_VM_ID"
    printf '%s' "$vms" | jq -e --argjson i "$vm_id" 'any(.[]; .id == $i)' >/dev/null || die "no VPS #$vm_id on this account"
  else
    vm_id="$(printf '%s' "$vms" | jq -r --arg n "$NAME" '[.[] | select(.hostname == $n or (.hostname | startswith($n + ".")))][0].id // empty')"
    if [ -z "$vm_id" ]; then
      local initial; initial="$(printf '%s' "$vms" | jq '[.[] | select(.state == "initial")]')"
      case "$(printf '%s' "$initial" | jq length)" in
        0) mode=buy ;;
        1) vm_id="$(printf '%s' "$initial" | jq -r '.[0].id')" ;;
        *) die "several VPSes are waiting for setup; pick one: HOSTINGER_VM_ID=<id> ./bootstrap.sh" ;;
      esac
    fi
  fi
  if [ "$mode" = buy ] && [ -f "$PENDING" ]; then
    die "an earlier purchase was still processing ($(cat "$PENDING")). Check hPanel → VPS: once it's listed, run this again to set it up. If that order failed, delete $PENDING and run again."
  fi
  [ "$mode" != buy ] && rm -f "$PENDING"
  if [ -z "$mode" ]; then
    state="$(printf '%s' "$vms" | jq -r --argjson i "$vm_id" '.[] | select(.id == $i) | .state')"
    case "$state" in
      initial) mode=setup ;;
      running) if printf '%s' "$vms" | jq -e --argjson i "$vm_id" --arg n "$NAME" \
                   '.[] | select(.id == $i) | (.hostname == $n or (.hostname | startswith($n + ".")))' >/dev/null
               then mode=reuse; else mode=adopt; fi ;;
      *) die "VPS #$vm_id is '$state'. Start it in hPanel (or wait), then run this again." ;;
    esac
  fi

  # --- Location + OS (needed to set up or buy) -----------------------------------------------
  if [ "$mode" = setup ] || [ "$mode" = buy ]; then
    h_call GET /api/vps/v1/data-centers; h_ok "listing data centres"; dcs="$H_BODY"
    if [ -n "${HOSTINGER_DC_ID:-}" ]; then dc_id="$HOSTINGER_DC_ID"
    else
      local cc
      for cc in $HOSTINGER_DC_PREFER; do
        dc_id="$(printf '%s' "$dcs" | jq -r --arg c "$cc" '[.[] | select((.location // "") | ascii_upcase == $c)][0].id // empty')"
        [ -n "$dc_id" ] && break
      done
      [ -n "$dc_id" ] || { printf '%s' "$dcs" | jq -r '.[] | "  #\(.id) \(.city), \(.location) (\(.continent))"'; die "none of '$HOSTINGER_DC_PREFER' is available; set HOSTINGER_DC_ID from the list above"; }
    fi
    dc_label="$(printf '%s' "$dcs" | jq -r --argjson i "$dc_id" '.[] | select(.id == $i) | "\(.city // .name), \(.location)"')"
    h_call GET /api/vps/v1/templates; h_ok "listing OS templates"; tpls="$H_BODY"
    tpl_id="${HOSTINGER_TEMPLATE_ID:-$(printf '%s' "$tpls" | jq -r '
      ([.[] | select(.name | test("^Ubuntu 24\\.04( LTS)?$"; "i"))][0].id) //
      ([.[] | select((.name | test("Ubuntu 24\\.04"; "i")) and ((.name | test(" with |panel|plesk|cpanel"; "i")) | not))][0].id) // empty')}"
    [ -n "$tpl_id" ] || die "no plain Ubuntu 24.04 template found; set HOSTINGER_TEMPLATE_ID"
    tpl_name="$(printf '%s' "$tpls" | jq -r --argjson i "$tpl_id" '.[] | select(.id == $i) | .name')"
    echo "  location: $dc_label (#$dc_id) · OS: $tpl_name (#$tpl_id)"
  fi

  # --- Budget guard (buying only) --------------------------------------------------------------
  PRICE_LINE="existing Hostinger VPS (no new charge)"
  local price_id=""
  if [ "$mode" = buy ]; then
    say "Budget check: $HOSTINGER_PLAN, $HOSTINGER_TERM-month term (cap: AUD \$${BUDGET_AUD}/mo)"
    h_call GET "/api/billing/v1/catalog?category=VPS"; h_ok "reading prices"
    local item pr cur first renew months fx
    item="$(printf '%s' "$H_BODY" | jq --arg p "$HOSTINGER_PLAN" '
      [.[] | select(.name | ascii_downcase | test("(^|[^a-z0-9])" + ($p | ascii_downcase) + "([^0-9]|$)"))][0] // empty')"
    [ -n "$item" ] || { printf '%s' "$H_BODY" | jq -r '.[].name' | sed 's/^/  /'; die "plan '$HOSTINGER_PLAN' not in the catalog; set HOSTINGER_PLAN to one of the names above"; }
    pr="$(printf '%s' "$item" | jq --argjson t "$HOSTINGER_TERM" '
      [.prices[] | select((if .period_unit == "year" then .period * 12 elif .period_unit == "month" then .period else -1 end) == $t)][0] // empty')"
    [ -n "$pr" ] || { printf '%s' "$item" | jq -r '.prices[] | "  \(.period) \(.period_unit)"'; die "no $HOSTINGER_TERM-month price for $HOSTINGER_PLAN; set HOSTINGER_TERM to one of the terms above (in months)"; }
    price_id="$(printf '%s' "$pr" | jq -r .id)"; cur="$(printf '%s' "$pr" | jq -r .currency)"
    first="$(printf '%s' "$pr" | jq -r '.first_period_price // .price')"; renew="$(printf '%s' "$pr" | jq -r .price)"
    months="$HOSTINGER_TERM"
    case "${FX_TO_AUD:-}:$cur" in
      :AUD) fx=1 ;; :USD) fx=1.60 ;; :EUR) fx=1.75 ;; :GBP) fx=2.05 ;;
      :*) die "prices are in $cur; set FX_TO_AUD (AUD per 1 $cur) and run again" ;;
      *) fx="$FX_TO_AUD" ;;
    esac
    local up_aud first_mo renew_mo
    up_aud="$(awk -v c="$first" -v f="$fx" -v t="$TAX_RATE" 'BEGIN{printf "%.2f", c/100*f*(1+t)}')"
    first_mo="$(awk -v c="$first" -v m="$months" -v f="$fx" -v t="$TAX_RATE" 'BEGIN{printf "%.2f", c/100/m*f*(1+t)}')"
    renew_mo="$(awk -v c="$renew" -v m="$months" -v f="$fx" -v t="$TAX_RATE" 'BEGIN{printf "%.2f", c/100/m*f*(1+t)}')"
    echo "  $(printf '%s' "$item" | jq -r .name): $cur $(awk -v c="$first" 'BEGIN{printf "%.2f", c/100}') for $months months, then $cur $(awk -v c="$renew" 'BEGIN{printf "%.2f", c/100}') per $months months"
    echo "  ≈ AUD \$${first_mo}/mo now, AUD \$${renew_mo}/mo after renewal (at $fx AUD/$cur, +$(awk -v t="$TAX_RATE" 'BEGIN{printf "%d", t*100}')% GST)"
    echo "  Charged UP FRONT today: ≈ AUD \$${up_aud}"
    awk -v a="$first_mo" -v b="$BUDGET_AUD" 'BEGIN{exit !(a<=b)}' \
      || die "≈AUD \$${first_mo}/mo is over the AUD \$${BUDGET_AUD} cap. Pick a smaller HOSTINGER_PLAN."
    if ! awk -v a="$renew_mo" -v b="$BUDGET_AUD" 'BEGIN{exit !(a<=b)}'; then
      [ "$ALLOW_RENEWAL_OVER_CAP" = 1 ] \
        || die "the renewal price (≈AUD \$${renew_mo}/mo) is over the AUD \$${BUDGET_AUD} cap. Pick a smaller plan, or ALLOW_RENEWAL_OVER_CAP=1 if you'll cancel or downgrade before it renews."
      echo "  ! renewal is over the cap (allowed by ALLOW_RENEWAL_OVER_CAP=1)"
    fi
    PRICE_LINE="≈AUD \$${first_mo}/mo ($HOSTINGER_PLAN, paid ≈AUD \$${up_aud} up front for $months months)"
    h_call GET /api/billing/v1/payment-methods; h_ok "reading payment methods"
    printf '%s' "$H_BODY" | jq -e 'any(.[]; .is_default and (.is_expired | not) and (.is_suspended | not))' >/dev/null \
      || die "no usable default payment method on your Hostinger account. Add one: https://hpanel.hostinger.com/billing/payment-methods"
  fi

  # --- Dry run stops here ----------------------------------------------------------------------
  if [ "$DRY_RUN" = 1 ]; then
    case "$mode" in
      reuse) say "Dry run: would REUSE VPS #$vm_id ($NAME), re-apply the firewall and ship files." ;;
      adopt) say "Dry run: would ADOPT running VPS #$vm_id: attach your key, run the post-install script as root (locks root login), firewall, ship." ;;
      setup) say "Dry run: would SET UP VPS #$vm_id (bought, not installed yet) with $tpl_name in $dc_label. No charge." ;;
      buy)   say "Dry run: would BUY $HOSTINGER_PLAN in $dc_label: $PRICE_LINE." ;;
    esac
    echo "  Nothing was bought or changed."; exit 0
  fi

  # --- Confirm ---------------------------------------------------------------------------------
  if [ "$ASSUME_YES" != 1 ]; then
    case "$mode" in
      buy)   read -r -p "Type buy to purchase $HOSTINGER_PLAN ($PRICE_LINE): " ans
             [ "$ans" = buy ] || die "aborted — nothing was bought" ;;
      setup) read -r -p "Install Ubuntu 24.04 + our setup on VPS #$vm_id? (no charge) [y/N] " ans
             [[ "$ans" =~ ^[Yy]$ ]] || die "aborted" ;;
      adopt) read -r -p "Run our setup on the RUNNING VPS #$vm_id as root? It turns off root and password logins. [y/N] " ans
             [[ "$ans" =~ ^[Yy]$ ]] || die "aborted" ;;
    esac
  fi

  # --- Post-install script (for buy/setup) ------------------------------------------------------
  local pi pi_id setup_body
  pi="$(<"$DIR/hostinger/post-install.sh")"; pi="${pi//"<YOUR_SSH_PUBLIC_KEY>"/$PUBKEY}"
  grep -q '<YOUR_SSH_PUBLIC_KEY>' <<<"$pi" && die "failed to put your SSH key into the post-install script"
  [ "$(printf '%s' "$pi" | wc -c)" -le 49152 ] || die "post-install script is over Hostinger's 48 KB limit"
  if [ "$mode" = buy ] || [ "$mode" = setup ]; then
    say "Post-install script"
    h_list /api/vps/v1/post-install-scripts
    pi_id="$(printf '%s' "$H_BODY" | jq -r --arg n "$PI_NAME" '[.[] | select(.name == $n)][0].id // empty')"
    local pbody; pbody="$(jq -n --arg n "$PI_NAME" --arg c "$pi" '{name:$n, content:$c}')"
    if [ -n "$pi_id" ]; then h_call PUT "/api/vps/v1/post-install-scripts/$pi_id" "$pbody"; h_ok "updating post-install script"; echo "  updated (#$pi_id)"
    else h_call POST /api/vps/v1/post-install-scripts "$pbody"; h_ok "uploading post-install script"; pi_id="$(printf '%s' "$H_BODY" | jq -r .id)"; echo "  uploaded (#$pi_id)"; fi
    setup_body="$(jq -n --argjson t "$tpl_id" --argjson d "$dc_id" --argjson p "$pi_id" --arg h "$NAME" \
      --arg kn "$NAME-$(hostname 2>/dev/null | tr -c 'a-zA-Z0-9-' '-' | head -c 20)" --arg k "$PUBKEY" \
      '{template_id:$t, data_center_id:$d, post_install_script_id:$p, hostname:$h, public_key:{name:$kn, key:$k}}')"
  fi

  # --- Buy / set up ----------------------------------------------------------------------------
  case "$mode" in
    buy)
      say "Buying $HOSTINGER_PLAN"
      h_call POST /api/vps/v1/virtual-machines "$(jq -n --arg i "$price_id" --argjson s "$setup_body" '{item_id:$i, setup:$s}')"
      [ "$H_CODE" = 202 ] && { date '+%F %T' > "$PENDING"; }
      [ "$H_CODE" = 202 ] && die "Payment is still processing. When hPanel shows the VPS, run ./bootstrap.sh again: it will find it and set it up (no second charge)."
      h_ok "buying the VPS"
      vm_id="$(printf '%s' "$H_BODY" | jq -r '.virtual_machine.id')"
      echo "  order #$(printf '%s' "$H_BODY" | jq -r '.order.id') $(printf '%s' "$H_BODY" | jq -r '.order.status') · VPS #$vm_id" ;;
    setup)
      say "Setting up VPS #$vm_id"
      h_call POST "/api/vps/v1/virtual-machines/$vm_id/setup" "$setup_body"; h_ok "setting up the VPS" ;;
    reuse|adopt)
      say "Making sure your SSH key is on VPS #$vm_id"
      h_list /api/vps/v1/public-keys
      local kid body; body="$(awk '{print $1" "$2}' <<<"$PUBKEY")"
      kid="$(printf '%s' "$H_BODY" | jq -r --arg k "$body" '[.[] | select((.key | split(" ")[0:2] | join(" ")) == $k)][0].id // empty')"
      if [ -z "$kid" ]; then
        h_call POST /api/vps/v1/public-keys "$(jq -n --arg n "$NAME-key" --arg k "$PUBKEY" '{name:$n, key:$k}')"; h_ok "uploading your key"
        kid="$(printf '%s' "$H_BODY" | jq -r .id)"
      fi
      h_call POST "/api/vps/v1/public-keys/attach/$vm_id" "$(jq -n --argjson i "$kid" '{ids:[$i]}')"; h_ok "attaching your key" ;;
  esac

  # --- Wait until running ----------------------------------------------------------------------
  say "Waiting for VPS #$vm_id to be running (a fresh install takes 5–15 minutes)"
  local i
  for i in $(seq 1 120); do
    h_vm "$vm_id"; state="$(printf '%s' "$VM" | jq -r .state)"
    [ "$state" = running ] && [ "$(printf '%s' "$VM" | jq -r .actions_lock)" != locked ] && break
    [ "$state" = error ] && die "VPS #$vm_id is in 'error'; check hPanel"
    sleep 10
  done
  [ "$state" = running ] || die "VPS #$vm_id isn't running after 20 minutes (state: $state)"
  IP="$(printf '%s' "$VM" | jq -r '[.ipv4[]?.address][0] // empty')"
  [ -n "$IP" ] || die "VPS #$vm_id has no IPv4 address yet"
  echo "  running at $IP ($(printf '%s' "$VM" | jq -r '.plan // "?"'), $(printf '%s' "$VM" | jq -r '.cpus') vCPU, $(( $(printf '%s' "$VM" | jq -r '.memory') / 1024 )) GB RAM)"

  # --- Firewall: SSH + Tailscale in, everything else dropped ------------------------------------
  say "Hostinger firewall (inbound: SSH + Tailscale only; Docker ports can't bypass it)"
  local fw fw_id want r
  h_list /api/vps/v1/firewall
  fw="$(printf '%s' "$H_BODY" | jq --arg n "$NAME-fw" '[.[] | select(.name == $n)][0] // empty')"
  if [ -z "$fw" ]; then
    h_call POST /api/vps/v1/firewall "$(jq -n --arg n "$NAME-fw" '{name:$n}')"; h_ok "creating the firewall"; fw="$H_BODY"
    echo "  created (#$(printf '%s' "$fw" | jq -r .id))"
  fi
  fw_id="$(printf '%s' "$fw" | jq -r .id)"
  for want in "TCP 22" "UDP 41641"; do
    set -- $want
    if ! printf '%s' "$fw" | jq -e --arg p "$1" --arg port "$2" 'any(.rules[]?; .protocol == $p and .port == $port and .action == "accept")' >/dev/null; then
      h_call POST "/api/vps/v1/firewall/$fw_id/rules" "$(jq -n --arg p "$1" --arg port "$2" '{protocol:$p, port:$port, source:"any", source_detail:"any"}')"
      h_ok "adding firewall rule $want"; echo "  + allow $want"
    fi
  done
  if [ "$(printf '%s' "$VM" | jq -r '.firewall_group_id // empty')" != "$fw_id" ]; then
    h_call POST "/api/vps/v1/firewall/$fw_id/activate/$vm_id"; h_ok "turning the firewall on"; echo "  activated on VPS #$vm_id"
  fi
  h_call POST "/api/vps/v1/firewall/$fw_id/sync/$vm_id"; h_ok "syncing the firewall"

  # --- Adopt: run the setup over SSH as root -----------------------------------------------------
  if [ "$mode" = adopt ]; then
    say "Running the post-install script on $IP as root"
    local R=(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "root@$IP")
    for i in $(seq 1 18); do "${R[@]}" true 2>/dev/null && break; sleep 10; done
    printf '%s' "$pi" | "${R[@]}" 'cat > /post_install && chmod 700 /post_install && /post_install > /post_install.log 2>&1; tail -3 /post_install.log' \
      || die "post-install over SSH failed; see /post_install.log on the VPS"
  fi

  SSH_WAIT_TRIES=90   # the post-install script creates the aurora user a few minutes after "running"
  READY_CMD='for i in $(seq 1 90); do [ -f /var/lib/aurora/post-install.done ] && exit 0; sleep 10; done; echo "post-install not finished: see /post_install.log" >&2; exit 1'
}
