"""Stealth and anti-detection utilities for browser automation."""

import random
from typing import Dict, Any
from playwright.sync_api import Page, BrowserContext


def get_stealth_config() -> Dict[str, Any]:
    """Get randomized browser configuration for stealth.

    Returns:
        Dict with viewport, user agent, locale, timezone
    """
    # Randomize viewport to appear more human-like
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
    ]

    # Realistic user agents (recent Chrome on macOS)
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    ]

    locales = ["en-US", "en-GB", "en-CA"]
    timezones = ["America/New_York", "America/Los_Angeles", "America/Chicago"]

    return {
        "viewport": random.choice(viewports),
        "user_agent": random.choice(user_agents),
        "locale": random.choice(locales),
        "timezone_id": random.choice(timezones),
        "has_touch": False,
        "is_mobile": False,
        "color_scheme": "light",
    }


def apply_stealth_scripts(page: Page) -> None:
    """Apply JavaScript-based stealth techniques to hide automation.

    Args:
        page: Playwright page instance
    """
    # Override navigator.webdriver
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    # Mock plugins with realistic Chrome plugins
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                return [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
                        description: "",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin},
                        1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: Plugin},
                        description: "",
                        filename: "internal-nacl-plugin",
                        length: 2,
                        name: "Native Client"
                    }
                ];
            }
        });
    """)

    # Mock languages
    page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)

    # Override Chrome detection
    page.add_init_script("""
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    """)

    # Override permissions
    page.add_init_script("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)

    # Add realistic screen properties
    page.add_init_script("""
        Object.defineProperty(screen, 'colorDepth', {
            get: () => 24
        });
        Object.defineProperty(screen, 'pixelDepth', {
            get: () => 24
        });
    """)

    # Mock hardwareConcurrency
    page.add_init_script("""
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
    """)

    # Override deviceMemory
    page.add_init_script("""
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
    """)


def add_human_behavior(page: Page) -> None:
    """Add random mouse movements and human-like behavior.

    Args:
        page: Playwright page instance
    """
    # Random mouse movement
    page.evaluate("""
        () => {
            setInterval(() => {
                const x = Math.floor(Math.random() * window.innerWidth);
                const y = Math.floor(Math.random() * window.innerHeight);
                const event = new MouseEvent('mousemove', {
                    clientX: x,
                    clientY: y
                });
                document.dispatchEvent(event);
            }, 5000 + Math.random() * 10000);
        }
    """)


def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0) -> float:
    """Get a random delay duration.

    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds

    Returns:
        Random delay duration
    """
    return random.uniform(min_seconds, max_seconds)


def human_scroll(page: Page, direction: str = "down", distance: int = None) -> None:
    """Perform human-like scrolling.

    Args:
        page: Playwright page instance
        direction: 'up' or 'down'
        distance: Scroll distance in pixels (random if None)
    """
    if distance is None:
        distance = random.randint(300, 800)

    if direction == "down":
        distance = abs(distance)
    else:
        distance = -abs(distance)

    # Smooth scroll with random steps
    steps = random.randint(5, 15)
    step_size = distance // steps

    for _ in range(steps):
        page.evaluate(f"window.scrollBy(0, {step_size})")
        page.wait_for_timeout(random.randint(50, 150))
