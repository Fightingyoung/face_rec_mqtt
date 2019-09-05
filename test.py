import cv2
import time
video = cv2.VideoCapture(0)
counter = 0
start = time.time()
while True:
    img = video.read()[1]
    cv2.imshow('test', img)
    counter += 1
    end = time.time()
    t = end - start
    if t >= 60:
        break
    if cv2.waitKey(100) & 0xff == ord('q'):
        break
print(counter / 60)
# 9.733333333333333