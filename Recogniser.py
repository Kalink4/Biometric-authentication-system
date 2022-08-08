import cv2
import db_module
from cv2 import imwrite
import numpy as np
import mediapipe as mp 
import time
import math
from tkinter import messagebox
def main_app(users):
    FACE_DETECTION_MODEL="models\\face_detection_yunet_2022mar.onnx"
    FACE_RECOGNITION_MODEL="models\\face_recognition_sface_2021dec.onnx"
    SCORE_THRESHOLD=0.9
    NMS_THRESHOLD=0.3
    TOP_K=5000
    detector = cv2.FaceDetectorYN.create(
        FACE_DETECTION_MODEL,
        "",
        (320, 320),
        SCORE_THRESHOLD,
        NMS_THRESHOLD,
        TOP_K
        )
    user=None
    scale=1.0
    deviceId=0
    cap = cv2.VideoCapture(deviceId,cv2.CAP_DSHOW)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale)
    detector.setInputSize([frame_width, frame_height])
    recognizer = cv2.FaceRecognizerSF.create(FACE_RECOGNITION_MODEL, "")
    #установка таймера,чтобы не ждать сто лет, если что-то пошло нетак
    face_found=False
    start_time=time.perf_counter()
    while time.perf_counter()-start_time<2:
        has_frame, frame = cap.read()
        if not has_frame: 
            print('Захват видео не удался')
            break
        #cv2.imshow('Auth', frame)
        face_found,face_points = detector.detect(frame)  # faces is a tuple
        #если удалось обнаружить лицо
        if  face_found:
            face1_align = recognizer.alignCrop(frame, face_points)
            face1_features = recognizer.feature(face1_align)
            frame = cv2.flip(frame, 1)
            break
    cap.release()
    cv2.destroyAllWindows()
    if face_found:
        COSINE_SIMILARITY_THRESHOLD = 0.363
        user_found=False
        #поиск человека по фото в базе данных
        for user,face2_features in users.items():
            cosine_score = recognizer.match(face1_features, face2_features, cv2.FaceRecognizerSF_FR_COSINE)
            if cosine_score >= COSINE_SIMILARITY_THRESHOLD:
                user_found=True
                break
        if  user_found:
            messagebox.showinfo("", "Пожалуйста, посмотрите вперед, а потом в любом направлении")
            is_alive,forward_frame,somewhere_frame=check_aliveness()
            if is_alive:
                face_forward = detector.detect(forward_frame)
                face_forward_align = recognizer.alignCrop(forward_frame, face_forward[1][0])
                face_forward_features = recognizer.feature(face_forward_align)
                #проверка сходства фото из базы и фото с камеры
                cosine_score = recognizer.match(face_forward_features, face2_features, cv2.FaceRecognizerSF_FR_COSINE)
                if cosine_score < COSINE_SIMILARITY_THRESHOLD:
                    check_forward = False
                else:
                    check_forward=True
                #somewhere_face = detector.detect(somewhere_frame)
                print("alive")
                face_somewhere_align = recognizer.alignCrop(somewhere_frame, face_forward[1][0])
                face_somewhere_features = recognizer.feature(face_somewhere_align)
                #проверка сходства фото из базы и фото с камеры
                cosine_score = recognizer.match(face_somewhere_features, face2_features, cv2.FaceRecognizerSF_FR_COSINE)
                if cosine_score < COSINE_SIMILARITY_THRESHOLD:
                    check_somewhere = False
                else:
                    check_somewhere=True
                if not (check_somewhere and check_forward):
                    user=None
            else:
                user=None
        else:
            user=None
            print("Проверка не пройдена")
    else:
        print("Лицо не распознано")
    return user

def check_aliveness():
    def get_distance(point1,point2):
        #print(point1,point2)
        x1,y1=point1
        x2,y2=point2
        distance=math.sqrt((x1-x2)**2+(y1-y2)**2)
        #print("distance", distance)
        return distance

    mp_face_mesh = mp.solutions.face_mesh
    LEFT_IRIS = [474,475, 476, 477]
    LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh: 
        look_forward=False
        look_somwhere=False
        check_passed=False
        start_time=time.perf_counter()
        while time.perf_counter()-start_time<5:
            success, image = cap.read()
            if not success:
                print("Изображение не получено")
                break
            image.flags.writeable = True
            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_image)
            #если точки получены
            if results.multi_face_landmarks:
                img_h, img_w = image.shape[:2]
                mesh_points=np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])
                (l_cx, l_cy), iris_l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
                (eye_l_cx, eye_l_cy), eye_l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_EYE]) 
                center_left_eye=np.array([eye_l_cx, eye_l_cy], dtype=np.int32)
                center_left_iris = np.array([l_cx, l_cy], dtype=np.int32)
                eye_l_radius=eye_l_radius*0.90
                cv2.circle(image, center_left_eye, int(eye_l_radius), (50,50,0), 1, cv2.LINE_AA)
                cv2.circle(image, center_left_iris, int(iris_l_radius), (86,228,250), 1, cv2.LINE_AA)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                d=get_distance(center_left_eye, center_left_iris)
                #для прохождения проверки необходимо сначала посмотреть вперед, а потом в любом направлении
                if look_forward:
                    if eye_l_radius-iris_l_radius<d<eye_l_radius+iris_l_radius:
                        look_somwhere=True
                        look_somwhere_image=image
                        break
                else:
                    if not (eye_l_radius-iris_l_radius<d<eye_l_radius+iris_l_radius):
                        look_forward_image=image
                        look_forward=True
            else:
                print("facemesh не получен")
                check_passed=False
        if look_forward and look_somwhere:
            check_passed=True
        if not check_passed:
                look_forward_image=None
                look_somwhere_image=None
        print("проверка пройдена", check_passed)
        return check_passed,look_forward_image,look_somwhere_image
