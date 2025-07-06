from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",               # Load environment variables from .env file (if present)
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Backend URL for GenAI AgentOS
    # 🔁 You can override this with an environment variable or use the default below.
    CLI_BACKEND_ORIGIN_URL: str = Field(
        default="http://localhost:5000",  # Default: local server (good for dev/testing)
        description="Base URL of the GenAI AgentOS backend (no trailing slash)"
    )

    @field_validator("CLI_BACKEND_ORIGIN_URL")
    def no_trailing_slash(cls, v: str):
        if v.endswith("/"):
            raise ValueError(
                "'CLI_BACKEND_ORIGIN_URL' must not end with a slash (remove trailing slash)."
            )
        return v

@lru_cache(maxsize=None)
def get_settings():
    return Settings()
