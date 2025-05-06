import math, time, numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
TIME=60

#управление роботом на основе таксиса (двигательного принципа) Брайтенберга

print('Program started')
client = RemoteAPIClient()
sim = client.getObject('sim')
defaultIdleFps = sim.getInt32Param(sim.intparam_idle_fps)
sim.setInt32Param(sim.intparam_idle_fps, 0) #set max loop rate


jointHandles = [0]*7
s="./LBRiiwa7R800/joint"
for i in range(7):
    jointHandles[i] = sim.getObject(s)
    s+=f"/link{i+2}_resp/joint"

# Run a simulation in stepping mode:
client.setStepping(True)
sim.startSimulation()
while (t := sim.getSimulationTime()) < TIME:
    print(f'Simulation time: {t:.2f}')

    #обработка информации
    _="test"

    #движение
    _="test"

    client.step()  # triggers next simulation step

#stop
sim.stopSimulation()
# Restore the original idle loop frequency:
sim.setInt32Param(sim.intparam_idle_fps, defaultIdleFps)
print('Program ended')
