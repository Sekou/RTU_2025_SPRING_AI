import cv2
import numpy as np

img = cv2.imread("images/0.jpg")

def swap(vec):
    return vec[::-1]

cv2.imshow("Image", img)

rgb_min = np.array(swap((142-10, 142-10, 166-10)), np.uint8)
rgb_max = np.array(swap((142+10, 142+10, 166+10)), np.uint8)
thresh = cv2.inRange(img, rgb_min, rgb_max)
cv2.imshow("Thresh", thresh)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV )

cv2.imshow("HSV", hsv)
hsv_min = np.array(swap((166-20, 37-15, 120-20)), np.uint8)
hsv_max = np.array(swap((166+20, 37+15, 120+20)), np.uint8)
thresh2 = cv2.inRange(hsv, hsv_min, hsv_max)

cv2.imshow("Thresh2", thresh2)


cv2.waitKey(0)
