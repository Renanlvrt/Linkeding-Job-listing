#!/usr/bin/env python3
"""
Alert User Script
-----------------
Emits audible alerts to notify the user of task status.

Usage:
    python alert_user.py success   # Task completed successfully
    python alert_user.py done      # Alias for success
    python alert_user.py waiting   # Waiting for user input

Exit codes:
    0 - Alert played successfully
    1 - Invalid argument or error
"""

import sys
import winsound


def play_success_sound():
    """Play a success/done sound (two ascending beeps)."""
    winsound.Beep(800, 200)
    winsound.Beep(1000, 200)
    winsound.Beep(1200, 300)


def play_waiting_sound():
    """Play a waiting/attention sound (two short beeps)."""
    winsound.Beep(600, 150)
    winsound.Beep(600, 150)


def main():
    if len(sys.argv) < 2:
        print("Usage: python alert_user.py <success|done|waiting>")
        sys.exit(1)

    alert_type = sys.argv[1].lower()

    if alert_type in ("success", "done"):
        play_success_sound()
        print('{"status": "success", "message": "Alert played: task complete"}')
    elif alert_type == "waiting":
        play_waiting_sound()
        print('{"status": "success", "message": "Alert played: waiting for input"}')
    else:
        print(f'{{"status": "error", "message": "Unknown alert type: {alert_type}"}}')
        sys.exit(1)


if __name__ == "__main__":
    main()
