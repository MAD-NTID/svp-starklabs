import yaml
from pathlib import Path

import django.db.models.deletion
from django.db import migrations, models


def seed_card_statuses(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    CardStatus = apps.get_model('cards', 'CardStatus')

    yaml_path = Path(__file__).resolve().parent.parent / 'tasks.yaml'
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    status_sets = {
        'devices': ['Everything is Operational', 'Operational', 'Offline', 'Maintenance', 'Unknown'],
        'networks': ['Everything is Operational', 'Connected', 'Disrupted', 'Unknown'],
        'security': ['Everything is Operational', 'Protected', 'Compromised', 'Unknown'],
        'software_ai': ['Everything is Operational', 'Online', 'Partial Online', 'Malfunctioning', 'Unknown'],
    }

    for slug, names in status_sets.items():
        try:
            card = Card.objects.get(slug=slug)
        except Card.DoesNotExist:
            continue
        for name in names:
            CardStatus.objects.get_or_create(card=card, name=name)


def backfill_status_fk(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    CardStatus = apps.get_model('cards', 'CardStatus')
    CurrentStatus = apps.get_model('cards', 'CurrentStatus')

    for cs in CurrentStatus.objects.all():
        old_status = cs.status
        if isinstance(old_status, str) and old_status:
            status_obj = CardStatus.objects.filter(card=cs.card, name=old_status).first()
            if not status_obj:
                status_obj = CardStatus.objects.get(card=cs.card, name='Unknown')
        else:
            status_obj = CardStatus.objects.get(card=cs.card, name='Unknown')
        CurrentStatus.objects.filter(id=cs.id).update(status_fk_id=status_obj.id)


def reverse_seed(apps, schema_editor):
    CardStatus = apps.get_model('cards', 'CardStatus')
    CardStatus.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_seed_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='cards.card')),
            ],
            options={
                'unique_together': {('card', 'name')},
            },
        ),
        migrations.RunPython(seed_card_statuses, reverse_seed),
        migrations.RemoveField(
            model_name='gamesettings',
            name='countdown_start',
        ),
        migrations.RemoveField(
            model_name='gamesettings',
            name='is_running',
        ),
        migrations.AddField(
            model_name='gamesettings',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Add FK column alongside old CharField
        migrations.AddField(
            model_name='currentstatus',
            name='status_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='cards.cardstatus'),
        ),
        # Backfill from old status text
        migrations.RunPython(backfill_status_fk, migrations.RunPython.noop),
        # Remove old CharField
        migrations.RemoveField(
            model_name='currentstatus',
            name='status',
        ),
        # Rename FK to the original name
        migrations.RenameField(
            model_name='currentstatus',
            old_name='status_fk',
            new_name='status',
        ),
    ]
