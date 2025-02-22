import pygame, sys, math, numpy as np
winSize=(800,600)
SURFACE_Y=winSize[1]*2/3

pygame.font.init()
def drawText(screen, x, y, text, sz=25):
    font = pygame.font.SysFont('Comic Sans MS', sz)
    screen.blit(font.render(text,  False, (0, 0, 0)), (x, y))

#[[0,350],[350,450],[450,800]], [0, 1, 2]
def discretize(val, ranges, vals):
    for i, r in enumerate(ranges):
        if r[0]<=val<r[1]:
            return vals[i]

def draw_plot(screen, vals, vmin, vmax):
    for i in range(1, len(vals)):
        v1, v2=vals[i-1], vals[i]
        DY=SURFACE_Y-600
        k=DY/(vmax-vmin)
        pygame.draw.line(screen, (0,0,255), (i-1, 600+k*v1), (i, 600+k*v2))


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
        y=SURFACE_Y
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

class QTable:
    def __init__(self):
        self.policy=dict()
    def createPolicy(self, history, statesVariants, actionsVariants):
        for sv in statesVariants:
            for av in actionsVariants:
                q=history.calcQ(sv, av)
                self.policy[f"{sv}+{av}"]=q

    def query(self, s):
        res=[[key,self.policy[key]] for key in self.policy.keys() if key.startswith(str(s)+"+")]
        return res

    def selectAction(self, s):
        variants=self.query(s)
        if len(variants)==0: return 1 #TODO: fix magic number
        aa=[v[0] for v in variants]
        aa=[a[a.index("+")+1:] for a in aa]
        qq=[v[1] for v in variants]
        i = np.argmax(qq)
        return int(aa[i])

class History:
    def __init__(self):
        self.records=[]
    def addRecord(self, s, a, r):
        self.records.append([len(self.records), s, a, r])
    def query(self, s, a):
        rr=[r for r in self.records if r[1]==s and r[2]==a]
        return rr
    def calcQ(self, s, a, horizon=20):
        rr=self.query(s, a)
        if len(rr)==0: return 0.5
        qq=[]
        for r in rr:
            q=0
            i0=r[0]
            discount0=0.7
            i1=min(i0+horizon, len(self.records))
            for i in range(i0, i1):
                discount=math.pow(discount0, i-i0)
                q += discount * self.records[i][-1]
            qq.append(q)
        return np.mean(qq)
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(str(self.records))
    def read(self, filename):
        with open(filename, "r") as f:
            self.records=eval(f.read())


if __name__ == "__main__":
    cart=Cart()
    fps=30
    dt=1/fps
    screen=pygame.display.set_mode(winSize)
    timer=pygame.time.Clock()

    history = History() #таблица исторических данных
    qtable = QTable() #таблица политики

    MODE="manual" #or "auto"

    qq=[]

    while True:

        xDiscr=discretize(cart.x, [[0,350],[350,450],[450,800]], [0, 1, 2])
        alphaDiscr=discretize(cart.alpha, [[-math.pi/2,-0.03],[-0.03,0.03],[0.03,math.pi/2]], [0, 1, 2])
        state = 10 * xDiscr + alphaDiscr
        action=discretize(cart.v, [[-300,-20],[-20,20],[20,300]], [0, 1, 2])
        reward = 1 / (5*abs(cart.alpha)+1) + 1 / (abs(400-cart.x)+1)

        estimated_q=0
        if len(history.records):
            estimated_q=history.calcQ(state, action)

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
                if event.key == pygame.K_1: #тест запроса к исторической таблице по паре состояние-действие
                    historySubset=history.query(11, 2)
                    print(historySubset)
                if event.key == pygame.K_2: #тест расчета интегральной оценки эффективности пары состояние-действие
                    Q=history.calcQ(11, 2)
                    print(Q)
                if event.key == pygame.K_3: #расчет оценок по всем комбинациям состояние-действие
                    #TODO: автоматизировать формирование комбинаций
                    qtable.createPolicy(history, [0, 1, 2, 10, 11, 12, 20,21,22], [0, 1, 2])
                    print(qtable.policy)
                if event.key == pygame.K_4: #подвыборка действий, доступных для указанного состояния
                    actionsSubset=qtable.query(state)
                    print(actionsSubset)
                if event.key == pygame.K_5: #переключение в режим автоматического движения по выученной таблице оценок
                   MODE="qtable"
                if event.key == pygame.K_r: #сбрасываем робота в удобное положение по центру экрана
                   cart.x=400
                   cart.alpha=cart.dalpha_dt=cart.dalpha_d2t=0
                   cart.v=cart.a=cart.control=0
                   qq=[]
                if event.key == pygame.K_i: #вывод информации
                   print("Сперва отклоните тележку и дайте ей поездить в экспертном режиме через кнопку M")
                   print("Далее, когда накопится достаточно историческеих записей, запустите формирование таблицы-политики через кнопку 3")
                   print("Переместите робота в центр экрана кнопеой R, и немного отклоните")
                   print("Запустите режим движения по таблице-политики кнопкой 5")
                if event.key == pygame.K_s: #сохранение истории движений робота в файл
                    history.save("history.txt")
                if event.key == pygame.K_l: #загрузка истории движений робота из файла
                    history.read("history.txt")

        state=xDiscr*10+alphaDiscr

        if MODE=="manual":
            history.addRecord(state, action, reward)
        elif MODE=="auto":
            cart.controlExpert()
        elif MODE=="qtable":
            a=qtable.selectAction(state)
            print(state, "->", a)
            if a==0:
                cart.control = -100
            if a==1:
                cart.control = 0
            if a==2:
                cart.control = 100

        cart.sim(dt)
        screen.fill((255,255,255))
        #1 координата тележки
        drawText(screen, 5, 5, f"x={cart.x:.1f}")
        #2 дискретное состояние по координате тележки
        drawText(screen, 5, 25, f"x*={xDiscr}")
        #3 угол балки (маятника)
        drawText(screen, 5, 45, f"alpha={cart.alpha:.2f}")
        #4 дискртеное состояние угла балки
        drawText(screen, 5, 65, f"alpha*={alphaDiscr}")
        #5 дискретизированное действие
        drawText(screen, 5, 85, f"action*={action}")
        #6 сиюминутное подкрепление
        drawText(screen, 5, 105, f"reward={reward:.2f}")
        #7 число записей в исторической таблице
        drawText(screen, 5, 125, f"numRecords={len(history.records)}")
        #8 обобщенное состояние, составленное из координаты тележки x и угла балки alpha
        drawText(screen, 5, 145, f"state={state}")
        #9 оценка достоверности для выполняемого вручную или автоматически действия
        drawText(screen, 5, 165, f"estQ={estimated_q:.2f}")

        qq.append(estimated_q)
        draw_plot(screen, qq, 0, 3)

        cart.draw(screen)
        pygame.display.flip()
        timer.tick(fps)

        #
        # k = abs(self.alpha)
        # if self.alpha < -0.01:
        #     self.control = 100 + 0.1 * dxCart * k
        # elif self.alpha > 0.01:
        #     self.control = -100 + 0.1 * dxCart * k

#fix reward //account for dalpha_dt
#fix horizon
#increase samples count in history
#filter samples count in history
#a = v?