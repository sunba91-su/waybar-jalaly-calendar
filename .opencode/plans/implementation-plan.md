# Implementation Plan: waybar-jalaly-calendar

## Permission Needed
I need `edit: *` permission to write files. Currently only plans directory is writable.
Please run: `/opencode` → Permissions → Allow editing, or run:
```bash
opencode settings set edit true
```

## Files to Create

### 1. `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "waybar-jalaly-calendar"
version = "1.0.0"
description = "Jalali (Persian/Solar Hijri) calendar module for Waybar"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "GPL-3.0-or-later" }
keywords = ["waybar", "sway", "persian-calendar", "jalali", "hijri"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Operating System :: POSIX :: Linux",
    "Topic :: Desktop Environment :: Window Managers",
]
dependencies = ["jdatetime>=3.8", "hijridate>=1.0"]

[project.urls]
Homepage = "https://github.com/sunba91-su/waybar-jalaly-calendar"
Repository = "https://github.com/sunba91-su/waybar-jalaly-calendar"

[project.scripts]
waybar-jalaly-calendar = "waybar_jalaly_calendar.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]

[project.optional-dependencies]
test = ["pytest>=7"]
```

### 2. `requirements.txt`
```
jdatetime>=3.8
hijridate>=1.0
```

### 3. `LICENSE`
GNU GPL v3 short form.

### 4. `src/waybar_jalaly_calendar/persian_utils.py`
```python
import jdatetime

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

WEEKDAYS_FA = [
    "شنبه", "یک\u200cشنبه", "دوشنبه", "سه\u200cشنبه",
    "چهارشنبه", "پنج\u200cشنبه", "جمعه",
]

MONTHS_FA = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]

MONTHS_HIJRI_AR = [
    "محرم", "صفر", "ربیع\u200cالاول", "ربیع\u200cالثانی",
    "جمادی\u200cالاول", "جمادی\u200cالثانی", "رجب", "شعبان",
    "رمضان", "شوال", "ذی\u200cالقعده", "ذی\u200cالحجه",
]


def to_persian_digits(text: str | int) -> str:
    if isinstance(text, int):
        text = str(text)
    return text.translate(PERSIAN_DIGITS)


def is_iran_weekend(j_date: jdatetime.date) -> bool:
    """Return True if Friday (Jomeh) in Iran.
    jdatetime.weekday(): 0=Sat, 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri
    """
    return j_date.weekday() == 6
```

### 5. `src/waybar_jalaly_calendar/holidays.py`
```python
import jdatetime
from hijridate import Gregorian as HijriGregorian


# Fixed Jalali holidays: (month, day) -> name
JALALI_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 1): "نوروز",
    (1, 2): "نوروز",
    (1, 3): "نوروز",
    (1, 4): "نوروز",
    (1, 12): "جمهوری اسلامی",
    (1, 13): "سیزده\u200cبدر",
    (3, 14): "رحلت امام خمینی",
    (3, 15): "قیام ۱۵ خرداد",
    (11, 22): "پیروزی انقلاب",
    (12, 29): "ملی\u200cشدن نفت",
}

# Hijri holidays: (month, day) -> name
HIJRI_HOLIDAYS: dict[tuple[int, int], str] = {
    (1, 9): "تاسوعا",
    (1, 10): "عاشورا",
    (2, 20): "اربعین",
    (2, 28): "رحلت پیامبر",
    (2, 30): "شهادت امام رضا",
    (7, 27): "مبعث",
    (8, 15): "ولادت امام مهدی",
    (9, 1): "ماه رمضان",
    (10, 1): "عید فطر",
    (10, 2): "تعطیل عید فطر",
    (12, 10): "عید قربان",
    (12, 18): "عید غدیر",
}


def get_jalali_holidays(j_date: jdatetime.date) -> list[str]:
    return [name for (m, d), name in JALALI_HOLIDAYS.items()
            if m == j_date.month and d == j_date.day]


