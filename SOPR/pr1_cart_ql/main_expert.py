#S. Diane, 2025
import pygame, sys, math, numpy as np

WIN_SIZE=(800, 600)
SURFACE_Y= WIN_SIZE[1] * 2 / 3
MAX_ANG = 1 #предельный угол отклонения маятника

pygame.font.init()
def draw_text(screen, x, y, text, sz=20): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    screen.blit(font.render(text,  False, (0, 0, 0)), (x, y))

def draw_plot(screen, vals, vmin, vmax, scale, color=(0,0,255)): #отрисовка графика
    y0 = WIN_SIZE[1] - scale/2
    for i in range(1, len(vals)):
        v1, v2, k=vals[i-1], vals[i], -scale/(vmax-vmin)
        pygame.draw.line(screen, color, (i - 1, y0 + k * v1), (i, y0 + k * v2))
    pygame.draw.line(screen, (100,100,100), (0, y0), (WIN_SIZE[0], y0 ))

def discretize(val, ranges, vals): #дискретизация параметра системы
    for i, r in enumerate(ranges):
        if r[0]<=val<r[1]: return vals[i]
    return -1

class Cart:
    def __init__(self):
        self.x, self.y, self.v, self.a= WIN_SIZE[0] / 2, SURFACE_Y - 25, 0, 0 #положение, скорость, ускорение
        self.control=0
        self.alpha=0.01 #угол балки
        self.dalpha_dt=0 #скорость падения
        self.dalpha_d2t=0 #ускорение падения
        self.bar_len=70 #длина балки
    def draw(self, screen):
        pygame.draw.line(screen, (0,0,0), (0,SURFACE_Y), (WIN_SIZE[0], SURFACE_Y), 1)
        w,h=60,35
        x1,x2=self.x-w/2, self.x+w/2
        y1,y2=self.y-h/2, self.y+h/2
        pygame.draw.rect(screen, (0,0,0), [x1, y1, x2-x1, y2-y1], 1)
        wheel_x1, wheel_x2 = self.x - w / 3, self.x + w / 3
        wheel_y1 = wheel_y2 = self.y + h / 2
        pygame.draw.circle(screen, (0,0,0), [wheel_x1, wheel_y1], 10, 1)
        pygame.draw.circle(screen, (0,0,0), [wheel_x2, wheel_y2], 10, 1)
        bar_x, bar_y = self.x, self.y - h / 2
        s,c=math.sin(self.alpha+math.pi/2), math.cos(self.alpha+math.pi/2)
        bar_x2, bar_y2 = bar_x + self.bar_len * c, bar_y - self.bar_len * s
        pygame.draw.line(screen, (0,0,0), (bar_x, bar_y), (bar_x2, bar_y2), 1)
    def simulate(self, dt):
        self.a=90*self.control
        self.v+=self.a * dt
        self.x += self.v * dt
        self.dalpha_d2t=0.9*math.sin(self.alpha) + 0.01*self.a*math.cos(self.alpha)
        self.dalpha_dt+=self.dalpha_d2t * dt
        self.alpha += self.dalpha_dt * dt
        self.alpha = min(MAX_ANG, max(-MAX_ANG, self.alpha))
    def control_expert(self):
        dxCart= WIN_SIZE[0] / 2 - self.x
        if self.alpha<-0.01:
            self.control=1
            if dxCart>0 and abs(self.alpha)>0.3:  self.control+= 0.1*dxCart
        elif self.alpha>0.01:
            self.control=-1
            if dxCart<0 and abs(self.alpha)>0.3:  self.control+= 0.1*dxCart
        else:
            self.control=0
    def control_expert2(self, k=0.1):
        self.control=-k*self.alpha

aa=[] #график угла маятника
def reset():
    cart.x = np.random.normal(400,50)
    cart.alpha = np.random.normal(0,0.1)
    cart.dalpha_dt = cart.dalpha_d2t = 0
    cart.v = cart.a = cart.control = 0
    aa.clear()

if __name__ == "__main__":
    fps=30; dt=1/fps
    screen=pygame.display.set_mode(WIN_SIZE)
    timer=pygame.time.Clock()
    mode= "manual" #режим программы

    cart=Cart() #робот-балансир
    last_x = cart.x

    while True:
        if mode== "auto":# режим экспертного управления
            cart.control_expert()
        need_draw=True

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                manual_control={pygame.K_a: -1,pygame.K_d: 1,pygame.K_z: 0}
                if event.key in manual_control: cart.control=manual_control[event.key]
                elif event.key == pygame.K_m: mode= "auto" if mode == "manual" else "manual"
                elif event.key == pygame.K_r: #сбрасываем робота в удобное положение по центру экрана
                    reset()
                    need_draw=False

        cart.simulate(dt)

        if cart.x<=0 or cart.x>=800 or abs(cart.alpha)*1.01>MAX_ANG:
            reset()
            need_draw=False

        if need_draw:
            screen.fill((255,255,255))

            #отрисовка тележки с маятником
            cart.draw(screen)

            # вывод текстовой информации
            #1 координата и скорость тележки
            draw_text(screen, 5, 5, f"x={cart.x:.1f}, dx_dt={cart.v:.1f}")
            #2 угол и угловая скорость балки
            draw_text(screen, 5, 25, f"alpha={cart.alpha:.2f}, dalpha_dt={cart.dalpha_dt:.2f}")
            #3 информация о режиме работы
            draw_text(screen, 5, 45, f"mode = {mode}")

            #отрисовка графиков
            aa.append(cart.alpha)
            draw_plot(screen, aa, 0, 3, 600-SURFACE_Y, (255,0,0))
            pygame.display.flip()

        timer.tick(fps)

        # k = abs(self.alpha)
        # if self.alpha < -0.01:
        #     self.control = 100 + 0.1 * dxCart * k
        # elif self.alpha > 0.01:
        #     self.control = -100 + 0.1 * dxCart * k
