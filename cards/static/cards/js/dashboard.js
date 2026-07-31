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

function createCardHTML(card) {
    const accentClass = 'card-accent-' + card.slug;
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
                    <div class="ms-4 flex-grow-1 text-start">
                        <div class="card-title-text">${card.title}</div>
                        <span class="status-badge" id="status-${card.slug}">Loading...</span>
                    </div>
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

    document.getElementById('intrusionDismissBtn').addEventListener('click', function () {
        intrusionDismissed = true;
        hideIntrusionOverlay();
    });

    fetchStatus();

    setInterval(fetchStatus, 5000);

    startCountdownTick();
});
