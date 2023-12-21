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
from dashboard.checkLocation import process_frame
import pyttsx3
import threading
import cv2
import time
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import os
import openai
from collections import Counter


questions = []
# API_KEY = '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' old_key
# API_KEY = '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' old
API_KEY = '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'
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")
stop_streaming = False
emotions = []
directions = []
position = []
location = []

def home(request):
    print(emotions, directions, position, location)
    return render(request, 'dashboard/home.html')

def feedback(request):
    tab = request.GET.get('tab', 'coaching')
    emotion_counts = Counter(emotions)
    
    length = len(emotions)
    up = ((emotion_counts['Fear'] + emotion_counts['Angry'] + emotion_counts['Disgust'] + emotion_counts['Sad']) / length) * 100
    happy = (emotion_counts['Happy'] / length) * 100
    neutral = (emotion_counts['Neutral'] / length) * 100
    surprise = (emotion_counts['Surprise'] / length) * 100
    feedback = api_call(generate_prompt_emotion_feedback())
    ec_center = int((directions[0] / directions[1]) * 100)
    context = {'tab': tab, 'up': int(up), 'happy': int(happy), 'neutral': int(neutral), 'surprise': int(surprise), 'max': max(emotions), 'feedback': feedback, 'ec_center': ec_center, 'loc1': location[0] > location[2] - location[0], 'loc2': location[1] > location[2] - location[1]}
    print(context)
    return render(request, 'dashboard/feedback.html', context)
    # print(emotions, directions, position)
    # return render(request, 'dashboard/feedback.html')


def getCam(request):
    return render(request, 'dashboard/camera.html')

def checkPosition(request):
    return render(request, 'dashboard/checkPosition.html')


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
            response = api_call(generate_prompt_questions(request.POST['topic'], request.POST['expertise'], request.POST['number'], request.POST['subtopic']))
            global questions
            questions = list(response.split('$'))
            questions.pop(-1)
            print("questions", questions)
            return render(request, 'dashboard/camera.html', {'questions': questions})
    else:
        form = InterviewForm()

    context = {'form': form}
    return render(request, 'dashboard/takeInterview.html', context)

def generate_prompt_questions(topic, expertise, number, specialization):
    if specialization != "":
        return f'generate {number} questions in the topic {topic} on {specialization} based on the expertise level {expertise}. give me just the questions. give me the questions in a single line without numbering the questions, add a dollar symbol after each question'
    return f'generate {number} questions on the topic {topic} based on the expertise level {expertise}. give me just the questions. give me the questions in a single line without numbering the questions, add a dollar symbol after each question'

def generate_prompt_emotion_feedback():
    return f'{emotions} These are the different emotion showed by  a person during his interview. Give him an advise consisting of 50 words. before starting the advise, tell his his previously show emotions, how that can effect his interview, what is dominant etc'

def api_call(promptt):
    response = openai.Completion.create(engine='text-davinci-003',
                                        prompt = promptt,
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
    global location
    emotions = []
    directions = [0,0]
    position = []
    location = [0, 0, 0]
    cap = cv2.VideoCapture(0)
    while not stop_streaming:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_flip = cv2.flip(frame, 1)
        if main_interview:
            cen, dis, tot = process_frame(frame_flip, False)
            location[0] += cen
            location[1] += dis
            location[2] += tot
            map_face_mesh = mp.solutions.face_mesh
            with map_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                results = face_mesh.process(frame_flip)
                em = face_emotion_detection(frame_flip)
                emotions.append(em)
                if results.multi_face_landmarks:
                    dir = iris_position_detection(frame_flip, results, True)
                    if dir == 'center':
                        directions[0] += 1
                    directions[1] += 1
        else:
            process_frame(frame_flip)
            # pass
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

@gzip.gzip_page
def checkPositionVideo(request):

    def generate():
        for frame in video_stream(False):
            yield frame
        print()
    
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace;boundary=frame')
   
def stop_streaming_view(request):
    stop_stream()
    return HttpResponse("Streaming stopped.")