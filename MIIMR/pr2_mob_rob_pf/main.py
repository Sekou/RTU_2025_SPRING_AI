
import sys, pygame
import numpy as np
import math

import pygame.draw

pygame.font.init()
def drawText(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

def rot(v, ang): #поворот вектора на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def limAng(ang): #ограничение угла в пределах +/-pi
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2): #расстояние между точками
    return np.linalg.norm(np.subtract(p1, p2))

def drawRotRect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

sz = (800, 600)

class Tree:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.color=(0,125,0)
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1 = np.array(self.get_pos())
        p2 = p1+[0,-35]
        pygame.draw.line(screen, self.color, p1, p2, 2)
        self.draw_branch(screen, p2, 10, 0.7, 0)
        self.draw_branch(screen, p2, 15, 0.7, 8)
        self.draw_branch(screen, p2, 20, 0.7, 16)
        self.draw_branch(screen, p2, 10, -0.7+math.pi, 0)
        self.draw_branch(screen, p2, 15, -0.7+math.pi, 8)
        self.draw_branch(screen, p2, 20, -0.7+math.pi, 16)
    def draw_branch(self, screen, p2, l, a, dy):
        s, c = math.sin(a), math.cos(a)
        pygame.draw.line(screen, self.color, p2+[0,dy], p2+[l*c, l*s+dy], 2)

class Landmark:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1 = np.array(self.get_pos())
        pygame.draw.circle(screen, (0,0,0), p1, 3, 2)

class Particle:
    def __init__(self, x, y):
        self.Q = 0
        self.x, self.y = x, y
        self.color = (0,0,255)
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1 = np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, 3, 2)

class ParticleFilter:
    def __init__(self, x0, y0, num=30, sigma=20):
        self.particles=[]
        self.num=num
        self.sigma=sigma
        for i in range(num):
            x_=np.random.normal(x0, self.sigma)
            y_=np.random.normal(y0, self.sigma)
            self.particles.append(Particle(x_, y_))
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
    def estimate(self, robot_pos, robot_ang, lm_pos, measured_dist, measured_ang):
        for p in self.particles:
            etalon_dist=dist(p.get_pos(), robot_pos)
            delta=measured_dist-etalon_dist
            x1, y1, x2, y2 = [*robot_pos, *lm_pos]
            a2 = math.atan2(y2 - y1, x2 - x1)
            etalon_ang = limAng(a2 - robot_ang)
            delta2=measured_ang-etalon_ang
            d=delta*0.1 + delta2*1
            p.Q=np.exp(-d*d*0.01)
            p.color=(0, 0, int(255*p.Q))
    def repopulate(self):
        self.particles=sorted(self.particles, key=lambda p: p.Q)
        self.particles=self.particles[self.num//2:]
        while len(self.particles)<self.num:
            i=np.random.randint(len(self.particles))
            p=self.particles[i]
            p2=Particle(np.random.normal(p.x, 5), np.random.normal(p.y, 5))
            self.particles.append(p2)
    def getResult(self):
        pp=[p.get_pos() for p in self.particles]
        return np.mean(pp, axis=0)

class Robot:
    def __init__(self, x, y):
        self.radius=15
        self.color=(0,0,0)
        self.x, self.y, self.a=x,y,0
        self.vlin, self.vrot=0,0
        self.observerd_lm=None #ориентир
        self.measurm_err_d=3 #ошибка измерения дальности
        self.measurm_err_a=0.05 #ошибка измерения угла
        self.last_measurm_d = 0
        self.last_measurm_a = 0
    def get_pos(self):
        return [self.x, self.y]
    def get_expected_lm_pos(self):
        p1=np.array(self.get_pos())
        a_ = self.a + self.last_measurm_a
        return p1 + [math.cos(a_) * self.last_measurm_d, math.sin(a_) * self.last_measurm_d]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        if self.observerd_lm:
            p2=self.get_expected_lm_pos()
            pygame.draw.line(screen, (180, 180, 180), p1, p2, 1)
            drawText(screen, f"{self.last_measurm_d:.0f}", *(0.5 * (p1 + p2)))
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        self.x+=c*self.vlin*dt
        self.y+=s*self.vlin*dt
        self.a+=self.vrot*dt

    def measure_dist(self, lm):
        d = dist(self.get_pos(), lm.get_pos()) + np.random.normal(0, self.measurm_err_d)
        self.last_measurm_d = d
        return d
    def measure_ang(self, lm):
        x1, y1, x2, y2=[*self.get_pos(), *lm.get_pos()]
        a1=self.a
        a2=math.atan2(y2-y1, x2-x1)
        da=limAng(a2-a1)
        da+=np.random.normal(0, self.measurm_err_a)
        self.last_measurm_a = da
        return da

def sim(robot, lm, dt):
    robot.simulate(dt)
    d = robot.measure_dist(lm)
    a = robot.measure_ang(lm)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    dt = 1 / fps

    robot = Robot(200, 200)
    lm = Landmark(500, 300)
    sim(robot, lm, dt)
    pf = ParticleFilter(*robot.get_expected_lm_pos())

    robot.observerd_lm=lm
    tree=Tree(500, 300)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w:
                    robot.vlin=50
                    robot.vrot = 0
                if ev.key == pygame.K_s: robot.vlin=-50
                if ev.key == pygame.K_a: robot.vrot=-1
                if ev.key == pygame.K_d: robot.vrot=+1
                if ev.key == pygame.K_z: robot.vrot = robot.vlin = 0
                if ev.key == pygame.K_1:
                    pf.estimate(robot.get_pos(), robot.a, lm.get_pos(), robot.measure_dist(lm), robot.measure_ang(lm))
                if ev.key == pygame.K_2:
                    pf.repopulate()

        sim(robot, lm, dt)
        pf.estimate(robot.get_pos(), robot.a, lm.get_pos(), robot.measure_dist(lm), robot.measure_ang(lm))

        pf.repopulate()

        res=pf.getResult()

        screen.fill((255, 255, 255))
        robot.draw(screen)
        lm.draw(screen)
        pf.draw(screen)

        pygame.draw.circle(screen, (255, 0, 0), res, 3, 3)

        tree.draw(screen)
        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024