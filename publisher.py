import paho.mqtt.client as mqtt
import cv2
import time
import json
import wx
import numpy as np
from PIL import ImageFont, Image, ImageDraw
import cnn_models
class Mqtt(object):
    def __init__(self, ip = '10.0.17.149', publish_topic = 'addr', subscribe_topic = 'server_ok', synchronous = None, video = None, kwargs = None, func = None, mask = None):
        # 发送和订阅的主题
        self.server_ok = False
        self.publish_topic = publish_topic
        self.subscribe_topic = subscribe_topic
        self.synchronous = synchronous
        # ip地址和端口
        # self.host = '10.0.17.149'
        self.host = ip
        self.port = 1883
        self.client_id = 'dc-' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.mqtt = mqtt.Client(self.client_id)
        self.mqtt.on_connect = self.on_connect
        self.kwargs = kwargs
        self.video = video
        if self.video != None:
            width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.face_img = None
        self.original_img = None
        self.rec_args = None
        self.func = func
        self.face_img_mark = False
        self.original_img_mark = False
        self.mask = mask
        self.detection_model_path = cnn_models.pose_face_detector_xml_location()
        self.face_detection = self.load_detection_model(self.detection_model_path)
        self.message_mark = True
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print('Connection successful')
        elif rc == 1:
            print('Connection refused - incorrect protocol version')
        elif rc == 2:
            print('Connection refused - invalid client identifier')
        elif rc == 3:
            print('Connection refused - server unavailable')
        elif rc == 4:
            print('Connection refused - bad username or password')
        elif rc == 5:
            print('Connection refused - not authorised')
        else:
            print('Currently unused')

    def draw_chinese_text(self, face_img, text, point=(10, 30)):
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
    # 连接MQTT服务器
    def on_mqtt_connect(self):
        try:
            self.mqtt.connect(self.host, self.port, 60)
        except:
            print('Connection failed')
            exit(1)
        self.mqtt.loop_start()

    # publish 消息
    def on_publish(self, payload):
        self.mqtt.publish(self.publish_topic, payload, 2)

    # 订阅函数
    def on_subscribe(self):
        self.mqtt.subscribe(self.subscribe_topic, 2)
        self.mqtt.subscribe((self.synchronous, 2))
        # 消息来的时候处理消息
        self.mqtt.on_message = self.on_message


    # 消息处理函数
    def on_message(self, client, userdata, msg):
        '''Click the register button to execute the method '''
        time_stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        print('Topic: {}, Message id: {}, Time stamp: {}'.format(msg.topic, msg.mid, time_stamp))
        font = cv2.FONT_HERSHEY_SIMPLEX
        if msg.topic == 'server_ok':
            self.server_ok = True
        else:
            if msg.topic == self.synchronous:
                self.message_mark == True
            else:
                message = msg.payload
                # if message[0] == 118:
                #     self.rec_image = cv2.imdecode(np.frombuffer(message[1:], np.uint8), cv2.IMREAD_COLOR)
                #     self.rec_image_mark = True
                # else:
                str_message = str(message, encoding='utf-8')
                self.rec_args = json.loads(str_message)
                if self.func == 'register':
                    w, h, c = self.original_img.shape
                    self.kwargs["count"] = self.rec_args["count"]
                    self.kwargs["eye_frame_counter"] = self.rec_args["eye_frame_counter"]
                    self.kwargs["mouth_frame_counter"] = self.rec_args["mouth_frame_counter"]
                    self.kwargs["blink_counter"] = self.rec_args["blink_counter"]
                    self.kwargs["mouth_open_counter"] = self.rec_args["mouth_open_counter"]
                    self.kwargs["pose_counter"] = self.rec_args["pose_counter"]
                    self.kwargs["p_down_mark"] = self.rec_args["p_down_mark"]
                    self.kwargs["p_up_mark"] = self.rec_args["p_up_mark"]
                    self.kwargs["y_right_mark"] = self.rec_args["y_right_mark"]
                    self.kwargs["y_left_mark"] = self.rec_args["y_left_mark"]
                    self.kwargs["get"] = self.rec_args["get"]
                    self.kwargs["get_pose"] = self.rec_args["get_pose"]
                    if self.kwargs["is_register_succ"] != 0:
                        self.kwargs["is_register_succ"] = self.rec_args["is_register_succ"]
                    mark = self.kwargs["is_register_succ"]
                    pose_mark = self.kwargs["get_pose"]
                    if self.original_img_mark == True:
                        if mark == 1:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您保持静止状态', (w // 2, 20))
                            self.face_img_mark = True
                        elif mark == 2:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您反复做眨眼动作', (w // 2, 20))
                            self.face_img_mark = True
                        elif mark == 3:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您反复做张嘴动作', (w // 2, 20))
                            self.face_img_mark = True
                        elif mark == 4:
                            self.face_img = self.draw_chinese_text(self.original_img, '请将人脸放入轮廓中', (w // 2, 20))
                            self.face_img_mark = True
                        elif mark == 6:
                            self.face_img = self.draw_chinese_text(self.original_img, '当前没有检测到人脸', (w // 2, 20))
                            self.face_img_mark = True
                        if pose_mark == 1:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您缓慢地向左转头', (w // 2, 20))
                            self.face_img_mark = True
                        elif pose_mark == 2:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您缓慢地向右转头', (w // 2, 20))
                            self.face_img_mark = True
                        elif pose_mark == 3:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您缓慢地向上转头', (w // 2, 20))
                            self.face_img_mark = True
                        elif pose_mark == 4:
                            self.face_img = self.draw_chinese_text(self.original_img, '请您缓慢地向下转头', (w // 2, 20))
                            self.face_img_mark = True
                        self.original_img_mark = False
                elif self.func == 'login':
                    self.face_img_mark = True
                    self.face_img = self.original_img
                    self.kwargs["counter"] = self.rec_args["counter"]
                    self.kwargs["mark"] = self.rec_args["mark"]
                    self.original_img_mark = False
                elif self.func == 'process':
                    # mysql_id = self.face.face_analyze_function(bgr_image, name, self.args.write_data, self.conn, f_id, mysql_id)
                    self.face_img_mark = True
                    self.face_img = self.original_img
                    self.kwargs['mysql_id'] = self.rec_args['mysql_id']
                    self.kwargs['emotion_text'] = self.rec_args['emotion_text']
                    self.kwargs['gender_text'] = self.rec_args['gender_text']
                    self.original_img_mark = False
                self.message_mark = True
    def join_header(self, header, payload):
        header = bytes(header, encoding='utf-8')
        return header + payload

    def load_detection_model(self, model_path):
        detection_model = cv2.CascadeClassifier(model_path)
        return detection_model

    def detect_faces(self, detection_model, gray_image_array):
        return detection_model.detectMultiScale(gray_image_array, 1.3, 5)

    def sent(self, mask_img):
        coordinate = [0, 0, 0, 0]
        try:
            if self.message_mark == True:
                frame = self.video.read()[1]

                # frame = np.rot90(frame)
                face_img = frame.copy()
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if self.mask != None:
                    w, h, c = face_img.shape
                    mask_right = cv2.resize(mask_img, (h, w))
                    cv2.add(face_img, mask_right, face_img)
                cv2.imwrite('test1.jpg', face_img)
                self.original_img = face_img
                self.original_img_mark = True
                # small_img = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # rgb_small_img = small_img[:, :, ::-1]
                coordinates = self.detect_faces(self.face_detection, gray_image)
                x, y, width, height = coordinate
                rgb_face = frame[y: y + 1, x: x + 1]
                if len(coordinates) > 0:
                    coordinate = coordinates[0]
                    x, y, width, height = coordinate
                    rgb_face = frame[y : y + height, x : x + width]
                image_data = cv2.imencode('.jpg', rgb_face)[1]
                data_encode = np.array(image_data)
                byte_encode = bytes('v', encoding='utf-8') + data_encode.tobytes()
                self.kwargs.update({'top' : str(y), 'right' : str(x + width), 'bottom' : str(y + height), 'left' : str(x)})
                args_byte = bytes(json.dumps(self.kwargs), encoding='utf-8')
                # args_byte = bytes('{}'.format(self.kwargs), encoding='utf-8')
                self.mqtt.publish(self.publish_topic, byte_encode, 2)
                self.mqtt.publish(self.publish_topic, args_byte, 2)
                self.message_mark = False
        except Exception as e:
            pass
        return coordinate
    def _rect_to_css(self, rect):
        return rect.top(), rect.right(), rect.bottom(), rect.left()
    def _trim_css_to_bounds(self, css, image_shape):
        return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

    def draw_bounding_box(self, face_coordinates, image_array, color):
        (top, right, bottom, left) = face_coordinates
        cv2.rectangle(image_array, (left, top), (right, bottom), color, 2)

    def draw_text(self, coordinates, image_array, text, color, x_offset=0, y_offset=0, font_scale=2, thickness=2):
        x, y = coordinates[:2]
        cv2.putText(image_array, text, (x + x_offset, y + y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, color, thickness, cv2.LINE_AA)
    def main(self):
        f_id = 0
        self.on_mqtt_connect()
        time_start = time.time()
        name = None
        mask_img = cv2.imread(self.mask)
        while True:
            try:
                time_end = time.time()
                t = time_end - time_start
                coordinate = self.sent(mask_img)
                self.on_subscribe()
                if self.face_img_mark == True:
                    if self.func == 'login' or self.func == 'process':
                        if coordinate[0] != coordinate[2] and coordinate[1] != coordinate[3]:
                            x, y, width, height = coordinate
                            my_coordinate = (y, x + width, y + height, x)
                            # print(my_coordinate)
                            self.draw_bounding_box(my_coordinate, self.face_img, (0, 0, 255))
                            if self.func == 'process':
                                if self.kwargs['gender_text'] == 'woman':
                                    color = (0, 0, 255)
                                else:
                                    color = (255, 0, 0)
                                self.draw_text(coordinate, self.face_img, self.kwargs['gender_text'], color, 0, -20, 1, 2)
                                self.draw_text(coordinate, self.face_img, self.kwargs['emotion_text'], color, 0, -50, 1, 2)
                    cv2.imshow("capture faces", self.face_img)
                    self.face_img_mark = False
                if cv2.waitKey(100) & 0xff == 27:
                    break
                if self.func == 'login':
                    if t > 30:
                        wx.MessageBox('您登陆超时，请确认您是否注册过')
                        break
                    if self.kwargs["mark"][0] != '0':
                        name = self.kwargs["mark"][0]
                        wx.MessageBox('恭喜%s，登录成功！！！' % (name))
                        break
                if self.func == 'process':
                    f_id += 1
                    self.kwargs['f_id'] = f_id
                if self.func == 'register':
                    if self.kwargs['is_register_succ'] == 0:
                        wx.MessageBox('恭喜%s注册成功，请刷脸登录' % (self.kwargs["name"]))
                        break
            except Exception as e:
                pass
        self.video.release()
        cv2.destroyAllWindows()
        return name