import paho.mqtt.client as mqtt
import time
import argparse
from processer_mqtt import Mqtt as user_mqtt
from threading import Thread
class Mqtt(object):
    def __init__(self, ip, database_ip, subscribe_topic, publish_topic):
        # 发送和订阅的主题
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.database_ip = database_ip
        # ip地址和端口
        # self.host = '10.0.17.149'
        self.host = ip
        self.port = 1883
        self.client_id = 'dc' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.mqtt = mqtt.Client(self.client_id)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message_come
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


    # 连接MQTT服务器
    def on_mqtt_connect(self):
        try:
            self.mqtt.connect(self.host, self.port, 60)
        except:
            print('Connection failed')
            exit(1)

    # 订阅函数
    def on_subscribe(self):
        self.mqtt.subscribe(self.subscribe_topic, 2)
        # 消息来的时候处理消息
        self.mqtt.on_message = self.on_message_come


    # 消息处理函数
    def on_message_come(self, client, userdata, msg):
        # print('Start receiving message:')
        time_stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        print('Topic: {}, Message id: {}, Time stamp: {}'.format(msg.topic, msg.mid, time_stamp))
        data = msg.payload
        client_ip = str(data, encoding='utf-8')
        try:
            user = user_mqtt(args.ip, 'result' + client_ip, 'args' + client_ip, 'synchronous' + client_ip, args.database_ip, client_ip)
            t = Thread(target=user.main)
            t.setDaemon(True)
            t.start()
        except Exception as e:
            pass

        # print(self.mqtt.publish(self.subscribe_topic, client_ip, 2))
    def main(self):
        self.on_mqtt_connect()
        self.on_subscribe()
        self.mqtt.loop_forever()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('-ip', default='10.0.17.149', type=str, help="ip")
    parser.add_argument('-database_ip', default='192.168.1.100',
                        help='IP of the mysql server which you are connecting, default is 192.168.1.100')
    args = parser.parse_args()
    mqtt = Mqtt(args.ip, args.database_ip, 'addr', 'server_ok')
    mqtt.main()