"""Environment-backed API configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    cors_origins: tuple[str, ...]
    ncbi_api_key: str | None
    ncbi_email: str

    @classmethod
    def from_environment(cls) -> Settings:
        origins = tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3001").split(",")
            if origin.strip()
        )
        return cls(
            environment=os.getenv("API_ENV", "development"),
            cors_origins=origins,
            ncbi_api_key=os.getenv("NCBI_API_KEY") or None,
            ncbi_email=os.getenv("NCBI_EMAIL", "developers@neurogenesis.ai"),
        )
