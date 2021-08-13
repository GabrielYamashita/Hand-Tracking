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
detector = HTM.handDetector(detectionCon=0.7, maxHands=1)

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
area = 0
colorVolume = (255, 0, 0)

# Aplicação:
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img, draw=False)
    lmList, boundingBox = detector.findPosition(img, draw=True)
    
    if len(lmList) != 0:
        # Filtro calculado com a Área:
        area = (boundingBox[2]-boundingBox[0]) * (boundingBox[3]-boundingBox[1]) // 100
        if 200 < area < 1250:
            # Distância entre Indicador e Dedão:
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # Coversão do Volume:
            volBar = np.interp(length, [50, 180], [400, 150]) # Conversão Posição-Barra
            volPercentage = np.interp(length, [50, 180], [0, 100]) # Conversão Posição-Porecentagem

            # Reduzindo o Step do Volume:
            smoothness = 10
            volPercentage = smoothness * round(volPercentage/smoothness)

            # Checando os Dedos para Cima>
            fingers = detector.fingersUp()

            # Dedinho para Setar o Volume:
            if not fingers[3]:
                volume.SetMasterVolumeLevelScalar(volPercentage/100, None) # Controle do Volume
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED) # Seta o volume quando o dedinho abaixa
                colorVolume = (0, 255, 0)
                time.sleep(0.2)
            else:
                colorVolume = (255, 0, 0)

        # Desenho da Barra de Volume:
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3) # Borda do Retângulo
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED) # Retângulo Volume
        cv2.putText(img, f'{int(volPercentage)}%', (25, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2) # Porcentagem
        cVol = int(volume.GetMasterVolumeLevelScalar()*100)
        cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVolume, 2)

    # FPS:
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

    # Inicialização da Câmera:
    cv2.imshow("Volume Control", img)
    cv2.waitKey(1)
