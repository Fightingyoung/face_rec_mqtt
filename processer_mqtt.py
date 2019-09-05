import paho.mqtt.client as mqtt
import time
import cv2
import numpy as np
import register
from analysis import face_analyze_class
import json
import my_face_rec_like_guard as face
import pymysql
class Mqtt(object):
    def __init__(self, ip, result_topic, args_topic, synchronous, database_ip, client_id):
        self.conn = pymysql.connect(host=database_ip, port=3306, user='root', passwd='123', db='face_image',
                                    charset='utf8')
        self.conn_known = pymysql.connect(host=database_ip, port=3306, user='root', passwd='123',
                                          db='known_face',
                                          charset='utf8')
        self.synchronous = synchronous
        self.host = ip
        self.port = 1883
        self.result_topic = result_topic
        self.args_topic = args_topic
        self.base_client_id = client_id
        self.client_id = self.base_client_id + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.mqtt = mqtt.Client(self.client_id)
        self.mqtt.on_connect = self.on_connect
        self.time_list = []
        self.result_list = []
        self.rec_image = None
        self.rec_args = None
        self.rec_image_mark = False
        self.rec_args_mark = False
        self.t = 0
        self.face_analyze = face_analyze_class()
    def on_mqtt_connect(self):
        self.mqtt.connect(self.host, self.port, 60)
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code {}".format(str(rc)))
        self.mqtt.subscribe(self.args_topic, qos=2)

    def on_message(self, client, userdata, msg):
        # time_stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        # print('Topic: {}, Message id: {}, Time stamp: {}'.format(msg.topic, msg.mid, time_stamp))
        # data = msg.payload
        # with open('/mnt/hgfs/Grocery_store/server/server/temp2.jpg', 'wb') as f:
        #     f.write(data)
        # img = cv2.imread('/mnt/hgfs/Grocery_store/server/server/temp2.jpg')
        # os.remove('F:/temp1.jpg')
        if msg.topic == 'args' + self.base_client_id:
            try:
                message = msg.payload
                if message[0] == 118:
                    self.rec_image = cv2.imdecode(np.frombuffer(message[1:], np.uint8), cv2.IMREAD_COLOR)
                    self.rec_image_mark = True
                else:
                    str_message = str(message, encoding='utf-8')
                    self.rec_args = json.loads(str_message)
                    self.rec_args_mark = True
                if self.rec_image_mark == True and self.rec_args_mark == True:
                    if 'register' in self.rec_args:
                        coordinate = (int(self.rec_args['top']), int(self.rec_args['right']), int(self.rec_args['bottom']), int(self.rec_args['left']))
                        result = register.get_picture(self.rec_args['platform'], coordinate, self.rec_image, self.rec_args['name'], self.conn_known, self.rec_args['count'],
                                                      self.rec_args['eye_frame_counter'], self.rec_args['mouth_frame_counter'], self.rec_args['blink_counter'],
                                                      self.rec_args['mouth_open_counter'], self.rec_args['pose_counter'], self.rec_args['p_down_mark'], self.rec_args['p_up_mark'],
                                                      self.rec_args['y_right_mark'], self.rec_args['y_left_mark'], self.rec_args['get'], self.rec_args['get_pose'], self.rec_args['w'], self.rec_args['h'])

                    if 'un_register' in self.rec_args:
                        coordinate = (int(self.rec_args['top']), int(self.rec_args['right']), int(self.rec_args['bottom']),int(self.rec_args['left']))
                        result = face.draw_box(self.rec_args['known_names'], self.rec_args['known_face_codings'], self.rec_image, self.rec_args['mark'], self.rec_args['counter'], coordinate)

                    if 'login' in self.rec_args:
                        coordinate = (int(self.rec_args['top']), int(self.rec_args['right']), int(self.rec_args['bottom']),int(self.rec_args['left']))
                        result = face.draw_box(self.rec_args['known_names'], self.rec_args['known_face_codings'], self.rec_image, self.rec_args['mark'], self.rec_args['counter'], coordinate)

                    if 'process' in self.rec_args:
                        coordinate = (int(self.rec_args['top']), int(self.rec_args['right']), int(self.rec_args['bottom']), int(self.rec_args['left']))
                        result = self.face_analyze.face_analyze_function(self.rec_image, self.rec_args['name'], self.rec_args['write_data'], self.conn, self.rec_args['f_id'], self.rec_args['mysql_id'],coordinate)
                    byte_result = bytes(json.dumps(result), encoding='utf-8')
                    self.mqtt.publish(self.result_topic, byte_result, 2)
                    # self.mqtt.publish(self.result_topic, byte_enecode, 2)
                    self.rec_image_mark = False
                    self.rec_args_mark = False
                    #self.client.publish(self.message_topic, str(p_id) + ',' + gender_text + ',' + str(emotion_label_arg) + ',' + emotion_text, 2)
            except Exception as e:
                self.mqtt.publish(self.synchronous, 'hello', 2)
                print(e)
    def main(self):
        self.on_mqtt_connect()
        # 启用订阅模式
        self.mqtt.on_connect = self.on_connect

        # 接收消息
        self.mqtt.on_message = self.on_message
        self.mqtt.loop_forever()



