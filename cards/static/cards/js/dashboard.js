let charts = {};
let countdownInterval = null;
let countdownSeconds = null;
let warningShown = false;
let failedShown = false;
let intrusionDismissed = false;
let previousIntrusionActive = false;
let selfDestructSeconds = null;
let selfDestructInterval = null;
let accomplishedShown = false;

const GOOD_STATUS = {
    devices: 'Operational',
    networks: 'Connected',
    security: 'Protected',
    software_ai: 'Online',
};

const GRAPH_HEIGHT = 120;
const GRAPH_HISTORY = 30;
const GRAPH_CONFIGS = {
    devices: {
        title: 'CPU Load',
        datasets: [{ label: 'CPU', color: '#00BCD4', max: 100, calmDelta: 6, spikeDelta: 35 }],
    },
    networks: {
        title: 'Network Traffic',
        max: 500,
        datasets: [
            { label: 'In', color: '#f5a623', max: 500, normalBase: 6, calmDelta: 6, spikeDelta: 300 },
            { label: 'Out', color: '#8a5a00', max: 500, normalBase: 150, calmDelta: 60, spikeDelta: 60 },
        ],
    },
    security: {
        title: 'Threats Blocked',
        type: 'bar',
        max: 50,
        datasets: [{ label: 'Blocked', color: '#b71c1c', max: 50, normalBase: 8, calmDelta: 4, spikeDelta: 30 }],
    },
    software_ai: {
        title: 'System Uptime',
        max: 100,
        datasets: [{ label: 'Uptime', color: '#F50057', max: 100, normalBase: 98, calmDelta: 2, spikeDelta: 45 }],
    },
};
let graphs = {};
let graphAlert = false;

function getStatusClass(status) {
    if (!status) return 'status-unknown';
    const s = status.toLowerCase().replace(/\s+/g, '-');
    if (['operational', 'online', 'connected', 'protected'].includes(s)) return 'status-operational';
    if (['offline', 'disrupted', 'compromised', 'malfunctioning'].includes(s)) return 'status-malfunctioning';
    if (['maintenance', 'partial-online'].includes(s)) return 'status-maintenance';
    return 'status-unknown';
}

function formatTime(seconds) {
    if (seconds === null || seconds === undefined) return '--:--';
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}

function updateCountdownDisplay() {
    const el = document.getElementById('countdown-display');
    if (!el) return;
    if (countdownSeconds !== null && countdownSeconds >= 0) {
        el.textContent = formatTime(countdownSeconds);
    } else {
        el.textContent = formatTime(0);
    }
}

function startCountdownTick() {
    if (countdownInterval) clearInterval(countdownInterval);
    countdownInterval = setInterval(function () {
        if (countdownSeconds !== null && countdownSeconds > 0) {
            countdownSeconds--;
            updateCountdownDisplay();
        }
    }, 1000);
}

function setCountdownVisible(visible) {
    const box = document.getElementById('countdown-box');
    if (!box) return;
    box.style.display = visible ? 'inline-flex' : 'none';
}

function createDonutChart(canvasId, pct, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    let color;
    if (pct >= 100) color = '#28a745';
    else color = '#D32F2F';
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [pct, 100 - pct],
                backgroundColor: [color, 'rgba(255,255,255,0.08)'],
                borderWidth: 0,
            }]
        },
        options: {
            cutout: '80%',
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            },
            animation: {
                animateRotate: true,
                duration: 600,
            },
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function () {}
        }]
    });
    return chart;
}

function updateDonutChart(chart, pct) {
    if (!chart) return;
    let color;
    if (pct >= 100) color = '#28a745';
    else color = '#D32F2F';
    chart.data.datasets[0].data = [pct, 100 - pct];
    chart.data.datasets[0].backgroundColor = [color, 'rgba(255,255,255,0.08)'];
    chart.update();
}

