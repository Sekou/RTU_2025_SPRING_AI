from pathlib import Path
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import cv2
import numpy as np
from threading import Thread
import time


def get_cam_frame(sim, handle):
    img, resX, resY = sim.getVisionSensorCharImage(handle)
    img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)
    img = cv2.flip(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 0)
    return img

def swap(vec):
    return vec[::-1]
#поиск целевого объекта
def find_object(img):
    rgb_min = np.array(swap((230, 230, 230)), np.uint8)
    rgb_max = np.array(swap((255, 255, 255)), np.uint8)
    thresh = cv2.inRange(img, rgb_min, rgb_max)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    c = max(contours, key=cv2.contourArea)
    x, y = c[0][0][0], c[0][0][1]
    return x, y

class Viewer:
    def __init__(self):
        self.frame = None
    def run(self):
        while True:
            if self.frame is not None:
                cv2.imshow("frame", self.frame)
                key = cv2.waitKey(20)
                if key == 27:  # exit on ESC
                    cv2.destroyAllWindows()
                    self.frame = None
                    break
            time.sleep(0.25)


print('Program started')

client = RemoteAPIClient()
sim = client.getObject('sim')

visionSensorHandle1 = sim.getObjectHandle('/diningChair[0]/kinect/rgb')
visionSensorHandle2 = sim.getObjectHandle('/diningChair[1]/kinect/rgb')
markerHandle = sim.getObjectHandle('/Quadcopter/Sphere')

print(visionSensorHandle1)
print(visionSensorHandle2)

v=Viewer()

a = Thread(target=v.run,args=())
a.start()

#калибровочное положение
pos0=sim.getObjectPosition(markerHandle, -1)
pos1=sim.getObjectPosition(visionSensorHandle1, -1)
pos2=sim.getObjectPosition(visionSensorHandle2, -1)
img1 = get_cam_frame(sim, visionSensorHandle1)
img2 = get_cam_frame(sim, visionSensorHandle2)
print("Initial marker pos = ", pos0)
print("Camera 1 pos = ", pos1)
print("Camera 2 pos = ", pos2)
x1, y1 = find_object(img1)
x2, y2 = find_object(img2)
print(f"x1={x1}, y1={y1}")
print(f"x2={x2}, y2={y2}")
#задача - зная калибровочное положение, определять координаты дрона x, y, z по двум камерам


# Run a simulation in stepping mode:
client.setStepping(False)
# sim.startSimulation()
while True:
    #Read camera
    t=sim.getSimulationTime()
    # print("t=", t)
    img1=get_cam_frame(sim, visionSensorHandle1)
    img2=get_cam_frame(sim, visionSensorHandle2)
    v.frame=img1
    x1, y1 = find_object(img1)
    x2, y2 = find_object(img2)
    # print(f"x1={x1}, y1={y1}")
    # print(f"x2={x2}, y2={y2}")
    # cv2.imshow("frame", img)
    # cv2.waitKey(0)
    # try:
    #     x, y = find_object(img)
    #     dx=x - img.shape[0]/2
    #     print("dx=", dx)
    #     setMovement(v, 0, dx/100)
    # except:
    #     pass


    client.step()  # triggers next simulation step