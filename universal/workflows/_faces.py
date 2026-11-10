"""Where is the face? Run by the modules' Python, which has OpenCV: python _faces.py video model.onnx samples_per_second
Prints one JSON line: samples with the face centre as a share of the frame, and how often a face was found."""
import json
import sys

import cv2

src, model, rate = sys.argv[1], sys.argv[2], float(sys.argv[3])
cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
step = max(1, round(fps / rate))
detector, samples, i = None, [], 0
while cap.grab():
    if i % step == 0:
        ok, frame = cap.retrieve()
        if ok:
            h, w = frame.shape[:2]
            k = 640 / max(w, h)
            small = cv2.resize(frame, (max(2, round(w * k)), max(2, round(h * k)))) if k < 1 else frame
            sh, sw = small.shape[:2]
            if detector is None:
                detector = cv2.FaceDetectorYN.create(model, '', (sw, sh), 0.6, 0.3, 50)
            _, faces = detector.detect(small)
            row = {'t': round(i / fps, 3)}
            if faces is not None and len(faces):
                f = max(faces, key=lambda r: r[2] * r[3] * r[-1])
                row.update(x=round(float(f[0] + f[2] / 2) / sw, 4), y=round(float(f[1] + f[3] / 2) / sh, 4), w=round(float(f[2]) / sw, 4))
            samples.append(row)
    i += 1
print(json.dumps({'samples': samples, 'coverage': round(sum('x' in r for r in samples) / max(1, len(samples)), 3)}))
