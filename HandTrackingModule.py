# Imports
import cv2
import mediapipe as mp
import time
import math


class handDetector():
    # Init
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.tipIds = [4, 8, 12, 16, 20]


    # Método para achar as mãos
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img


    # Método para Achar a Posição dos Pontos 
    def findPosition(self, img, handNumber=0, draw=True):
        xList = []
        yList = []
        boundingBox = []

        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNumber]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                xList.append(cx)
                yList.append(cy)

                self.lmList.append([id, cx, cy])

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            boundingBox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (boundingBox[0]-20, boundingBox[1]-20),
                 (boundingBox[2]+20, boundingBox[3]+20), (0, 255, 0), 2)
        return self.lmList, boundingBox


    # Método para Checar Quais Dedos Estão para Cima:
    def fingersUp(self, D=True):
        fingers = []
        
        # Dedão
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]: # Mão Direita
            fingers.append(1)
        # if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1] and E: # Mão Esquerda
        #     fingers.append(1)
        else:
            fingers.append(0)

        # Outros Dedos
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    # Método para Achar a Distância entre Dois Dedos
    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]  # Posição Dedão
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]  # Posição Indicador
        cx, cy = (x1+x2)//2, (y1+y2)//2  # Posição Ponto Médio

        if draw:
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)  # Círculo do Dedão
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)  # Círculo do Indicador
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3) # Linha entre o Dedão e Indicador
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)  # Círculo do Ponto Médio

        length = math.hypot(x2-x1, y2-y1)  # Tamanho
        return length, img, [x1, y1, x2, y2, cx, cy]


# Hand Tracking Module
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList)

        # FPS:
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        # Inicialização:
        cv2.imshow("Hand Tracking", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()