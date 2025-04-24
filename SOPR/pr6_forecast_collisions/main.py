
import sys, pygame
import numpy as np
import math

#класс прямоугольного объекта
class Rect:
    def __init__(self, x, y, w, h, color):
        self.x, self.y, self.w, self.h, self.color=x, y, w, h, color
    def get_pos(self):
        return [self.x, self.y]
    def set_pos(self, pos):
        self.x, self.y = [*pos]
    def contains(self, pos):
        return self.x-self.w/2 < pos[0] < self.x+self.w/2 and \
               self.y-self.h/2 < pos[1] < self.y+self.h/2
    def draw(self, screen):
        bb=[self.x-self.w/2, self.y-self.h/2, self.w, self.h]
        pygame.draw.rect(screen, self.color, bb, 0)

class Wall(Rect):
    def __init__(self, x, y, length, is_vertical):
        self.is_vertical=is_vertical
        if is_vertical:
            super().__init__(x, y, 15, length, (0,0,0))
        else:
            super().__init__(x, y, length, 15, (0, 0, 0))

class Obst(Rect):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, (0,0,255))
        self.vx=25
        self.vy=-35
        self.collision_delay=0

    def find_collision_pt(self, wall):
        pp=[[self.x-self.w/2, self.y-self.h/2], [self.x+self.w/2, self.y-self.h/2],
            [self.x+self.w/2, self.y+self.h/2], [self.x-self.w/2, self.y+self.h/2]]
        if not wall.is_vertical:
            for p in pp:
                y_top=wall.y-wall.h/2 #верхняя грань стены
                if p[1]>y_top and p[1]-y_top<10:
                    return wall
                y_down=wall.y+wall.h/2 #нижняя грань стены
                if p[1]<y_down and y_down-p[1]<10:
                    return wall
        else:
            for p in pp:
                x_left=wall.x-wall.w/2 #левая грань стены
                if p[0]<x_left and x_left-p[0]<10:
                    return wall
                x_right=wall.x+wall.w/2 #правая грань стены
                if p[0]>x_right and p[0]-x_right<10:
                    return wall
        return None

    def sim(self, dt, walls):
        for wall in walls:
            found_wall = self.find_collision_pt(wall)
            if self.collision_delay < 0.0001 and found_wall:
                if found_wall.is_vertical:
                    self.vx=-self.vx
                else:
                    self.vy=-self.vy
                self.collision_delay=1
            elif self.collision_delay>0:
                self.collision_delay-=dt

        self.x+=self.vx*dt
        self.y+=self.vy*dt

class Agent(Rect):
    def __init__(self, x, y, sz):
        super().__init__(x, y, sz, sz, (255,0,0))

pygame.font.init()
def drawText(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    screen.blit(font.render(s, True, (0,0,0)), (x,y))

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

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    agent=Agent(sz[0]/2, sz[1]/2, 50)

    obsts=[Obst(200, 350, 50, 75)]

    walls = [ Wall(400, 50, 500, False),
            Wall(150, 300, 500, True),
            Wall(400, 550, 500, False),
            Wall(650, 300, 500, True)]

    grasped_obj=None
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button==1 and agent.contains(ev.pos):
                    grasped_obj=agent
            if ev.type == pygame.MOUSEMOTION:
                if grasped_obj:
                    grasped_obj.set_pos(ev.pos)
            if ev.type == pygame.MOUSEBUTTONUP:
                if grasped_obj:
                    grasped_obj=None

        dt=1/fps

        for o in obsts:
            o.sim(dt, walls)
            # wall=o.find_collision_pt(walls[2])
            # if wall:
            #     print("Collision")

        screen.fill((255, 255, 255))

        agent.draw(screen)

        for obst in obsts:
            obst.draw(screen)

        for wall in walls:
            wall.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024
