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

#
# moveBody=function(index)
#     local p={initialP[1],initialP[2],initialP[3]}
#     local o={initialO[1],initialO[2],initialO[3]}
#     moveToPose(legBase,antBase,p,o,vel,accel)
#     if (index==0) then
#         -- up/down
#         p[3]=p[3]-0.03*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel*2,accel)
#         p[3]=p[3]+0.03*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel*2,accel)
#     end
#     if (index==1) then
#         -- 4x twisting
#         o[1]=o[1]+5*math.pi/180
#         o[2]=o[2]-05*math.pi/180
#         o[3]=o[3]-15*math.pi/180
#         p[1]=p[1]-0.03*sizeFactor
#         p[2]=p[2]+0.015*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[1]=o[1]-10*math.pi/180
#         o[3]=o[3]+30*math.pi/180
#         p[2]=p[2]-0.04*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[1]=o[1]+10*math.pi/180
#         o[2]=o[2]+10*math.pi/180
#         p[2]=p[2]+0.03*sizeFactor
#         p[1]=p[1]+0.06*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[1]=o[1]-10*math.pi/180
#         o[3]=o[3]-30*math.pi/180
#         p[2]=p[2]-0.03*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#     end
#     if (index==2) then
#         -- rolling
#         p[3]=p[3]-0.0*sizeFactor
#         o[1]=o[1]+17*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[1]=o[1]-34*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[1]=o[1]+17*math.pi/180
#         p[3]=p[3]+0.0*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#     end
#     if (index==3) then
#         -- pitching
#         p[3]=p[3]-0.0*sizeFactor
#         o[2]=o[2]+15*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[2]=o[2]-30*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[2]=o[2]+15*math.pi/180
#         p[3]=p[3]+0.0*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#     end
#     if (index==4) then
#         -- yawing
#         p[3]=p[3]+0.0*sizeFactor
#         o[3]=o[3]+30*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[3]=o[3]-60*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         o[3]=o[3]+30*math.pi/180
#         moveToPose(legBase,antBase,p,o,vel,accel)
#         p[3]=p[3]-0.0*sizeFactor
#         moveToPose(legBase,antBase,p,o,vel,accel)
#     end
# end