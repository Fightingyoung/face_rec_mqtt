import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from face_change_detector import change_detector
import cnn_models
import dlib
from my_pose_detector import main

def draw_bounding_box(face_coordinates, image_array, color):
    (top, right, bottom, left) = face_coordinates
    cv2.rectangle(image_array, (left, top), (right, bottom), color, 2)

def draw_chinese_text(face_img, text, point = (10, 30)):
    '''
    The function to write chinese on frame
    :param face_img: Current frame
    :param text: The chinese content will be write on face_img
    :param point: The location showing chinese content
    :return: A frame with words written on it
    '''
    rgb_face_image = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    rgb_pillow_face_image = Image.fromarray(rgb_face_image)
    draw = ImageDraw.Draw(rgb_pillow_face_image)
    font = ImageFont.truetype("simhei.ttf", 20, encoding="utf-8")
    draw.text(point, text, (255, 0, 0), font=font)
    return cv2.cvtColor(np.array(rgb_pillow_face_image), cv2.COLOR_RGB2BGR)
def is_parallel(mask_corordinate, corordinate, w, h):
    '''
    The function to determine if a face is parallel to a lens
    :param mask_corordinate:The location of face profile in face profile mask
    :param corordinate:The location of face in current frame
    :param w:he width of video frame
    :param h:The height of video frame
    :return:face_and_lens_is_parallel
    '''
    top, right, bottom, left = corordinate
    mask_left, mask_top, mask_right, mask_bottom = mask_corordinate
    outline_left = int(h / 1150 * mask_left)
    outline_top = int(w / 817 * mask_top)
    outline_right = int(h / 1150 * mask_right)
    outline_bottom = int(w / 817 * mask_bottom)
    # cv2.rectangle(img, (outline_left, outline_top), (outline_right, outline_bottom), (0, 0, 255), 2)
    outline_w = outline_right - outline_left
    outline_h = outline_bottom - outline_top
    face_w = right - left
    face_h = bottom - top
    padding_rate = 0.6
    up_rate = 0.25
    down_rate = 0.04
    left_right_rate = 0.06
    if top < outline_top + outline_h * up_rate + face_h * padding_rate and top > outline_top + outline_h * up_rate - face_h * padding_rate:
        if bottom < outline_bottom - outline_h * down_rate + face_h * padding_rate and bottom > outline_bottom - outline_h * down_rate - face_h * padding_rate:
            if left < outline_left + outline_w * left_right_rate + face_w * padding_rate and left > outline_left + outline_w * left_right_rate - face_w * padding_rate:
                if right < outline_right - outline_w * left_right_rate + face_w * padding_rate and right > outline_right - outline_w * left_right_rate - face_w * padding_rate:
                    return True
    return False

