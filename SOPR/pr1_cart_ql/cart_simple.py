import pygame, sys, math, numpy as np
winSize=(800,600)
class Cart:
    def __init__(self):
        self.x,self.v,self.a=winSize[0]/2, 0,0 #положение, скорость, ускорение
        self.control=0
        self.y=0
        self.alpha=0.01 #угол балки
        self.dalpha_dt=0 #скорость падения
        self.dalpha_d2t=0 #ускорение падения
        self.barL=70 #длина балки
    def draw(self, screen):
        y=winSize[1]*2/3
        pygame.draw.line(screen, (0,0,0),(0,y), (winSize[0],y), 1)
        self.y=y-25
        w,h=60,35
        x1,x2=self.x-w/2, self.x+w/2
        y1,y2=self.y-h/2, self.y+h/2
        pygame.draw.rect(screen, (0,0,0), [x1, y1, x2-x1, y2-y1], 1)
        wheelX1, wheelX2 = self.x-w/3, self.x+w/3
        wheelY1 = wheelY2 = self.y+h/2
        pygame.draw.circle(screen, (0,0,0), [wheelX1, wheelY1],10, 1)
        pygame.draw.circle(screen, (0,0,0), [wheelX2, wheelY2],10, 1)
        barX, barY = self.x, self.y-h/2
        s,c=math.sin(self.alpha+math.pi/2), math.cos(self.alpha+math.pi/2)
        barX2, barY2 = barX+self.barL*c, barY-self.barL*s
        pygame.draw.line(screen, (0,0,0),(barX, barY), (barX2, barY2), 1)
    def sim(self, dt):

        self.a=0.9*self.control
        self.v+=self.a * dt
        self.x += self.v * dt

        self.dalpha_d2t=0.9*self.alpha + 0.01*self.a
        self.dalpha_dt+=self.dalpha_d2t * dt
        self.alpha += self.dalpha_dt * dt
        maxAng=1
        if self.alpha>maxAng: self.alpha=maxAng
        if self.alpha<-maxAng: self.alpha=-maxAng

    def controlExpert(self):
        dxCart=winSize[0]/2-self.x
        if self.alpha<-0.01:
            self.control=100
            if dxCart>0 and abs(self.alpha)>0.3:  self.control+= 0.1*dxCart
        elif self.alpha>0.01:
            self.control=-100
            if dxCart<0 and abs(self.alpha)>0.3:  self.control+= 0.1*dxCart
        else:
            self.control=0

if __name__ == "__main__":
    cart=Cart()
    fps=30
    dt=1/fps
    screen=pygame.display.set_mode(winSize)
    timer=pygame.time.Clock()

    MODE="manual" #or "auto"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    cart.control=-100
                if event.key == pygame.K_d:
                    cart.control=100
                if event.key == pygame.K_m:
                    MODE="auto" if MODE=="manual" else "manual"

        if MODE=="auto":
            cart.controlExpert()

        cart.sim(dt)
        screen.fill((255,255,255))
        cart.draw(screen)
        pygame.display.flip()
        timer.tick(fps)

        #
        # k = abs(self.alpha)
        # if self.alpha < -0.01:
        #     self.control = 100 + 0.1 * dxCart * k
        # elif self.alpha > 0.01:
        #     self.control = -100 + 0.1 * dxCart * k