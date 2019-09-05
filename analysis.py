import argparse
import time
import cv2
import numpy
import numpy as np
from keras.models import load_model
from face_classification.src.utils import datasets
from face_classification.src.utils import inference
from face_classification.src.utils.inference import load_detection_model, draw_text
from face_classification.src.utils import preprocessor
from face_classification.src.utils.preprocessor import preprocess_input
import write_image
from write_image import path_init, write_emotion_train_data, write_gender_train_data, write_detection_train_data
import tensorflow as tf
graph = tf.get_default_graph()
class face_analyze_class(object):
    def __init__(self):
        self.detection_model_path = 'face_classification/trained_models/detection_models/haarcascade_frontalface_default.xml'
        self.emotion_model_path = 'face_classification/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
        self.gender_model_path = 'face_classification/trained_models/gender_models/simple_CNN.81-0.96.hdf5'
        self.face_detection = load_detection_model(self.detection_model_path)
        self.emotion_classifier = load_model(self.emotion_model_path, compile=False)
        self.gender_classifier = load_model(self.gender_model_path, compile=False)
        self.class_emotion_dir, self.class_gender_dir, self.detection_dir = path_init()
        self.indexs_emotion = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0}
        self.indexs_gender = {'0': 0, '1': 0}
        self.indexs_detection = 0
    def save_data(self, _rgb_face, _gray_face, mysql_id, f_id, gender_text, emotion_label_arg, gender_label_arg, emotion_text, write_data, conn, name):
        '''
        :param _rgb_face: Images saving to gender train data
        :param rgb_image: Images saving to detection train data
        :param _gray_face: Images saving to emotion train data
        :param mysql_id: The number of records stored in the mysql database
        :param f_id: The frame Numbers of Videocapture captures
        :param gender_text: The gender text detected
        :param emotion_label_arg: The emotion label detected
        :param gender_label_arg:The gender label detected
        :param bounding_box:The location of the face in the picture
        :param emotion_text:The emotion text detected
        :param write_data: A parameter indicating whether to write the training set
        :param conn: The connection instance of mysql database
        :param name: The name of current user
        :return: The number of records stored in the mysql database
        '''
        if f_id % 5 == 0:
            print(write_data)
            if write_data == 'True':
                print("&&&&&&&&&&&&&&&&&&&&")
                if gender_label_arg != -1:
                    _rgb_face = cv2.cvtColor(_rgb_face, cv2.COLOR_BGR2RGB)
                    # file_image = os.path.join("./my_images", format("file-%3d.png(%s)", time.ctime().replace(' ', '-')))
                    write_gender_train_data(self.class_gender_dir, _rgb_face, str(gender_label_arg),
                                            time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time())) + '-' + str(
                                                self.indexs_gender[str(gender_label_arg)]) + '.jpg')
                    self.indexs_gender[str(gender_label_arg)] += 1

                # 将图片写入训练数据集
                if emotion_label_arg != -1:
                    # img = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
                    # write_detection_train_data(self.detection_dir, img,
                    #                            time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time())) + '-' + str(
                    #                                self.indexs_detection) + '.jpg', emotion_label_arg, bounding_box)
                    # self.indexs_detection += 1
                    write_emotion_train_data(self.class_emotion_dir, _gray_face, str(emotion_label_arg),
                                             time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time())) + '-' + str(
                                                 self.indexs_emotion[str(emotion_label_arg)]) + '.jpg')
                    self.indexs_emotion[str(emotion_label_arg)] += 1
            try:
                cursor = conn.cursor()
                sql = "INSERT" + " INTO %s values(" % (name) + str(
                    mysql_id) + ",\"" + gender_text + "\"," + "%d," % emotion_label_arg + "\"" + emotion_text + "\"," + "current_timestamp);"
                cursor.execute(sql)
                conn.commit()
                mysql_id += 1
            except Exception as e:
                print(e.args)
        return mysql_id
    def face_analyze_function(self, bgr_image, name, write_data, conn, f_id, mysql_id, coordinate):
        '''
        :param bgr_image: The image going to analysis
        :param name:The name of user currently login
        :param write_data:
        :param conn:A parameter indicating whether to write the training set
        :param f_id:The frame Numbers of Videocapture captures
        :param mysql_id:The number of records stored in the mysql database
        :return:The number of records stored in the mysql database
        '''
        gender_text = ''
        emotion_text = ''
        emotion_label_arg = -1
        gender_label_arg = -1
        if coordinate[0] != coordinate[2] and coordinate[1] != coordinate[3]:
            global graph
            _rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
            _gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            emotion_labels = datasets.get_labels('fer2013')
            gender_labels = datasets.get_labels('imdb')
            # hyper-parameters for bounding boxes shape
            emotion_target_size = self.emotion_classifier.input_shape[1:3]
            gender_target_size = self.gender_classifier.input_shape[1:3]
            # faces = detect_faces(self.face_detection, gray_image)
            # self.kwargs.update({'top': str(y), 'right': str(x + width), 'bottom': str(y + height), 'left': str(x)})
            try:
                rgb_face = cv2.resize(_rgb_image, (gender_target_size))
                gray_face = cv2.resize(_gray_image, (emotion_target_size))
            except:
                pass
            rgb_face = preprocess_input(rgb_face, False)
            rgb_face = np.expand_dims(rgb_face, 0)
            with graph.as_default():
                gender_prediction = self.gender_classifier.predict(rgb_face)
            gender_label_arg = np.argmax(gender_prediction)
            gender_text = gender_labels[gender_label_arg]
            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            with graph.as_default():
                emotion_label_arg = np.argmax(self.emotion_classifier.predict(gray_face))
            emotion_text = emotion_labels[emotion_label_arg]
            mysql_id = self.save_data(_rgb_image, _gray_image, mysql_id, f_id, gender_text, emotion_label_arg,
                                      gender_label_arg, emotion_text, write_data, conn, name)
        result = {'mysql_id' : mysql_id, 'gender_text' : gender_text, 'emotion_text' : emotion_text}
        return result