def get_hijri_holidays(j_date: jdatetime.date) -> list[str]:
    g = j_date.togregorian()
    h = HijriGregorian(g.year, g.month, g.day).to_hijri()
    return [name for (m, d), name in HIJRI_HOLIDAYS.items()
            if m == h.month and d == h.day]


def days_to_nowruz(j_today: jdatetime.date) -> int:
    next_year = j_today.year
    nowruz = jdatetime.date(next_year, 1, 1)
    if j_today > nowruz:
        nowruz = jdatetime.date(next_year + 1, 1, 1)
    return (nowruz - j_today).days


def get_all_holidays(j_date: jdatetime.date) -> list[str]:
    return get_jalali_holidays(j_date) + get_hijri_holidays(j_date)
```

### 6. `src/waybar_jalaly_calendar/calendar.py`
```python
import json
import os
import sys
from datetime import date, timedelta

import jdatetime

from .holidays import days_to_nowruz, get_all_holidays
from .persian_utils import (
    MONTHS_FA,
    WEEKDAYS_FA,
    is_iran_weekend,
    to_persian_digits,
)

STATE_FILE = "/tmp/waybar-jalaly-state"
HEADER_WEEKDAYS = "ش   ی   د   س   چ   پ   ج"


def _read_offset() -> int:
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get("offset", 0)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0


def _write_offset(offset: int) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump({"offset": offset}, f)


def _build_calendar_grid(j_date: jdatetime.date) -> str:
    lines = []
    month = j_date.month
    year = j_date.year
    first_day = jdatetime.date(year, month, 1)
    # jdatetime weekday: 0=Sat ... 6=Fri
    start_col = first_day.weekday()
    if month == 12:
        days_in_month = 30 if j_date.isleap() else 29
    elif month <= 6:
        days_in_month = 31
    else:
        days_in_month = 30

    today = jdatetime.date.today()

    lines.append(f"  {MONTHS_FA[month - 1]} {to_persian_digits(year)}")
    lines.append(HEADER_WEEKDAYS)

    row = ["  "] * 7
    for d in range(1, days_in_month + 1):
        col = (start_col + d - 1) % 7
        day_str = str(d).rjust(2)
        if jdatetime.date(year, month, d) == today:
            day_str = f"<b>{day_str}</b>"
        row[col] = day_str
        if col == 6 or d == days_in_month:
            lines.append(" ".join(row))
            row = ["  "] * 7

    return "\n".join(lines)


def main() -> None:
    try:
        offset = _read_offset()
        j_today = jdatetime.date.today()
        g_today = j_today.togregorian()

        month_offset = jdatetime.date(
            j_today.year + (j_today.month + offset - 1) // 12,
            (j_today.month + offset - 1) % 12 + 1,
            1,
        )

        holidays = get_all_holidays(j_today)
        weekday_name = WEEKDAYS_FA[j_today.weekday()]
        month_name = MONTHS_FA[j_today.month - 1]

        css_class = ""
        if holidays:
            css_class = "holiday"
        elif is_iran_weekend(j_today):
            css_class = "weekend"

        icon = " " if css_class == "holiday" else ""
        text = f"{icon} {to_persian_digits(f'{j_today.day} {month_name} {j_today.year}')}"

        tooltip_lines = []
        tooltip_lines.append(
            f"{weekday_name} {to_persian_digits(f'{j_today.day} {month_name} {j_today.year}')}"
        )
        if holidays:
            tooltip_lines.append(f"  {', '.join(map(to_persian_digits, holidays))}")
        tooltip_lines.append("")
        tooltip_lines.append(
            f"میلادی: {to_persian_digits(f'{g_today.year}/{g_today.month:02d}/{g_today.day:02d}')}"
        )

        from hijridate import Gregorian as HijriGregorian

        h_today = HijriGregorian(g_today.year, g_today.month, g_today.day).to_hijri()
        tooltip_lines.append(
            f"قمری: {to_persian_digits(f'{h_today.day} {MONTHS_HIJRI_AR[h_today.month - 1] if True else \"\"} {h_today.year}')}"
        )

        nd = days_to_nowruz(j_today)
        if nd == 0:
            tooltip_lines.append("  نوروز مبارک!")
        elif nd == 1:
            tooltip_lines.append("  فردا نوروز")
        elif nd < 100:
            tooltip_lines.append(f"  {to_persian_digits(str(nd))} روز تا نوروز")

        days_in_year = 366 if j_today.isleap() else 365
        start_of_year = jdatetime.date(j_today.year, 1, 1)
        day_of_year = (j_today - start_of_year).days + 1
        remaining = days_in_year - day_of_year
        tooltip_lines.append(
            f"  {to_persian_digits(str(remaining))} روز تا پایان سال"
        )

        tooltip_lines.append("")
        tooltip_lines.append(_build_calendar_grid(month_offset))

        output = {
            "text": text,
            "tooltip": "\n".join(tooltip_lines),
            "class": css_class,
            "alt": weekday_name,
        }
        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"text": " --", "tooltip": f"Error: {e}"}))
        sys.stderr.write(f"waybar-jalaly-calendar: {e}\n")