function buildLegendHTML(datasets) {
    return '<span class="graph-legend">' + datasets.map(function (ds) {
        return '<span class="legend-item"><i class="legend-dot" style="background:' + ds.color + '"></i>' + ds.label + '</span>';
    }).join('') + '</span>';
}

function createCardHTML(card) {
    const accentClass = 'card-accent-' + card.slug;
    const hasGraph = GRAPH_CONFIGS.hasOwnProperty(card.slug);
    const titleColClass = hasGraph ? 'ms-4 text-start' : 'ms-4 flex-grow-1 text-start';
    const graphHTML = hasGraph
        ? '<div class="graph-wrapper ms-4 flex-grow-1">' +
            '<div class="graph-canvas-wrap"><canvas id="graph-' + card.slug + '"></canvas></div>' +
            '<div class="graph-label">' +
                '<span class="graph-title">' + GRAPH_CONFIGS[card.slug].title + '</span>' +
                (GRAPH_CONFIGS[card.slug].datasets.length > 1 ? buildLegendHTML(GRAPH_CONFIGS[card.slug].datasets) : '') +
            '</div>' +
          '</div>'
        : '';
    return `
    <div class="col-md-6 col-12 mb-4">
        <div class="small-box bg-card ${accentClass}">
            <div class="inner">
                <div class="d-flex align-items-center">
                    <div class="donut-wrapper">
                        <canvas id="donut-${card.slug}" width="120" height="120"></canvas>
                        <div class="donut-center-label">
                            <i class="fa-solid ${card.icon} fa-2x"></i>
                        </div>
                    </div>
                    <div class="${titleColClass}">
                        <div class="card-title-text">${card.title}</div>
                        <span class="status-badge" id="status-${card.slug}">Loading...</span>
                    </div>
                    ${graphHTML}
                </div>
            </div>
            <div class="small-box-footer">
                <span id="tasks-${card.slug}">0/0 tasks</span>
                <span id="override-${card.slug}" style="display:none;">
                    <i class="fa-solid fa-lock" title="Manually overridden"></i>
                </span>
            </div>
        </div>
    </div>`;
}

function hexToRgba(hex, alpha) {
    const h = hex.replace('#', '');
    return 'rgba(' +
        parseInt(h.substring(0, 2), 16) + ',' +
        parseInt(h.substring(2, 4), 16) + ',' +
        parseInt(h.substring(4, 6), 16) + ',' +
        alpha + ')';
}

function buildFillGradient(ctx, height, color) {
    const g = ctx.createLinearGradient(0, height, 0, 0);
    g.addColorStop(0, hexToRgba(color, 0.35));
    g.addColorStop(1, hexToRgba(color, 0.02));
    return g;
}

function seedSeries(count, max, base, delta) {
    const out = [];
    let v = base;
    for (let i = 0; i < count; i++) {
        v = Math.max(0, Math.min(max, v + (Math.random() - 0.5) * 2 * delta));
        out.push(Math.round(v));
    }
    return out;
}

function initGraphs() {
    Object.keys(GRAPH_CONFIGS).forEach(function (slug) {
        const cfg = GRAPH_CONFIGS[slug];
        const canvas = document.getElementById('graph-' + slug);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const datasets = cfg.datasets.map(function (ds) {
            const isBar = cfg.type === 'bar';
            const dsObj = {
                label: ds.label,
                data: seedSeries(GRAPH_HISTORY, ds.max, ds.normalBase || ds.max * 0.4, ds.calmDelta),
                borderColor: ds.color,
                backgroundColor: buildFillGradient(ctx, GRAPH_HEIGHT, ds.color),
                borderWidth: 2,
                pointRadius: 0,
                pointHitRadius: 0,
                fill: true,
                tension: 0.4,
            };
            if (isBar) {
                dsObj.borderWidth = 0;
                dsObj.borderRadius = 2;
                dsObj.barPercentage = 0.7;
                dsObj.categoryPercentage = 0.9;
            }
            return dsObj;
        });
        graphs[slug] = new Chart(ctx, {
            type: cfg.type || 'line',
            data: { labels: new Array(GRAPH_HISTORY).fill(''), datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                },
                scales: {
                    x: { display: false },
                    y: { display: false, min: 0, max: cfg.datasets[0].max },
                },
            },
        });
    });
}

