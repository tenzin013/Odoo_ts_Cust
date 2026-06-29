/** @odoo-module **/
/**
 * Face Enrollment Widget — Client-Side face-api.js
 * Registered in the "view_widgets" registry so it can be used as
 * <widget name="FaceCaptureWidget"/> inside an hr.employee form view.
 */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, useRef, onWillUnmount, xml } from "@odoo/owl";

const FACEAPI_CDN = "https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js";
const MODELS_URL  = "/hr_attendance_face_detection/static/models";

let _faceApiReady = null;

function ensureFaceApi() {
    if (_faceApiReady) return _faceApiReady;
    _faceApiReady = (async () => {
        if (!window.faceapi) {
            await new Promise((res, rej) => {
                const s = document.createElement("script");
                s.src = FACEAPI_CDN;
                s.onload = res;
                s.onerror = () => rej(new Error("Failed to load face-api.js from CDN"));
                document.head.appendChild(s);
            });
        }
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(MODELS_URL),
            faceapi.nets.faceLandmark68TinyNet.loadFromUri(MODELS_URL),
            faceapi.nets.faceRecognitionNet.loadFromUri(MODELS_URL),
        ]);
    })();
    return _faceApiReady;
}

class FaceCaptureWidget extends Component {
    static props = {
        // view_widgets receive these standard props; we only need record
        record: { type: Object },
        readonly: { type: Boolean, optional: true },
        // accept (and ignore) any extra props Odoo passes
        "*": true,
    };

    static template = xml`
<div class="o_face_capture_widget">
    <!-- Status message -->
    <t t-if="state.statusMsg">
        <div class="alert alert-info py-1 mb-2" t-esc="state.statusMsg"/>
    </t>

    <!-- Video always in DOM; hidden until streaming (avoids null ref timing issue) -->
    <video t-ref="video" autoplay="autoplay" muted="muted"
           t-att-style="state.streaming ? 'width:320px;height:240px;border-radius:6px;display:block;margin-bottom:8px;' : 'display:none'"/>

    <!-- Canvas preview (shown after capture) -->
    <canvas t-ref="canvas"
            t-att-style="state.captured ? 'width:320px;height:240px;border-radius:6px;display:block;margin-bottom:8px;' : 'display:none'"/>

    <!-- Buttons -->
    <div class="d-flex gap-2 flex-wrap">
        <t t-if="!state.streaming and !state.captured">
            <button class="btn btn-primary btn-sm"
                    t-on-click="startCamera"
                    t-att-disabled="state.modelLoading">
                <i class="fa fa-camera me-1"/>
                <t t-if="state.modelLoading">Loading models…</t>
                <t t-else="">Capture from Webcam</t>
            </button>
        </t>
        <t t-if="state.streaming">
            <button class="btn btn-success btn-sm" t-on-click="captureSnapshot">
                <i class="fa fa-circle me-1"/>Capture
            </button>
            <button class="btn btn-secondary btn-sm" t-on-click="_stopStream">
                Cancel
            </button>
        </t>
        <t t-if="state.captured">
            <button class="btn btn-primary btn-sm"
                    t-on-click="saveEncoding"
                    t-att-disabled="state.loading">
                <i class="fa fa-save me-1"/>
                <t t-if="state.loading">Saving…</t>
                <t t-else="">Save Encoding</t>
            </button>
            <button class="btn btn-secondary btn-sm"
                    t-on-click="retake"
                    t-att-disabled="state.loading">
                <i class="fa fa-refresh me-1"/>Retake
            </button>
        </t>
    </div>
</div>`;

    setup() {
        this.notification = useService("notification");
        this.orm          = useService("orm");
        this.videoRef     = useRef("video");
        this.canvasRef    = useRef("canvas");
        this.state        = useState({
            streaming:    false,
            captured:     false,
            loading:      false,
            modelLoading: false,
            statusMsg:    "",
        });
        this._stream = null;
        onWillUnmount(() => this._stopStream());
    }

    async startCamera() {
        this.state.modelLoading = true;
        this.state.statusMsg    = "Loading AI models…";
        try {
            await ensureFaceApi();
            this._stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: "user" },
                audio: false,
            });
            // Set streaming=true first so the <video> element renders,
            // then assign srcObject on the next microtask tick.
            this.state.streaming = true;
            this.state.captured  = false;
            this.state.statusMsg = "Position face in frame, then click Capture.";
            await new Promise(r => setTimeout(r, 0));
            const video = this.videoRef.el;
            if (!video) throw new Error("Video element not found after render");
            video.srcObject = this._stream;
            await video.play();
        } catch (err) {
            this.notification.add(`Camera / model error: ${err.message}`, { type: "danger" });
            this.state.statusMsg = "";
        } finally {
            this.state.modelLoading = false;
        }
    }

    captureSnapshot() {
        const video  = this.videoRef.el;
        const canvas = this.canvasRef.el;
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        this.state.captured  = true;
        this.state.statusMsg = "Snapshot captured. Click Save Encoding.";
        this._stopStream();
    }

    retake() {
        this.state.captured  = false;
        this.state.statusMsg = "";
        this.startCamera();
    }

    async saveEncoding() {
        const canvas = this.canvasRef.el;
        this.state.loading   = true;
        this.state.statusMsg = "Detecting face and computing descriptor…";
        try {
            await ensureFaceApi();
            const options   = new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.5 });
            const detection = await faceapi
                .detectSingleFace(canvas, options)
                .withFaceLandmarks(true)
                .withFaceDescriptor();

            if (!detection) {
                this.notification.add(
                    "No face detected. Please retake with a clearer frontal photo.",
                    { type: "warning" }
                );
                this.state.statusMsg = "";
                return;
            }

            const descriptorArray = Array.from(detection.descriptor);
            const b64 = canvas.toDataURL("image/jpeg", 0.92).split(",")[1];

            const response = await fetch("/hr_attendance_face/enroll_descriptor", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    jsonrpc: "2.0", method: "call", id: Date.now(),
                    params: {
                        employee_id: this.props.record.resId,
                        face_image:  b64,
                        descriptor:  descriptorArray,
                    },
                }),
            });

            const ct = response.headers.get("content-type") || "";
            if (!ct.includes("application/json")) {
                const text    = await response.text();
                const preview = text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 200);
                throw new Error(`Server returned non-JSON (HTTP ${response.status}): ${preview}`);
            }

            const json = await response.json();
            if (json.error) throw new Error(json.error.data?.message || json.error.message);
            if (json.result?.status !== "ok") throw new Error(json.result?.message || "Enrolment failed");

            this.notification.add("Face descriptor saved successfully!", { type: "success" });
            this.state.statusMsg = "Enrolled ✓";
            this.state.captured  = false;
            this.props.record.load();
        } catch (err) {
            this.notification.add(`Error: ${err.message}`, { type: "danger" });
            this.state.statusMsg = "";
        } finally {
            this.state.loading = false;
        }
    }

    _stopStream() {
        if (this._stream) {
            this._stream.getTracks().forEach(t => t.stop());
            this._stream = null;
        }
        this.state.streaming = false;
    }
}

// ── Register in view_widgets (required for <widget name="..."/> in form views) ──
registry.category("view_widgets").add("FaceCaptureWidget", {
    component: FaceCaptureWidget,
});
