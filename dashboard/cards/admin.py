from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import AdminSite
from django.utils import timezone as tz
from django.shortcuts import redirect
from .models import Card, CardStatus, CurrentStatus, GameSettings, TaskCheck, Team


STATUS_MAP = {
    'devices': 'Operational',
    'networks': 'Connected',
    'security': 'Protected',
    'software_ai': 'Online',
}

DEFAULT_TEAM_ASSIGNMENT = {
    'devices': 'Circuit',
    'networks': 'Signal',
    'security': 'Cipher',
    'software_ai': 'Code',
}


def _set_all_cards_operational():
    for card in Card.objects.all():
        cs, _ = CurrentStatus.objects.get_or_create(card=card)
        cs.tasks_completed = cs.tasks_total
        cs.manual_override = True
        if card.slug in STATUS_MAP:
            real_status = CardStatus.objects.filter(card=card, name=STATUS_MAP[card.slug]).first()
            if real_status:
                cs.status = real_status
        cs.save()


def _clear_all_overrides():
    CurrentStatus.objects.all().update(manual_override=False, tasks_completed=0)


def _rotate_teams():
    cards = list(Card.objects.filter(team__isnull=False).order_by('order'))
    if len(cards) < 2:
        return
    teams = [c.team for c in cards]
    for i, card in enumerate(cards):
        card.team = teams[i - 1]
        card.save(update_fields=['team'])


def _reset_teams_to_default():
    for slug, team_name in DEFAULT_TEAM_ASSIGNMENT.items():
        team = Team.objects.filter(name=team_name).first()
        Card.objects.filter(slug=slug).update(team=team)


def _start_countdown(obj):
    obj.start_time = tz.now()
    obj.save()
    return 'Countdown started.'


def _reset_countdown(obj):
    obj.start_time = None
    obj.mission_accomplished = False
    obj.intrusion_applied = False
    obj.save()
    _set_all_cards_operational()
    return 'Countdown reset.'


def _trigger_intrusion(obj):
    obj.intrusion_time = tz.now()
    obj.mission_accomplished = False
    obj.intrusion_applied = True
    obj.save()
    _clear_all_overrides()
    return 'Intrusion triggered now.'


def _clear_intrusion(obj):
    obj.intrusion_time = None
    obj.mission_accomplished = False
    obj.intrusion_applied = False
    obj.save()
    _set_all_cards_operational()
    _reset_teams_to_default()
    return 'Intrusion cleared and statuses/teams reset.'


def _simulate_accomplished(obj):
    obj.intrusion_time = tz.now()
    obj.mission_accomplished = True
    obj.intrusion_applied = True
    obj.save()
    _clear_all_overrides()
    for card in Card.objects.all():
        cs, _ = CurrentStatus.objects.get_or_create(card=card)
        cs.tasks_completed = cs.tasks_total
        if card.slug in STATUS_MAP:
            real_status = CardStatus.objects.filter(card=card, name=STATUS_MAP[card.slug]).first()
            if real_status:
                cs.status = real_status
        cs.save()
    return 'Mission Accomplished simulated.'


def _rotate_teams_now(obj):
    _rotate_teams()
    return 'Teams rotated clockwise.'


ACTION_FUNCS = {
    '_start_countdown': _start_countdown,
    '_reset_countdown': _reset_countdown,
    '_trigger_intrusion': _trigger_intrusion,
    '_clear_intrusion': _clear_intrusion,
    '_simulate_accomplished': _simulate_accomplished,
    '_rotate_teams': _rotate_teams_now,
}


class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'team', 'icon', 'order']
    prepopulated_fields = {'slug': ('title',)}


class CurrentStatusAdmin(admin.ModelAdmin):
    list_display = ['card', 'status_name', 'tasks_completed', 'tasks_total', 'manual_override', 'updated_at']
    list_editable = ['manual_override']

    def status_name(self, obj):
        return obj.status.name if obj.status else 'None'
    status_name.short_description = 'Status'
    status_name.admin_order_field = 'status'

    def save_model(self, request, obj, form, change):
        if obj.status:
            if obj.status.name == 'Everything is Operational':
                card_slug = obj.card.slug
                if card_slug in STATUS_MAP:
                    real_status = CardStatus.objects.filter(card=obj.card, name=STATUS_MAP[card_slug]).first()
                    if real_status:
                        obj.status = real_status
                obj.manual_override = True
            elif obj.status.name == 'Maintenance':
                obj.manual_override = True
        super().save_model(request, obj, form, change)


class GameSettingsAdmin(admin.ModelAdmin):
    change_form_template = 'admin/game_settings_change.html'

    def get_fields(self, request, obj=None):
        return ['countdown_minutes', 'start_time', 'intrusion_time']

    def render_change_form(self, request, context, *args, **kwargs):
        context['show_start_button'] = True
        context['show_reset_button'] = True
        context['show_intrusion_now_button'] = True
        context['show_clear_intrusion_button'] = True
        return super().render_change_form(request, context, *args, **kwargs)

    def response_change(self, request, obj):
        for key, func in ACTION_FUNCS.items():
            if key in request.POST:
                self.message_user(request, func(obj), messages.SUCCESS)
                return redirect(request.path)
        return super().response_change(request, obj)


class StarkLabAdminSite(AdminSite):
    index_template = 'admin/starklab_index.html'

    def index(self, request, extra_context=None):
        if request.method == 'POST':
            obj = GameSettings.objects.first()
            if obj:
                for key, func in ACTION_FUNCS.items():
                    if key in request.POST:
                        messages.success(request, func(obj))
                        return redirect('admin:index')
        return super().index(request, extra_context)


admin_site = StarkLabAdminSite(name='admin')
admin_site.register(Card, CardAdmin)
admin_site.register(Team)
admin_site.register(CardStatus)
admin_site.register(CurrentStatus, CurrentStatusAdmin)
admin_site.register(GameSettings, GameSettingsAdmin)
admin_site.register(TaskCheck)
