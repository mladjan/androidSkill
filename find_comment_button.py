#!/usr/bin/env python3
"""Interactive tool to find the correct comment button coordinates."""

import subprocess
import time
from rich.console import Console

console = Console()

def get_screen_size():
    """Get device screen size."""
    result = subprocess.run(
        ["adb", "shell", "wm", "size"],
        capture_output=True,
        text=True
    )
    # Output: "Physical size: 1080x2400"
    import re
    match = re.search(r'(\d+)x(\d+)', result.stdout)
    if match:
        return int(match.group(1)), int(match.group(2))
    return (1080, 2400)

def tap(x, y):
    """Tap at coordinates."""
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])
    time.sleep(0.5)

def take_screenshot(name):
    """Take screenshot."""
    subprocess.run(["adb", "shell", "screencap", "-p", f"/sdcard/{name}.png"])
    subprocess.run(["adb", "pull", f"/sdcard/{name}.png", f"data/{name}.png"])
    subprocess.run(["adb", "shell", "rm", f"/sdcard/{name}.png"])
    console.print(f"[green]Screenshot saved: data/{name}.png[/green]")

def main():
    console.print("[cyan]🎯 TikTok Comment Button Coordinate Finder[/cyan]\n")

    width, height = get_screen_size()
    console.print(f"[yellow]Screen size: {width}x{height}[/yellow]\n")

    console.print("[yellow]Instructions:[/yellow]")
    console.print("1. Make sure TikTok is open and showing a video on For You feed")
    console.print("2. This script will tap different locations on the RIGHT SIDE")
    console.print("3. Find which one opens the comment section\n")

    input("[cyan]Press Enter when TikTok is ready...[/cyan]")

    # Take initial screenshot
    take_screenshot("initial")

    # Test different Y positions on the right side
    x_right = int(width * 0.95)  # Far right edge

    test_positions = [
        ("Top Right", int(height * 0.45)),
        ("Upper Middle Right", int(height * 0.55)),
        ("Middle Right", int(height * 0.60)),
        ("Lower Middle Right", int(height * 0.65)),
        ("Lower Right", int(height * 0.70)),
        ("Bottom Right", int(height * 0.75)),
    ]

    for i, (name, y_pos) in enumerate(test_positions, 1):
        console.print(f"\n[yellow]Test {i}: {name} - ({x_right}, {y_pos})[/yellow]")
        console.print("[dim]Will tap in 2 seconds...[/dim]")
        time.sleep(2)

        tap(x_right, y_pos)
        time.sleep(2)

        screenshot_name = f"test_{i}_{name.lower().replace(' ', '_')}"
        take_screenshot(screenshot_name)

        console.print(f"[cyan]Did this open the comment section? Check: data/{screenshot_name}.png[/cyan]")

        response = input("[yellow]Did it work? (y/n) or 'q' to quit: [/yellow]").lower()

        if response == 'y':
            console.print(f"\n[green]✓ Found it! Correct coordinates:[/green]")
            console.print(f"[green]X: {x_right} ({x_right/width:.2%} of width)[/green]")
            console.print(f"[green]Y: {y_pos} ({y_pos/height:.2%} of height)[/green]")

            console.print(f"\n[cyan]Update the code with:[/cyan]")
            console.print(f"comment_icon_x = int(width * {x_right/width:.3f})")
            console.print(f"comment_icon_y = int(height * {y_pos/height:.3f})")
            return
        elif response == 'q':
            console.print("[yellow]Quitting...[/yellow]")
            return

        # Go back if something else opened
        console.print("[dim]Pressing back button...[/dim]")
        subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_BACK"])
        time.sleep(2)

    console.print("\n[yellow]Finished all tests. Check the screenshots in data/ folder.[/yellow]")
    console.print("[yellow]The comment button should be one of these positions.[/yellow]")

if __name__ == "__main__":
    main()
