import cv2
import numpy as np
import time
def get_face_features(name):
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

    scale=1.0
    deviceId=0
    cap = cv2.VideoCapture(deviceId,cv2.CAP_DSHOW)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale)
    detector.setInputSize([frame_width, frame_height])
    recognizer = cv2.FaceRecognizerSF.create(FACE_RECOGNITION_MODEL, "")
    face_found=False
    face_features=None
    start_time=time.perf_counter()
    while time.perf_counter()-start_time<2:
        has_frame, frame = cap.read()
        if not has_frame:
            print('Захват видео не удался')
            return None
        faces_found,face_points = detector.detect(frame)  # faces is a tuple
        print("faces_found",faces_found)
            #если удалось обнаружить лицо
        if  type(face_points)==np.ndarray:
            face_found=True
            face_align = recognizer.alignCrop(frame, face_points)
            face_features = recognizer.feature(face_align)
            break
    cap.release()
    cv2.destroyAllWindows()
    return face_features