import cv2
import mediapipe as mp
import pandas as pd
import os
import numpy as np


def image_processed(file_path):
    hand_img = cv2.imread(file_path)
    # 1. Convertir a RGB
    img_rgb = cv2.cvtColor(hand_img, cv2.COLOR_BGR2RGB)
    # 2. Dar la vuelta a la imagen
    img_flip = cv2.flip(img_rgb, 1)
    mp_hands = mp.solutions.hands
    # Inicializamos las manos
    hands = mp_hands.Hands(static_image_mode=True,
                           max_num_hands=1, min_detection_confidence=0.7)
    # Resultados de la detección
    output = hands.process(img_flip)
    hands.close()
    # Extraemos la información de las manos
    try:
        data = output.multi_hand_landmarks[0]
        # print(data)
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
        return (finalClean)

    # Si no detecta ninguna mano, devuelve un array de ceros
    except:
        return (np.zeros([1, 42], dtype=int)[0])


def make_csv():
    my_path = '/Users/chrisalanapazaaguilar/Documents/Others/ASL Recognition With Flutter/ai/scikit-learn/'
    file_name = open(my_path+'american_train_dataset.csv', 'w')
    # Recorremos las carpetas
    for root, dirs, files in os.walk(my_path+'dataset/Train'):
        dirs.sort()
        # Recorremos los archivos
        for file in files:
            if file.endswith('.jpg'):
                file_path = os.path.join(root, file)

                # Nos quedamos con el nombre de la carpeta
                label = file_path.split('/')[-2]
                # Procesamos la imagen
                data = image_processed(file_path)

                for i in data:
                    # Añadimos los datos al csv
                    file_name.write(str(i))
                    file_name.write(',')

                # Añadimos la etiqueta
                file_name.write(label)
                file_name.write('\n')

    # Cerramos el archivo
    file_name.close()
    print('CSV creado')


if __name__ == "__main__":
    make_csv()
