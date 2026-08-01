from django.core.management.base import BaseCommand

from cards.models import Card, CurrentStatus, GameSettings, TaskCheck
from cards.status_utils import (
    check_ping,
    check_port,
    load_yaml,
    sync_manual_task_rows,
    update_card_progress,
)


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
                sync_manual_task_rows(card, tasks)
                continue

            for task in tasks:
                task_type = task.get('type', 'ping')

                if task_type == 'manual':
                    TaskCheck.objects.update_or_create(
                        card=card,
                        task_id=task['id'],
                        defaults={
                            'title': task.get('title', task['id']),
                            'host': task.get('host', ''),
                            'is_manual': True,
                            'result': False,
                        },
                    )
                    self.stdout.write(f"  {task['id']}: manual (instructor check)")
                    continue

                host = task.get('host', '')
                port = task.get('port')

                if task_type == 'port' and port:
                    result = check_port(host, port)
                else:
                    result = check_ping(host)

                TaskCheck.objects.update_or_create(
                    card=card,
                    task_id=task['id'],
                    defaults={
                        'title': task.get('title', task['id']),
                        'host': host,
                        'result': result,
                    },
                )
                self.stdout.write(f"  {task['id']}: {host} -> {'OK' if result else 'FAIL'}")

            completed, _, status_name = update_card_progress(card, config)
            self.stdout.write(f" {slug}: {status_name} ({completed}/{num_tasks})")

        self.stdout.write(self.style.SUCCESS('Status check complete'))
