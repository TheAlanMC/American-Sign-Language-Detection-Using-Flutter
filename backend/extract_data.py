# Preprocesamiento del dataset para poder entrenar el modelo
import cv2
import os
import numpy as np


def image_processed(file_path):
    # Leemos la imagen, asumimos que las imagenes se encuentra enfocada solo la mano
    hand_img = cv2.imread(file_path)
    # Procesamos la imagen
    # 1. Convertir a escala de grises
    img_gray = cv2.cvtColor(hand_img, cv2.COLOR_BGR2GRAY)
    # 3. Darle un contraste
    img_gray = cv2.equalizeHist(img_gray)
    # 4. Darle la vuelta a la imagen
    img_gray = cv2.flip(img_gray, 1)
    # # 5. Convertir a un array
    img_gray = np.array(img_gray).reshape(-1)
    return img_gray


def make_csv():

    # Creamos un dataframe vacío
    mypath = 'dataset/asl_alphabet_train/asl_alphabet_train'
    file_name = open('american_train.csv', 'w')

    # Recorremos las carpetas
    for root, dirs, files in os.walk(mypath):
        # Ordenamos los archivos de forma alfabética
        dirs.sort()
        # Recorremos los archivos
        for file in files:
            if file.endswith('.jpg'):
                file_path = os.path.join(root, file)
                # Nos quedamos con el nombre de la carpeta
                label = file_path.split('/')[1].upper()
                # Añadimos la etiqueta
                file_name.write(label)
                # Procesamos la imagen
                data = image_processed(file_path)
                for i in data:
                    # Añadimos los datos al csv
                    file_name.write(str(i))
                    if i != data[-1]:
                        file_name.write(',')
                file_name.write('\n')
    # Cerramos el archivo
    file_name.close()
    print('CSV creado')


if __name__ == "__main__":
    make_csv()
