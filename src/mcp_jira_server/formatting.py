from typing import Any


def _user_name(user: Any) -> str | None:
    if user is None:
        return None
    return getattr(user, "displayName", None) or getattr(user, "name", None)


def issue_to_dict(issue: Any) -> dict:
    fields = issue.fields
    return {
        "key": issue.key,
        "url": issue.permalink() if hasattr(issue, "permalink") else None,
        "summary": getattr(fields, "summary", None),
        "description": getattr(fields, "description", None),
        "status": getattr(fields.status, "name", None) if getattr(fields, "status", None) else None,
        "issue_type": getattr(fields.issuetype, "name", None) if getattr(fields, "issuetype", None) else None,
        "priority": getattr(fields.priority, "name", None) if getattr(fields, "priority", None) else None,
        "project": getattr(fields.project, "key", None) if getattr(fields, "project", None) else None,
        "assignee": _user_name(getattr(fields, "assignee", None)),
        "reporter": _user_name(getattr(fields, "reporter", None)),
        "labels": list(getattr(fields, "labels", []) or []),
        "created": getattr(fields, "created", None),
        "updated": getattr(fields, "updated", None),
    }


def comment_to_dict(comment: Any) -> dict:
    return {
        "id": comment.id,
        "author": _user_name(getattr(comment, "author", None)),
        "body": comment.body,
        "created": comment.created,
        "updated": getattr(comment, "updated", None),
    }


def transition_to_dict(transition: dict) -> dict:
    return {
        "id": transition["id"],
        "name": transition["name"],
        "to_status": transition.get("to", {}).get("name"),
    }
