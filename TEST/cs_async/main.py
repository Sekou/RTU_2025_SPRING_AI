import math, time, numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

#управление роботом на основе таксиса (двигательного принципа) Брайтенберга

print('Program started')
TIME=60

client = RemoteAPIClient()
sim = client.getObject('sim')

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
v0 = 2

# Run a simulation in asynchronous mode:
client.setStepping(False)
while (t := sim.getSimulationTime()) < TIME:
    print(f'Simulation time: {t:.2f}')

    # motion
    for i in range(16):
        val = sim.readProximitySensor(usensors[i])
        res, dist = val[0], val[1]
        if res > 0 and dist < noDetectionDist:
            if dist < maxDetectionDist:
                dist = maxDetectionDist
            detect[i] = 1 - (dist - maxDetectionDist) / (noDetectionDist - maxDetectionDist)
        else:
            detect[i] = 0

    vLeft = v0 + np.dot(braitenbergL, detect)
    vRight = v0 + np.dot(braitenbergR, detect)

    sim.setJointTargetVelocity(motorLeft, vLeft)
    sim.setJointTargetVelocity(motorRight, vRight)

# If you need to make sure we really stopped:
while sim.getSimulationState() != sim.simulation_stopped:
    time.sleep(0.1)

print('Program ended')

