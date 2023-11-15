import cv2
import numpy as np

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390,
            249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154,
             155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_IRIS = [474, 475, 476, 477]
LEFT_IRIS = [469, 470, 471, 472]
L_H_LEFT = [33]
L_H_RIGHT = [133]
R_H_LEFT = [362]
R_H_RIGHT = [263]
cap = cv2.VideoCapture(0)
# directions = []
print("sravya eye")


def euclidean_distance(pnt1, pnt2):
    x1, y1 = pnt1.ravel()
    x2, y2 = pnt2.ravel()
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (0.5)


def iris_position(center, right, left):
    center_to_right = euclidean_distance(center, right)
    tot = euclidean_distance(right, left)
    ratio = center_to_right / tot
    position = ""
    if ratio <= 0.42:
        position = "right"
    elif ratio > 0.42 and ratio <= 0.57:
        position = "center"
    else:
        position = "left"
    return position, ratio


def iris_position_detection(img, results, draw=False):
    img_height, img_width = img.shape[:2]
    # list[(x,y), (x,y)....]
    mesh_coord = np.array([np.multiply([p.x, p.y], [img_width, img_height]).astype(
        int) for p in results.multi_face_landmarks[0].landmark])
    # if draw :
    # cv2.polylines(img, [mesh_coord[LEFT_IRIS]], True, (0, 255, 0), 1, cv2.LINE_AA)
    # cv2.polylines(img, [mesh_coord[RIGHT_IRIS]], True, (0, 255, 0), 1, cv2.LINE_AA)
    (l_x, l_y), l_radius = cv2.minEnclosingCircle(mesh_coord[LEFT_IRIS])
    (r_x, r_y), r_radius = cv2.minEnclosingCircle(mesh_coord[RIGHT_IRIS])
    center_left = np.array([l_x, l_y], dtype=np.int32)
    center_right = np.array([r_x, r_y], dtype=np.int32)
    cv2.circle(img, center_left, int(l_radius), (255, 0, 255), 1, cv2.LINE_AA)
    cv2.circle(img, center_right, int(r_radius), (255, 0, 255), 1, cv2.LINE_AA)
    iris_pos, ratio = iris_position(
        center_right, mesh_coord[R_H_RIGHT], mesh_coord[R_H_LEFT][0])
    # print(iris_pos)
    # directions.append(iris_pos)
    cv2.putText(img, f"Iris_position : {iris_pos}", (30, 30),
                cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 1, cv2.LINE_AA)
    # print(directions)
    return iris_pos
