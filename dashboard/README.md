# StarkLab Escape Room Dashboard — API

Django dashboard that tracks escape-room team statuses, countdown, and intrusion state.
This document covers the task-completion API and the connectivity-check API used by task webpages.

## Base URL

The API lives on the dashboard server, e.g. `http://<dashboard-host>:8000`. All requests
are JSON and all responses are JSON.

## Authentication

Every API call requires the same secret key, sent as a bearer token:

```
Authorization: Token <key>
```

The key comes from the `ESCAPE_ROOM_API_KEY` environment variable
(set in `compose.yaml` / `run.ps1`). Local default: `starklab-api-key-2026`.

The server answers `OPTIONS` preflight requests and sends
`Access-Control-Allow-Origin: *`, so task webpages hosted on **any** server can call the API.

---

## Configuring tasks (`cards/tasks.yaml`)

Tasks drive every card on the dashboard. They are defined in `cards/tasks.yaml`, which is
bind-mounted into the container (`./cards/tasks.yaml:/app/cards/tasks.yaml` in `compose.yaml`
/ `run.ps1`). Edit the host file and changes are picked up by the next `check_status` run
(every 5 seconds in Docker) — no restart needed.

### Structure

```yaml
cards:
  devices:                       # card slug — also the `card` value in the API
    title: Hardware & IT         # card name shown on the dashboard
    icon: fa-microchip           # Font Awesome icon class
    tasks:
      - id: printer_online       # unique per card — the `task` value in the API
        title: "Printer is online"  # shown in the task-detail modal
        type: port               # ping | port | manual
        host: 192.168.2.13       # host to check (ping/port only)
        port: 9100               # TCP port to check (port type only)
      - id: ram_replaced
        title: "Replace bad RAM"
        type: manual             # no host/port — completed by the instructor or the API
    statuses:
      all_complete: Operational  # shown when every task is complete
      partial: "Partial Online"  # shown when some (not all) are complete
      none_complete: Offline     # shown when none are complete
```

### Task types

| type     | Check performed                | Completed by                                    |
| -------- | ------------------------------ | ----------------------------------------------- |
| `ping`   | ICMP ping to `host`            | automatic (every 5 seconds)                     |
| `port`   | TCP connection to `host:port`  | automatic (every 5 seconds)                     |
| `manual` | no check                       | instructor (admin → Manual Tasks) or `POST /api/task/update/` |

`type` defaults to `ping` if omitted.

### Status names

`statuses` maps completion to a status label:

- `all_complete` — shown when every task is complete
- `partial` — shown when some (not all) tasks are complete. Optional; if omitted, partial
  completion is treated as `none_complete`
- `none_complete` — shown when no tasks are complete

### Rules and notes

- `id` must be unique within a card; it is the `task` value sent to `/api/task/update/`.
- The card slug (`devices`, `networks`, `security`, `software_ai`) is the `card` value in the API.
- Cards appear on the dashboard in the order they appear under `cards:`.
- Database rows sync automatically on each `check_status` run: new tasks are added, removed
  tasks are dropped, and manual-task state is preserved.
- Keep the file valid YAML — a syntax error makes the check loop fail until it is corrected.
- Optional top-level `countdown_minutes` sets the game countdown, e.g.:

  ```yaml
  countdown_minutes: 45
  ```
- `CHECK_TIMEOUT` (seconds, default `1`) — network check timeout (env var). Raise it if
  hosts are slow to respond; lower it for faster check cycles.

---

## 1. Mark a manual task complete

Marks a `type: manual` task (defined in `cards/tasks.yaml`) as complete or not.
Network-checked tasks (`ping` / `port`) cannot be set by this API — their state is driven
by real checks.

| Method | URL               |
| ------ | ----------------- |
| POST   | `/api/task/update/` |

### Request body

