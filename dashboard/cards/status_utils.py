import socket
import subprocess
import sys
from pathlib import Path

import yaml
from django.utils import timezone as tz

from cards.models import CardStatus, CurrentStatus, TaskCheck

YAML_PATH = Path(__file__).resolve().parent / 'tasks.yaml'

TIMEOUT = 3


def check_ping(host):
    try:
        if sys.platform == "win32":
            cmd = ["ping", "-n", "1", "-w", str(TIMEOUT * 1000), host]
        else:
            cmd = ["ping", "-c", "1", "-W", str(TIMEOUT), host]
        result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT + 2)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def check_port(host, port):
    try:
        sock = socket.create_connection((host, port), timeout=TIMEOUT)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def load_yaml():
    with open(YAML_PATH, 'r') as f:
        return yaml.safe_load(f)


def sync_manual_task_rows(card, tasks):
    """Create TaskCheck rows for manual tasks, never touching existing rows."""
    for task in tasks:
        if task.get('type') == 'manual':
            TaskCheck.objects.get_or_create(
                card=card,
                task_id=task['id'],
                defaults={
                    'title': task.get('title', task['id']),
                    'host': task.get('host', ''),
                    'is_manual': True,
                    'result': False,
                    'manual_complete': False,
                },
            )


def update_card_progress(card, config=None):
    """Recompute a card's tasks_completed/tasks_total/status from stored TaskCheck rows.

    Returns (completed, num_tasks, status_name).
    """
    if config is None:
        config = load_yaml()

    cfg = config.get('cards', {}).get(card.slug, {})
    tasks = cfg.get('tasks', [])
    statuses_map = cfg.get('statuses', {})
    num_tasks = len(tasks)

    sync_manual_task_rows(card, tasks)

    current_task_ids = [t['id'] for t in tasks]
    if tasks:
        TaskCheck.objects.filter(card=card).exclude(task_id__in=current_task_ids).delete()

    checks = {tc.task_id: tc for tc in TaskCheck.objects.filter(card=card)}

    completed = 0
    for task in tasks:
        tc = checks.get(task['id'])
        if tc is None:
            continue
        if tc.is_manual:
            if tc.manual_complete:
                completed += 1
        elif tc.result:
            completed += 1

    current, _ = CurrentStatus.objects.get_or_create(card=card)
    current.tasks_total = num_tasks
    current.tasks_completed = completed

    if completed == num_tasks:
        status_name = statuses_map.get('all_complete', 'Online')
    elif completed == 0 or 'partial' not in statuses_map:
        status_name = statuses_map.get('none_complete', 'Offline')
    else:
        status_name = statuses_map['partial']

    status_obj, _ = CardStatus.objects.get_or_create(card=card, name=status_name)
    current.status = status_obj
    current.updated_at = tz.now()
    current.save()

    return completed, num_tasks, status_name
