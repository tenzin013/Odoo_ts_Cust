# face-api.js Model Files

Place the following model files in this directory so the kiosk works **offline**
(no CDN dependency). Download from:
https://github.com/justadudewhohacks/face-api.js/tree/master/weights

Required files:
- tiny_face_detector_model-weights_manifest.json
- tiny_face_detector_model-shard1
- face_landmark_68_tiny_model-weights_manifest.json
- face_landmark_68_tiny_model-shard1
- face_recognition_model-weights_manifest.json
- face_recognition_model-shard1
- face_recognition_model-shard2

If these files are absent, the kiosk loads models from CDN (requires internet).
Change MODELS_URL in face_api_kiosk.js and face_enrollment.js to point here.

Current MODELS_URL = '/hr_attendance_face_detection/static/models'
