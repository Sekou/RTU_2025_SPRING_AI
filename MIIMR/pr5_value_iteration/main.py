
import sys, pygame
import numpy as np
import math
import table2d

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

# def value_iteration(grid):


def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    grid = table2d.Table(200,200,400,300, 8, 6)
    grid.getCell(0,0).text="R"
    grid.getCell(2,3).text="O"
    grid.getCell(3,3).text="O"
    grid.getCell(4,3).text="O"
    grid.getCell(4,2).text="O"
    grid.getCell(7,5).text="G"

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        dt=1/fps

        screen.fill((255, 255, 255))

        grid.draw(screen)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024