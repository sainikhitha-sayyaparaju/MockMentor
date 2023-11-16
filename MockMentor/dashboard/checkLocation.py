import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def is_face_centered(face_coordinates, frame_width, frame_height, tolerance=0.15):
    distance_to_center_x = abs(face_coordinates[0] + face_coordinates[2] // 2 - frame_width // 2) / frame_width
    distance_to_center_y = abs(face_coordinates[1] + face_coordinates[3] // 2 - frame_height // 2) / frame_height
    return distance_to_center_x < tolerance and distance_to_center_y < tolerance


def is_face_at_right_distance(face_coordinates, reference_distance, tolerance=0.15):
    face_height = face_coordinates[3]
    return abs(face_height - reference_distance) / reference_distance < tolerance

def process_frame(frame):
    frame_height, frame_width, _ = frame.shape

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        if is_face_centered((x, y, w, h), frame_width, frame_height):
            cv2.putText(frame, "Face Centered", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, "Face Not Centered", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        if is_face_at_right_distance((x, y, w, h), reference_distance=150):
            cv2.putText(frame, "Right Distance", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        else:
            cv2.putText(frame, "Wrong Distance", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
