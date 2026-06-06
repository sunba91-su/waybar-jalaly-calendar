#!/usr/bin/env bash
# install.sh — Automated installer for waybar-jalaly-calendar
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[x]${NC} $1"; exit 1; }

command -v python3 &>/dev/null || err "python3 is required but not found."
command -v pip3 &>/dev/null   || err "pip3 is required but not found."

info "Python $(python3 --version)"
info "pip $(pip3 --version | cut -d' ' -f2)"

info "Installing waybar-jalaly-calendar..."
pip3 install --user -e . 2>&1 | tail -1

INSTALL_DIR="${HOME}/.local/bin"
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    warn "${INSTALL_DIR} is not in your PATH."
    warn 'Add this to your shell config:  export PATH="${HOME}/.local/bin:${PATH}"'
fi

info "Verifying..."
if command -v waybar-jalaly-calendar &>/dev/null; then
    info "waybar-jalaly-calendar installed successfully!"
    output=$(waybar-jalaly-calendar 2>/dev/null || true)
    text=$(echo "$output" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('text',''))" 2>/dev/null || echo "N/A")
    echo "  Test output: $text"
else
    warn "waybar-jalaly-calendar not found in PATH after install."
    warn "Try: python3 -m waybar_jalaly_calendar"
fi

echo ""
info "──────────────────────────────────────────────"
info " Quick Start:"
info "──────────────────────────────────────────────"
echo ""
echo "  1. Add to ~/.config/waybar/config:"
echo ""
echo '     "custom/shamsi-date": {'
echo '         "exec": "waybar-jalaly-calendar",'
echo '         "format": "{}",'
echo '         "interval": 3600,'
echo '         "return-type": "json",'
echo '         "signal": 1,'
echo '         "on-click": "waybar-jalaly-calendar --reset && pkill -SIGRTMIN+1 waybar",'
echo '         "on-scroll-up": "waybar-jalaly-calendar --next && pkill -SIGRTMIN+1 waybar",'
echo '         "on-scroll-down": "waybar-jalaly-calendar --prev && pkill -SIGRTMIN+1 waybar"'
echo '     },'
echo ""
echo "  2. Add to ~/.config/waybar/style.css:"
echo ""
echo '     #custom-shamsi-date { font-weight: bold; }'
echo '     #custom-shamsi-date.holiday { color: #bf616a; }'
echo '     #custom-shamsi-date.weekend { color: #ebcb8b; }'
echo ""
echo "  3. Reload Waybar:"
echo "     pkill -SIGRTMIN+1 waybar"
echo "     # or: pkill waybar && waybar &"
echo "──────────────────────────────────────────────"
