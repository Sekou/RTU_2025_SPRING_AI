from pathlib import Path
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import cv2
import numpy as np

#поиск целевого объекта
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

print('Program started')

client = RemoteAPIClient()
sim = client.getObject('sim')

visionSensorHandle1 = sim.getObjectHandle('/diningChair[0]/kinect/rgb')
visionSensorHandle2 = sim.getObjectHandle('/diningChair[1]/kinect/rgb')

print(visionSensorHandle1)
print(visionSensorHandle2)


# Run a simulation in stepping mode:
client.setStepping(True)
sim.startSimulation()
while True:
    #Read camera
    img, resX, resY = sim.getVisionSensorCharImage(visionSensorHandle1)
    img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)
    img = cv2.flip(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 0)
    cv2.imshow("frame", img)
    cv2.waitKey(0)
    # try:
    #     x, y = find_object(img)
    #     dx=x - img.shape[0]/2
    #     print("dx=", dx)
    #     setMovement(v, 0, dx/100)
    # except:
    #     pass


    client.step()  # triggers next simulation step