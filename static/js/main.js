// Xtudio — main.js
// Platform-wide JavaScript utilities

'use strict';

// ---- Sidebar ----

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    // Mobile: show/hide via 'open' class
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('open');
        return;
    }

    // Desktop: collapse/expand
    const isCollapsed = sidebar.classList.toggle('collapsed');
    try {
        localStorage.setItem('sidebar_collapsed', isCollapsed ? '1' : '0');
    } catch (e) {
        // localStorage may be unavailable in some contexts
    }
}

// Restore sidebar collapse state on page load
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    if (sidebar && window.innerWidth > 768) {
        try {
            if (localStorage.getItem('sidebar_collapsed') === '1') {
                sidebar.classList.add('collapsed');
            }
        } catch (e) {}
    }
});

// Close sidebar on mobile when clicking outside
document.addEventListener('click', function (e) {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (
        sidebar &&
        window.innerWidth <= 768 &&
        sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        (!toggleBtn || !toggleBtn.contains(e.target))
    ) {
        sidebar.classList.remove('open');
    }
});

// ---- User Menu ----

function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (!menu) return;
    menu.classList.toggle('open');
}

// Close user menu when clicking outside
document.addEventListener('click', function (e) {
    const trigger = document.querySelector('.user-menu-trigger');
    const menu = document.getElementById('userMenu');
    if (menu && menu.classList.contains('open')) {
        if (trigger && trigger.contains(e.target)) {
            return; // the toggle will handle it
        }
        if (!menu.contains(e.target)) {
            menu.classList.remove('open');
        }
    }
});

// ---- Alerts auto-dismiss ----

document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 5000);
    });
});

// ---- Confirmation modal (Remove document) ----

function closeMsgModal() {
    const modal = document.getElementById('msg-modal');
    if (!modal) return;
    modal.style.transition = 'opacity 0.25s ease';
    modal.style.opacity = '0';
    setTimeout(function () {
        modal.style.display = 'none';
        modal.style.opacity = '';
        modal.style.transition = '';
    }, 250);
}

// ---- CSRF helper for fetch() calls ----

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    // Fallback: read from cookie
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        const [k, v] = c.trim().split('=');
        if (k === name) return decodeURIComponent(v);
    }
    return '';
}

// Extend fetch with CSRF header automatically
function apiFetch(url, options = {}) {
    const defaults = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'same-origin',
    };
    return fetch(url, {
        ...defaults,
        ...options,
        headers: { ...defaults.headers, ...(options.headers || {}) },
    });
}

// ---- Notification unread count polling ----
// Polls every 30 seconds to update the badge without page refresh

(function startNotifPolling() {
    const badge = document.querySelector('.notif-badge');
    const navBadge = document.querySelector('.nav-label .badge');

    function updateBadge(count) {
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = '';
            } else {
                badge.style.display = 'none';
            }
        }
        if (navBadge) {
            if (count > 0) {
                navBadge.textContent = count;
                navBadge.style.display = '';
            } else {
                navBadge.style.display = 'none';
            }
        }
    }

    function poll() {
        fetch('/api/v1/notifications/unread-count/', {
            credentials: 'same-origin',
            headers: { 'Accept': 'application/json' },
        })
        .then(function (res) {
            if (res.ok) return res.json();
        })
        .then(function (data) {
            if (data && typeof data.count === 'number') {
                updateBadge(data.count);
            }
        })
        .catch(function () {
            // Silently ignore — user may not be authenticated
        });
    }

    // Only poll if user appears authenticated (badge element exists)
    if (badge || navBadge) {
        setInterval(poll, 30000);
    }
})();
