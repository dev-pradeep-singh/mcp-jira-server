# mcp-jira-server

An [MCP](https://modelcontextprotocol.io) server that gives AI assistants (Claude Desktop, Claude Code, etc.) access to Jira Cloud, built on the official [`jira`](https://pypi.org/project/jira/) Python library.

## Tools

| Tool | Description |
| --- | --- |
| `search_issues` | Search issues with JQL |
| `get_issue` | Get full details of an issue |
| `create_issue` | Create a new issue |
| `update_issue` | Update fields on an issue |
| `delete_issue` | Delete an issue |
| `add_comment` | Add a comment to an issue |
| `get_comments` | List comments on an issue |
| `list_transitions` | List available workflow transitions for an issue |
| `transition_issue` | Move an issue through its workflow |
| `assign_issue` | Assign (or unassign) an issue |
| `list_projects` | List visible projects |
| `get_issue_types` | List issue types, globally or per-project |
| `get_current_user` | Get the authenticated user's profile |

## Setup

1. Install dependencies (Python 3.10+):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. Create a Jira Personal Access Token (PAT) in your Jira instance.

3. Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

  ```
  JIRA_URL=https://your-domain.atlassian.net/jira
  JIRA_PAT_TOKEN=your-pat-token
  ```

  Note: for this server setup, include `/jira` at the end of `JIRA_URL`.

4. Run the server directly to sanity-check it starts:

   ```bash
   mcp-jira-server
   ```

   (It communicates over stdio and expects an MCP client on the other end, so it will
   just sit waiting for input — Ctrl+C to stop.)

## Using with Claude Code

Claude Code auto-detects a `.mcp.json` file at the project root. Copy the template
and fill in your own values:

```bash
cp .mcp.json.example .mcp.json
```

```json
{
  "mcpServers": {
    "jira": {
      "command": "/absolute/path/to/mcp-jira-server/.venv/bin/mcp-jira-server",
      "args": [],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net/jira",
        "JIRA_PAT_TOKEN": "your-pat-token"
      }
    }
  }
}
```

`.mcp.json` is gitignored because it holds a real PAT token — only
`.mcp.json.example` (no secrets) is meant to be committed. Reload the Claude Code
window after adding/editing it, then run `/mcp` in a chat to confirm the `jira`
server connected.

Alternatively, register it via the CLI instead of hand-editing the file:

```bash
claude mcp add jira \
  -e JIRA_URL=https://your-domain.atlassian.net/jira \
  -e JIRA_PAT_TOKEN=your-pat-token \
  -- /absolute/path/to/mcp-jira-server/.venv/bin/mcp-jira-server
```

## Using with Claude Desktop

Add the same `mcpServers` block shown above to `claude_desktop_config.json`.

## Notes

- Authentication uses Jira PAT token auth.
- `assignee` fields accept either an Atlassian account ID or an email address.
- `additional_fields` on `create_issue` and the raw `fields` dict on `update_issue`
  let you pass any Jira field (including custom fields) that isn't otherwise exposed.
