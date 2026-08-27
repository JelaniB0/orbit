"""Application configuration loaded from the environment."""

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings for the Orbit API."""

    app_name: str = "Orbit"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings from Orbit-prefixed environment variables."""
        return cls(app_name=os.getenv("ORBIT_APP_NAME", "Orbit"))

