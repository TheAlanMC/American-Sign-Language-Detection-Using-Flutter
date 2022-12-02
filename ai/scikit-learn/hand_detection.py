import time
import cv2
import mediapipe as mp
import joblib
import numpy as np
import os

# temporizador para introducir cada letra
mytext = ''
prev_time = time.time()
curr_time = time.time()

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Inicializamos las manos
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       max_num_hands=1, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)
clf = joblib.load(
    '/Users/chrisalanapazaaguilar/Documents/Others/ASL Recognition With Flutter/ai/scikit-learn/model.pkl')
# limpieza de datos


def data_clean(landmark):

    data = landmark[0]

    try:
        data = str(data)
        data = data.strip().split('\n')
        garbage = ['landmark {', '  visibility: 0.0', '  presence: 0.0', '}']

        # Eliminamos los datos que no nos interesan
        without_garbage = []

        for i in data:
            if i not in garbage:
                without_garbage.append(i)

        # Limpiamos los datos
        clean = []

        for i in without_garbage:
            i = i.strip()
            clean.append(i[2:])

        # Eliminamos el eje z
        finalClean = []
        for i in range(0, len(clean)):
            if (i+1) % 3 != 0:
                finalClean.append(float(clean[i]))
        return ([finalClean])

    except:
        return (np.zeros([1, 42], dtype=int)[0])


while cap.isOpened():
    success, image = cap.read()

    image = cv2.flip(image, 1)
    #image = cv2.flip(image, -1)

    h, w, c = image.shape                 # altura, anchura y profundidad de la imagen

    if not success:
        break

    # damos la vuelta a la imagen horizontalmente para una visualización más cómoda y convertimos a RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # para mejorar el rendimiento marcamos la imagen como no mutable para pasarlo por referencia
    image.flags.writeable = False
    results = hands.process(image)

    # dibujammos la detección de mano
    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cleaned_landmark = data_clean(results.multi_hand_landmarks)
        # print(cleaned_landmark)

        if cleaned_landmark:
            y_pred = clf.predict(cleaned_landmark)
            if (str(y_pred[0]) == 'SPACE' and mytext != ''):
                prev_time = time.time()
                mytext = ''
            elif (str(y_pred[0]) != 'SPACE'):
                cv2.putText(image, str(
                    y_pred[0]), (w-200, 70), cv2.FONT_HERSHEY_DUPLEX, 3, (52, 195, 235), 3)
                curr_time = time.time()
                diff_time = curr_time - prev_time
                if diff_time < 1:
                    display_time = 3
                elif diff_time < 2:
                    display_time = 2
                elif diff_time <= 3:
                    display_time = 1
                cv2.putText(image, str(display_time), (10, 70),
                            cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 3)
        if curr_time - prev_time > 3:
            mytext += str(y_pred[0])
            prev_time = time.time()
            cv2.putText(image, "Ok", (w//2, h//2),
                        cv2.FONT_HERSHEY_DUPLEX, 3, (235, 107, 52), 3)
    else:
        prev_time = time.time()
    cv2.putText(image, mytext, (10, h - 50),
                cv2.FONT_HERSHEY_DUPLEX, 3, (235, 143, 52), 3)
    cv2.imshow('Detecion de manos', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
