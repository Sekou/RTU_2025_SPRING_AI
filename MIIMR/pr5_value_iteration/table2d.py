#2024, S. Diane, table class for pygame

import pygame

class Cell: #ячейка
    def __init__(self, id):
        self.id=id
        self.text = ""
        self.value = 0
        self.reward = 0
        self.selected = False

class Table: #таблица
    def __init__(self, x0, y0, width, height, nx, ny):
        self.x0,self.y0 =  x0, y0
        self.width,self.height = width, height
        self.nx,self.ny = nx, ny
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 20)
        numCells=nx*ny
        self.cells=[Cell(i) for i in range(numCells)]
    def convert_ix_iy(self, ind):
        return ind%self.nx, ind//self.nx
    def get_cell_neighbours(self, ix0, iy0):
        for ix in range(ix0-1, ix0+2):
            for iy in range(iy0-1, iy0+2):
                if 0<=ix<self.nx and 0<=iy<self.ny:
                    yield self.get_cell(ix, iy)
    def get_ix_iy(self, mouseX, mouseY):
        w, h = self.width / self.nx, self.height / self.ny
        iy = (mouseY - self.y0) / h
        ix = (mouseX - self.x0) / w
        return int(ix), int(iy)
    def get_cell(self, ix, iy): #объект ячейки
        return self.cells[iy*self.nx+ix]
    def get_cell_bb(self, ix, iy): #рамка ячейки
        y = round(self.y0 + iy * self.height / self.ny)
        y_ = round(self.y0 + (iy + 1) * self.height / self.ny)
        x = round(self.x0 + ix * self.width / self.nx)
        x_ = round(self.x0 + (ix + 1) * self.width / self.nx)
        return [x, y, x_ - x, y_ - y]
    def get_cell_center(self, ix, iy): #центр ячейки
        bb = self.get_cell_bb(ix, iy)
        return [bb[0]+0.5*bb[2], bb[1]+0.5*bb[3]]
    def draw_text(self, screen, txt, bb, dx, dy, color=(0,0,0)):
        img = self.font.render(txt, True, color)
        r = img.get_rect()
        r[0] += bb[0] + dx
        r[1] += bb[1] + dy
        screen.blit(img, r)
    def draw(self, screen):
        for iy in range(self.ny):
            for ix in range(self.nx):
                #контур ячейки
                bb = self.get_cell_bb(ix, iy)
                c=self.cells[iy*self.nx+ix]
                color=(255, 0, 0) if c.selected else (50, 0, 0)
                w=3 if c.selected else 1
                pygame.draw.rect(screen, color, bb, w)
                # текст ячейки
                if c.text:
                    self.draw_text(screen, c.text, bb, 1, 1, color=(0, 0, 255))
                self.draw_text(screen, f"{c.value:.1f}", bb, 5, 12)
                self.draw_text(screen, f"{c.reward:.1f}", bb, 5, 25)
