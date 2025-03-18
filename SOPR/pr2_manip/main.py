# 2025, by S. Diane

import pygame
from oauthlib.uri_validate import segment
from pygame.locals import *
import sys, pygame, math
import numpy as np

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p2, p1))


pygame.font.init()
def drawText(screen, s, x, y, sz=30, color=(0,0,0)): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    screen.blit(font.render(s, True, (0,0,0)), (x,y))

def calc_circular_dist(alpha1, alpha2):
    d=alpha2-alpha1
    d2=math.pi*2+d
    if d2>math.pi: d2-=math.pi*2
    return d if abs(d)<abs(d2) else d2

# звено манипулятора
class Link:
    def __init__(self, L, alpha):
        self.L = L  # длина звена
        self.alpha = alpha  # локальный угол поворота
        self.P1 = np.zeros(2)  # координаты точки основания
        self.Angle = 0  # глобальный угол поворота
        self.P2 = np.zeros(2)  # координаты конечной точки

    def calc(self):  # расчет
        s, c = math.sin(self.Angle), math.cos(self.Angle)
        self.P2 = self.P1 + self.L * np.array([c, s])

    def draw(self, screen):
        pygame.draw.line(screen, (0, 0, 0), self.P1, self.P2, 3)
        pygame.draw.circle(screen, (0, 0, 255), self.P1, 3)
        pygame.draw.circle(screen, (0, 0, 255), self.P2, 3)


# манипуляционный робот с ангулярной кинематикой
class RobotManipulator:
    def __init__(self, lengths):
        self.lengths = lengths
        self.links = [Link(lengths[i], -0.3) for i in range(len(lengths))]
        self.endPos = np.zeros(2)
        self.traj = []

    def update_traj(self):
        if not self.traj or dist(self.endPos, self.traj[-1])>10:
            self.traj.append(self.endPos)
            #TODO: path simplifictaion

    def draw(self, screen):  # отрисовка
        for l in self.links:
            l.draw(screen)
        self.drawBasement(screen)
        for i in range(1, len(self.traj)):
            pygame.draw.line(screen, (255, 0, 255), self.traj[i-1], self.traj[i], 1)

    def drawBasement(self, screen):
        pC = self.links[0].P1
        pL, pR = [pC[0] - 10, pC[1]], [pC[0] + 10, pC[1]]
        pygame.draw.line(screen, (0, 0, 0), pL, pR, 3)
        for p in [pL, pC, pR]:
            pygame.draw.line(screen, (0, 0, 0), p, [p[0] - 5, p[1] + 5], 3)

    def setAngles(self, angles):  # прямая задача кинематики
        for i in range(len(self.links)):
            self.links[i].alpha = angles[i]
        self.calc()
        return (self.endPos)

    def calc(self):  # расчет
        for l in self.links:
            l.Angle = 0
        for i in range(len(self.links)):
            self.links[i].Angle = self.links[i].alpha
            if (i > 0):
                self.links[i].Angle += self.links[i - 1].Angle
                self.links[i].P1 = self.links[i - 1].P2
            self.links[i].calc()
            self.endPos = self.links[-1].P2

    def solve_IK(self, x, y): #решение обратной задачи кинематики
        def find_q(ind): #подбор конкретной обобщенной координаты
            d0=dist(self.endPos, [x,y])
            dd, aa=[],[]
            for a in np.arange(0, 2*math.pi, 0.05):
                self.links[ind].alpha=a
                self.calc()
                dd.append(dist(self.endPos, [x, y]))
                aa.append(a)
            self.links[ind].alpha = aa[np.argmin(dd)]

        for j in range(3): #TODO: make solving in 1 pass
            for i in range(len(self.links)):
                find_q(i)

    def calc_Jacobi_mat(self):
        #TODO: account for more links
        l1, l2=self.links[0].L, self.links[1].L
        a1, a2=self.links[0].alpha, self.links[1].alpha
        s1,s12=math.sin(a1),math.sin(a1+a2)
        c1,c12=math.cos(a1),math.cos(a1+a2)
        dx_dq1=-l1*s1-l2*s12
        dx_dq2=-l2*s12
        dy_dq1 = l1 * c1 + l2 * c12
        dy_dq2 = l2 * c12
        J=[[dx_dq1, dx_dq2],[dy_dq1, dy_dq2]]
        return J


