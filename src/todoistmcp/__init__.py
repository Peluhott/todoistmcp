from todoist_api_python.api import TodoistAPI
from mcp.server.mcpserver import MCPServer
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
token = os.getenv("TODOIST_API_TOKEN")
api = TodoistAPI(token)
mcp = MCPServer("todoist")

#list projects
@mcp.tool()
def list_projects() -> list[dict]:
    """ Return the list of active projects for the user"""
    projects = []
    for page in api.get_projects():
        for project in page:
            projects.append({"id": project.id, "name": project.name})
    return projects

# turn a Todoist Task into the simple info Claude gets back
def task_to_dict(task) -> dict:
    return {
        "id": task.id,
        "content": task.content,
        "project_id": task.project_id,
        "due": task.due.string if task.due else None,
        "priority": task.priority,
    }

# add a task
@mcp.tool()
def add_task(content: str, project_id: str | None = None, due_string: str | None = None, priority: int | None = None, description: str | None = None) -> dict:
    """Add a new task to Todoist.

    Args:
        content: The task text, e.g. "Buy milk".
        project_id: ID of the project to add it to. Get it from list_projects.
            Leave empty to add the task to the Inbox.
        due_string: When it's due in plain words, e.g. "tomorrow at 5pm", "next friday" or "every monday".
        priority: 1 = normal, 2 = medium, 3 = high, 4 = urgent (4 shows as P1 in the Todoist app).
        description: Extra notes or details for the task.
    """
    task = api.add_task(content=content, project_id=project_id, due_string=due_string, priority=priority, description=description)
    return task_to_dict(task)

# one task in add_multiple_tasks
class NewTask(BaseModel):
    content: str
    project_id: str | None = None
    due_string: str | None = None
    priority: int | None = None
    description: str | None = None

#add multiple task at once
@mcp.tool()
def add_multiple_tasks(tasks: list[NewTask]) -> dict:
    """Add several tasks to Todoist at once.

    Use this instead of calling add_task repeatedly. Each task takes the same fields as add_task.
    Returns the tasks that were added and any that failed, with the error for each failure.
    """
    success = []
    fail = []
    for t in tasks:
        try:
            success.append(add_task(content=t.content, project_id=t.project_id, due_string=t.due_string, priority=t.priority, description=t.description))
        except Exception as e:
            fail.append({"content": t.content, "error": str(e)})
    return {"added": success, "failed": fail}

#read tasks that I have to do 
@mcp.tool()
def read_tasks(query:str) -> list[dict]:
    """Find active tasks using a Todoist filter query.

    Args:
        query: A Todoist filter, NOT plain English. Building blocks:
            - Dates: today, tomorrow, overdue, no date, 7 days, due before: oct 20
            - Project: #Inbox (escape spaces: #My\\ Project)
            - Label: @errands
            - Priority: p1 (urgent) to p4 (normal)
            - Text: search: milk
            Combine with & (and), | (or), ! (not), and ( ) to group.
            Examples:
            - "what's on today" -> today | overdue
            - "this week" -> 7 days
            - "urgent work stuff" -> #Work & p1
    """
    tasks = []
    for page in api.filter_tasks(query=query):
        for task in page:
            tasks.append(task_to_dict(task))
    return tasks

@mcp.tool()
def read_project_tasks(project_id: str) -> list[dict]:
    """Get all active (not completed) tasks in a project.

    Args:
        project_id: ID of the project. Get it from list_projects.
    """
    tasks = []
    for page in api.get_tasks(project_id=project_id):
        for task in page:
            tasks.append(task_to_dict(task))
    return tasks

# update a task
@mcp.tool()
def update_task(task_id: str, content: str | None = None, due_string: str | None = None, priority: int | None = None, description: str | None = None) -> dict:
    """Change an existing task. Only the fields you pass are changed.

    Args:
        task_id: ID of the task. Get it from read_tasks or read_project_tasks.
        content: New task text.
        due_string: New due date in plain words, e.g. "today", "oct 18", "next sunday", "no date".
        priority: 1 = normal, 2 = medium, 3 = high, 4 = urgent (4 shows as P1 in the Todoist app).
        description: New notes or details for the task.
    """
    task = api.update_task(task_id=task_id, content=content, due_string=due_string, priority=priority, description=description)
    return task_to_dict(task)

#mark them as complete
@mcp.tool()
def mark_complete(task_ids: list[str]) -> dict:
    """Mark one or more tasks as complete.

    Get task IDs from read_tasks or read_project_tasks. To complete a single task, pass a list with one ID.
    Repeating tasks (e.g. "every monday") aren't closed; Todoist moves them to their next date.
    Returns the IDs that were completed and any that failed, with the error for each failure.

    Args:
        task_ids: IDs of the tasks to complete.
    """
    completed = []
    failed = []
    for task_id in task_ids:
        try:
            if api.complete_task(task_id=task_id):
                completed.append(task_id)
            else:
                failed.append({"task_id": task_id, "error": "Todoist did not confirm the task was completed"})
        except Exception as e:
            failed.append({"task_id": task_id, "error": str(e)})
    return {"completed": completed, "failed": failed}


def main() -> None:
    mcp.run()
