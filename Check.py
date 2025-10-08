import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    cv2.imshow('Live Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()








# import cv2
# import time
#
# cap = cv2.VideoCapture(0)
#
# # Try setting higher FPS and lower resolution
# cap.set(cv2.CAP_PROP_FPS, 60)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#
# # Initialize timing
# prev_time = time.time()
# frame_count = 0
# fps=0
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     frame_count += 1
#     current_time = time.time()
#     elapsed = current_time - prev_time
#
#     # Update FPS every second
#     if elapsed >= 1:
#         fps = frame_count / elapsed
#         frame_count = 0
#         prev_time = current_time
#
#     # Display FPS on frame
#     cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#
#     cv2.imshow("Webcam FPS", frame)
#     if cv2.waitKey(1) == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()