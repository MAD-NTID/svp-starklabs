import json
from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone as tz
from .models import Card, CardStatus, CurrentStatus, GameSettings, TaskCheck


def dashboard(request):
    cards = Card.objects.all().order_by('order')
    game_settings = GameSettings.objects.first()
    return render(request, 'cards/dashboard.html', {
        'cards_json': json.dumps([{
            'slug': c.slug,
            'title': c.title,
            'icon': c.icon,
            'order': c.order,
            'team_name': c.team.name if c.team else '',
            'team_color': c.team.color if c.team else '',
        } for c in cards]),
        'countdown_minutes': game_settings.countdown_minutes if game_settings else 60,
    })


def api_status(request):
    cards = list(Card.objects.all().order_by('order'))
    data = []

    checks_by_card = defaultdict(list)
    for tc in TaskCheck.objects.filter(card__in=cards).order_by('card_id', 'task_id'):
        checks_by_card[tc.card_id].append({
            'title': tc.title,
            'result': tc.manual_complete if tc.is_manual else tc.result,
        })

    for card in cards:
        cs = CurrentStatus.objects.filter(card=card).select_related('status').first()
        data.append({
            'slug': card.slug,
            'title': card.title,
            'icon': card.icon,
            'team_name': card.team.name if card.team else '',
            'team_color': card.team.color if card.team else '',
            'status': cs.status.name if cs and cs.status else 'Unknown',
            'tasks_completed': cs.tasks_completed if cs else 0,
            'tasks_total': cs.tasks_total if cs else 0,
            'manual_override': cs.manual_override if cs else False,
            'last_updated': cs.updated_at.isoformat() if cs and cs.updated_at else None,
            'tasks': checks_by_card.get(card.id, []),
        })

    game_settings = GameSettings.objects.first()
    countdown_visible = False
    countdown_remaining = None
    intrusion_active = False
    intrusion_scheduled = False

    if game_settings:
        now = tz.now()

        if game_settings.start_time:
            if now >= game_settings.start_time:
                countdown_visible = True
                elapsed = (now - game_settings.start_time).total_seconds()
                total = game_settings.countdown_minutes * 60
                countdown_remaining = max(0, total - int(elapsed))

        if game_settings.intrusion_time:
            intrusion_scheduled = True
            if now >= game_settings.intrusion_time:
                intrusion_active = True
                if not game_settings.intrusion_applied:
                    CurrentStatus.objects.all().update(manual_override=False)
                    game_settings.intrusion_applied = True
                    game_settings.save(update_fields=['intrusion_applied'])

        if intrusion_active and game_settings and not game_settings.mission_accomplished:
            all_done = all(
                cs.tasks_completed >= cs.tasks_total and cs.tasks_total > 0
                for cs in CurrentStatus.objects.select_related('card').all()
            )
            if all_done:
                game_settings.mission_accomplished = True
                game_settings.start_time = None
                game_settings.save(update_fields=['mission_accomplished', 'start_time'])
                countdown_visible = False
                countdown_remaining = None

    last_updated = None
    latest = CurrentStatus.objects.order_by('-updated_at').first()
    if latest and latest.updated_at:
        last_updated = latest.updated_at.isoformat()

    return JsonResponse({
        'cards': data,
        'countdown_visible': countdown_visible,
        'countdown_remaining': countdown_remaining,
        'intrusion_active': intrusion_active,
        'intrusion_scheduled': intrusion_scheduled,
        'mission_accomplished': game_settings.mission_accomplished if game_settings else False,
        'last_updated': last_updated,
    })
