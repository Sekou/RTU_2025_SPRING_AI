import math, time, numpy as np
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
TIME=60

#управление роботом на основе таксиса (двигательного принципа) Брайтенберга

print('Program started')
client = RemoteAPIClient()
sim = client.getObject('sim')
defaultIdleFps = sim.getInt32Param(sim.intparam_idle_fps)
sim.setInt32Param(sim.intparam_idle_fps, 0) #set max loop rate


# Run a simulation in stepping mode:
client.setStepping(True)
sim.startSimulation()

last_t=-100500
while (t := sim.getSimulationTime()) < TIME:
    print(f'Simulation time: {t:.2f}')
    if t-last_t>0.2:
        h=sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.05, 0.05, 0.05], 0)
        sim.setObjectPosition(h, -1, [0,0,0.25])

        p=[sim.shapefloatparam_init_velocity_x,
           sim.shapefloatparam_init_velocity_y,
           sim.shapefloatparam_init_velocity_z]
        v=[0,1,4]
        for a, b in zip(p, v):
            sim.setObjectFloatParameter(h, a, b)

        sim.setObjectSpecialProperty(h, sim.objectspecialproperty_detectable)
        sim.setObjectInt32Param(h, sim.shapeintparam_static, 0)
        sim.setObjectInt32Param(h, sim.shapeintparam_respondable, 1)
        last_t=t


    client.step()  # triggers next simulation step

#stop
sim.stopSimulation()
# Restore the original idle loop frequency:
sim.setInt32Param(sim.intparam_idle_fps, defaultIdleFps)
print('Program ended')
