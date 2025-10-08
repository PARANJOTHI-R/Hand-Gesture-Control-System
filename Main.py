import cv2
import numpy as np
import Handtracking as htm
import time
import autopy

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
frameR = 100
smoothening = 5
sensitivity = 2.0
clickCooldown = 0.4
lastClickTime = 0
alpha = 0.65
deadzone = 2
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(cv2.CAP_PROP_FPS, 60)

detector = htm.handDetector(maxHands=1)


wScr, hScr = 1920, 1080

while True:

    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)


    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]


        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        # 🔊 Gesture: Hand Open → Unmute
        currentTime = time.time()
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

        if fingers[1] == 1 and fingers[2] == 0:

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr * sensitivity))  # 📌 Sensitivity applied
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr * sensitivity))  # 📌 Sensitivity applied


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


            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY


        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)


            if length < 40:
                currentTime = time.time()
                if currentTime - lastClickTime > clickCooldown:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                               15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()
                    lastClickTime = currentTime


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)
