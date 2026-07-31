from django.contrib import admin
from django.utils import timezone as tz
from django.shortcuts import redirect
from django.contrib import messages
from .models import Card, CardStatus, CurrentStatus, GameSettings


STATUS_MAP = {
    'devices': 'Operational',
    'networks': 'Connected',
    'security': 'Protected',
    'software_ai': 'Online',
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


class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'icon', 'order']
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
        if '_start_countdown' in request.POST:
            obj.start_time = tz.now()
            obj.save()
            self.message_user(request, 'Countdown started.', messages.SUCCESS)
            return redirect(request.path)
        if '_reset_countdown' in request.POST:
            obj.start_time = None
            obj.mission_accomplished = False
            obj.intrusion_applied = False
            obj.save()
            _set_all_cards_operational()
            self.message_user(request, 'Countdown reset.', messages.SUCCESS)
            return redirect(request.path)
        if '_trigger_intrusion' in request.POST:
            obj.intrusion_time = tz.now()
            obj.mission_accomplished = False
            obj.intrusion_applied = True
            obj.save()
            _clear_all_overrides()
            self.message_user(request, 'Intrusion triggered now.', messages.SUCCESS)
            return redirect(request.path)
        if '_clear_intrusion' in request.POST:
            obj.intrusion_time = None
            obj.mission_accomplished = False
            obj.intrusion_applied = False
            obj.save()
            _set_all_cards_operational()
            self.message_user(request, 'Intrusion cleared and statuses reset.', messages.SUCCESS)
            return redirect(request.path)
        if '_simulate_accomplished' in request.POST:
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
            self.message_user(request, 'Mission Accomplished simulated.', messages.SUCCESS)
            return redirect(request.path)
        return super().response_change(request, obj)


admin.site.register(Card, CardAdmin)
admin.site.register(CardStatus)
admin.site.register(CurrentStatus, CurrentStatusAdmin)
admin.site.register(GameSettings, GameSettingsAdmin)
