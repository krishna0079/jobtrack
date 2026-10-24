/**
 * JobTrack — Main JavaScript
 * Handles: navigation, alerts, form validation, dynamic interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initAlerts();
  initFormValidation();
  initConfirmDialogs();
  initNotificationActions();
  initSearchAutofocus();
});

/* ─── Mobile Navigation ─────────────────────────────────────── */
function initMobileNav() {
  const hamburger = document.getElementById('jt-hamburger');
  const navLinks = document.getElementById('jt-nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      hamburger.setAttribute('aria-expanded', isOpen);
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

/* ─── Alert Auto-dismiss ────────────────────────────────────── */
function initAlerts() {
  const alerts = document.querySelectorAll('.jt-alert');
  alerts.forEach((alert) => {
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateX(100%)';
      setTimeout(() => alert.remove(), 300);
    }, 5000);

    // Close button
    const closeBtn = alert.querySelector('.jt-alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        setTimeout(() => alert.remove(), 300);
      });
    }
  });
}

/* ─── Form Validation ───────────────────────────────────────── */
function initFormValidation() {
  // Registration form
  const regForm = document.getElementById('register-form');
  if (regForm) {
    regForm.addEventListener('submit', (e) => {
      const password = regForm.querySelector('[name="password"]');
      const confirm = regForm.querySelector('[name="confirm_password"]');
      const email = regForm.querySelector('[name="email"]');

      if (email && !isValidEmail(email.value)) {
        e.preventDefault();
        showFieldError(email, 'Enter a valid email address.');
        return;
      }

      if (password && password.value.length < 8) {
        e.preventDefault();
        showFieldError(password, 'Password must be at least 8 characters.');
        return;
      }

      if (password && confirm && password.value !== confirm.value) {
        e.preventDefault();
        showFieldError(confirm, 'Passwords do not match.');
        return;
      }
    });
  }

  // Login form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const email = loginForm.querySelector('[name="email"]');
      const password = loginForm.querySelector('[name="password"]');

      if (email && !email.value.trim()) {
        e.preventDefault();
        showFieldError(email, 'Email is required.');
        return;
      }

      if (password && !password.value) {
        e.preventDefault();
        showFieldError(password, 'Password is required.');
        return;
      }
    });
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showFieldError(field, message) {
  // Remove existing error
  const existing = field.parentElement.querySelector('.jt-field-error');
  if (existing) existing.remove();

  const error = document.createElement('div');
  error.className = 'jt-field-error';
  error.style.cssText = 'color: #EF4444; font-size: 0.8rem; margin-top: 4px; font-weight: 500;';
  error.textContent = message;
  field.parentElement.appendChild(error);
  field.style.borderColor = '#EF4444';

  field.addEventListener('input', () => {
    error.remove();
    field.style.borderColor = '';
  }, { once: true });

  field.focus();
}

/* ─── Confirmation Dialogs ──────────────────────────────────── */
function initConfirmDialogs() {
  document.querySelectorAll('[data-confirm]').forEach((el) => {
    el.addEventListener('click', (e) => {
      const message = el.dataset.confirm || 'Are you sure?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });
}

/* ─── Notification AJAX Actions ─────────────────────────────── */
function initNotificationActions() {
  // Mark single notification as read
  document.querySelectorAll('.jt-notif-mark-read').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const csrfToken = getCSRFToken();
      try {
        const resp = await fetch(`/notifications/${id}/read/`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
          },
        });
        if (resp.ok) {
          const item = btn.closest('.jt-notif-item');
          if (item) {
            item.classList.remove('jt-notif-item--unread');
            const dot = item.querySelector('.jt-notif-dot');
            if (dot) dot.style.display = 'none';
          }
          btn.remove();
          updateNotifBadge(-1);
        }
      } catch (err) {
        console.error('Failed to mark notification as read:', err);
      }
    });
  });

  // Mark all as read
  const markAllBtn = document.getElementById('mark-all-read');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', async () => {
      const csrfToken = getCSRFToken();
      try {
        const resp = await fetch('/notifications/mark-all-read/', {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
          },
        });
        if (resp.ok) {
          document.querySelectorAll('.jt-notif-item--unread').forEach((item) => {
            item.classList.remove('jt-notif-item--unread');
            const dot = item.querySelector('.jt-notif-dot');
            if (dot) dot.style.display = 'none';
          });
          document.querySelectorAll('.jt-notif-mark-read').forEach((b) => b.remove());
          updateNotifBadge(0, true);
        }
      } catch (err) {
        console.error('Failed to mark all as read:', err);
      }
    });
  }
}

function updateNotifBadge(delta, setToZero = false) {
  const badge = document.querySelector('.jt-notif-badge');
  if (!badge) return;
  if (setToZero) {
    badge.textContent = '0';
    badge.style.display = 'none';
    return;
  }
  let count = parseInt(badge.textContent) || 0;
  count = Math.max(0, count + delta);
  badge.textContent = count;
  badge.style.display = count > 0 ? 'inline-flex' : 'none';
}

function getCSRFToken() {
  const cookie = document.cookie.split(';').find((c) => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}

/* ─── Search Autofocus ──────────────────────────────────────── */
function initSearchAutofocus() {
  const searchInput = document.getElementById('job-search-input');
  if (searchInput && searchInput.value) {
    searchInput.focus();
    searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
  }
}
