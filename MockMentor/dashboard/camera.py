import cv2
import os
import urllib.request
import numpy as np
from django.conf import settings
import mediapipe as mp
from dashboard.eyeGazeDetection import iris_position_detection
from dashboard.emotionDetection import face_emotion_detection
import time


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.questions = ['question1', 'question2', 'question3']
        self.index = 0
        self.n = 3

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        frame_flip = cv2.flip(image, 1)
        question = self.questions[self.index]
        cv2.putText(image, "question", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # time.sleep(5)  # Wait for 5 seconds
        # self.index = (self.index + 1) % self.n

        # results = mp.solutions.face_mesh.process(
        #     cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # if results.multi_face_landmarks:
        #     iris_position_detection(frame_flip, results, True)
        # face_emotion_detection(frame_flip)
        map_face_mesh = mp.solutions.face_mesh
        with map_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
            results = face_mesh.process(frame_flip)
            face_emotion_detection(frame_flip)
            if results.multi_face_landmarks:
                iris_position_detection(frame_flip, results, True)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()


class IPWebCam(object):
    def __init__(self, key):
        self.url = key + "/shot.jpg"

    def __del__(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        print(self.url)
        imgResp = urllib.request.urlopen(self.url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # faces_detected = face_detection_webcam.detectMultiScale(
        #     gray, scaleFactor=1.3, minNeighbors=5)
        # for (x, y, w, h) in faces_detected:
        #     cv2.rectangle(img, pt1=(x, y), pt2=(x + w, y + h),
        #                   color=(255, 0, 0), thickness=2)
        resize = cv2.resize(img, (640, 480), interpolation=cv2.INTER_LINEAR)
        frame_flip = cv2.flip(resize, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()