def insert_to_database(conn, face_id, faces):
    '''
    The function inserting face describer into database
    :param conn: Mysql Database connection that will be used when inserting face describer into database
    :param face_id: The id marking diffrent user's faces
    :param faces: The container storing frame including face will be registered
    :return: is_insert_into_database_successfully
    '''
    feature_extrator_path = cnn_models.pose_landmark_predict_model_5()
    feature_extrator = dlib.shape_predictor(feature_extrator_path)
    face_recognition_model_path = cnn_models.pose_face_recognition_location()
    face_encoder = dlib.face_recognition_model_v1(face_recognition_model_path)
    encodings = []
    try:
        for face in faces:
            h, w, c = face.shape
            location = dlib.rectangle(0, 0, w, h)
            landsmark_set = feature_extrator(face, location)
            encoding = np.array(face_encoder.compute_face_descriptor(face, landsmark_set, 1))
            encodings.append(encoding)
        while 5 - len(encodings):
            encodings.append(encodings[len(encodings) - 1])
        cursor = conn.cursor()
        sql = '''INSERT INTO known_face values("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % (
        face_id, face_id, str(list(encodings[4])), str(list(encodings[2])),
        str(list(encodings[3])), str(list(encodings[0])), str(list(encodings[1])))
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
def get_pose_pic(p_up_mark, p_down_mark, y_left_mark, y_right_mark, face_img, faces, w, h, pose_counter):
    '''
    #The method to get a multi-gesture face
    :param p_up_mark:The mark of pitch degree(nose-up pitch) ok
    :param p_down_mark:The mark of pitch degree(nose-down pith) ok
    :param y_left_mark:The mark of yaw degree(nose-left yaw) ok
    :param y_right_mark:The mark of yaw degree(nose-right yaw) ok
    :param face_img:Current face frame that should be edit
    :param faces:The container of multi-gesture face image
    :param frame:The frame that will be put into faces
    :param w:The width of video frame
    :param h:The height of video frame
    :param pose_counter:The counter of frames that meet one condition
    :return:is_get_all_pose, face_img, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
    '''
    r, y, p = main(face_img, 'FP32')
    print('r:%f\ty:%f\tp:%f' % (r, y, p))
    if y_left_mark == False:
        # face_img = draw_chinese_text(face_img, '请您缓慢地向左转头', (w // 2, 20))
        if y > 10 and y_left_mark == False:
            pose_counter += 1
            if pose_counter > 8:
                # cv2.imwrite('test_left.jpg', frame)
                faces.append(face_img)
                pose_counter = 0
                y_left_mark = True
        return 1, faces, pose_counter, p_up_mark, p_down_mark, y_left_mark, y_right_mark
    if y_left_mark == True and y_right_mark == False:
        # face_img = draw_chinese_text(face_img, '请您缓慢地向右转头', (w // 2, 20))
        if y < 4:
            pose_counter += 1
            if pose_counter > 8:
                # cv2.imwrite('test_right.jpg', frame)
                faces.append(face_img)
                pose_counter = 0
                y_right_mark = True
        return 2, faces, pose_counter, p_up_mark, p_down_mark, y_left_mark, y_right_mark

    if y_left_mark == True and y_right_mark == True and p_up_mark == False:
        # face_img = draw_chinese_text(face_img, '请您缓慢地向上抬头', (w // 2, 20))
        if p < -2:
            pose_counter += 1
            if pose_counter > 8:
                # cv2.imwrite('test_up.jpg', frame)
                faces.append(face_img)
                pose_counter = 0
                p_up_mark = True
        return 3, faces, pose_counter, p_up_mark, p_down_mark, y_left_mark, y_right_mark

    if y_left_mark == True and y_right_mark == True and p_up_mark == True and p_down_mark == False:
        # face_img = draw_chinese_text(face_img, '请您缓慢地向下点头', (w // 2, 20))
        if p > -3:
            pose_counter += 1
            if pose_counter > 8:
                # cv2.imwrite('test_down.jpg', frame)
                faces.append(face_img)
                pose_counter = 0
                p_down_mark = True
        return 4, faces, pose_counter, p_up_mark, p_down_mark, y_left_mark, y_right_mark
    if p_down_mark:
        return 0, faces, pose_counter, p_up_mark, p_down_mark, y_left_mark, y_right_mark
def alive_detector(get, face_image, eye_frame_counter, mouth_frame_counter,
                   blink_counter, mouth_open_counter, mask_coordinate, coordinate, w, h,
                   count, get_pose, faces, conn, name):
    '''
    The function will be use as alive_detector
    :param get: A sign of complete vivisection
    :param rgb_small_img:Current frame that had been resize as a minimum value which can find a face by face detector
    :param small_corordinate:The locations of face in current frame
    :param eye_frame_counter:The counter of frame that can be judged as blinks
    :param mouth_frame_counter:The counter of frame that can be judged as mouth-open
    :param blink_counter:The counter of blinks times
    :param mouth_open_counter:The counter of mouth-open times
    :param mask_corordinate:The location of face profile in face profile mask
    :param corordinate:The location of face in current frame
    :param w:The width of current frame
    :param h:The height of current frame
    :param count:The number of frames the user holds still
    :param get_pose:A sign of complete muti-gesture face capture
    :param faces:The container of frame that include muti-gesture faces
    :param frame:Unprocessed video frames which will be used for registration
    :param conn:Mysql Database connection that will be used when inserting face describer into database
    :param name:User's name will be registed
    :param face_img:video frames which will be process by alive-detector
    :return:is_registered_successfully, face_img, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
    '''
    h_1, w_1, c_1 = face_image.shape
    blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter = \
        change_detector(face_image, (0, w_1, h_1, 0), eye_frame_counter, mouth_frame_counter, blink_counter,
                        mouth_open_counter, 0.28, 0.55)
    if is_parallel(mask_coordinate, coordinate, w, h):
        if blink_counter > 4 and mouth_open_counter > 4:
            get = True
            if count >= 50 and get_pose == 0:
                # cv2.imwrite('known_face/0/' + name + '.jpg', frame)
                faces.append(face_image)
                insert_to_database(conn, name, faces)
                return 0, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
            elif get_pose == 0:
                count += 1
                return 1, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
        if blink_counter <= 4:
            # face_img = draw_chinese_text(face_img, '请您反复做眨眼动作', (w // 2, 20))
            return 2, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
        if blink_counter > 4 and mouth_open_counter <= 4:
            # face_img = draw_chinese_text(face_img, '请您反复做张嘴动作', (w // 2, 20))
            return 3, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
    elif not get:
        count = 0
        return 4, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
    return 5, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get
def get_picture(mask_coordinate, coordinate, face_frame, name, conn, count, eye_frame_counter,
                mouth_frame_counter, blink_counter, mouth_open_counter,  pose_counter, p_down_mark, p_up_mark,
                y_right_mark, y_left_mark, get, get_pose, w, h):
    '''
    Method to execute at registration time
    :param mask_image:Face profile mask
    :param mask_corordinate:The location of face profile in face profile mask
    :param cap:opencv VideoCapture object
    :param name:User's name will be registed
    :param conn:Mysql Database connection that will be used when inserting face describer into database
    :return:
    '''
    # parallel = False
    is_register_succ = 0
    faces = []
    if coordinate[0] != coordinate[2] and coordinate[1] != coordinate[3]:
        # def alive_detector(rgb_small_img, small_corordinate, eye_frame_counter, mouth_frame_counter,
        #                    blink_counter, mouth_open_counter, mask_corordinate, corordinate, w, h,
        #                    count, frame, conn, name):
        is_register_succ, blink_counter, mouth_open_counter, eye_frame_counter, mouth_frame_counter, count, get= alive_detector(get,
            face_frame, eye_frame_counter, mouth_frame_counter,
            blink_counter, mouth_open_counter, mask_coordinate, coordinate, w, h,
            count, get_pose, faces, conn, name)
        if get == True:
            get_pose, faces, pose_counter, p_up_mark, p_down_mark, y_left_mark, y_right_mark = get_pose_pic(p_up_mark, p_down_mark, y_left_mark,
                                                                                                                      y_right_mark, face_frame, faces, w, h, pose_counter)
    else:
        # face_img = draw_chinese_text(face_img, '当前没有检测到人脸', (w // 2, 20))
        get_pose = 5
        is_register_succ = 6
    result = {'is_register_succ' : is_register_succ, 'count' : count, 'eye_frame_counter' : eye_frame_counter,
              'mouth_frame_counter' : mouth_frame_counter, 'blink_counter' : blink_counter, 'mouth_open_counter' : mouth_open_counter,
              'pose_counter': pose_counter, 'p_down_mark': p_down_mark, 'p_up_mark': p_up_mark,
              'y_right_mark': y_right_mark,
              'y_left_mark': y_left_mark, 'get': get, 'get_pose': get_pose
              }
    return result