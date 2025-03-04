
import sys, pygame
from random import random

import numpy as np
import math

import random

from fontTools.ttLib.scaleUpem import visit
from soupsieve import select

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

def rot(v, ang): #поворот вектора на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def lim_ang(ang): #ограничение угла в пределах +/-pi
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2): #расстояние между точками
    return np.linalg.norm(np.subtract(p1, p2))

def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rot_arr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

class Obj:
    def __init__(self, id, x, y, sz):
        self.id, self.x, self.y, self.sz = id, x, y, sz
        self.selected=False
    def draw(self, screen):
        colors=[(255,0,0), (0,255,0), (0,0,255), (128,128,0), (128,0,128), (0,128,128)]
        if self.selected:
            pygame.draw.circle(screen, (0,0,0),
                               (self.x, self.y-self.sz/2), 3)
        pygame.draw.rect(screen, colors[self.id],
                         [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz])
        draw_text(screen, f"{self.id}", self.x-4, self.y-4, 25)

class Event: # событие = передикат = действие
    def __init__(self, parent, i_swap, all_objects, depth=0):
        self.depth=depth #глубина узла
        self.i_swap=i_swap #индекс перестановки
        self.objects=[*all_objects] #массив переставленных объектов
        if i_swap>=0:
            swap(i_swap, self.objects)
        self.parent=parent #родительский узел
        self.next_events=[] #варианты дальнейших перестановок

    def generate_next_events(self, all_objects, remaining_objects, max_depth=6):
        if self.depth>=max_depth: return
        for i, o in enumerate(all_objects):
            # if o not in remaining_objects: continue #допущение: нельзя переставлять объект дважды
            # remaining_objects2=[o2 for o2 in remaining_objects if o2!=o]
            remaining_objects2=remaining_objects
            if remaining_objects2:#рекурсивная генерация дальнейших событий
                ev=Event(self, i, all_objects, self.depth+1) #новое событие по сортировке объектов
                ev.generate_next_events(all_objects, remaining_objects2)
                self.next_events.append(ev)
    def to_string(self):
        return "; ".join(str(o.id) for o in self.objects)
    def to_string_full(self):
        pad="".join(["\t"]*self.depth)
        s=pad+self.to_string()+"\n"
        for e in self.next_events:
            s+=pad+e.to_string_full()
        return s
    def get_path(self):
        n=self
        res=[]
        while n.parent:
            res.append(n)
            n=n.parent
        return res

class Graph:
    def __init__(self, objects):
        self.root_event=Event(None, -1, objects) #корневое событие по сортировке объектов
        self.root_event.generate_next_events(objects, objects)
    def to_string(self):
        return  self.root_event.to_string_full()
    def find_plan(self, desired_result): # например, desired_result = "0; 2; 1; 3; 4; 5"
        result=None
        min_depth=math.inf
        #требуется реализовать обход графа в ширину
        current_nodes=[self.root_event]
        for n in current_nodes:
            if n.to_string()==desired_result: #предикат узла равен результату
                return n.get_path()
            else:
                current_nodes.extend(n.next_events)
        return None

sz = (800, 600)

def swap(index, objects):
    i=(index+1)%len(objects)
    objects[i-1], objects[i] = objects[i], objects[i-1]
    objects[i-1].x, objects[i].x = objects[i].x, objects[i-1].x

#TODO: проверить на какой глубине отсекать дерево событий + достаточно ли 5 уровней

def main():
    random.seed(0)
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    index = 0 #индекс объекта

    # obj=Obj(0, 200, 200, 30)
    objs=[]

    for i in range(6):
        objs.append( Obj(i, 200+35*i, 200, 30) )

    objs2=[Obj(o.id, o.x, o.y + 50, o.sz) for o in objs]
    random.shuffle(objs2)

    graph = Graph(objs)

    for o1,o2 in zip(objs, objs2):
        o2.x = o1.x

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_i:
                    swap(index, objs)
                    for o in objs: o.selected=False
                    index=(index+1)%len(objs)
                    objs[index].selected=True
                    objs[(index+1)%len(objs)].selected=True
                if ev.key == pygame.K_p:
                    s=graph.to_string()
                    # print(s)
                    with open("graph.txt", "w") as f:
                        f.write(s)
                if ev.key == pygame.K_f:
                    # path=graph.find_plan("4; 5; 3; 1; 2; 0")
                    #path=graph.find_plan("5; 1; 2; 3; 4; 0")
                    path=graph.find_plan("0; 2; 1; 3; 4; 5")
                    for n in path:
                        print(n.i_swap)
                        print(n.to_string())

        dt=1/fps

        screen.fill((255, 255, 255))

        for obj in objs:
            obj.draw(screen)
        for obj in objs2:
            obj.draw(screen)

        draw_text(screen, f"Index = {index}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024