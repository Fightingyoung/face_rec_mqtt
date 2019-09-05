# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import os
import re
import face_recognition_API
import PIL.Image
import numpy
import numpy as np

def scan_known_people(known_people_folder):
    '''

    :param known_people_folder: known people folder
    :return: known_names, known_face_encoding
    '''
    known_names = []
    known_face_encoding = []
    for dir in dir_in_folder(known_people_folder):
        for file in image_files_in_folder(dir):
            basename = os.path.splitext(os.path.basename(file))[0]
            img = face_recognition_API.load_image_file(file)
            encodings = face_recognition_API.face_encodings(img)
            if len(encodings) > 1:
                click.echo("WARNING: More than one face foundd in {}. Only considering the first face.".format(file))
            if len(encodings) == 0:
                click.echo("WARING: No faces found in {}. Ignoring file.".format(file))
            else:
                known_names.append(basename)
                print(encodings[0])
                known_face_encoding.append(encodings[0])
    return known_names, known_face_encoding


def print_result(filename, name, distance, show_distance=False):
    if show_distance:
        print("{},{},{}".format(filename, name, distance))
    else:
        print("{},{}".format(filename, name))


def test_image(coordinate, small_img, known_names, known_face_encodings, tolerance=0.35):
    '''

    :param image_to_check: Pictures that need to be authenticated
    :param known_names: The names of peoples had registed
    :param known_face_encodings:The feature vector of face had registed
    :param tolerance: Threshold to determine whether a face is a match
    :return:is_match, The feature vector of face of unknowwn people, name
    '''

    # Scale down image if it's giant so things run a little faster
    has_true = False
    if max(small_img.shape) > 1600:
        pil_img = PIL.Image.fromarray(small_img)
        pil_img.thumbnail((1600, 1600), PIL.Image.LANCZOS)
        small_img = np.array(pil_img)
    unknown_encodings = face_recognition_API.face_encodings(small_img, coordinate)
    for unknown_encoding in unknown_encodings:
        result_temp = []
        distances = face_recognition_API.face_distance(known_face_encodings, unknown_encoding)#列表的每一行对应一种姿态的距离
        result_arr = np.array(distances)
        row, col = result_arr.shape
        for i in range(col):
            print(result_arr[:, i])
            result_temp.append(min(result_arr[:, i]))
        result = list(np.array(result_temp) <= tolerance)
        if True in result:
            # [print_result(image_to_check, name, distance, show_distance) for is_match, name, distance in zip(result, known_names, distances) if is_match]
            for is_match, name, distance in zip(result, known_names, distances):
                if is_match:
                    return True, unknown_encoding, name
        else:
            # print_result(image_to_check, "please try again!!!", None, show_distance)
            # print("please try again!!!")
            return False, unknown_encoding, None
    if not unknown_encodings:
        # print out fact that no faces were found in image
        #print_result(image_to_check, "please alter a pase", None, show_distance)
        # print("please try again!!!")
        return False, unknown_encodings, None

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def dir_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder)]


def rec(coordinate, known_face_encodings, known_names, small_img):
    return test_image(coordinate, small_img, known_names, known_face_encodings)