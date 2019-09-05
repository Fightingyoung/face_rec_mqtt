from __future__ import print_function
import sys
from argparse import ArgumentParser, SUPPRESS
import cv2
import cnn_models
from openvino.inference_engine import IENetwork, IEPlugin
import numpy
def main(image, model):
    model_xml = cnn_models.pose_face_rec_model_xml(model)
    model_bin = cnn_models.pose_face_rec_model_bin(model)
    # Plugin initialization for specified device and load extensions library if specified
    plugin = IEPlugin(device='CPU', plugin_dirs=None)
    # Read IR
    net = IENetwork(model=model_xml, weights=model_bin)
    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))
    exec_net = plugin.load(network=net, num_requests=2)
    # Read and pre-process input image
    n, c, h, w = net.inputs[input_blob].shape
    del net
    in_frame = cv2.resize(image, (w, h))
    in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    in_frame = in_frame.reshape((n, c, h, w))
    exec_net.start_async(request_id=0, inputs={input_blob: in_frame})
    # Parse detection results of the current request
    if exec_net.requests[0].wait(-1) == 0:
        res = exec_net.requests[0].outputs

    # print('r:%f\ty:%f\tp%f' % (res['angle_r_fc'][0][0], res['angle_y_fc'][0][0], res['angle_p_fc'][0][0]))

    return res['angle_r_fc'][0][0], res['angle_y_fc'][0][0], res['angle_p_fc'][0][0]

# cap = cv2.VideoCapture(0) # 调整参数实现读取视频或调用摄像头
# mask = cv2.imread('mask_laptop.jpg')
# # frame = np.rot90(frame)
#
# while 1:
#     ret, frame = cap.read()
#     face_img = frame.copy()
#     w, h, c = face_img.shape
#     mask_right = cv2.resize(mask, (h, w))
#     cv2.add(face_img, mask_right, face_img)
#     cv2.imshow("cap", face_img)
#     # main(frame, 'FP32')
#     if cv2.waitKey(100) & 0xff == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()
