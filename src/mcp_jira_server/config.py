import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class JiraConfig:
    url: str
    pat_token: str

    @classmethod
    def from_env(cls) -> "JiraConfig":
        url = os.environ.get("JIRA_URL", "").rstrip("/")
        pat_token = os.environ.get("JIRA_PAT_TOKEN", "")

        missing = [
            name
            for name, value in (
                ("JIRA_URL", url),
                ("JIRA_PAT_TOKEN", pat_token),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): "
                f"{', '.join(missing)}. Set them in your environment or a .env file."
            )

        return cls(url=url, pat_token=pat_token)
