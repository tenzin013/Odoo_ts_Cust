/**
 * HR Attendance Face Detection — Kiosk JS (Client-Side face-api.js)
 * ==================================================================
 * Architecture:
 *  1. On boot: load face-api.js TinyFaceDetector + FaceRecognitionNet models
 *  2. Fetch all employee face descriptors from server (JSON, stored at enrolment)
 *  3. Auto-scan loop: detect + describe face in-browser, match against stored
 *     descriptors using Euclidean distance, POST only employee_id + GPS to
 *     /hr_attendance_face/kiosk/checkin (no image sent, no server-side ML)
 *
 * face-api.js CDN: https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js
 * Models hosted under: /hr_attendance_face_detection/static/models/
 */

(function () {
    "use strict";

    // ── Constants ─────────────────────────────────────────────────────────────
    const SCAN_INTERVAL_MS  = 2500;   // auto-scan every 2.5 s
    const RESULT_DISPLAY_MS = 4000;   // show result for 4 s then reset
    const MATCH_THRESHOLD   = 0.50;   // Euclidean distance; lower = stricter
    const SCAN_WIDTH        = 640;
    const SCAN_HEIGHT       = 480;

    // face-api.js CDN (loaded via kiosk template <script> tag)
    const FACEAPI_CDN = "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js";
    const MODELS_URL  = "/hr_attendance_face_detection/static/models";

    // ── DOM references ────────────────────────────────────────────────────────
    const app         = document.getElementById("face_kiosk_app");
    const video       = document.getElementById("kiosk_video");
    const scanBar     = document.getElementById("kiosk_scanning_indicator");
    const statusBox   = document.getElementById("kiosk_status");
    const successCard = document.getElementById("kiosk_success_card");
    const errorCard   = document.getElementById("kiosk_error_card");
    const btnScan     = document.getElementById("btn_scan");
    const btnRetry    = document.getElementById("btn_retry");
    const clockEl     = document.getElementById("kiosk_clock");
    const gpsLabel    = document.getElementById("gps_label");
    const gpsStatus   = document.querySelector(".gps-status");
    const loadingOverlay = document.getElementById("kiosk_loading_overlay");

    const geofencingEnabled = app && app.dataset.geofencing === "1";

    // ── State ─────────────────────────────────────────────────────────────────
    let scanLoop        = null;
    let isScanning      = false;
    let gpsPosition     = null;
    let gpsWatchId      = null;
    let labeledDescriptors = [];   // faceapi.LabeledFaceDescriptors[]
    let modelsLoaded    = false;

    // ── Clock ─────────────────────────────────────────────────────────────────
    function updateClock() {
        if (clockEl) clockEl.textContent = new Date().toLocaleTimeString();
    }
    setInterval(updateClock, 1000);
    updateClock();

    // ── Loading overlay ───────────────────────────────────────────────────────
    function setLoadingMessage(msg) {
        const el = document.getElementById("kiosk_loading_msg");
        if (el) el.textContent = msg;
    }
    function hideLoadingOverlay() {
        if (loadingOverlay) loadingOverlay.classList.add("hidden");
    }

    // ── Load face-api.js from CDN then load models ────────────────────────────
    async function loadFaceApi() {
        setLoadingMessage("Loading face recognition library…");
        await new Promise((resolve, reject) => {
            if (window.faceapi) return resolve();
            const s = document.createElement("script");
            s.src = FACEAPI_CDN;
            s.onload = resolve;
            s.onerror = () => reject(new Error("Failed to load face-api.js from CDN"));
            document.head.appendChild(s);
        });

        setLoadingMessage("Loading AI models…");
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(MODELS_URL),
            faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODELS_URL),
            faceapi.nets.faceRecognitionNet.loadFromUri(MODELS_URL),
        ]);
        modelsLoaded = true;
    }

    // ── Fetch employee descriptors from server ────────────────────────────────
    async function loadEmployeeDescriptors() {
        setLoadingMessage("Loading employee face data…");
        const data = await rpcCall("/hr_attendance_face/get_encodings", {});
        if (!data || !data.employees || !data.employees.length) {
            showError("No Employees", "No enrolled employees found. Please enrol faces first.");
            return;
        }

        labeledDescriptors = data.employees
            .filter(e => e.encoding && e.encoding.length === 128)
            .map(e => {
                const desc = new Float32Array(e.encoding);
                return {
                    id: e.id,
                    name: e.name,
                    descriptor: desc,
                };
            });

        if (!labeledDescriptors.length) {
            showError("No Enrolled Faces", "No face descriptors found. Please enrol employee faces.");
        }
    }

    // ── Camera ────────────────────────────────────────────────────────────────
    async function startCamera() {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: SCAN_WIDTH, height: SCAN_HEIGHT, facingMode: "user" },
            audio: false,
        });
        video.srcObject = stream;
        await video.play();
    }

    // ── GPS ───────────────────────────────────────────────────────────────────
    function startGPS() {
        if (!geofencingEnabled || !navigator.geolocation) return;
        setGpsLabel("Acquiring GPS…", "");
        gpsWatchId = navigator.geolocation.watchPosition(
            (pos) => {
                gpsPosition = pos.coords;
                setGpsLabel(
                    `GPS: ${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`,
                    "ok"
                );
            },
            (err) => {
                gpsPosition = null;
                setGpsLabel("GPS unavailable: " + err.message, "outside");
            },
            { enableHighAccuracy: true, maximumAge: 10000, timeout: 15000 }
        );
    }

    function setGpsLabel(text, cls) {
        if (!gpsLabel) return;
        gpsLabel.textContent = text;
        if (gpsStatus) {
            gpsStatus.classList.remove("ok", "outside");
            if (cls) gpsStatus.classList.add(cls);
        }
    }

    // ── Client-side face detection + matching ─────────────────────────────────
    async function detectAndMatch() {
        if (!modelsLoaded || !labeledDescriptors.length) return null;

        const options = new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.5 });
        const detection = await faceapi
            .detectSingleFace(video, options)
            .withFaceLandmarks(true)
            .withFaceDescriptor();

        if (!detection) return { status: "no_face" };

        // Find best match
        let bestMatch = null;
        let bestDist  = Infinity;

        for (const emp of labeledDescriptors) {
            const dist = faceapi.euclideanDistance(detection.descriptor, emp.descriptor);
            if (dist < bestDist) {
                bestDist  = dist;
                bestMatch = emp;
            }
        }

        if (!bestMatch || bestDist > MATCH_THRESHOLD) {
            return { status: "no_match", distance: bestDist };
        }

        return {
            status: "matched",
            employee_id: bestMatch.id,
            employee_name: bestMatch.name,
            confidence: Math.round((1 - bestDist) * 100),
            distance: bestDist,
        };
    }

    // ── Auto-scan loop ────────────────────────────────────────────────────────
    function startAutoScan() {
        if (scanLoop) return;
        scanLoop = setInterval(triggerScan, SCAN_INTERVAL_MS);
    }

    function stopAutoScan() {
        if (scanLoop) { clearInterval(scanLoop); scanLoop = null; }
    }

    async function triggerScan() {
        if (isScanning || !modelsLoaded) return;
        isScanning = true;
        scanBar && scanBar.classList.remove("hidden");

        try {
            const match = await detectAndMatch();
            if (!match || match.status === "no_face") {
                showIdle("Position your face in the oval", "Face recognition will start automatically");
                return;
            }
            if (match.status === "no_match") {
                showIdle("Scanning…", "Looking for a match");
                return;
            }

            // Matched — geofence check then record attendance
            stopAutoScan();
            showIdle("Recognised!", "Recording attendance…");

            if (geofencingEnabled && !gpsPosition) {
                showError("GPS Required", "Enable location access for attendance.");
                setTimeout(() => { resetUI(); startAutoScan(); }, RESULT_DISPLAY_MS);
                return;
            }

            const payload = {
                employee_id: match.employee_id,
                latitude:    gpsPosition ? gpsPosition.latitude  : null,
                longitude:   gpsPosition ? gpsPosition.longitude : null,
            };

            const result = await rpcCall("/hr_attendance_face/kiosk/checkin", payload);
            result.confidence = match.confidence;
            handleResult(result);

        } catch (err) {
            showError("Error", err.message || "Recognition failed.");
            setTimeout(() => { resetUI(); startAutoScan(); }, RESULT_DISPLAY_MS);
        } finally {
            isScanning = false;
            scanBar && scanBar.classList.add("hidden");
        }
    }

    // ── Handle server checkin result ──────────────────────────────────────────
    function handleResult(res) {
        if (!res) return;
        if (res.status === "ok") {
            showSuccess(res);
            setTimeout(() => { resetUI(); startAutoScan(); }, RESULT_DISPLAY_MS);
        } else {
            const msgs = {
                outside: ["Outside Location", res.message || "Not within an allowed zone."],
                error:   ["Error", res.message || "An error occurred."],
            };
            const [title, msg] = msgs[res.status] || ["Failed", res.message || "Unknown error."];
            showError(title, msg);
            setTimeout(() => { resetUI(); startAutoScan(); }, RESULT_DISPLAY_MS);
        }
    }

    // ── UI helpers ────────────────────────────────────────────────────────────
    function hideAll() {
        statusBox   && statusBox.classList.add("hidden");
        successCard && successCard.classList.add("hidden");
        errorCard   && errorCard.classList.add("hidden");
    }

    function showIdle(title, sub) {
        hideAll();
        if (!statusBox) return;
        statusBox.querySelector("h2").textContent = title || "Position your face in the oval";
        statusBox.querySelector("p").textContent  = sub   || "Face recognition will start automatically";
        statusBox.classList.remove("hidden");
    }

    function showSuccess(res) {
        hideAll();
        if (!successCard) return;
        const isCheckIn = res.action === "check_in";
        document.getElementById("result_action_badge").textContent = isCheckIn ? "CHECK IN" : "CHECK OUT";
        document.getElementById("result_action_badge").className   = "action-badge " + (isCheckIn ? "check-in" : "check-out");
        document.getElementById("result_name").textContent         = res.employee_name || "";
        document.getElementById("result_time").textContent         = new Date().toLocaleTimeString();

        const locEl = document.getElementById("result_location");
        if (res.location) {
            locEl.textContent = "📍 " + res.location;
            locEl.classList.remove("hidden");
        } else {
            locEl.classList.add("hidden");
        }

        const pct = Math.round(res.confidence || 0);
        document.getElementById("confidence_fill").style.width = pct + "%";
        document.getElementById("confidence_pct").textContent  = pct + "%";

        successCard.classList.remove("hidden");
    }

    function showError(title, message) {
        hideAll();
        if (!errorCard) return;
        document.getElementById("error_title").textContent   = title;
        document.getElementById("error_message").textContent = message;
        errorCard.classList.remove("hidden");
    }

    function resetUI() {
        hideAll();
        showIdle("Position your face in the oval", "Face recognition will start automatically");
    }

    // ── JSON-RPC helper ────────────────────────────────────────────────────────
    async function rpcCall(url, params) {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", id: Date.now(), params }),
        });

        // Guard: if Odoo returned HTML (login redirect / 404 / error page)
        // instead of JSON, surface a useful message rather than a parse crash.
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            const text = await response.text();
            const preview = text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 200);
            throw new Error(
                `Server returned HTTP ${response.status} (${response.statusText}) — not JSON.\n` +
                `URL: ${url}\nResponse preview: ${preview}`
            );
        }

        const json = await response.json();
        if (json.error) {
            const msg = json.error.data?.message || json.error.message || JSON.stringify(json.error);
            throw new Error(msg);
        }
        return json.result;
    }

    // ── Odoo session init (ensures a public session cookie exists) ───────────
    async function ensureSession() {
        try {
            await fetch("/web/dataset/call_kw", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
                body: JSON.stringify({
                    jsonrpc: "2.0", method: "call", id: 1,
                    params: { model: "res.lang", method: "search_read",
                              args: [[]], kwargs: { fields: ["code"], limit: 1 } }
                }),
            });
        } catch (e) { /* ignore — just warming up the session */ }
    }

    // ── Boot sequence ─────────────────────────────────────────────────────────
    async function boot() {
        if (!app) return;
        try {
            await ensureSession();
            await Promise.all([
                loadFaceApi(),
                startCamera(),
                loadEmployeeDescriptors(),
            ]);
            startGPS();
            hideLoadingOverlay();
            showIdle("Position your face in the oval", "Face recognition will start automatically");
            startAutoScan();
        } catch (err) {
            setLoadingMessage("Failed to start: " + err.message);
            console.error("Kiosk boot error:", err);
        }
    }

    // ── Button handlers ───────────────────────────────────────────────────────
    btnScan  && btnScan.addEventListener("click",  () => { stopAutoScan(); triggerScan().then(startAutoScan); });
    btnRetry && btnRetry.addEventListener("click", () => { resetUI(); startAutoScan(); });

    // Boot after DOM ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

})();