function pushGraphPoint(slug) {
    const cfg = GRAPH_CONFIGS[slug];
    if (!cfg || !graphs[slug]) return;
    const chart = graphs[slug];
    chart.data.datasets.forEach(function (ds, i) {
        const dsCfg = cfg.datasets[i];
        const last = ds.data.length ? ds.data[ds.data.length - 1] : dsCfg.max * 0.4;
        const amp = graphAlert ? dsCfg.spikeDelta : dsCfg.calmDelta;
        let next = last + (Math.random() - 0.5) * 2 * amp;
        next = Math.min(dsCfg.max, Math.max(0, next));
        ds.data.push(next);
        if (ds.data.length > GRAPH_HISTORY) ds.data.shift();
    });
    chart.update();
}

function setGraphMode(alert) {
    if (graphAlert === alert) return;
    graphAlert = alert;
    Object.keys(GRAPH_CONFIGS).forEach(function (slug) {
        const chart = graphs[slug];
        const cfg = GRAPH_CONFIGS[slug];
        if (!chart) return;
        const ctx = chart.ctx;
        chart.data.datasets.forEach(function (ds, i) {
            const color = alert ? (i === 0 ? '#D32F2F' : '#8B0000') : cfg.datasets[i].color;
            ds.borderColor = color;
            ds.backgroundColor = buildFillGradient(ctx, GRAPH_HEIGHT, color);
        });
        chart.update();
    });
}

function renderCardState(card, isPreIntrusion) {
    var statusEl = document.getElementById('status-' + card.slug);
    var tasksEl = document.getElementById('tasks-' + card.slug);
    var overrideEl = document.getElementById('override-' + card.slug);
    var footerEl = tasksEl ? tasksEl.closest('.small-box-footer') : null;

    var displayStatus = card.status;
    var displayCompleted = card.tasks_completed;
    var displayTotal = card.tasks_total;

    if (isPreIntrusion) {
        displayStatus = GOOD_STATUS[card.slug] || 'Online';
        displayCompleted = displayTotal;
    }

    if (statusEl) {
        statusEl.textContent = displayStatus;
        statusEl.className = 'status-badge ' + getStatusClass(displayStatus);
    }
    if (tasksEl) {
        if (isPreIntrusion) {
            tasksEl.textContent = '';
            tasksEl.style.display = 'none';
        } else {
            tasksEl.style.display = 'inline';
            tasksEl.textContent = displayCompleted + '/' + displayTotal + ' tasks';
        }
    }
    if (overrideEl) {
        overrideEl.style.display = card.manual_override ? 'inline' : 'none';
    }
    if (footerEl) {
        footerEl.style.display = isPreIntrusion ? 'none' : '';
    }

    var pct;
    if (isPreIntrusion) {
        pct = 100;
    } else {
        pct = displayTotal > 0 ? Math.round((displayCompleted / displayTotal) * 100) : 0;
    }
    if (charts[card.slug]) {
        updateDonutChart(charts[card.slug], pct);
    }
}

