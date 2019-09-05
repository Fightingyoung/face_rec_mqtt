import cv2
import numpy as np

with open('../datasets/test.txt') as f:
    a = f.read()
    arrayy = a.strip().split(' ')
    #print(type(arrayy))
    T2 = [int(x) for x in arrayy]
    #T2 = [map(int, x) for x in arrayy]
    gray_image = np.array(T2).reshape(48,48)
   #  array = [[] for i in range(48)]
   #  for i in range(1,2305):
   #      if i == 2304:
   #          array[47].append(arrayy[i - 1])
   #      else:
   #          array[int(i / 48)].append(arrayy[i - 1])
   # # print(array)
   #  gray_image = np.squeeze(array)
   #  print(gray_image)
    cv2.imwrite('../datasets/test.jpg',gray_image)
