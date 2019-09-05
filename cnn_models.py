import pkg_resources

def pose_face_detector_location():
    return pkg_resources.resource_filename(__name__, 'models/mmod_human_face_detector.dat')
def pose_face_recognition_location():
    return pkg_resources.resource_filename(__name__, 'models/dlib_face_recognition_resnet_model_v1.dat')

def pose_landmark_predict_model_68():
    return pkg_resources.resource_filename(__name__, 'models/shape_predictor_68_face_landmarks.dat')
def pose_landmark_predict_model_5():
    return pkg_resources.resource_filename(__name__, 'models/shape_predictor_5_face_landmarks.dat')

def pose_face_rec_model_xml(device):
    return pkg_resources.resource_filename(__name__, 'models/%s/head-pose-estimation-adas-0001.xml' % (device))

def pose_face_rec_model_bin(device):
    return pkg_resources.resource_filename(__name__, 'models/%s/head-pose-estimation-adas-0001.bin' % (device))

def pose_face_detector_xml_location():
    return pkg_resources.resource_filename(__name__, 'models/haarcascade_frontalface_default.xml')