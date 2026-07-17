from typing import Any

from jira import JIRAError
from mcp.server.fastmcp import FastMCP

from .client import get_client
from .formatting import comment_to_dict, issue_to_dict, transition_to_dict

mcp = FastMCP(
    "jira",
    instructions=(
        "Tools for managing Jira issues: searching with JQL, reading, creating, "
        "updating, transitioning, commenting on, assigning, and deleting issues, "
        "plus looking up projects and issue types."
    ),
)


def _wrap_jira_error(action: str, error: JIRAError) -> RuntimeError:
    detail = "; ".join(error.response.json().get("errorMessages", [])) if error.response is not None else str(error)
    extra_errors = error.response.json().get("errors") if error.response is not None else None
    if extra_errors:
        detail = f"{detail} {extra_errors}".strip()
    return RuntimeError(f"Failed to {action}: {detail or error.text}")


@mcp.tool()
def search_issues(jql: str, max_results: int = 50, start_at: int = 0) -> dict:
    """Search Jira issues using JQL (Jira Query Language).

    Example jql: 'project = ABC AND status = "In Progress" ORDER BY updated DESC'
    """
    client = get_client()
    try:
        issues = client.search_issues(jql, startAt=start_at, maxResults=max_results)
    except JIRAError as e:
        raise _wrap_jira_error("search issues", e) from e
    return {
        "total": issues.total,
        "start_at": start_at,
        "count": len(issues),
        "issues": [issue_to_dict(issue) for issue in issues],
    }


@mcp.tool()
def get_issue(issue_key: str) -> dict:
    """Get the full details of a single Jira issue by its key (e.g. 'ABC-123')."""
    client = get_client()
    try:
        issue = client.issue(issue_key)
    except JIRAError as e:
        raise _wrap_jira_error(f"get issue {issue_key}", e) from e
    return issue_to_dict(issue)


@mcp.tool()
def create_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
    labels: list[str] | None = None,
    parent_key: str | None = None,
    additional_fields: dict[str, Any] | None = None,
) -> dict:
    """Create a new Jira issue.

    - project_key: key of the project the issue belongs to (e.g. 'ABC').
    - issue_type: name of the issue type (e.g. 'Task', 'Bug', 'Story', 'Subtask').
    - assignee: account ID or email of the assignee, if known.
    - parent_key: parent issue key, required when issue_type is a subtask.
    - additional_fields: any extra Jira fields (including custom fields) to set,
      keyed by field id, merged into the create request as-is.
    """
    client = get_client()
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
    if description is not None:
        fields["description"] = description
    if priority is not None:
        fields["priority"] = {"name": priority}
    if assignee is not None:
        fields["assignee"] = {"accountId": assignee} if "@" not in assignee else {"emailAddress": assignee}
    if labels is not None:
        fields["labels"] = labels
    if parent_key is not None:
        fields["parent"] = {"key": parent_key}
    if additional_fields:
        fields.update(additional_fields)

    try:
        issue = client.create_issue(fields=fields)
    except JIRAError as e:
        raise _wrap_jira_error("create issue", e) from e
    return issue_to_dict(issue)


@mcp.tool()
def update_issue(issue_key: str, fields: dict[str, Any]) -> str:
    """Update fields on an existing Jira issue.

    'fields' is a raw Jira fields dict, e.g. {"summary": "New summary"} or
    {"description": "New description", "priority": {"name": "High"}}.
    """
    client = get_client()
    try:
        issue = client.issue(issue_key)
        issue.update(fields=fields)
    except JIRAError as e:
        raise _wrap_jira_error(f"update issue {issue_key}", e) from e
    return f"Updated {issue_key}"


@mcp.tool()
def delete_issue(issue_key: str) -> str:
    """Permanently delete a Jira issue by its key. This cannot be undone."""
    client = get_client()
    try:
        issue = client.issue(issue_key)
        issue.delete()
    except JIRAError as e:
        raise _wrap_jira_error(f"delete issue {issue_key}", e) from e
    return f"Deleted {issue_key}"


@mcp.tool()
def add_comment(issue_key: str, comment: str) -> dict:
    """Add a comment to a Jira issue."""
    client = get_client()
    try:
        result = client.add_comment(issue_key, comment)
    except JIRAError as e:
        raise _wrap_jira_error(f"add comment to {issue_key}", e) from e
    return comment_to_dict(result)


@mcp.tool()
def get_comments(issue_key: str) -> list[dict]:
    """Get all comments on a Jira issue."""
    client = get_client()
    try:
        comments = client.comments(issue_key)
    except JIRAError as e:
        raise _wrap_jira_error(f"get comments for {issue_key}", e) from e
    return [comment_to_dict(c) for c in comments]


@mcp.tool()
def list_transitions(issue_key: str) -> list[dict]:
    """List the workflow transitions currently available for a Jira issue."""
    client = get_client()
    try:
        transitions = client.transitions(issue_key)
    except JIRAError as e:
        raise _wrap_jira_error(f"list transitions for {issue_key}", e) from e
    return [transition_to_dict(t) for t in transitions]


@mcp.tool()
def transition_issue(issue_key: str, transition: str, comment: str | None = None) -> str:
    """Move a Jira issue through its workflow (e.g. 'Done', 'In Progress').

    'transition' may be either a transition id or its display name, as
    returned by list_transitions.
    """
    client = get_client()
    try:
        available = {t["name"].lower(): t["id"] for t in client.transitions(issue_key)}
        transition_id = available.get(transition.lower(), transition)
        kwargs = {"comment": comment} if comment else {}
        client.transition_issue(issue_key, transition_id, **kwargs)
    except JIRAError as e:
        raise _wrap_jira_error(f"transition {issue_key}", e) from e
    return f"Transitioned {issue_key} to '{transition}'"


@mcp.tool()
def assign_issue(issue_key: str, assignee: str | None) -> str:
    """Assign a Jira issue to a user (account ID or email), or pass null to unassign."""
    client = get_client()
    try:
        client.assign_issue(issue_key, assignee)
    except JIRAError as e:
        raise _wrap_jira_error(f"assign {issue_key}", e) from e
    return f"Assigned {issue_key} to {assignee}" if assignee else f"Unassigned {issue_key}"


@mcp.tool()
def list_projects() -> list[dict]:
    """List all Jira projects visible to the authenticated user."""
    client = get_client()
    try:
        projects = client.projects()
    except JIRAError as e:
        raise _wrap_jira_error("list projects", e) from e
    return [{"key": p.key, "name": p.name, "id": p.id} for p in projects]


@mcp.tool()
def get_issue_types(project_key: str | None = None) -> list[dict]:
    """List available issue types, optionally scoped to a specific project."""
    client = get_client()
    try:
        if project_key:
            project = client.project(project_key)
            types = project.issueTypes
        else:
            types = client.issue_types()
    except JIRAError as e:
        raise _wrap_jira_error("get issue types", e) from e
    return [{"id": t.id, "name": t.name, "subtask": getattr(t, "subtask", False)} for t in types]


@mcp.tool()
def get_current_user() -> dict:
    """Get the Jira user profile for the authenticated account (useful to confirm auth is working)."""
    client = get_client()
    try:
        me = client.myself()
    except JIRAError as e:
        raise _wrap_jira_error("get current user", e) from e
    return {
        "account_id": me.get("accountId"),
        "email": me.get("emailAddress"),
        "display_name": me.get("displayName"),
        "active": me.get("active"),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