| Field      | Type    | Required | Description |
| ---------- | ------- | -------- | ----------- |
| `card`     | string  | yes      | Card slug, e.g. `devices`, `networks`, `security`, `software_ai` |
| `task`     | string  | yes      | Task id from `tasks.yaml`, e.g. `ram_replaced` |
| `complete` | boolean | no       | `true`/`false`. Omit to **toggle** the current state. Accepts bool or `"true"`/`"false"`/`"1"`/`"0"` |

### Response

```json
{
  "ok": true,
  "card": "devices",
  "task": "ram_replaced",
  "complete": true,
  "tasks_completed": 4,
  "tasks_total": 4,
  "status": "Operational"
}
```

### Example JS — set complete

```js
async function markComplete(card, task, complete = true) {
  const res = await fetch('http://<dashboard-host>:8000/api/task/update/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Token <API_KEY>',
    },
    body: JSON.stringify({ card, task, complete }),
  });
  const data = await res.json();
  console.log(data); // { ok, complete, tasks_completed, tasks_total, status }
}

markComplete('devices', 'ram_replaced', true);
```

### Example JS — toggle (no `complete`)

```js
await fetch('http://<dashboard-host>:8000/api/task/update/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Token <API_KEY>',
  },
  body: JSON.stringify({ card: 'devices', task: 'ram_replaced' }),
});
```

### Example JS — read ids from the page URL

Serve the task page as `task.html?card=devices&task=ram_replaced`:

```js
const params = new URLSearchParams(location.search);
const payload = {
  card: params.get('card'),
  task: params.get('task'),
  complete: true,
};

const res = await fetch('http://<dashboard-host>:8000/api/task/update/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Token <API_KEY>',
  },
  body: JSON.stringify(payload),
});
const data = await res.json();
if (data.ok) console.log(`Task marked complete: ${data.status}`);
```

---

## 2. Check if a host is reachable

Pings a host, or checks whether a TCP port is open. Read-only.

| Method | URL          |
| ------ | ------------ |
| POST   | `/api/check/` |

### Request body

| Field  | Type    | Required | Description |
| ------ | ------- | -------- | ----------- |
| `host` | string  | yes      | Hostname or IP address |
| `port` | integer | no       | If present (1–65535), a TCP port check is done; otherwise a ping |

### Response

```json
{
  "ok": true,
  "host": "192.168.2.13",
  "port": 9100,
  "method": "port",
  "reachable": true,
  "response_time_ms": 42
}
```

(`method` is `"port"` or `"ping"`; `port` is `null` for a ping.)

### Example JS — full page with a form

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Connectivity Check</title>
</head>
<body>
  <form id="checkForm">
    <label>Host/IP <input type="text" id="host" value="192.168.2.13" required></label>
    <label>Port (optional, empty = ping) <input type="number" id="port" min="1" max="65535"></label>
    <button type="submit">Check</button>
  </form>
  <pre id="result">Waiting...</pre>

  <script>
    const API_URL = 'http://<dashboard-host>:8000/api/check/';
    const API_KEY = '<API_KEY>';

    async function checkHost(host, port = null) {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${API_KEY}`,
        },
        body: JSON.stringify({ host, port }),
      });
      return res.json();
    }

    document.getElementById('checkForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const host = document.getElementById('host').value.trim();
      const portInput = document.getElementById('port').value;
      const port = portInput === '' ? null : Number(portInput);

      const out = document.getElementById('result');
      out.textContent = 'Checking...';

      const data = await checkHost(host, port);
      if (!data.ok) {
        out.textContent = `Error: ${data.error || 'request failed'}`;
        return;
      }
      out.textContent = JSON.stringify(data, null, 2);
    });
  </script>
</body>
</html>
```

---

## Errors

| Status | Meaning |
| ------ | ------- |
| 400    | Missing/invalid body field (`host`, `card`, `task`, `port`, `complete`), invalid JSON |
| 401    | Missing or wrong `Authorization: Token <key>` |
| 404    | Unknown card slug or task id |
| 405    | Wrong HTTP method (only `POST` is allowed) |
