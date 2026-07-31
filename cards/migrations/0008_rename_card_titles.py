from django.db import migrations


TITLE_RENAMES = {
    'devices': ('Devices', 'Hardware & IT'),
    'networks': ('Networks', 'Networking'),
    'security': ('Security', 'Cybersecurity'),
}


def rename_titles(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    for slug, (old, new) in TITLE_RENAMES.items():
        Card.objects.filter(slug=slug, title=old).update(title=new)


def reverse_titles(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    for slug, (old, new) in TITLE_RENAMES.items():
        Card.objects.filter(slug=slug, title=new).update(title=old)


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0007_teams'),
    ]

    operations = [
        migrations.RunPython(rename_titles, reverse_titles),
    ]
