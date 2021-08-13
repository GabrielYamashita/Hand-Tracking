# Imports:
import cv2
import time
import numpy as np
import math

import HandTrackingModule as HTM

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Configs:
# Configs Câmera
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# App Hand Tracking
detector = HTM.handDetector(detectionCon=0.7)

# Configs Volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVolume = volRange[0]
maxVolume = volRange[1]

# Variáveis Importantes
pTime = 0
vol = 0
volBar = 400
volPercentage = 0

# Aplicação:
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img, draw=True)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        # Filter based on Size:

        # Find Distance Between Index and Thumb

        # Convert Volume

        # Reduce Resolution to Make It Smoother

        # Check Fingers Up

        # If Pinky is Down Set Volume 

        # Drawings

        # Frame Rate (FPS)

        x1, y1 = lmList[4][1], lmList[4][2]  # Posição Dedão
        x2, y2 = lmList[8][1], lmList[8][2]  # Posição Indicador
        cx, cy = (x1+x2)//2, (y1+y2)//2  # Posição Ponto Médio

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)  # Círculo do Dedão
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)  # Círculo do Indicador
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3) # Linha entre o Dedão e Indicador
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)  # Círculo do Ponto Médio

        length = math.hypot(x2-x1, y2-y1)  # Tamanho

        # Hand Range (50 - 200)
        # Volume Range (-65 - 0)
        vol = np.interp(length, [50, 200], [minVolume, maxVolume]) # Conversão Posição-Volume
        volBar = np.interp(length, [50, 200], [400, 150]) # Conversão Posição-Barra
        volPercentage = np.interp(length, [50, 220], [0, 100]) # Conversão Posição-Porecentagem
        
        volume.SetMasterVolumeLevel(vol, None)  # Controle do Volume

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED) # Muda Valor quando Igual a 0

    # Desenho da Barra de Volume:
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3) # Borda do Retângulo
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED) # Retângulo Volume
    cv2.putText(img, f'{int(volPercentage)}%', (25, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2) # Porcentagem

    # FPS:
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (25, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # Inicialização da Câmera:
    cv2.imshow("Volume Control", img)
    cv2.waitKey(1)
