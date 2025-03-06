import math, time, numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
TIME=60

#управление омниколесным роботом

print('Program started')
client = RemoteAPIClient()
sim = client.getObject('sim')
defaultIdleFps = sim.getInt32Param(sim.intparam_idle_fps)
sim.setInt32Param(sim.intparam_idle_fps, 0) #set max loop rate

#Prepare initial values and retrieve handles:
wheelJoints = [-1, -1, -1, -1] #front left, rear left, rear right, front right
wheelJoints[0] = sim.getObject('./youBot/rollingJoint_fl')
wheelJoints[1] = sim.getObject('./youBot/rollingJoint_rl')
wheelJoints[2] = sim.getObject('./youBot/rollingJoint_rr')
wheelJoints[3] = sim.getObject('./youBot/rollingJoint_fr')

def set_movement(vx, vy, va):
    sim.setJointTargetVelocity(wheelJoints[0],-vx-vy-va)
    sim.setJointTargetVelocity(wheelJoints[1],-vx+vy-va)
    sim.setJointTargetVelocity(wheelJoints[2],-vx-vy+va)
    sim.setJointTargetVelocity(wheelJoints[3],-vx+vy+va)

# Run a simulation in stepping mode:
client.setStepping(True)
sim.startSimulation()
while (t := sim.getSimulationTime()) < TIME:
    print(f'Simulation time: {t:.2f}')

    #движение
    set_movement(1, 0.2, -0.3)

    client.step()  # triggers next simulation step

#stop
sim.stopSimulation()
# Restore the original idle loop frequency:
sim.setInt32Param(sim.intparam_idle_fps, defaultIdleFps)
print('Program ended')

#
# sim=require'sim'
#
# function setMovement(forwBackVel,leftRightVel,rotVel)
#     -- Apply the desired wheel velocities:
#     sim.setJointTargetVelocity(wheelJoints[1],-forwBackVel-leftRightVel-rotVel)
#     sim.setJointTargetVelocity(wheelJoints[2],-forwBackVel+leftRightVel-rotVel)
#     sim.setJointTargetVelocity(wheelJoints[3],-forwBackVel-leftRightVel+rotVel)
#     sim.setJointTargetVelocity(wheelJoints[4],-forwBackVel+leftRightVel+rotVel)
# end
#
# function sysCall_thread()
#     --Prepare initial values and retrieve handles:
#     wheelJoints={-1,-1,-1,-1} -- front left, rear left, rear right, front right
#     wheelJoints[1]=sim.getObject('../rollingJoint_fl')
#     wheelJoints[2]=sim.getObject('../rollingJoint_rl')
#     wheelJoints[3]=sim.getObject('../rollingJoint_rr')
#     wheelJoints[4]=sim.getObject('../rollingJoint_fr')
#     armJoints={}
#     for i=0,4,1 do
#         armJoints[i+1]=sim.getObject('../youBotArmJoint'..i)
#     end
#
#     setMovement(0,0.5,0)
#     sim.wait(10)
#     setMovement(0,0,0.5)
# end

