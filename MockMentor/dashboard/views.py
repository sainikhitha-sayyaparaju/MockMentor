from django.shortcuts import render, redirect
from . forms import *
from . models import *
from django.contrib import messages
from django.http.response import StreamingHttpResponse
from django.http.response import StreamingHttpResponse, HttpResponse
from dashboard.camera import VideoCamera, IPWebCam
from PIL import Image
from io import BytesIO
import base64
import mediapipe as mp
import cv2
from dashboard.emotionDetection import face_emotion_detection
from dashboard.eyeGazeDetection import iris_position_detection
# from checkLocation import process_frame
import pyttsx3
import threading
import cv2
import time
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import os
import openai


questions = []
# API_KEY = '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' old_key
API_KEY = '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'
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")
stop_streaming = False
emotions = []
directions = []
position = []


def home(request):
    print(emotions, directions, position)
    return render(request, 'dashboard/home.html')

def feedback(request):
    print(emotions, directions, position)
    return render(request, 'dashboard/feedback.html')


def getCam(request):
    return render(request, 'dashboard/camera.html')


def history(request):
    context = {'interviews': Interview.objects.all()}
    return render(request, 'dashboard/history.html', context)


def takeInterview(request):
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form. is_valid():
            Interview.objects.create(
                topic=request.POST['topic'],
                subtopic=request.POST['subtopic'],
                expertise=request.POST['expertise'],
                number=request.POST['number']
            )
            messages.success(
                request, f'interview scheduled succesfully!')
            response = get_questions(request.POST['topic'], request.POST['expertise'], request.POST['number'], request.POST['subtopic'])
            global questions
            questions = list(response.split('$'))
            questions.pop(-1)
            print("questions", questions)
            if request.POST['way'] == 'mobile':
                return redirect('camKey')
            else:
                return render(request, 'dashboard/camera.html', {'questions': questions})
    else:
        form = InterviewForm()

    context = {'form': form}
    return render(request, 'dashboard/takeInterview.html', context)


def getCamKey(request):
    print(request.method)
    key = ""
    if request.method == 'POST':
        print(request.POST.get('key'))
        key = request.POST.get('key')
        messages.success(
            request, f"key taken successfully!")
        context = {'key': key}
        return render(request, "dashboard/cameraMobile.html", context)
    
    return render(request, "dashboard/camKey.html")



def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request, key):
    print(key, "webcam")
    return StreamingHttpResponse(gen(IPWebCam(key)),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def getStreaming(request):
    cap = cv2.VideoCapture(0)
    map_face_mesh = mp.solutions.face_mesh
    with map_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                iris_position_detection(frame, results, True)
            # face_emotion_detection(frame)
            ret, jpeg = cv2.imencode('.jpg', frame)
            cv2.imshow("image", jpeg.tobytes())
            # cv2.imshow("image", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()



def generate_prompt(topic, expertise, number, specialization):
    if specialization == "":
        return f'generate {number} questions in the topic {topic} on {specialization} based on the expertise level {expertise}. give me just the questions. give me the questions in a single line without numbering the questions, add a dollar symbol after each question'
    return f'generate {number} questions on the topic {topic} based on the expertise level {expertise}. give me just the questions. give me the questions in a single line without numbering the questions, add a dollar symbol after each question'

def get_questions(topic, expertise, number, specialization):
    response = openai.Completion.create(engine='text-davinci-003',
                                        prompt = generate_prompt(topic, expertise, number, specialization),
                                        temperature = 0.7,
                                        max_tokens = 512)["choices"][0]["text"]
    return response

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 140)
    engine.say(text)
    engine.runAndWait()

# Function to ask questions in a loop
def ask_questions():
    for question in questions:
        threading.Thread(target=speak, args=(question,)).start()
        time.sleep(5)

def stop_stream():
    global stop_streaming
    stop_streaming = True

def video_stream(main_interview):
    global emotions
    global directions
    global position
    emotions = []
    directions = []
    position = []
    cap = cv2.VideoCapture(0)
    while not stop_streaming:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_flip = cv2.flip(frame, 1)
        if main_interview:
            map_face_mesh = mp.solutions.face_mesh
            with map_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                results = face_mesh.process(frame_flip)
                em = face_emotion_detection(frame_flip)
                emotions.append(em)
                if results.multi_face_landmarks:
                    dir = iris_position_detection(frame_flip, results, True)
                    directions.append(dir)
        else:
            # process_frame(frame_flip)
            pass
        _, buffer = cv2.imencode('.jpg', frame_flip)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@gzip.gzip_page
def main_interview(request):
    print("que", questions)
    audio_thread = threading.Thread(target=ask_questions)
    audio_thread.start()

    def generate():
        for frame in video_stream(True):
            yield frame
        print()
    
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace;boundary=frame')
   
def stop_streaming_view(request):
    stop_stream()
    return HttpResponse("Streaming stopped.")