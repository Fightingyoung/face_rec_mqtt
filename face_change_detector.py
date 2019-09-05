import cv2
from scipy.spatial import distance as dist
from imutils import face_utils
import cnn_models
import dlib
predictor_path = cnn_models.pose_landmark_predict_model_68()
predictor = dlib.shape_predictor(predictor_path)
def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    #  vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect
    ratio = (A + B) / (2.0 * C)
    return ratio
def mouth_aspect_ratio(mouth):
    # compute the euclidean distances between the two sets of
    #  vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(mouth[2], mouth[9])
    B = dist.euclidean(mouth[4], mouth[8])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(mouth[0], mouth[6])
    # compute the eye aspect
    ratio = (A + B) / (2.0 * C)
    return ratio
# def eye_detector():
def _css_to_rect(css):
    return dlib.rectangle(css[3], css[0], css[1], css[2])
def change_detector(img, coordinate, eye_frame_counter, mouth_frame_counter, blink_counter, mouth_open_counter, eye_thresh = 0.25, mouth_thresh = 0.88):
    # "chin": points[0:17],
    # "left_eyebrow": points[17:22],
    # "right_eyebrow": points[22:27],
    # "nose_bridge": points[27:31],
    # "nose_tip": points[31:36],
    # "left_eye": points[36:42],
    # "right_eye": points[42:48],
    # "top_lip": points[48:55] + [points[64]] + [points[63]] + [points[62]] + [points[61]] + [points[60]],
    # "bottom_lip": points[54:60] + [points[48]] + [points[60]] + [points[67]] + [points[66]] + [points[65]] + [
    #     points[64]]
    rect = _css_to_rect(coordinate)
    shape = predictor(img, rect)# 检测特征点
    points = face_utils.shape_to_np(shape)# convert the facial landmark (x, y)-coordinates to a NumPy array
    leftEye = points[36 : 42]# 取出左眼对应的特征点
    rightEye = points[42 : 48]# 取出右眼对应的特征点
    mouth = points[48 :60]
    leftEAR = eye_aspect_ratio(leftEye)# 计算左眼EAR
    rightEAR = eye_aspect_ratio(rightEye)# 计算右眼EAR
    eye_ear = (leftEAR + rightEAR) / 2.0# 求左右眼EAR的均值
    mouth_ear = mouth_aspect_ratio(mouth)
    leftEyeHull = cv2.convexHull(leftEye)# 寻找左眼轮廓
    rightEyeHull = cv2.convexHull(rightEye)# 寻找右眼轮廓

    mouth = cv2.convexHull(mouth)

    cv2.drawContours(img, [leftEyeHull], -1, (0, 255, 0), 1)# 绘制左眼轮廓
    cv2.drawContours(img, [rightEyeHull], -1, (0, 255, 0), 1)# 绘制右眼轮廓
    cv2.drawContours(img, [mouth], -1, (0, 255, 0), 1)
    # cv2.drawContours(img, [mouth_bottom_hull], -1, (0, 255, 0), 1)
    # 如果EAR小于阈值，开始计算连续帧，只有连续帧计数超过EYE_AR_CONSEC_FRAMES时，才会计做一次眨眼
    if eye_ear < eye_thresh:
        eye_frame_counter += 1
        if eye_frame_counter >= 3:
            blink_counter += 1
    else:
        eye_frame_counter = 0
    if mouth_ear > mouth_thresh:

        mouth_frame_counter += 1
        if mouth_frame_counter >= 3:
            mouth_open_counter += 1
    else:
        mouth_frame_counter = 0
    # 在图像上显示出眨眼次数blink_counter和EAR
    return blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter