# -*- coding:utf-8 -*-
from face_recognition import rec
import cv2
from face_recognition_API import face_locations
from threading import Thread
import numpy as np
rtsp = "rtsp://192.168.1.101"
# video = cv2.VideoCapture(0)
color = (0, 0, 255)
def RotateClockWise90(img):
    trans_img = cv2.transpose(img)
    new_img = cv2.flip(trans_img, 1)
    return new_img


# 逆时针旋转90度
def RotateAntiClockWise90(img):
    trans_img = cv2.transpose( img )
    new_img = cv2.flip( trans_img, 0)
    return new_img

def draw_bounding_box(face_coordinates, image_array, color):
    (top, right, bottom, left) = face_coordinates
    cv2.rectangle(image_array, (left, top), (right, bottom), color, 2)
def draw_mask(face_coordinates, image_array, color, mask):
    (top, right, bottom, left) = face_coordinates
    try:
        width = right - left
        num = int(0.2 * width)
        width = width + 2 * num
        height = bottom - top
        right_mask = cv2.resize(mask, (width, height))
        big_mask = np.zeros(image_array.shape, dtype=image_array.dtype)
        n = (right + num) - (left - num )
        big_mask[top - height : bottom - height, left - num : right + num] = right_mask
    except:
        pass
    cv2.rectangle(image_array, (left, top), (right, bottom), color, 2)
    # cv2.add(image_array, big_mask, image_array)
    h, w, c = image_array.shape
    for row in range(h):
        for col in range(w):
            try:
                if sum(big_mask[row, col]) != 0:
                    image_array[row, col] = big_mask[row, col]
            except:
                pass
def face_recognition(coordinate, known_names, small_img, known_face_encodings, mark):
    ismatch, hasface, name = rec(coordinate, known_face_encodings, known_names, small_img)
    try:
        hasface.any()
        if ismatch:
            mark[0] = '%s' % name
    except:
        pass

def get_mask(mask):
    crown = cv2.imread(mask)
    mask = cv2.inRange(crown, np.array([0, 0, 0]), np.array([220, 220, 220]))
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,8))) #开运算
    h, w, c = crown.shape
    for row in range(h):
        for col in range(w):
            if opening[row, col] == 0:
                crown[row, col] = [0, 0, 0]
    return crown

def draw_box(known_names, known_face_encodings, img, mark, counter, coordinate):
    # img = RotateClockWise90(img)
    t1 = None
    if coordinate[0] != coordinate[2] and coordinate[1] != coordinate[3]:
        cv2.imwrite('test.jpg', img)
        try:
            small_img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            rgb_small_img = small_img[:, :, ::-1]
            h, w, c = rgb_small_img.shape
            # face_recognition(coordinate, known_names, known_face_coding, small_img, mark)
            if counter % 10 == 0:
                # if t1 == None:
                #     # t1 = Thread(target=face_recognition, args=([(0, w, h, 0)], known_names, small_img, known_face_encodings, mark, ))
                #     # t1.start()
                # if not t1.isAlive():
                #     t1 = None
                face_recognition([(0, w, h, 0)], known_names, rgb_small_img, known_face_encodings, mark)
            # coordinate = tuple([i * 4 for i in list(coordinate)])
            # corordinate =  tuple(list(map(lambda x: x * 4, list(corordinate))))
            # draw_mask(corordinate, img, color, mask)
            # draw_bounding_box(coordinate, img, color)
        except Exception as e:
            print(e)
            pass
        counter += 1
    else:
        pass
    result = {'mark' : mark, 'counter' : counter}
    return result
# video = cv2.VideoCapture(0)
# draw_box(video)