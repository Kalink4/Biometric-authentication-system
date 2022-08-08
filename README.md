# Biometric-authentication-system
**Система биометрической аутентификации по изображению лица с защитой от атаки подмены**

Чтобы пройти проверку витальности, сначала необходимо посмотреть прямо в камеру, а после этого отвести взгляд в сторону.
Установка зависимостей: 'pip install requirements.txt'
* Проверка осуществляется с помощью модуля facemesh Mediapipe.
* Для обнаружения и распознавания лиц используются модели: face_detection_yunet_2022mar.onnx и face_recognition_sface_2021dec.onnx. 
![screen-gif](./demo_auth.gif)

_За основу для GUI взят проект: https://github.com/joeVenner/FaceRecognition-GUI-APP._
