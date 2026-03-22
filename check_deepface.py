from deepface import DeepFace
res = DeepFace.verify("test_frames/frame_00.jpg", "data/frank_1.jpg", enforce_detection=False)
print(res)
