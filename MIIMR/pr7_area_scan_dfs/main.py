
import sys, pygame
import numpy as np
import math

#поиск на графе местности в глубину (построение маршрута обхода)

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

class Area:
    def __init__(self, pts):
        self.pts=pts
    def draw(self, screen):
        for i in range(len(self.pts)):
            pygame.draw.line(screen, (0,0,255), self.pts[i-1], self.pts[i], 2)

class Edge:
    def __init__(self, n1, n2, w):
        self.n1=n1
        self.n2=n2
        self.w=w
    def draw(self, screen):
        pygame.draw.line(screen, (255,0,0), self.n1.get_pos(), self.n2.get_pos(), 2)

class Node:
    def __init__(self, pos):
        self.pos=pos
        self.edges=[]
    def get_pos(self):
        return self.pos
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 255, 0), self.get_pos(),2)

class Graph:
    def __init__(self, pts):
        self.nodes=[Node(p) for p in pts]
    def connect(self):
        for n in self.nodes:
            nn=[n2 for n2 in self.nodes if n2.pos[0]>n.pos[0] or n2.pos[1]>n.pos[1]]
            dd=[dist(n.pos, n2.pos) for n2 in nn]
            pairs=zip(dd, nn)
            pairs=sorted(pairs)
            pairs=list(pairs)
            n.edges.append(Edge(n, pairs[0][1]))
            n.edges.append(Edge(n, pairs[2][1]))

    def draw(self, screen):
        for n in self.nodes:
            n.draw(screen)

#see. https://www.eecs.umich.edu/courses/eecs380/HANDOUTS/PROJ2/InsidePoly.html
def point_inside_polygon2(point, vertices): #based on Randolph Franklin
    c = 0
    x, y = point
    for i in range(-1,len(vertices)-1):
        x1, y1 = vertices[i]
        x2, y2 = vertices[i + 1]
        if (y1 <= y and y < y2) or (y2 <= y and y < y1):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = 1 - c
    return c

def point_inside_polygon(p, poly, include_edges=True): #проверка нахождения точки внутри полигона
    # uses intersection count parity check for horizontal line
    (x,y),n,inside,(p1x, p1y) = p, len(poly), False, poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if p1y == p2y:
            if y == p1y:
                if min(p1x, p2x) <= x <= max(p1x, p2x): # horizontal edge
                    inside = include_edges
                    break
                if x < min(p1x, p2x): inside = not inside # point is to the left from current edge
        else:  # p1y!= p2y
            if min(p1y, p2y) <= y <= max(p1y, p2y):
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x
                if x == xinters:  # point on the edge
                    inside = include_edges
                    break
                if x < xinters:
                    inside = not inside # point is to the left from current edge
        p1x, p1y = p2x, p2y
    return inside

#определяем точки внутри многоугольника
def get_pts_inside(area, step=20):
    pts=[]
    for x in range(0, 800, step):
        for y in range(0, 600, step):
            check = point_inside_polygon2([x, y], area.pts)
            if check: pts.append([x,y])
    return pts

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    area=Area([[100, 100], [400, 150], [600,200], [500, 400], [200, 200]])
    pts_=get_pts_inside(area, 20)
    graph=Graph(pts_)
    graph.connect()

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps
        screen.fill((255, 255, 255))
        area.draw(screen)
        graph.draw(screen)
        # for p in pts_:
        #     pygame.draw.circle(screen, (0,0,0), p, 3)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024