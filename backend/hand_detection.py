import tensorflow as tf
import cv2
import numpy as np


cap = cv2.VideoCapture(0)

# cargamos el modelo
path = 'model.tflite'  # ruta del modelo
interpreter = tf.lite.Interpreter(model_path=path)
interpreter.allocate_tensors()
# obtenemos los detalles de la entrada
input_details = interpreter.get_input_details()
# obtenemos los detalles de la salida
output_details = interpreter.get_output_details()


def image_processing_as_array(hand_img):
    # Procesamos la imagen
    # 1. Convertir a escala de grises
    img_gray = cv2.cvtColor(hand_img, cv2.COLOR_BGR2GRAY)
    # 3. Darle un contraste
    img_gray = cv2.equalizeHist(img_gray)
    # 4. Darle la vuelta a la imagen
    # img_gray = cv2.flip(img_gray, 1)
    # 5. Escalar la imagen
    img_gray = cv2.resize(img_gray, (28, 28))
    # 6. Convertir a un array
    img_gray = np.array(img_gray).reshape(-1)
    # 7. Normalizar los datos
    img_gray = img_gray / 255.0
    # 8. Convertir a un array de 3 dimensiones
    img_gray = img_gray.reshape(-1, 28, 28, 1)
    return img_gray


while cap.isOpened():
    success, image = cap.read()

    # para mejorar el rendimiento marcamos la imagen como no mutable para pasarlo por referencia
    image.flags.writeable = False

    # damos la vuelta a la imagen
    image = cv2.flip(image, 1)

    w, h, _ = image.shape

    # cuadro en el centro de la imagen de 500x500

    # 1. Obtenemos el centro de la imagen
    center_x = w // 2
    center_y = h // 2

    # 2. Obtenemos el punto de inicio del cuadro
    start_x = center_x - 250
    start_y = center_y - 250

    # 3. Obtenemos el punto final del cuadro
    end_x = center_x + 250
    end_y = center_y + 250

    # 4. Dibujamos el cuadro
    cv2.rectangle(image, (start_y, start_x), (end_y, end_x), (0, 255, 0), 2)

    # 5. Obtenemos la imagen del cuadro
    hand_img = image[start_x:end_x, start_y:end_y]

    # procesamos la imagen
    img = image_processing_as_array(hand_img)

    # predecimos la imagen
    input_shape = input_details[0]['shape']
    input_data = np.array(img, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()  # invocamos el modelo
    output_data = interpreter.get_tensor(
        output_details[0]['index'])  # obtenemos la salida

    # obtenemos la etiqueta de la prediccion
    with open('labels.txt', 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    prediction = np.argmax(output_data)  # obtenemos el indice de la prediccion
    # print(labels[prediction])  # imprimimos la etiqueta de la prediccion

    # imprimimos la prediccion en la imagen
    cv2.putText(image, labels[prediction], (5, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('Detecion de manos', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()
