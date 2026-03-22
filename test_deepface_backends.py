# test_deepface_backends.py
from deepface import DeepFace
import cv2, os

frame_path = "test_frames/frame_00.jpg"
ref_path = "data/frank_1.jpg"

backends = ["opencv", "mtcnn", "retinaface", "mediapipe"]
for backend in backends:
    try:
        print("Probando backend:", backend)
        res = DeepFace.verify(frame_path, ref_path, enforce_detection=False, detector_backend=backend)
        print(res)
    except Exception as e:
        print("Error con backend", backend, ":", e)
    print("-" * 40)