```

### 7. `src/waybar_jalaly_calendar/__init__.py`
```python
"""waybar-jalaly-calendar - Jalali (Persian) calendar module for Waybar."""
```

### 8. `src/waybar_jalaly_calendar/__main__.py`
```python
import argparse
import json
import os

STATE_FILE = "/tmp/waybar-jalaly-state"


def main_cli():
    parser = argparse.ArgumentParser(description="Waybar Jalaly Calendar")
    parser.add_argument("--reset", action="store_true", help="Reset to current month")
    parser.add_argument("--next", action="store_true", help="Next month")
    parser.add_argument("--prev", action="store_true", help="Previous month")
    args = parser.parse_args()

    if args.reset:
        with open(STATE_FILE, "w") as f:
            json.dump({"offset": 0}, f)
        return

    offset = 0
    try:
        with open(STATE_FILE) as f:
            offset = json.load(f).get("offset", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if args.next:
        offset += 1
    elif args.prev:
        offset -= 1

    with open(STATE_FILE, "w") as f:
        json.dump({"offset": offset}, f)


def main():
    main_cli()


if __name__ == "__main__":
    main()
```

### 9. `config/waybar-config.jsonc`
```jsonc
{
  "custom/shamsi-date": {
    "exec": "waybar-jalaly-calendar",
    "format": "{}",
    "interval": 3600,
    "return-type": "json",
    "signal": 1,
    "on-click": "waybar-jalaly-calendar --reset && pkill -SIGRTMIN+1 waybar",
    "on-scroll-up": "waybar-jalaly-calendar --next && pkill -SIGRTMIN+1 waybar",
    "on-scroll-down": "waybar-jalaly-calendar --prev && pkill -SIGRTMIN+1 waybar"
  }
}
```

### 10. `examples/style.css`
```css
#custom-shamsi-date {
    color: #eceff4;
    font-weight: bold;
    padding: 0 8px;
    margin: 2px 0;
    border-radius: 4px;
}

#custom-shamsi-date.holiday {
    color: #bf616a; /* red for holidays */
}

#custom-shamsi-date.weekend {
    color: #ebcb8b; /* yellow for Friday */
}
```

### 11. `tests/test_calendar.py`
```python
from waybar_jalaly_calendar.persian_utils import is_iran_weekend, to_persian_digits
from waybar_jalaly_calendar.holidays import get_jalali_holidays, days_to_nowruz
import jdatetime


def test_friday_is_weekend():
    # Farvardin 7, 1405 = Friday (جمعه) = jdatetime weekday 6
    friday = jdatetime.date(1405, 1, 7)
    assert is_iran_weekend(friday)


def test_saturday_not_weekend():
    saturday = jdatetime.date(1405, 1, 2)
    assert not is_iran_weekend(saturday)


