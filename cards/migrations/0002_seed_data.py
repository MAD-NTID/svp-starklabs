import yaml
from pathlib import Path
from django.db import migrations


def seed_data(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    CurrentStatus = apps.get_model('cards', 'CurrentStatus')
    GameSettings = apps.get_model('cards', 'GameSettings')

    yaml_path = Path(__file__).resolve().parent.parent / 'tasks.yaml'
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    card_configs = config.get('cards', {})
    for order, (slug, cfg) in enumerate(card_configs.items()):
        card, _ = Card.objects.get_or_create(
            slug=slug,
            defaults={
                'title': cfg['title'],
                'icon': cfg['icon'],
                'order': order,
            }
        )
        CurrentStatus.objects.get_or_create(
            card=card,
            defaults={
                'status': 'Unknown',
                'tasks_total': len(cfg.get('tasks', [])),
            }
        )

    GameSettings.objects.get_or_create(
        id=1,
        defaults={'countdown_minutes': config.get('countdown_minutes', 60)}
    )


def reverse_seed(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    CurrentStatus = apps.get_model('cards', 'CurrentStatus')
    GameSettings = apps.get_model('cards', 'GameSettings')
    Card.objects.all().delete()
    CurrentStatus.objects.all().delete()
    GameSettings.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
