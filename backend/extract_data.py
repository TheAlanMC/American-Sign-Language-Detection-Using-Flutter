# Preprocesamiento del dataset para poder entrenar el modelo
import cv2
import os
import numpy as np
import pandas as pd


def image_processing(file_path):
    # Leemos la imagen
    hand_img = cv2.imread(file_path)
    # Procesamos la imagen
    # 1. Convertir a escala de grises
    img_gray = cv2.cvtColor(hand_img, cv2.COLOR_BGR2GRAY)
    # 3. Darle un contraste
    img_gray = cv2.equalizeHist(img_gray)
    # 4. Darle la vuelta a la imagen
    img_gray = cv2.flip(img_gray, 1)
    return img_gray


def image_processing_as_array(label, file_path):
    # Leemos la imagen
    hand_img = cv2.imread(file_path)
    # Procesamos la imagen
    # 1. Convertir a escala de grises
    img_gray = cv2.cvtColor(hand_img, cv2.COLOR_BGR2GRAY)
    # 3. Darle un contraste
    img_gray = cv2.equalizeHist(img_gray)
    # 4. Darle la vuelta a la imagen
    img_gray = cv2.flip(img_gray, 1)
    # 5. Escalar la imagen
    img_gray = cv2.resize(img_gray, (28, 28))
    # 5. Convertir a un array
    img_gray = np.array(img_gray).reshape(-1)
    # 6. Añadir la etiqueta
    img_array = np.append(label, img_gray)
    # 7. Devolver el array
    return img_array


def make_csv():
    mypath = 'dataset/asl_alphabet_train/asl_alphabet_train'
    file_name = open('american_train_200.csv', 'w')
    # add header
    file_name.write('label,')
    for i in range(200*200-1):
        file_name.write('pixel' + str(i) + ',')
    file_name.write('pixel' + str(200*200-1) + '\n')

    # Recorremos las carpetas
    for root, dirs, files in os.walk(mypath):
        # Ordenamos los archivos de forma alfabética
        dirs.sort()
        # Recorremos los archivos
        i = 0
        for file in files:
            if file.endswith('.jpg'):
                file_path = os.path.join(root, file)
                # Nos quedamos con el nombre de la carpeta
                label = file_path.split('/')[3].upper()
                # Procesamos la imagen
                data = image_processing_as_array(label, file_path)
                np.savetxt(file_name, data.reshape(
                    1, -1), delimiter=',', fmt='%s')
                i += 1
            if i == 1000:
                break
    # Cerramos el archivo
    file_name.close()
    print('CSV creado')


def make_bw():
    mypath = 'dataset/asl_alphabet_train/asl_alphabet_train'
    # Recorremos las carpetas
    for root, dirs, files in os.walk(mypath):
        # Ordenamos los archivos de forma alfabética
        dirs.sort()
        # Recorremos los archivos
        for file in files:
            if file.endswith('.jpg'):
                file_path = os.path.join(root, file)
                # Procesamos la imagen
                data = image_processing(file_path)
                cv2.imwrite(file_path, data)
    print('Imagenes convertidas a blanco y negro')


if __name__ == "__main__":
    # make_bw()
    make_csv()