def test_persian_digits():
    assert to_persian_digits(1403) == "۱۴۰۳"
    assert to_persian_digits("15") == "۱۵"


def test_nowruz_holiday():
    nowruz = jdatetime.date(1405, 1, 1)
    holidays = get_jalali_holidays(nowruz)
    assert "نوروز" in holidays


def test_days_to_nowruz():
    last_day = jdatetime.date(1404, 12, 29)
    nd = days_to_nowruz(last_day)
    assert nd == 1  # next day is Nowruz
```

### 12. `Makefile`
```makefile
.PHONY: install uninstall install-system install-user dev

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
INSTALL_DIR ?= $(HOME)/.local/bin

install-user:
	@echo "Installing waybar-jalaly-calendar for current user..."
	pip install --user -e .
	@echo ""
	@echo "Done! Make sure $(INSTALL_DIR) is in your PATH."
	@echo "Then add 'custom/shamsi-date' to your Waybar config (see config/)."

install-system:
	@echo "Installing waybar-jalaly-calendar system-wide..."
	sudo pip install -e .
	@echo "Done!"

install: install-user

uninstall:
	pip uninstall waybar-jalaly-calendar -y
	rm -f /tmp/waybar-jalaly-state
	@echo "Uninstalled."

dev:
	pip install -e .
	@echo "Development install complete. Run 'waybar-jalaly-calendar' to test."

test:
	pip install -e ".[test]"
	python -m pytest tests/
```

### 13. `install.sh` — Automated Installer Script

```bash
#!/usr/bin/env bash
# install.sh — Automated installer for waybar-jalaly-calendar
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[x]${NC} $1"; exit 1; }

# --- Pre-flight checks ---
command -v python3 &>/dev/null || err "python3 is required but not found."
command -v pip3 &>/dev/null   || err "pip3 is required but not found."

# Check dependencies can be installed
info "Python $(python3 --version)"
info "pip $(pip3 --version | cut -d' ' -f2)"

# --- Install Python package ---
info "Installing waybar-jalaly-calendar..."
pip3 install --user -e . 2>&1 | tail -1

INSTALL_DIR="${HOME}/.local/bin"
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    warn "${INSTALL_DIR} is not in your PATH."
    warn "Add this to your shell config:  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
fi

# --- Verify installation ---
info "Verifying..."
if command -v waybar-jalaly-calendar &>/dev/null; then
    info "waybar-jalaly-calendar installed successfully!"
    waybar-jalaly-calendar 2>/dev/null && echo "  → Test output: $(python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('text',''))" <<<"$(waybar-jalaly-calendar 2>/dev/null)")"
else
    warn "waybar-jalaly-calendar not found in PATH after install."
    warn "Try: python3 -m waybar_jalaly_calendar"
fi

# --- Waybar config guidance ---
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
echo "  3. Reload Waybar:  pkill -SIGRTMIN+1 waybar  (or  pkill waybar && waybar &)"
echo "──────────────────────────────────────────────"
```

### 14. `README.md`
Full documentation covering:
- What it does (Persian calendar in Waybar)
- Quick start: `make install` or `./install.sh`
- Installation: pip, pipx, from source, AUR (future)
- Waybar configuration (JSON + CSS)
- Features: Jalali + Hijri + Gregorian dates, holiday detection, monthly calendar grid tooltip, Nowruz countdown, click/scroll navigation, Persian numerals
- Uninstallation: `make uninstall`
- Dependencies: jdatetime, hijridate
- License: GPL-3.0

## Installer Strategy Summary

| Method | Command | Best for |
|---|---|---|
| **install.sh** | `./install.sh` | First-time users, interactive setup |
| **Makefile** | `make install` | Developers, quick install |
| **pip** | `pip install .` | Python users, virtual envs |
| **pipx** | `pipx install .` | Isolated install (recommended) |

The user runs ONE command and the module is installed, verified, and they see exact copy-paste instructions for Waybar config.
