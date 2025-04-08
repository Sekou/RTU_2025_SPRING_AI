import itertools
import sys, pygame
import numpy as np
import math
from mobile_robot2d import Robot, dist

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf = font.render(s, True, (0, 0, 0))
    screen.blit(surf, (x, y))
sz = (800, 600)


def predictXYA(x, y, ang, L, vlin, steer, dt):
    v = [vlin * dt, 0]
    s, c = math.sin(ang), math.cos(ang)
    delta = [v[0] * c - v[1] * s, v[0] * s + v[1] * c]
    x += delta[0]
    y += delta[1]
    if steer != 0:
        R = L / steer
        ang += vlin * dt / R
    return [x, y, ang]

if __name__=="__main__":
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot = Robot(100, 100, 1)

    time = 0
    ind_goal=0
    goals = [
        [600, 500],
        [200, 500],
        [200, 200],
        [600, 200]]

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sys.exit(0)
        dt = 1 / fps
        screen.fill((255, 255, 255))

        goal=goals[ind_goal]
        robot.goto(goal, dt)

        robot.sim(dt)

        predictions=[]
        for t in np.arange(0,1, 0.1):
            p_curr=[robot.x, robot.y, robot.alpha]
            if predictions: p_curr=predictions[-1]
            p = predictXYA(*p_curr, robot.L, robot.speed, robot.steer, t)
            predictions.append(p)

        if dist(robot.getPos(), goal)<30:
            ind_goal=(ind_goal+1)%len(goals)

        robot.draw(screen)

        for g in goals:
            r=7 if g==goal else 4
            pygame.draw.circle(screen, (255, 0, 0), g, r, 3)

        for p in predictions:
            pygame.draw.circle(screen, (0, 255, 0), p[:2], 5, 3)

        drawText(screen, f"Time = {time:.3f}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)
        time += dt
