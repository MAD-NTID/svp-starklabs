from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Card(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class CardStatus(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='statuses')
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('card', 'name')

    def __str__(self):
        return self.name


class CurrentStatus(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name='current_status')
    status = models.ForeignKey(CardStatus, on_delete=models.PROTECT, null=True)
    tasks_completed = models.IntegerField(default=0)
    tasks_total = models.IntegerField(default=0)
    manual_override = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.card.title}: {self.status.name if self.status else 'None'}"


class GameSettings(models.Model):
    countdown_minutes = models.IntegerField(default=60)
    start_time = models.DateTimeField(null=True, blank=True)
    intrusion_time = models.DateTimeField(null=True, blank=True)
    mission_accomplished = models.BooleanField(default=False)
    intrusion_applied = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Game Settings"

    def __str__(self):
        return f"Countdown: {self.countdown_minutes}min, Intrusion: {self.intrusion_time}"
