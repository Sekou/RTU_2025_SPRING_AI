
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

def place_rewards(grid):
    for c in grid.cells:
        if c.text=="G": c.reward, c.value=100, 0
        elif c.text=="O": c.reward, c.value=-100, 0
        else: c.reward, c.value= 0, 0

def value_iteration(grid):
    gamma=0.1
    nx, ny = grid.nx, grid.ny
    for i in range(0, ny):
        for j in range(0, nx):
            c=grid.get_cell(j, i)
            cc=list(grid.get_cell_neighbours(j, i))
            i_best=np.argmax([c_.value for c_ in cc])
            c_best=cc[i_best]
            if c.reward==0:
                c.value += gamma * (c_best.value - c.value)
            else:
                c.value=c.reward

            # p_cell = 1 / (1 + len(cc))  # вероятность перехода в клетку
            # c.value = p_cell * c.reward
            # for c_ in cc:
                # c.value+=p_cell*(c_.value*gamma+c_.reward)
                # c.value=max(c.value, c_.value*gamma+c_.reward)

def find_path(grid):
    path=[]
    r=[c for c in grid.cells if c.text=="R"][0]
    i_next=r.id
    last_val=-1
    while True:
        path.append(i_next)
        ix, iy = grid.convert_ix_iy(i_next)
        neighbours=list(grid.get_cell_neighbours(ix, iy))
        i_local = np.argmax([n.value for n in neighbours])
        i_next = neighbours[i_local].id
        if neighbours[i_local].value<=last_val:
            break
        last_val=neighbours[i_local].value
    return path

def draw_path(screen, grid, path):
    for i in range(1, len(path)):
        i1, i2=path[i-1], path[i]
        ix1, iy1=grid.convert_ix_iy(i1)
        ix2, iy2=grid.convert_ix_iy(i2)
        c1=grid.get_cell_center(ix1, iy1)
        c2=grid.get_cell_center(ix2, iy2)
        pygame.draw.line(screen, (255,0,0), c1, c2, 2)

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    grid = table2d.Table(200,200,400,300, 8, 6)
    grid.get_cell(0, 0).text= "R"
    grid.get_cell(2, 3).text= "O"
    grid.get_cell(3, 3).text= "O"
    grid.get_cell(4, 3).text= "O"
    grid.get_cell(4, 2).text= "O"
    grid.get_cell(7, 5).text= "G"

    place_rewards(grid)

    path=[]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    value_iteration(grid)
                if ev.key == pygame.K_2:
                    path=find_path(grid)
                    print(path)

        dt=1/fps

        screen.fill((255, 255, 255))

        grid.draw(screen)
        draw_path(screen, grid, path)

        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024