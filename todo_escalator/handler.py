import logging
import os
from datetime import datetime, date

from todoist_api_python.api import TodoistAPI

from todo_escalator.utilities import Priority

API_TOKEN = os.getenv("API_TOKEN")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def escalate_task(api: TodoistAPI, task_id: str) -> None:
    """
    Raise priority level of tasks with the "@escalate" label.

    :param api: TodoistAPI
    :param task_id: id of a task
    """
    task_obj = api.get_task(task_id=task_id)
    task_date = datetime.strptime(task_obj.due.date, "%Y-%m-%d").date()
    priority_level = task_obj.priority
    if task_date == date.today():
        log.info(f"Parsing task with date: {task_date}, priority_level: {priority_level}.")
        if priority_level < Priority.red:
            priority_level += 1
        api.update_task(task_id=task_id, priority=priority_level)
        print(f"Update task \"{task_obj.content}\" to priority {priority_level}.")


def lambda_handler(event=None, context=None):
    try:
        log.info("Connecting to API...")
        api = TodoistAPI(API_TOKEN)
        log.info("Connected.")
        tasks = api.get_tasks(label="escalate")
        log.info(f"{len(tasks)} tasks to escalate.")
        for task in tasks:
            escalate_task(api, task.id)
    except Exception as error:
        print(error)

    current_time = datetime.now().time()
    name = context.function_name
    log.info("Your cron function " + name + " ran at " + str(current_time))

    return {
        "status_code": 200
    }


if __name__ == "__main__":
    lambda_handler()
