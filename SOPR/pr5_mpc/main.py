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

def calc_dist_segm(p, segm):
    (x1, y1), (x2, y2), (x3, y3) = segm[0], segm[1], p
    px,py = x2 - x1,y2 - y1
    norm = px * px + py * py
    u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)
    if u > 1:u = 1
    elif u < 0:u = 0
    x, y = x1 + u * px, y1 + u * py
    dx, dy = x - x3, y - y3
    dist = (dx * dx + dy * dy) ** .5
    return dist

def calc_dist_path(p, path):
    segments=zip(path[:-1], path[1:])
    dd=[calc_dist_segm(p, s) for s in segments]
    return min(dd)

def calc_integral_err_path(pts, path):
    ee=[calc_dist_path(p, path) for p in pts]
    return np.mean(ee)

def controlMPC(robot, path):
    bestF = None
    bestE = 100500
    ff = []
    for steer in [-1, -0.5, 0, 0.5, 1]:
        f = Forecast(robot.L, robot.getPos(), robot.alpha, 50, steer, 1, 0.1)
        f.predict()
        ff.append(f)
        p=f.predictions[-1][:2]
        err = calc_dist_path(p, path)
        err_ = calc_integral_err_path([p[:2] for p in f.predictions], path)
        e_goal = dist(p, goal)
        e_total = 1 * err_ + 1 * e_goal
        if e_total < bestE:
            bestE = e_total
            bestF = f
    robot.speed=bestF.speed
    robot.steer=bestF.steer

class Forecast:
    def __init__(self, L, pos0, alpha0, speed, steer, delta_t, dt):
        self.L, self.speed, self.steer, self.delta_t, self.dt = L, speed, steer, delta_t, dt
        self.p0=[*pos0, alpha0]
        self.predictions=[]
    def predict(self):
        self.predictions=[]
        for t in np.arange(0,self.delta_t, self.dt):
            p_curr=self.p0
            if self.predictions: p_curr=self.predictions[-1]
            p = predictXYA(*p_curr, self.L, self.speed, self.steer, t)
            self.predictions.append(p)
    def draw(self, screen, color=(0,255,0)):
        for p in self.predictions:
            pygame.draw.circle(screen, color, p[:2], 5, 3)

if __name__=="__main__":
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot = Robot(100, 100, 1)

    time = 0
    ind_goal=0

    path = [
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

        goal=path[ind_goal]
        # robot.goto(goal, dt)
        controlMPC(robot, path)

        robot.sim(dt)

        bestF=None
        bestE=100500

        ff=[]
        for steer in [-1, -0.5, 0, 0.5, 1]:
            f=Forecast(robot.L, robot.getPos(), robot.alpha, robot.speed, steer, 1, 0.1)
            f.predict()
            ff.append(f)
            # err0=calc_dist_path([100,100], [[100,0], [0,100]])
            err = calc_dist_path(f.predictions[-1][:2], path)
            err_ = calc_integral_err_path([p[:2] for p in f.predictions], path)
            e_goal=dist(robot.getPos(), goal)
            e_total=1*err_ + 1*e_goal

            if e_total < bestE:
                bestE=e_total
                bestF=f

        if dist(robot.getPos(), goal)<30:
            ind_goal=(ind_goal+1)%len(path)

        robot.draw(screen)

        for i,g in enumerate(path):
            r=7 if g==goal else 4
            pygame.draw.circle(screen, (255, 0, 0), g, r, 3)
            if i>0: pygame.draw.line(screen, (0,0,255), path[i - 1], path[i], 2)

        for f in ff:
            color=(0,255,0) if f==bestF else (255, 0, 0)
            f.draw(screen, color)

        drawText(screen, f"Time = {time:.3f}", 5, 5)
        drawText(screen, f"Err = {err:.3f}", 5, 25)
        drawText(screen, f"Err (Line) = {err_:.3f}", 5, 45)

        pygame.display.flip()
        timer.tick(fps)
        time += dt

