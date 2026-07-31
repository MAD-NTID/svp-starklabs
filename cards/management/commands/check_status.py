import os
import sys
import socket
import subprocess
from pathlib import Path

import yaml
from django.core.management.base import BaseCommand
from django.utils import timezone as tz

from cards.models import Card, CardStatus, CurrentStatus, GameSettings

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
    yaml_path = Path(__file__).resolve().parent.parent.parent / 'tasks.yaml'
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


class Command(BaseCommand):
    help = 'Check task statuses and update dashboard cards'

    def handle(self, *args, **options):
        config = load_yaml()

        if 'countdown_minutes' in config:
            GameSettings.objects.update_or_create(
                id=1,
                defaults={'countdown_minutes': config['countdown_minutes']},
            )

        card_configs = config.get('cards', {})

        for slug, cfg in card_configs.items():
            tasks = cfg.get('tasks', [])
            statuses_map = cfg.get('statuses', {})
            num_tasks = len(tasks)

            card, _ = Card.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': cfg['title'],
                    'icon': cfg['icon'],
                    'order': list(card_configs.keys()).index(slug),
                }
            )

            try:
                current = CurrentStatus.objects.get(card=card)
            except CurrentStatus.DoesNotExist:
                current = CurrentStatus(card=card)

            if current.manual_override or (current.status and current.status.name == 'Maintenance'):
                self.stdout.write(f"  Skipping {slug} (manual override or maintenance)")
                continue

            completed = 0
            for task in tasks:
                host = task['host']
                task_type = task.get('type', 'ping')
                port = task.get('port')

                if task_type == 'port' and port:
                    result = check_port(host, port)
                else:
                    result = check_ping(host)

                if result:
                    completed += 1
                self.stdout.write(f"  {task['id']}: {host} -> {'OK' if result else 'FAIL'}")

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

            self.stdout.write(f" {slug}: {status_name} ({completed}/{num_tasks})")

        self.stdout.write(self.style.SUCCESS('Status check complete'))
