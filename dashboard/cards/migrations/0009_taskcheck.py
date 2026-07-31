from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0008_rename_card_titles'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('host', models.CharField(max_length=255)),
                ('result', models.BooleanField(default=False)),
                ('checked_at', models.DateTimeField(auto_now=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_checks', to='cards.card')),
            ],
            options={
                'ordering': ['task_id'],
                'unique_together': {('card', 'task_id')},
            },
        ),
    ]
