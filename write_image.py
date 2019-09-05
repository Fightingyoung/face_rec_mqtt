# -*-coding: utf-8-*-
import cv2
import os
curdir = os.path.abspath(os.path.dirname(__file__))
curdir = os.path.join(curdir, 'train_data')
def path_init():
    curdir_emotion = os.path.join(curdir, 'emotion')
    curdir_gender = os.path.join(curdir, 'gender')
    curdir_detection = os.path.join(curdir, 'detection')
    dirs_emotion = ['0', '1', '2', '3', '4', '5', '6']
    dirs_gender = ['0', '1']
    class_emotion_dir = {}
    class_gender_dir = {}
    for dr in dirs_emotion:
        dest = os.path.join(curdir_emotion,dr)
        class_emotion_dir[dr] = dest
        if not os.path.exists(dest):
            os.mkdir(dest)
        # else:
        #     shutil.rmtree(dest)
        #     os.mkdir(dest)
    for dr in dirs_gender:
        dest = os.path.join(curdir_gender, dr)
        class_gender_dir[dr] = dest
        if not os.path.exists(dest):
            os.mkdir(dest)
        # else:
        #     shutil.rmtree(dest)
        #     os.mkdir(dest)
    return class_emotion_dir, class_gender_dir, curdir_detection
def write_emotion_train_data(class_emotion_dir, img, label, id):
    # id :**.jpg
    destdir = os.path.join(class_emotion_dir[label], id)
    cv2.imwrite(destdir, img)
def write_gender_train_data(class_gender_dir, img, label, id):
    # id :**.jpg
    destdir = os.path.join(class_gender_dir[label], id)
    cv2.imwrite(destdir, img)
def write_detection_train_data(detection_dir, img, id, e_id, bounding_box):

    destdir = os.path.join(detection_dir,id)
    print(destdir)
    cv2.imwrite(destdir, img)
    with open(os.path.join(detection_dir, 'train.txt'), 'a') as f:
        f.seek(0, 2)
        f.write(id + ',' + str(e_id) + ',' + bounding_box + '\n')