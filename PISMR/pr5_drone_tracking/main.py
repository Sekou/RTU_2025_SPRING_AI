from pathlib import Path
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import cv2
import numpy as np

print('Program started')

client = RemoteAPIClient()
sim = client.getObject('sim')

visionSensorHandle1 = sim.getObjectHandle('/diningChair[0]/kinect/rgb')
visionSensorHandle2 = sim.getObjectHandle('/diningChair[1]/kinect/rgb')

print(visionSensorHandle1)
print(visionSensorHandle2)