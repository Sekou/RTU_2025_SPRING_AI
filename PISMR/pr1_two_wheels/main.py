import math, time, numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
TIME=60

#управление роботом на основе таксиса (двигательного принципа) Брайтенберга

print('Program started')
client = RemoteAPIClient()
sim = client.getObject('sim')
defaultIdleFps = sim.getInt32Param(sim.intparam_idle_fps)
sim.setInt32Param(sim.intparam_idle_fps, 0) #set max loop rate

usensors = []
for i in range(16):
    usensors.append(sim.getObject(f"./PioneerP3DX/ultrasonicSensor[{i}]"))
motorLeft = sim.getObject("./PioneerP3DX/leftMotor")
motorRight = sim.getObject("./PioneerP3DX/rightMotor")

noDetectionDist = 0.5
maxDetectionDist = 0.2
detect = np.zeros(16)
braitenbergL = [-0.2, -0.4, -0.6, -0.8, -1, -1.2, -1.4, -1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
braitenbergR = [-1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Run a simulation in stepping mode:
client.setStepping(True)
sim.startSimulation()
while (t := sim.getSimulationTime()) < TIME:
    print(f'Simulation time: {t:.2f}')

    #чтение датчиков
    for i in range(16):
        val = sim.readProximitySensor(usensors[i])
        res, dist=val[0], val[1]
        if res > 0 and dist < noDetectionDist:
            if dist < maxDetectionDist:
                dist = maxDetectionDist
            detect[i] = 1 - (dist - maxDetectionDist) / (noDetectionDist - maxDetectionDist)
        else: detect[i] = 0

    #движение
    v0 = 2
    vLeft = v0 + np.dot(braitenbergL, detect)
    vRight = v0 + np.dot(braitenbergR, detect)
    sim.setJointTargetVelocity(motorLeft, vLeft)
    sim.setJointTargetVelocity(motorRight, vRight)

    client.step()  # triggers next simulation step

#stop
sim.stopSimulation()
# Restore the original idle loop frequency:
sim.setInt32Param(sim.intparam_idle_fps, defaultIdleFps)
print('Program ended')
