"""Utility functions for encryption, timing, and helpers."""

import random
import time
from datetime import datetime, timedelta
from typing import Optional

from cryptography.fernet import Fernet

from src.config import config


class EncryptionHelper:
    """Helper class for encrypting and decrypting sensitive data."""

    def __init__(self):
        """Initialize with encryption key from config."""
        key = config.get_or_create_encryption_key()
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> bytes:
        """Encrypt a string and return bytes."""
        return self.cipher.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt bytes and return string."""
        return self.cipher.decrypt(encrypted_data).decode()


class TimingHelper:
    """Helper class for human-like timing and delays."""

    @staticmethod
    def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """Sleep for a random duration between min and max seconds."""
        time.sleep(random.uniform(min_seconds, max_seconds))

    @staticmethod
    def typing_delay(text: str, wpm: Optional[int] = None) -> float:
        """Calculate realistic typing delay for given text."""
        if wpm is None:
            wpm = config.TYPING_SPEED_WPM

        # Average word length is 5 characters
        characters_per_minute = wpm * 5
        characters_per_second = characters_per_minute / 60

        # Calculate base time
        base_time = len(text) / characters_per_second

        # Add random variance (±20%)
        variance = base_time * 0.2
        return base_time + random.uniform(-variance, variance)

    @staticmethod
    def calculate_next_run(comments_today: int, target_per_day: int) -> Optional[datetime]:
        """Calculate when the agent should run next."""
        if comments_today >= target_per_day:
            # Hit daily limit, schedule for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.replace(hour=random.randint(8, 10), minute=random.randint(0, 59), second=0)

        # Calculate remaining comments and time
        remaining_comments = target_per_day - comments_today
        now = datetime.now()
        end_of_day = now.replace(hour=23, minute=59, second=59)
        remaining_seconds = (end_of_day - now).total_seconds()

        # Distribute remaining comments
        if remaining_seconds > 0:
            average_interval = remaining_seconds / remaining_comments
            # Add randomness (50% to 150% of average)
            next_interval = average_interval * random.uniform(0.5, 1.5)
            next_run = now + timedelta(seconds=next_interval)

            # Ensure minimum delay
            min_delay = timedelta(minutes=config.MIN_DELAY_MINUTES)
            if next_run - now < min_delay:
                next_run = now + min_delay

            return next_run

        return None

    @staticmethod
    def human_scroll_time() -> float:
        """Get random scroll time to appear human-like."""
        return random.uniform(config.SCROLL_TIME_MIN, config.SCROLL_TIME_MAX)


# Singleton instances
encryption = EncryptionHelper()
timing = TimingHelper()
