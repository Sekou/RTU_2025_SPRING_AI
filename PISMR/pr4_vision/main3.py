


from pathlib import Path
script_dir = Path(__file__).parent.absolute()
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import cv2
import numpy as np

def swap(vec):
    return vec[::-1]
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

wheelJoints=[-1,-1,-1,-1] #front left, rear left, rear right, front right
wheelJoints[0]=sim.getObject('/youBot/rollingJoint_fl')
wheelJoints[1]=sim.getObject('/youBot/rollingJoint_rl')
wheelJoints[2]=sim.getObject('/youBot/rollingJoint_rr')
wheelJoints[3]=sim.getObject('/youBot/rollingJoint_fr')

visionSensorHandle = sim.getObjectHandle('/youBot/kinect/rgb')

def setMovement(forwBackVel,leftRightVel,rotVel):
    sim.setJointTargetVelocity(wheelJoints[0],-forwBackVel-leftRightVel-rotVel)
    sim.setJointTargetVelocity(wheelJoints[1],-forwBackVel+leftRightVel-rotVel)
    sim.setJointTargetVelocity(wheelJoints[2],-forwBackVel-leftRightVel+rotVel)
    sim.setJointTargetVelocity(wheelJoints[3],-forwBackVel+leftRightVel+rotVel)


defaultIdleFps = sim.getInt32Param(sim.intparam_idle_fps)
sim.setInt32Param(sim.intparam_idle_fps, 0)

# Run a simulation in stepping mode:
client.setStepping(True)
sim.startSimulation()
last_t=sim.getSimulationTime()
img_ind=0
while (t := sim.getSimulationTime()) < 30:
    #youBot motion
    v=7; w=1.8
    # if(t<5): setMovement(v, 0, 0)
    # elif(t<15): setMovement(v, 0, w)
    # elif(t<25): setMovement(v, 0, w)
    # elif(t<35): setMovement(v, 0, 0)
    if(t-last_t>0.5):
        #Read camera
        img, resX, resY = sim.getVisionSensorCharImage(visionSensorHandle)
        img = np.frombuffer(img, dtype=np.uint8).reshape(resY, resX, 3)
        img = cv2.flip(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 0)
        # cv2.imwrite(f"{script_dir}/images/{img_ind}.jpg", img)
        # img_ind+=1
        last_t=t
        try:
            x, y = find_object(img)
            dx=x - img.shape[0]/2
            print("dx=", dx)
            setMovement(v, 0, dx/100)
        except:
            pass


    client.step()  # triggers next simulation step

#youBot stop
setMovement(0, 0, 0)

sim.stopSimulation()
sim.setInt32Param(sim.intparam_idle_fps, defaultIdleFps)
print('Program ended')