function showIntrusionOverlay() {
    var overlay = document.getElementById('intrusionOverlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideIntrusionOverlay() {
    var overlay = document.getElementById('intrusionOverlay');
    if (overlay) overlay.style.display = 'none';
}

function fetchStatus() {
    fetch('/api/status/')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var isPreIntrusion = !data.intrusion_active;
            var isIntrusionActive = data.intrusion_active;

            setGraphMode(data.intrusion_active);

            data.cards.forEach(function (card) {
                renderCardState(card, isPreIntrusion);
            });

            // Intrusion overlay logic
            var isExpired = data.countdown_visible && data.countdown_remaining !== null && data.countdown_remaining <= 0;
            if (isIntrusionActive && !intrusionDismissed && !isExpired) {
                showIntrusionOverlay();
            } else {
                hideIntrusionOverlay();
            }

            // Reset intrusion dismiss state when intrusion becomes inactive
            if (!isIntrusionActive && previousIntrusionActive) {
                intrusionDismissed = false;
            }
            previousIntrusionActive = isIntrusionActive;

            // Countdown logic
            if (data.countdown_visible) {
                setCountdownVisible(true);
                countdownSeconds = data.countdown_remaining;
                updateCountdownDisplay();

                var countdownBox = document.getElementById('countdown-box');
                if (countdownSeconds !== null && countdownSeconds > 0 && countdownSeconds <= 300) {
                    countdownBox.classList.add('flashing');
                } else {
                    countdownBox.classList.remove('flashing');
                }

                if (countdownSeconds <= 300 && countdownSeconds > 0 && !warningShown) {
                    warningShown = true;
                    var modal = new bootstrap.Modal(document.getElementById('warningModal'));
                    modal.show();
                }

                if (countdownSeconds <= 0 && !failedShown) {
                    failedShown = true;
                    document.getElementById('missionFailedOverlay').style.display = 'flex';

                    selfDestructSeconds = 300;
                    var timerEl = document.getElementById('self-destruct-timer');
                    if (timerEl) timerEl.textContent = formatTime(selfDestructSeconds);
                    if (selfDestructInterval) clearInterval(selfDestructInterval);
                    selfDestructInterval = setInterval(function () {
                        if (selfDestructSeconds !== null && selfDestructSeconds > 0) {
                            selfDestructSeconds--;
                            var el = document.getElementById('self-destruct-timer');
                            if (el) el.textContent = formatTime(selfDestructSeconds);
                        }
                    }, 1000);
                }
            } else {
                setCountdownVisible(false);
                countdownSeconds = null;
                document.getElementById('missionFailedOverlay').style.display = 'none';
                var countdownBox = document.getElementById('countdown-box');
                if (countdownBox) countdownBox.classList.remove('flashing');
                if (selfDestructInterval) {
                    clearInterval(selfDestructInterval);
                    selfDestructInterval = null;
                }
                selfDestructSeconds = null;
                warningShown = false;
                failedShown = false;
                document.getElementById('missionAccomplishedOverlay').style.display = 'none';
                accomplishedShown = false;
            }

            // Mission accomplished logic
            if (data.mission_accomplished && !accomplishedShown) {
                accomplishedShown = true;
                intrusionDismissed = true;
                hideIntrusionOverlay();
                document.getElementById('missionAccomplishedOverlay').style.display = 'flex';
                document.getElementById('missionFailedOverlay').style.display = 'none';
                failedShown = true;
            }

            if (data.last_updated) {
                var lu = document.getElementById('last-updated-time');
                if (lu) {
                    var d = new Date(data.last_updated);
                    lu.textContent = d.toLocaleTimeString();
                }
            }
        })
        .catch(function (err) {
            console.error('Dashboard fetch error:', err);
        });
}

document.addEventListener('DOMContentLoaded', function () {
    var container = document.getElementById('cards-container');
    if (!container) return;

    var cardsData = container.getAttribute('data-cards');
    if (!cardsData) return;

    var cards = JSON.parse(cardsData);
    var html = '';
    cards.forEach(function (card) {
        html += createCardHTML(card);
    });
    container.innerHTML = html;

    cards.forEach(function (card) {
        setTimeout(function () {
            charts[card.slug] = createDonutChart('donut-' + card.slug, 0, card.title);
        }, 100);
    });

    initGraphs();

    Object.keys(GRAPH_CONFIGS).forEach(function (slug) {
        setInterval(function () {
            pushGraphPoint(slug);
        }, 2000);
    });

    document.getElementById('intrusionDismissBtn').addEventListener('click', function () {
        intrusionDismissed = true;
        hideIntrusionOverlay();
    });

    fetchStatus();

    setInterval(fetchStatus, 5000);

    startCountdownTick();
});
