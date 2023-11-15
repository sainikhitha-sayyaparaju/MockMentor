# import cv2
# import dlib

# # Load pre-trained face detector and facial landmarks predictor
# face_detector = dlib.get_frontal_face_detector()
# landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# # Function to check if the face is centered
# def is_face_centered(face_landmarks, frame_width, frame_height, tolerance=0.1):
#     # Assuming 68 facial landmarks, the center can be determined using landmarks 30 (nose tip) and 8 (jaw)
#     nose_tip = face_landmarks.part(30)
#     jaw_point = face_landmarks.part(8)

#     # Calculate the horizontal distance from the nose tip to the center of the frame
#     distance_to_center_x = abs(nose_tip.x - frame_width // 2) / frame_width

#     # Calculate the vertical distance from the jaw point to the center of the frame
#     distance_to_center_y = abs(jaw_point.y - frame_height // 2) / frame_height

#     # Check if the face is within the specified tolerance of the center in both dimensions
#     return distance_to_center_x < tolerance and distance_to_center_y < tolerance


# # Function to check if the face is at the right distance
# def is_face_at_right_distance(face_landmarks, reference_distance, tolerance=0.1):
#     # Assuming 68 facial landmarks, the distance can be determined using landmarks 30 (nose tip) and 8 (jaw)
#     nose_tip = face_landmarks.part(30)
#     jaw_point = face_landmarks.part(8)

#     # Calculate the vertical distance between the nose tip and the jaw point
#     actual_distance = abs(nose_tip.y - jaw_point.y)

#     # Check if the actual distance is within the specified tolerance of the reference distance
#     return abs(actual_distance - reference_distance) / reference_distance < tolerance

# # Main function for processing each frame
# def process_frame(frame):
#     frame_height, frame_width, _ = frame.shape

#     # Convert the frame to grayscale for face detection
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Detect faces in the frame
#     faces = face_detector(gray)

#     for face in faces:
#         # Get facial landmarks for the detected face
#         landmarks = landmark_predictor(gray, face)

#         # Check if the face is centered
#         if is_face_centered(landmarks, frame_width, frame_height):
#             cv2.putText(frame, "Face Centered", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         else:
#             cv2.putText(frame, "Face Not Centered", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

#         # Check if the face is at the right distance (e.g., 150 pixels in this example)
#         if is_face_at_right_distance(landmarks, reference_distance=150):
#             cv2.putText(frame, "Right Distance", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
#         else:
#             cv2.putText(frame, "Wrong Distance", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

#     return frame




