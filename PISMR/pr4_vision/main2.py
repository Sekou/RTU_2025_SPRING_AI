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

im2 = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
contours, hierarchy = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(img, contours, -1, (0,255,0), 3)

c = max(contours, key = cv2.contourArea)

x,y = c[0][0][0], c[0][0][1]
cv2.circle(img, (x, y), 3, (0, 0, 255), 3)

print(x, y)


def find_object(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow("HSV", hsv)
    hsv_min = np.array(swap((166 - 20, 37 - 15, 120 - 20)), np.uint8)
    hsv_max = np.array(swap((166 + 20, 37 + 15, 120 + 20)), np.uint8)
    thresh2 = cv2.inRange(hsv, hsv_min, hsv_max)
    contours, hierarchy = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    c = max(contours, key=cv2.contourArea)
    x, y = c[0][0][0], c[0][0][1]
    return x, y

x, y = find_object(img)
print(x, y)



# cv2.drawContours(thresh2, contours, -1, (0,255,0), 3)
cv2.imshow("Contours", img)

cv2.waitKey(0)
