# -*- coding:utf-8 -*-
import wx
import cv2
import os
import argparse
import pymysql
from threading import Thread
from publisher import Mqtt
mark = False
import socket
class MyFrame(wx.Frame):

    def __init__(self,  parent,  id, myaddr):
        # log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, filename = 'message.log', stream=sys.stdout)
        # log.info("example")
        self.mqtt = Mqtt()
        self.mqtt.on_mqtt_connect()
        self.mqtt.mqtt.subscribe(self.mqtt.subscribe_topic, 2)
        self.mqtt.mqtt.on_message = self.mqtt.on_message
        # while self.mqtt.server_ok == False:
        self.myaddr = myaddr
        self.mqtt.mqtt.publish(self.mqtt.publish_topic, self.myaddr, 2)
        wx.Frame.__init__(self,  parent,  id,  '用户管理界面',  size=(400,  300))
        # 创建面板
        panel = wx.Panel(self)
        parser = argparse.ArgumentParser(description = 'Faces analyze system')
        parser.add_argument('-write_data', help = 'write data into train_data floder, default is False', default = False)
        parser.add_argument('-cam', type=int, default='0', help='Choose a device you will used capture video, default is 1')
        parser.add_argument('-database_ip', default='192.168.1.100',
                            help='IP of the mysql server which you are connecting, default is 192.168.1.100')
        parser.add_argument('-mqtt_server_ip', default='10.0.17.149',
                            help='IP of the mqtt server which you are connecting, default is 10.0.17.149')
        parser.add_argument('-platform', default = 'tablet', help='The platform on which this program is currently running, default is tablet')
        self.args = parser.parse_args()
        self.conn = pymysql.connect(host=self.args.database_ip, port=3306, user='root', passwd='123', db='face_image',
                                    charset='utf8')
        self.conn_known = pymysql.connect(host=self.args.database_ip, port=3306, user='root', passwd='123', db='known_face',
                                    charset='utf8')
        # 创建“确定”和“取消”按钮, 并绑定事件
        self.bt_register = wx.Button(panel,  label='注册')
        self.bt_register.Bind(wx.EVT_BUTTON, self.OnclickRegister)
        self.bt_exit = wx.Button(panel, label='注销')
        self.bt_exit.Bind(wx.EVT_BUTTON, self.OnclickExit)
        self.bt_login = wx.Button(panel, label='登录')
        self.bt_login.Bind(wx.EVT_BUTTON, self.OnclickLogin)
        self.bt_cancel = wx.Button(panel,  label='取消')
        self.bt_cancel.Bind(wx.EVT_BUTTON, self.OnclickCancel)
        self.title = wx.StaticText(panel, label="请您先注册，再使用")
        # # 创建文本，左对齐
        self.label_user = wx.StaticText(panel,  label="昵称:")
        self.text_user = wx.TextCtrl(panel,  style=wx.TE_LEFT)
        # self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        # 添加容器，容器中控件按横向并排排列
        hsizer_user = wx.BoxSizer(wx.HORIZONTAL)
        hsizer_user.Add(self.label_user,  proportion=0,  flag=wx.ALL,  border=5)
        hsizer_user.Add(self.text_user,  proportion=1,  flag=wx.ALL,  border=5)
        hsizer_button = wx.BoxSizer(wx.HORIZONTAL)
        hsizer_button.Add(self.bt_register,  proportion=0,  flag=wx.ALIGN_CENTER,  border=5)
        hsizer_button.Add(self.bt_exit, proportion=0, flag=wx.ALIGN_CENTER, border=5)
        hsizer_button.Add(self.bt_login, proportion=0, flag=wx.ALIGN_CENTER, border=5)

        hsizer_button.Add(self.bt_cancel,  proportion=0,  flag=wx.ALIGN_CENTER,  border=5)
        # 添加容器，容器中控件按纵向并排排列
        vsizer_all = wx.BoxSizer(wx.VERTICAL)
        vsizer_all.Add(self.title,  proportion=0,  flag=wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER,
                        border=15)
        vsizer_all.Add(hsizer_user,  proportion=0,  flag=wx.EXPAND | wx.LEFT | wx.RIGHT,  border=45)
        # vsizer_all.Add(hsizer_pwd,  proportion=0,  flag=wx.EXPAND | wx.LEFT | wx.RIGHT,  bordevent.Skip()er=45)
        vsizer_all.Add(hsizer_button,  proportion=0,  flag=wx.ALIGN_CENTER | wx.TOP,  border=15)
        panel.SetSizer(vsizer_all)
    # def OnIconfiy(self, event):
    #     wx.MessageBox('Frame has been iconized!', 'Prompt')
    def OnclickRegister(self, event):
        '''Click the register button to execute the method'''
        t = Thread(target=self.register, args=(event,))
        t.setDaemon(True)
        t.start()
    def OnclickLogin(self, event):
        '''Click the cancel button to execute the method'''
        t = Thread(target = self.face_process, args = (event, ))
        t.setDaemon(True)
        t.start()
        # self.face_process(video_process, name)
    def OnclickCancel(self, event):  # 没有event点击取消会报错
        '''Click the cancel button to execute the method '''
        self.Close(True)

    def OnclickExit(self, event):
        '''Click the unregister button to execute the method'''
        t = Thread(target=self.exit, args=(event,))
        t.setDaemon(True)
        t.start()

    def register(self, event):
        btn = event.GetEventObject()
        btn.Disable()
        count = 0
        eye_frame_counter = 0
        mouth_frame_counter = 0
        blink_counter = 0
        mouth_open_counter = 0
        pose_counter = 0
        p_down_mark = False
        p_up_mark = False
        y_right_mark = False
        y_left_mark = False
        get = False  # 是否完成活体检测
        get_pose = 5  # 是否采集多姿态照片
        is_register_succ = 5
        platform = [360, 141, 778, 643]
        mask = 'mask_tablet.jpg'
        name = self.text_user.GetValue()  # 获取输入的用户名
        if name == '':
            wx.MessageBox('昵称不能为空')
            self.bt_register.Enable()
            return
        video = cv2.VideoCapture(self.args.cam)
        h = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        w = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if self.args.platform == 'laptop':
            platform = [400, 186, 741, 626]
            mask = 'mask_laptop.jpg'
        known_face_id = self.find_known_name(self.conn_known)

        if not self.find_face_id(name, known_face_id):
            wx.MessageBox('系统检测到已经有人用该昵称注册过账号，如果您没有注册过，请换个名称再试')
            self.bt_register.Enable()
            return
        try:
            key_args = {"register": True, "platform": platform, "name": name,
                        "count": count, "eye_frame_counter": eye_frame_counter,
                        "mouth_frame_counter": mouth_frame_counter, "blink_counter": blink_counter,
                        "mouth_open_counter": mouth_open_counter, "pose_counter": pose_counter,
                        "p_down_mark": p_down_mark, "p_up_mark": p_up_mark, "y_right_mark": y_right_mark,
                        "y_left_mark": y_left_mark, "w": w, "h": h, "is_register_succ": is_register_succ, "get": get, "get_pose": get_pose}
            # key_args = json.dumps(key_args)
            mqtt = Mqtt('10.0.17.149', 'args' + self.myaddr, 'result' + self.myaddr, 'synchronous' + self.myaddr, video, key_args, 'register', mask)
            mqtt.main()
        except Exception as e:
            pass
        self.bt_register.Enable()
    def login(self, video, mark):
        known_names, known_face_codings = self.get_known_face(self.conn_known)
        counter = 0
        name = None
        try:
            key_args = {'login': True, 'known_names': known_names, 'known_face_codings': known_face_codings,
                      'mark': mark, 'counter': counter}
            mqtt = Mqtt('10.0.17.149', 'args' + self.myaddr, 'result' + self.myaddr, 'synchronous' + self.myaddr, video, key_args, 'login')
            name = mqtt.main()
        except Exception as e:
            pass
        return name

    def face_process(self, event):
        btn = event.GetEventObject()
        btn.Disable()
        mark = ['0']
        video = cv2.VideoCapture(self.args.cam)
        name = self.login(video, mark)
        if name:
            video_process = cv2.VideoCapture(self.args.cam)
            try:
                sql_table = '''create table %s(f_id int(11), emotion char(20), emotion_id int(11), gender char(20), time datetime)''' % (name)
                cursor = self.conn.cursor()
                cursor.execute(sql_table)
                self.conn.commit()
            except:
                pass
            try:
                cursor = self.conn.cursor()
                sql = "select f_id from %s;" % (name)
                cursor.execute(sql)
                # conn.commit()
                desc = cursor.description
                data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            except:
                pass
            f_id = 0
            mysql_id = len(data_dict) + 1
            try:
                key_args = {'process': True, 'write_data': self.args.write_data,
                      'f_id' : f_id, 'mysql_id' : mysql_id, 'emotion_text' : '', 'gender_text' : '', 'name' : name}
                # key_args = json.dumps(key_args)
                mqtt = Mqtt('10.0.17.149', 'args' + self.myaddr, 'result' + self.myaddr, 'synchronous' + self.myaddr, video_process, key_args, 'process')
                name = mqtt.main()
                self.bt_login.Enable()
            except Exception as e:
                pass
        else:
            self.bt_login.Enable()
    def exit(self, event):
        btn = event.GetEventObject()
        btn.Disable()
        wx.MessageBox("接下来我们需要先验证您的身份")
        mark = ['0']
        try:
            video = cv2.VideoCapture(self.args.cam)
            name = self.login(video, mark)
            if name == None:
                wx.MessageBox('系统没有检测到您的注册记录，请确认您是否注册过')
                self.bt_exit.Enable()
                return
            # path = 'known_face\\0\\%s.jpg' % name
            # print(path)
            cursor = self.conn_known.cursor()
            sql = '''delete from known_face where face_id = "%s"''' % name
            cursor.execute(sql)
            self.conn_known.commit()
            # os.remove(path)
            wx.MessageBox('%s注销成功' % name)
            self.bt_exit.Enable()
        except Exception as e:
            return
    def is_known(self, name, folder):
        for dir in os.listdir(folder):
            for file in os.listdir(os.path.join(folder, dir)):
                basename = os.path.splitext(os.path.basename(file))[0]
                if name == basename:
                    return True
        return False

    def find_face_id(self, face_id, known_face_id):
        for id in known_face_id:
            if face_id == id:
                return False
        return True

    def find_known_name(self, conn):
        known_face_id = []
        try:
            cursor = conn.cursor()
            sql = "select face_id from known_face;"
            cursor.execute(sql)
            # conn.commit()
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for dic in data_dict:
                known_face_id.append(dic['face_id'])
        except Exception as e:
            print(e.args)
        return known_face_id
    def get_known_face(self, conn):
        # conn = pymysql.connect(host='192.168.1.100', port=3306, user='root', passwd='123', db='known_face', charset='utf8')
        known_names = []
        known_face_codings = []
        try:
            cursor = conn.cursor()
            sql = "select name, face, face_up, face_down, face_left, face_right from known_face;"
            cursor.execute(sql)
            # conn.commit()
            desc = cursor.description
            data_list = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for data_dict in data_list:
                # 键为字段
                known_names.append(data_dict['name'])
                feature_str_face = data_dict['face'].lstrip('[').rstrip(']')
                feature_str_face_up = data_dict['face_up'].lstrip('[').rstrip(']')
                feature_str_face_down = data_dict['face_down'].lstrip('[').rstrip(']')
                feature_str_face_left = data_dict['face_left'].lstrip('[').rstrip(']')
                feature_str_face_right = data_dict['face_right'].lstrip('[').rstrip(']')

                feature_face = [float(value) for value in feature_str_face.split(',')]
                feature_face_up = [float(value) for value in feature_str_face_up.split(',')]
                feature_face_down = [float(value) for value in feature_str_face_down.split(',')]
                feature_face_left = [float(value) for value in feature_str_face_left.split(',')]
                feature_face_right = [float(value) for value in feature_str_face_right.split(',')]
                feature = [feature_face, feature_face_up, feature_face_down, feature_face_left, feature_face_right]
                known_face_codings.append(feature)
        except Exception as e:
            print(e.args)
        return known_names, known_face_codings

if __name__ == '__main__':
    # 获取本机电脑名
    myname = socket.getfqdn(socket.gethostname())
    # 获取本机ip
    myaddr = socket.gethostbyname(myname)
    app = wx.App()                      # 初始化
    frame = MyFrame(parent=None, id=-1, myaddr = myaddr)  # 实例MyFrame类，并传递参数
    frame.Show()                        # 显示窗口
    app.MainLoop()               # 调用主循环方法
