from django.db import migrations, models
import django.db.models.deletion


TEAM_ASSIGNMENT = {
    'devices': ('Circuit', '#2196F3'),
    'networks': ('Signal', '#4CAF50'),
    'security': ('Cipher', '#9C27B0'),
    'software_ai': ('Code', '#FF9800'),
}


def seed_teams(apps, schema_editor):
    Team = apps.get_model('cards', 'Team')
    Card = apps.get_model('cards', 'Card')

    teams = {}
    for slug, (name, color) in TEAM_ASSIGNMENT.items():
        team, _ = Team.objects.get_or_create(name=name, defaults={'color': color})
        teams[slug] = team

    for slug, team in teams.items():
        Card.objects.filter(slug=slug).update(team=team)


def reverse_teams(apps, schema_editor):
    Card = apps.get_model('cards', 'Card')
    Team = apps.get_model('cards', 'Team')
    Card.objects.all().update(team=None)
    Team.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0006_gamesettings_intrusion_applied'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('color', models.CharField(max_length=7)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='card',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cards', to='cards.team'),
        ),
        migrations.RunPython(seed_teams, reverse_teams),
    ]