class TrajSegment:
    def __init__(self, p1, p2):
        self.p1, self.p2=p1, p2
    def draw(self, screen):  # отрисовка
        pygame.draw.line(screen, (0,0,255), self.p1, self.p2, 2)

#TODO: отрезок
#TODO: интерполяция координат
#TODO: отрисовка траектории концевой точки манипулятора



if __name__ == "__main__":

    MODE="manual"

    # графические переменные
    width = 800
    height = 600
    timer = pygame.time.Clock()
    fps = 3
    dt = 1 / fps
    screen = pygame.display.set_mode((width, height))
    pos = (0, 0)

    segment = TrajSegment([370, 280], [430, 370])

    # основные переменные

    r = RobotManipulator([200, 120])
    r.links[0].P1 = [300, 450]

    qq1, qq2 = [], []

    while True:  # цикл моделирования
        for events in pygame.event.get():
            if events.type == QUIT:
                sys.exit(0)
            if events.type == KEYDOWN:
                if events.key == pygame.K_1:
                    r.solve_IK(*segment.p1)
                    qq1=[l.alpha for l in r.links]
                if events.key == pygame.K_2:
                    r.solve_IK(*segment.p2)
                    qq2=[l.alpha for l in r.links]
                if events.key == pygame.K_p:
                    print(qq1)
                    print(qq2)
                if events.key == pygame.K_z:
                    MODE = "test motion"
                    r.traj=[]
                if events.key == pygame.K_x:
                    MODE = "manual"
                    r.traj = []
                if events.key == pygame.K_c:
                    MODE = "interpolation"
                    r.traj = []
                if events.key == pygame.K_v:
                    MODE = "interpolation2"
                    r.traj = []

        screen.fill((255, 255, 255))
        if MODE == "test motion":
            r.links[0].alpha += -0.2 * dt
            r.links[1].alpha += 0.4 * dt
            r.update_traj()
        if MODE == "interpolation":
            ww=[0.1, 0.1]
            qq = [l.alpha for l in r.links]
            dqdq=[calc_circular_dist(qq1[i], qq2[i]) for i, l in enumerate(r.links)]
            for i, l in enumerate(r.links):
                dq=calc_circular_dist(qq[i], qq2[i])
                if abs(dq)>0.05:
                    l.alpha+=ww[i]*dt*np.sign(dqdq[i])
            r.update_traj()
        if MODE == "interpolation2":
            dpos=np.subtract(segment.p2, segment.p1)
            if dist(r.endPos, segment.p2)>5:
                J=r.calc_Jacobi_mat()
                Jinv=np.linalg.inv(J)
                dq = np.matmul(Jinv, dpos)
                for i, l in enumerate(r.links):
                    l.alpha+=0.1*dq[i]*dt
            r.update_traj()

        r.calc()
        r.draw(screen)
        segment.draw(screen)

        drawText(screen, f"q1={r.links[0].alpha:.2f}", 5, 5)
        drawText(screen, f"q2={r.links[1].alpha:.2f}", 5, 25)
        drawText(screen, f"x={r.endPos[0]:.2f}", 5, 45)
        drawText(screen, f"y={r.endPos[1]:.2f}", 5, 65)
        if qq1 and qq2:
            drawText(screen, f"dq1={calc_circular_dist(qq1[0], qq2[0]):.2f}", 5, 85)
            drawText(screen, f"dq2={calc_circular_dist(qq1[1], qq2[1]):.2f}", 5, 105)

        pygame.display.flip()
        timer.tick(fps)
