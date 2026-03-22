import cv2, os
os.makedirs("captures", exist_ok=True)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
ret, frame = cap.read()
if ret:
    cv2.imwrite("captures/frame_for_debug.jpg", frame)
    print("Saved captures/frame_for_debug.jpg shape=", frame.shape, "dtype=", frame.dtype)
else:
    print("No frame captured (ret=False)")
cap.release()
