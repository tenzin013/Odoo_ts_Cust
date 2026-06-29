/* ─── Face Attendance Kiosk — Full-Screen UI ─────────────────────────────── */

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --primary:    #4f46e5;
    --primary-dk: #3730a3;
    --success:    #16a34a;
    --danger:     #dc2626;
    --warning:    #d97706;
    --bg:         #0f172a;
    --bg2:        #1e293b;
    --border:     #334155;
    --text:       #f1f5f9;
    --muted:      #94a3b8;
    --radius:     16px;
}

body.o_face_kiosk_body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', 'Segoe UI', sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* ── Header ─────────────────────────────────────────────────────────────── */
.kiosk-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 32px;
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}

.kiosk-company-name {
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -.5px;
}

.kiosk-clock {
    font-size: 1.5rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    color: var(--primary);
    min-width: 100px;
    text-align: right;
}

/* ── Main Layout ─────────────────────────────────────────────────────────── */
.kiosk-main {
    flex: 1;
    display: flex;
    gap: 32px;
    padding: 28px 40px;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* ── Camera ──────────────────────────────────────────────────────────────── */
.kiosk-camera-wrapper {
    position: relative;
    width: 480px;
    height: 360px;
    border-radius: var(--radius);
    overflow: hidden;
    background: #000;
    box-shadow: 0 0 0 3px var(--border), 0 20px 60px rgba(0,0,0,0.5);
    flex-shrink: 0;
}

#kiosk_video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scaleX(-1); /* mirror */
}

#kiosk_overlay {
    position: absolute;
    inset: 0;
    pointer-events: none;
}

.kiosk-face-guide {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
}

.face-oval {
    width: 200px;
    height: 260px;
    border: 3px dashed rgba(255,255,255,0.5);
    border-radius: 50%;
    animation: pulse-border 2s ease-in-out infinite;
}

@keyframes pulse-border {
    0%, 100% { border-color: rgba(255,255,255,0.35); }
    50%       { border-color: rgba(79,70,229,0.85); }
}

.scanning-bar {
    position: absolute;
    left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    animation: scan-sweep 1.4s linear infinite;
    top: 0;
}

@keyframes scan-sweep {
    0%   { top: 0; }
    100% { top: 100%; }
}

.scanning-bar.hidden { display: none; }

/* ── Side Panel ──────────────────────────────────────────────────────────── */
.kiosk-panel {
    flex: 1;
    max-width: 380px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}

/* Status idle */
.kiosk-status {
    text-align: center;
    padding: 32px 24px;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    width: 100%;
}

.kiosk-status h2   { font-size: 1.3rem; margin-bottom: 8px; }
.kiosk-status p    { color: var(--muted); font-size: .9rem; }
.kiosk-status.idle { color: var(--muted); }

/* Result cards */
.kiosk-result-card {
    text-align: center;
    padding: 32px 24px;
    border-radius: var(--radius);
    width: 100%;
    animation: card-pop .3s ease;
}

@keyframes card-pop {
    from { transform: scale(.9); opacity: 0; }
    to   { transform: scale(1);  opacity: 1; }
}

.kiosk-result-card.success {
    background: linear-gradient(135deg, #052e16, #14532d);
    border: 1px solid #16a34a;
    color: #f0fdf4;
}

.kiosk-result-card.error {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    border: 1px solid var(--danger);
    color: #fef2f2;
}

.kiosk-result-card h2 { font-size: 1.5rem; margin: 12px 0 6px; }
.kiosk-result-card p  { font-size: .9rem; opacity: .8; margin: 4px 0; }

.result-avatar { color: rgba(255,255,255,0.3); }

.action-badge {
    display: inline-block;
    padding: 4px 18px;
    border-radius: 999px;
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.action-badge.check-in  { background: #16a34a; color: #fff; }
.action-badge.check-out { background: #2563eb; color: #fff; }

.result-time     { font-size: 1.1rem; font-weight: 600; }
.result-location { font-size: .85rem; color: #86efac; }

/* Confidence bar */
.confidence-bar-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    font-size: .8rem;
    opacity: .85;
}

.confidence-bar {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.15);
    border-radius: 999px;
    overflow: hidden;
}

.confidence-fill {
    height: 100%;
    background: #4ade80;
    border-radius: 999px;
    transition: width .4s ease;
}

/* GPS status */
.gps-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: .85rem;
    color: var(--muted);
    padding: 8px 16px;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 999px;
    width: 100%;
    justify-content: center;
}

.gps-status.ok      { color: #4ade80; border-color: #16a34a; }
.gps-status.outside { color: #fca5a5; border-color: var(--danger); }

/* Buttons */
.kiosk-controls { display: flex; gap: 12px; width: 100%; justify-content: center; }

.btn-kiosk {
    padding: 14px 32px;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-kiosk.primary {
    background: var(--primary);
    color: #fff;
}
.btn-kiosk.primary:hover  { background: var(--primary-dk); transform: translateY(-1px); }
.btn-kiosk.primary:active { transform: translateY(0); }

.btn-kiosk.secondary {
    background: var(--bg2);
    color: var(--text);
    border: 1px solid var(--border);
}
.btn-kiosk.secondary:hover { border-color: var(--primary); color: var(--primary); }

.btn-kiosk:disabled { opacity: .5; cursor: not-allowed; transform: none !important; }

.hidden { display: none !important; }

/* ── Footer ──────────────────────────────────────────────────────────────── */
.kiosk-footer {
    text-align: center;
    padding: 10px;
    font-size: .75rem;
    color: var(--border);
    background: var(--bg2);
    border-top: 1px solid var(--border);
    flex-shrink: 0;
}

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
    .kiosk-main          { flex-direction: column; padding: 16px; }
    .kiosk-camera-wrapper { width: 100%; max-width: 400px; height: 300px; }
    .kiosk-panel         { max-width: 100%; }
}

/* ── Loading Overlay ────────────────────────────────────────────────────── */
.kiosk-loading-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.92);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    color: #fff;
}
.kiosk-loading-overlay.hidden {
    display: none;
}
.kiosk-loading-box {
    text-align: center;
    padding: 2rem;
}
.kiosk-loading-box .fa-spinner {
    color: #6366f1;
    display: block;
    margin-bottom: 1rem;
}
.kiosk-loading-box p {
    font-size: 1rem;
    color: #cbd5e1;
}
