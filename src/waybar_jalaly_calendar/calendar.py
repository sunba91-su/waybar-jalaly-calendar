import json
import sys

import jdatetime
from hijridate import Gregorian as HijriGregorian

from .holidays import days_to_nowruz, get_all_holidays
from .persian_utils import (
    MONTHS_FA,
    MONTHS_HIJRI_AR,
    WEEKDAYS_FA,
    is_iran_weekend,
    to_persian_digits,
)

STATE_FILE = "/tmp/waybar-jalaly-state"
HEADER_WEEKDAYS = "ش   ی   د   س   چ   پ   ج"


def read_offset() -> int:
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get("offset", 0)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0


def _build_calendar_grid(target_month: jdatetime.date) -> str:
    lines = []
    month = target_month.month
    year = target_month.year

    first_day = jdatetime.date(year, month, 1)
    start_col = first_day.weekday()

    if month == 12:
        days_in_month = 30 if target_month.isleap() else 29
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
        offset = read_offset()
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
            tooltip_lines.append(
                f"  {', '.join(map(to_persian_digits, holidays))}"
            )

        h_today = HijriGregorian(
            g_today.year, g_today.month, g_today.day
        ).to_hijri()
        tooltip_lines.append("")
        tooltip_lines.append(
            f"میلادی: {to_persian_digits(f'{g_today.year}/{g_today.month:02d}/{g_today.day:02d}')}"
        )
        tooltip_lines.append(
            f"قمری: {to_persian_digits(f'{h_today.day} {MONTHS_HIJRI_AR[h_today.month - 1]} {h_today.year}')}"
        )

        nd = days_to_nowruz(j_today)
        if nd == 0:
            tooltip_lines.append("  نوروز مبارک!")
        elif nd == 1:
            tooltip_lines.append("  فردا نوروز")
        else:
            tooltip_lines.append(
                f"  {to_persian_digits(str(nd))} روز تا نوروز"
            )

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
        fallback = {"text": " --", "tooltip": f"Error: {e}"}
        print(json.dumps(fallback))
        sys.stderr.write(f"waybar-jalaly-calendar: {e}\n")
