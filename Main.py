import cv2
import numpy as np
import Handtracking as htm
import time
import pyautogui

# 🔇 Audio control setup for mute/unmute
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

isMuted = False
muteCooldown = 1.0
lastMuteTime = 0

##########################
wCam, hCam = 640, 480
frameR = 50
smoothening = 5
sensitivity = 2.0   # 👈 Increased sensitivity for faster cursor response
clickCooldown = 0.4
lastClickTime = 0
scrollCooldown = 0.0000001
lastScrollTime = 0
scrollSpeed = 85
alpha = 0.65      # 👈 Increased alpha for less laggy smoothing (more responsive)
deadzone = 2        # 👈 Reduced deadzone to react to smaller movements
#########################
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(cv2.CAP_PROP_FPS, 60)

detector = htm.handDetector(maxHands=1)
wScr, hScr = pyautogui.size()

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        fingers = detector.fingersUp()

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        currentTime = time.time()

        # 1. 🔇 Audio Control (Mute/Unmute)
        # 🔊 Gesture: Hand Open → Unmute
        if fingers == [1, 1, 1, 1, 1] and isMuted and currentTime - lastMuteTime > muteCooldown:
            volume.SetMute(0, None)
            isMuted = False
            lastMuteTime = currentTime
            cv2.putText(img, "🔊 Unmuted", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # 🔇 Gesture: Hand Closed → Mute
        elif fingers == [0, 0, 0, 0, 0] and not isMuted and currentTime - lastMuteTime > muteCooldown:
            volume.SetMute(1, None)
            isMuted = True
            lastMuteTime = currentTime
            cv2.putText(img, "🔇 Muted", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        # --- SCROLL FUNCTIONALITY ---
        elif currentTime - lastScrollTime > scrollCooldown:

            # 📜 Scroll UP Gesture: Index, Middle, Ring UP (0, 1, 1, 1, 0)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[0] == 0 and fingers[4] == 0:
                pyautogui.scroll(scrollSpeed)  # Positive value scrolls up
                lastScrollTime = currentTime
                cv2.putText(img, "⬆️ Scroll UP", (400, 450), cv2.FONT_HERSHEY_PLAIN, 2, (255, 165, 0), 3)

            # 📜 Scroll DOWN Gesture: Pinky UP (0, 0, 0, 0, 1)
            elif fingers == [0, 0, 0, 0, 1]:
                pyautogui.scroll(-scrollSpeed)  # Negative value scrolls down
                lastScrollTime = currentTime
                cv2.putText(img, "⬇️ Scroll DOWN", (400, 450), cv2.FONT_HERSHEY_PLAIN, 2, (255, 165, 0), 3)

        # 2. 🖱️ Mouse Movement: Index finger up
        # Only process movement if we are not in a scrolling state (handled by 'elif' above)
        # The movement check needs to ensure the ring/pinky aren't accidentally up,
        # but your original code only checks fingers[1] and fingers[2]. Let's stick to that.
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr * sensitivity))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr * sensitivity))

            dx = abs(x3 - plocX)
            dy = abs(y3 - plocY)

            if dx > deadzone or dy > deadzone:
                clocX = alpha * x3 + (1 - alpha) * plocX
                clocY = alpha * y3 + (1 - alpha) * plocY
            else:
                clocX = plocX
                clocY = plocY

            clocX = max(0, min(clocX, wScr - 1))
            clocY = max(0, min(clocY, hScr - 1))

            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 3. 🖱️ Click Gesture: Index + Middle finger pinch
        # This gesture check must be separate from the scroll and move checks.
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            length, img, lineInfo = detector.findDistance(8, 12, img)

            # Check for short distance (pinch) and click cooldown
            if length < 40 and currentTime - lastClickTime > clickCooldown:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                lastClickTime = currentTime

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Virtual Mouse and Scroll", img)
    cv2.waitKey(1)