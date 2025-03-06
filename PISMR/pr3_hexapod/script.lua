sim=require'sim'
simIK=require'simIK'

function sysCall_init()
    antBase=sim.getObject('../base')
    legBase=sim.getObject('../legBase')

    local simLegTips={}
    simLegTargets={}
    for i=1,6,1 do
        simLegTips[i]=sim.getObject('../footTip'..i-1)
        simLegTargets[i]=sim.getObject('../footTarget'..i-1)
    end
    initialPos={}
    for i=1,6,1 do
        initialPos[i]=sim.getObjectPosition(simLegTips[i],legBase)
    end
    legMovementIndex={1,4,2,6,3,5}
    stepProgression=0
    realMovementStrength=0

    --IK:
    local simBase=sim.getObject('..')
    ikEnv=simIK.createEnvironment()
    -- Prepare the ik group, using the convenience function 'simIK.addElementFromScene':
    ikGroup=simIK.createGroup(ikEnv)
    for i=1,#simLegTips,1 do
        simIK.addElementFromScene(ikEnv,ikGroup,simBase,simLegTips[i],simLegTargets[i],simIK.constraint_position)
    end

    movData={}
    movData.vel=0.5
    movData.amplitude=0.16
    movData.height=0.04
    movData.dir=0
    movData.rot=0
    movData.strength=0
end

function sysCall_actuation()
    dt=sim.getSimulationTimeStep()

    dx=movData.strength-realMovementStrength
    if (math.abs(dx)>dt*0.1) then
        dx=math.abs(dx)*dt*0.5/dx
    end
    realMovementStrength=realMovementStrength+dx

    spsp={}
    for leg=1,6,1 do
        sp=(stepProgression+(legMovementIndex[leg]-1)/6) % 1
        offset={0,0,0}
        if (sp<(1/3)) then
            offset[1]=sp*3*movData.amplitude/2
        else
            if (sp<(1/3+1/6)) then
                s=sp-1/3
                offset[1]=movData.amplitude/2-movData.amplitude*s*6/2
                offset[3]=s*6*movData.height
            else
                if (sp<(2/3)) then
                    s=sp-1/3-1/6
                    offset[1]=-movData.amplitude*s*6/2
                    offset[3]=(1-s*6)*movData.height
                else
                    s=sp-2/3
                    offset[1]=-movData.amplitude*(1-s*3)/2
                end
            end
        end
        md=movData.dir+math.abs(movData.rot)*math.atan2(initialPos[leg][1]*movData.rot,-initialPos[leg][2]*movData.rot)
        offset2={offset[1]*math.cos(md)*realMovementStrength,offset[1]*math.sin(md)*realMovementStrength,offset[3]*realMovementStrength}
        p={initialPos[leg][1]+offset2[1],initialPos[leg][2]+offset2[2],initialPos[leg][3]+offset2[3]}
        sim.setObjectPosition(simLegTargets[leg],p,legBase) -- We simply set the desired foot position. IK is handled after that
    end
    simIK.handleGroup(ikEnv,ikGroup,{syncWorlds=true,allowError=true})

    stepProgression=stepProgression+dt*movData.vel
end

setStepMode=function(stepVelocity,stepAmplitude,stepHeight,movementDirection,rotationMode,movementStrength)
    movData={}
    movData.vel=stepVelocity
    movData.amplitude=stepAmplitude
    movData.height=stepHeight
    movData.dir=math.pi*movementDirection/180
    movData.rot=rotationMode
    movData.strength=movementStrength
end

function sysCall_thread()

end

