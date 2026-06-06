# waybar-jalaly-calendar

**تقویم جلالی برای وی‌بار** — Jalali (Persian/Solar Hijri) calendar module for [Waybar](https://github.com/Alexays/Waybar).

![Preview](https://img.shields.io/badge/waybar-module-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)
![License](https://img.shields.io/badge/license-GPLv3-blue)

## Features

- **Jalali date** in the bar with full Persian text (e.g., `۱۶ خرداد ۱۴۰۵`)
- **Calendar grid** in tooltip showing the full month
- **Holiday detection** — both fixed Jalali holidays (Nowruz, 22 Bahman, etc.) and movable Hijri holidays (Ashura, Ramadan, Eid)
- **Nowruz countdown** — shows days remaining until the new year
- **Year-end countdown** — remaining days in the current year
- **Gregorian & Hijri dates** in tooltip
- **Click navigation** — scroll through months in the tooltip
- **Weekend styling** — Friday (جمعه) gets a special CSS class
- **Persian numerals** — numbers displayed in Arabic-Indic digits (۰-۹)

## Requirements

- Python 3.9+
- [jdatetime](https://pypi.org/project/jdatetime/) — Jalali date library
- [hijridate](https://pypi.org/project/hijridate/) — Hijri date conversion

## Installation

### Quick install (recommended)

```bash
git clone https://github.com/sunba91-su/waybar-jalaly-calendar.git
cd waybar-jalaly-calendar
./install.sh
```

### Using pip

```bash
git clone https://github.com/sunba91-su/waybar-jalaly-calendar.git
cd waybar-jalaly-calendar
pip install --user .
```

### Using pipx (isolated)

```bash
pipx install .
```

### Using Makefile

```bash
make install     # user install
# or
make install-system  # system-wide
```

## Waybar Configuration

Add to your `~/.config/waybar/config`:

```json
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
```

Add to your `~/.config/waybar/style.css`:

```css
#custom-shamsi-date {
    font-weight: bold;
    padding: 0 8px;
}

#custom-shamsi-date.holiday {
    color: #bf616a; /* red for holidays */
}

#custom-shamsi-date.weekend {
    color: #ebcb8b; /* yellow for Friday */
}
```

Then restart Waybar:

```bash
pkill waybar && waybar &
# or, if signals are configured:
pkill -SIGRTMIN+1 waybar
```

## Usage

Once installed and configured, the calendar appears in your Waybar:

- **Bar text**: ` ۱۶ خرداد ۱۴۰۵` (current date with Persian digits)
- **Tooltip** (hover): Full date info, Hijri date, Nowruz countdown, and a monthly calendar grid with today highlighted
- **Scroll up/down**: Navigate through months in the tooltip
- **Click**: Reset back to the current month

### CLI Commands

```bash
waybar-jalaly-calendar       # Output Waybar JSON (called by Waybar)
waybar-jalaly-calendar --reset  # Reset to current month
waybar-jalaly-calendar --next  # Show next month
waybar-jalaly-calendar --prev  # Show previous month
```

## Development

```bash
git clone https://github.com/sunba91-su/waybar-jalaly-calendar.git
cd waybar-jalaly-calendar
pip install -e ".[test]"
python -m pytest tests/ -v
```

## Uninstall

```bash
make uninstall
# or
pip uninstall waybar-jalaly-calendar
```

## Holiday Categories

The module detects two categories of holidays:

### Fixed Jalali Holidays
- Nowruz (1–4 Farvardin)
- Islamic Republic Day (12 Farvardin)
- Sizdah Bedar (13 Farvardin)
- Death of Khomeini (14 Khordad)
- 15 Khordad Uprising (15 Khordad)
- Islamic Revolution Victory (22 Bahman)
- Nationalization of Oil (29 Esfand)

### Hijri (Lunar) Holidays
- Tasua (9 Muharram)
- Ashura (10 Muharram)
- Arba'een (20 Safar)
- Death of Prophet (28 Safar)
- Martyrdom of Imam Reza (30 Safar)
- Mab'ath (27 Rajab)
- Birth of Imam Mahdi (15 Sha'ban)
- Ramadan (1 Ramadan)
- Eid al-Fitr (1–2 Shawwal)
- Eid al-Adha (10 Dhu al-Hijjah)
- Eid al-Ghadir (18 Dhu al-Hijjah)

## License

GNU General Public License v3.0 or later. See [LICENSE](LICENSE).
