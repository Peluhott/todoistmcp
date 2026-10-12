# Todoist MCP Server

An MCP server that lets Claude read and manage your Todoist tasks.

## Tools

| Tool | What it does |
|---|---|
| `list_projects` | Lists your projects and their IDs |
| `read_project_tasks` | Gets all open tasks in a project |
| `read_tasks` | Finds tasks with a Todoist filter, e.g. `today \| overdue` |
| `add_task` | Adds a task |
| `add_multiple_tasks` | Adds several tasks at once |
| `update_task` | Changes a task's text, due date, priority or notes |
| `mark_complete` | Completes one or more tasks |

## Setup

1. Install [uv](https://docs.astral.sh/uv/):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Clone the repo and install the packages:
   ```bash
   git clone <repo-url> todoistmcp
   cd todoistmcp
   uv sync
   ```
3. Add your Todoist API token. You can find it in Todoist under **Settings → Integrations → Developer**.
   ```bash
   cp .env.example .env
   # then edit .env: TODOIST_API_TOKEN=your-token
   ```
4. Add the server to Claude Code:
   ```bash
   claude mcp add todoist -s user -- uv run --directory /full/path/to/todoistmcp todoistmcp
   ```
5. Restart Claude and ask something like *"what's on my Todoist today?"*
