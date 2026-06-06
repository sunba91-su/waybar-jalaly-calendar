import argparse
import json
import os

from .calendar import main as calendar_main, STATE_FILE


def handle_cli():
    parser = argparse.ArgumentParser(
        description="Waybar Jalaly Calendar - Persian calendar module for Waybar"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset calendar view to current month",
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="Show next month in calendar tooltip",
    )
    parser.add_argument(
        "--prev",
        action="store_true",
        help="Show previous month in calendar tooltip",
    )
    args = parser.parse_args()

    if not (args.reset or args.next or args.prev):
        calendar_main()
        return

    offset = 0
    if not args.reset:
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
    handle_cli()


if __name__ == "__main__":
    main()
