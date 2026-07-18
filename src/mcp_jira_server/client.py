from functools import lru_cache

from jira import JIRA, JIRAError

from .config import JiraConfig


@lru_cache(maxsize=1)
def get_client() -> JIRA:
    config = JiraConfig.from_env()
    try:
        return JIRA(server=config.url, token_auth=config.pat_token)
    except JIRAError as e:
        detail = e.response.json().get("errorMessage", e.text) if e.response is not None else str(e)
        raise RuntimeError(
            f"Failed to connect to Jira at {config.url}: {detail}. "
            "Check JIRA_URL and JIRA_PAT_TOKEN."
        ) from e
