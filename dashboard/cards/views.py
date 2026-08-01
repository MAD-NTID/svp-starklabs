import json
import time
from collections import defaultdict
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone as tz
from django.views.decorators.csrf import csrf_exempt
from .models import Card, CardStatus, CurrentStatus, GameSettings, TaskCheck
from .status_utils import check_ping, check_port, load_yaml, update_card_progress


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


def _cors_headers(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    return response


def _parse_complete(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ('1', 'true', 'yes'):
            return True
        if v in ('0', 'false', 'no'):
            return False
    return None


@csrf_exempt
def api_task_update(request):
    if request.method == 'OPTIONS':
        return _cors_headers(JsonResponse({}))

    if request.method != 'POST':
        return _cors_headers(JsonResponse({'error': 'method not allowed'}, status=405))

    expected = f'Token {settings.TASK_API_KEY}'
    if request.META.get('HTTP_AUTHORIZATION') != expected:
        return _cors_headers(JsonResponse({'error': 'unauthorized'}, status=401))

    try:
        body = json.loads(request.body or b'{}')
    except (json.JSONDecodeError, ValueError):
        return _cors_headers(JsonResponse({'error': 'invalid JSON'}, status=400))

    card_slug = body.get('card')
    task_id = body.get('task')
    if not card_slug or not task_id:
        return _cors_headers(JsonResponse({'error': 'card and task are required'}, status=400))

    config = load_yaml()
    cfg = config.get('cards', {}).get(card_slug)
    if not cfg:
        return _cors_headers(JsonResponse({'error': 'card not found'}, status=404))

    task_cfg = next((t for t in cfg.get('tasks', []) if t['id'] == task_id), None)
    if not task_cfg:
        return _cors_headers(JsonResponse({'error': 'task not found'}, status=404))

    if task_cfg.get('type') != 'manual':
        return _cors_headers(JsonResponse({'error': 'only manual tasks can be updated via API'}, status=400))

    if 'complete' in body:
        complete = _parse_complete(body['complete'])
        if complete is None:
            return _cors_headers(JsonResponse({'error': 'complete must be a boolean'}, status=400))
    else:
        complete = None

    card, _ = Card.objects.get_or_create(
        slug=card_slug,
        defaults={'title': cfg['title'], 'icon': cfg['icon'], 'order': list(config['cards'].keys()).index(card_slug)},
    )

    tc, _ = TaskCheck.objects.get_or_create(
        card=card,
        task_id=task_id,
        defaults={
            'title': task_cfg.get('title', task_id),
            'host': task_cfg.get('host', ''),
            'is_manual': True,
            'result': False,
        },
    )
    tc.title = task_cfg.get('title', task_id)
    tc.is_manual = True
    if complete is not None:
        tc.manual_complete = complete
    else:
        tc.manual_complete = not tc.manual_complete
    tc.save()

    completed, total, status_name = update_card_progress(card, config)

    return _cors_headers(JsonResponse({
        'ok': True,
        'card': card_slug,
        'task': task_id,
        'complete': tc.manual_complete,
        'tasks_completed': completed,
        'tasks_total': total,
        'status': status_name,
    }))


@csrf_exempt
def api_check_host(request):
    if request.method == 'OPTIONS':
        return _cors_headers(JsonResponse({}))

    if request.method != 'POST':
        return _cors_headers(JsonResponse({'error': 'method not allowed'}, status=405))

    expected = f'Token {settings.TASK_API_KEY}'
    if request.META.get('HTTP_AUTHORIZATION') != expected:
        return _cors_headers(JsonResponse({'error': 'unauthorized'}, status=401))

    try:
        body = json.loads(request.body or b'{}')
    except (json.JSONDecodeError, ValueError):
        return _cors_headers(JsonResponse({'error': 'invalid JSON'}, status=400))

    host = body.get('host')
    if not host or not isinstance(host, str):
        return _cors_headers(JsonResponse({'error': 'host is required'}, status=400))
    host = host.strip()
    if not host or len(host) > 255:
        return _cors_headers(JsonResponse({'error': 'invalid host'}, status=400))

    port = body.get('port')
    if port is not None:
        if not isinstance(port, int) or isinstance(port, bool):
            return _cors_headers(JsonResponse({'error': 'port must be an integer'}, status=400))
        if not (1 <= port <= 65535):
            return _cors_headers(JsonResponse({'error': 'port out of range'}, status=400))

    start = time.perf_counter()
    if port is not None:
        reachable = check_port(host, port)
        method = 'port'
    else:
        reachable = check_ping(host)
        method = 'ping'
    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

    return _cors_headers(JsonResponse({
        'ok': True,
        'host': host,
        'port': port,
        'method': method,
        'reachable': reachable,
        'response_time_ms': elapsed_ms,
    }))
