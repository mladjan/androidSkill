"""Configuration management using environment variables."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
BROWSER_PROFILES_DIR = DATA_DIR / "browser_profiles"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
BROWSER_PROFILES_DIR.mkdir(exist_ok=True)


class Config:
    """Application configuration."""

    # AI Configuration (OpenRouter or OpenAI)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

    # Bot Configuration
    COMMENTS_PER_DAY: int = int(os.getenv("COMMENTS_PER_DAY", "10"))
    MIN_DELAY_MINUTES: int = int(os.getenv("MIN_DELAY_MINUTES", "30"))
    MAX_DELAY_MINUTES: int = int(os.getenv("MAX_DELAY_MINUTES", "90"))

    # Bot Behavior
    SCROLL_TIME_MIN: int = int(os.getenv("SCROLL_TIME_MIN", "10"))
    SCROLL_TIME_MAX: int = int(os.getenv("SCROLL_TIME_MAX", "30"))
    TYPING_SPEED_WPM: int = int(os.getenv("TYPING_SPEED_WPM", "60"))

    # Security
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = BASE_DIR / os.getenv("LOG_FILE", "data/logs/bot.log")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/database.db")

    # Browser
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

    # CAPTCHA Solving
    SADCAPTCHA_API_KEY: Optional[str] = os.getenv("SADCAPTCHA_API_KEY", "")

    @classmethod
    def generate_encryption_key(cls) -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()

    @classmethod
    def get_or_create_encryption_key(cls) -> str:
        """Get existing encryption key or create a new one."""
        if cls.ENCRYPTION_KEY:
            return cls.ENCRYPTION_KEY

        # Generate new key and save to .env
        new_key = cls.generate_encryption_key()
        env_file = BASE_DIR / ".env"

        if env_file.exists():
            with open(env_file, "a") as f:
                f.write(f"\nENCRYPTION_KEY={new_key}\n")
        else:
            with open(env_file, "w") as f:
                f.write(f"ENCRYPTION_KEY={new_key}\n")

        cls.ENCRYPTION_KEY = new_key
        return new_key

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set. Run: python main.py config set-openai-key <key>")

        if cls.COMMENTS_PER_DAY < 1 or cls.COMMENTS_PER_DAY > 50:
            errors.append("COMMENTS_PER_DAY must be between 1 and 50")

        if cls.MIN_DELAY_MINUTES < 1:
            errors.append("MIN_DELAY_MINUTES must be at least 1")

        if cls.MAX_DELAY_MINUTES <= cls.MIN_DELAY_MINUTES:
            errors.append("MAX_DELAY_MINUTES must be greater than MIN_DELAY_MINUTES")

        return errors


# Initialize config
config = Config()
