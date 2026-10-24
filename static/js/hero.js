/**
 * JobTrack — Fluid Vector Stream Canvas
 * Interactive background for landing page per hero.md spec.
 */

(function () {
  'use strict';

  const canvas = document.getElementById('fluid-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d', { alpha: false });
  let W, H, cols, rows;
  let time = 0;
  let mouse = { x: -9999, y: -9999 };
  let smoothMouse = { x: -9999, y: -9999 };

  const SPACING = 35;
  const BASE_LEN = 14;
  const ACTIVE_LEN = 22;
  const INFLUENCE = 220;
  const LERP = 0.08;
  const TIME_STEP = 0.008;

  /* ─── Theme Detection ────────────────────────────────────── */
  const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  let theme = getTheme();

  function getTheme() {
    return darkQuery.matches
      ? { bg: '#080d1a', base: [59, 130, 246], active: [147, 197, 253] }
      : { bg: '#f0f7ff', base: [30, 64, 175], active: [29, 78, 216] };
  }

  darkQuery.addEventListener('change', () => {
    theme = getTheme();
  });

  /* ─── Canvas Resize ──────────────────────────────────────── */
  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cols = Math.ceil(W / SPACING) + 2;
    rows = Math.ceil(H / SPACING) + 2;
  }

  resize();
  window.addEventListener('resize', resize);

  /* ─── Mouse Tracking ─────────────────────────────────────── */
  canvas.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  canvas.addEventListener('mouseleave', () => {
    mouse.x = -9999;
    mouse.y = -9999;
  });

  // Touch support
  canvas.addEventListener('touchmove', (e) => {
    if (e.touches.length > 0) {
      mouse.x = e.touches[0].clientX;
      mouse.y = e.touches[0].clientY;
    }
  }, { passive: true });

  canvas.addEventListener('touchend', () => {
    mouse.x = -9999;
    mouse.y = -9999;
  });

  /* ─── Animation Loop ─────────────────────────────────────── */
  function draw() {
    // Smooth mouse tracking (LERP)
    smoothMouse.x += (mouse.x - smoothMouse.x) * LERP;
    smoothMouse.y += (mouse.y - smoothMouse.y) * LERP;

    // Clear
    ctx.fillStyle = theme.bg;
    ctx.fillRect(0, 0, W, H);

    time += TIME_STEP;

    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const x = i * SPACING;
        const y = j * SPACING;

        // Vector field angle
        let angle = Math.sin(x * 0.003 + time) + Math.cos(y * 0.003 + time);

        // Mouse distance
        const dx = smoothMouse.x - x;
        const dy = smoothMouse.y - y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        let len = BASE_LEN;
        let alpha = 0.25;
        let r = theme.base[0], g = theme.base[1], b = theme.base[2];

        if (dist < INFLUENCE) {
          // Push angle (repelling force)
          const pushAngle = Math.atan2(dy, dx) + Math.PI;
          const influence = 1 - dist / INFLUENCE;

          // Interpolate toward push angle
          angle = angle + (pushAngle - angle) * influence * 0.8;

          // Expand length and increase alpha
          len = BASE_LEN + (ACTIVE_LEN - BASE_LEN) * influence;
          alpha = 0.25 + (0.8 - 0.25) * influence;

          // Shift toward active color
          r = theme.base[0] + (theme.active[0] - theme.base[0]) * influence;
          g = theme.base[1] + (theme.active[1] - theme.base[1]) * influence;
          b = theme.base[2] + (theme.active[2] - theme.base[2]) * influence;
        }

        // Draw line segment
        const ex = x + Math.cos(angle) * len;
        const ey = y + Math.sin(angle) * len;

        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(ex, ey);
        ctx.strokeStyle = `rgba(${Math.round(r)},${Math.round(g)},${Math.round(b)},${alpha})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    }

    requestAnimationFrame(draw);
  }

  requestAnimationFrame(draw);
})();
