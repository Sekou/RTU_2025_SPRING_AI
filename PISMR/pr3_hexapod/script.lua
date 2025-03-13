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

    --IK:
    local simBase=sim.getObject('..')
    ikEnv=simIK.createEnvironment()
    -- Prepare the ik group, using the convenience function 'simIK.addElementFromScene':
    ikGroup=simIK.createGroup(ikEnv)
    for i=1,#simLegTips,1 do
        simIK.addElementFromScene(ikEnv,ikGroup,simBase,simLegTips[i],simLegTargets[i],simIK.constraint_position)
    end

end

function sysCall_actuation()
    if sim.getStringSignal("IK")=="calc" then
        simIK.handleGroup(ikEnv,ikGroup,{syncWorlds=true,allowError=true})
    end
end


function sysCall_thread()

end

