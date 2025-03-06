import math, time, numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
TIME=60
NUM_LEGS=6

#управление гексаподом
print('Program started')
client = RemoteAPIClient()
sim = client.getObject('sim')

#Prepare initial values and retrieve handles:
antBase=sim.getObject('./hexapod/base')
legBase=sim.getObject('./hexapod/legBase')
simLegTips = [None]*NUM_LEGS
simLegTargets = [None]*NUM_LEGS
for i in range(NUM_LEGS):
    simLegTips[i] = sim.getObject(f'./hexapod/footTip{i}')
    simLegTargets[i] = sim.getObject(f'./hexapod/footTarget{i}')
initialPos = [None]*NUM_LEGS
for i in range(NUM_LEGS):
    initialPos[i] = sim.getObjectPosition(simLegTips[i], legBase)
legMovementIndex = {1, 4, 2, 6, 3, 5}
stepProgression = 0
realMovementStrength = 0

movData = {}
movData["vel"] = 0.5
movData["amplitude"] = 0.16
movData["height"] = 0.04
movData["dir"]= 0
movData["rot"] = 0
movData["strength"] = 0

def moveToPose(obj,relObj,pos,euler,vel,accel):
    print(pos)
    print(euler)
    params = {
        "object": obj,
        "relObject": relObj,
        "targetPose": sim.buildPose(pos, euler),
        "maxVel": [vel],
        "maxAccel": [accel],
        "maxJerk": [0.1],
        "metric": [1, 1, 1, 0.1]
    }
    sim.moveToPose(params)

# Run a simulation in async mode:
client.setStepping(False)

sizeFactor = sim.getObjectSizeFactor(antBase)
vel = 0.05
accel = 0.05
initialP = [0, 0, 0]
initialO = [0, 0, 0]
initialP[2] = initialP[2] - 0.03 * sizeFactor

while (t := sim.getSimulationTime()) < TIME:
    print(f'Simulation time: {t:.2f}')

    #движение
    p = [initialP[0], initialP[1]+t, initialP[2]]
    o = [initialO[0], initialO[1], initialO[2]]
    moveToPose(legBase, antBase, p, o, vel, accel)
    # moveToPose()

    client.step()  # triggers next simulation step

print('Program ended')
