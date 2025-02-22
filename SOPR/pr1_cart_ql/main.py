#S. Diane, 2025
import pygame, sys, math, numpy as np

winSize=(800,600)
SURFACE_Y=winSize[1]*2/3

MAX_ANG = 1

pygame.font.init()
def drawText(screen, x, y, text, sz=25):
    font = pygame.font.SysFont('Comic Sans MS', sz)
    screen.blit(font.render(text,  False, (0, 0, 0)), (x, y))

def discretize(val, ranges, vals):
    for i, r in enumerate(ranges):
        if r[0]<=val<r[1]: return vals[i]
    return -1

def draw_plot(screen, vals, vmin, vmax, scale, color=(0,0,255)):
    for i in range(1, len(vals)):
        v1, v2, k=vals[i-1], vals[i], -scale/(vmax-vmin)
        pygame.draw.line(screen, color, (i-1, winSize[1]+k*v1), (i, winSize[1]+k*v2))

class Cart:
    def __init__(self):
        self.x, self.y, self.v,self.a=winSize[0]/2, SURFACE_Y-25, 0, 0 #положение, скорость, ускорение
        self.control=0
        self.alpha=0.01 #угол балки
        self.dalpha_dt=0 #скорость падения
        self.dalpha_d2t=0 #ускорение падения
        self.barL=70 #длина балки
    def draw(self, screen):
        pygame.draw.line(screen, (0,0,0),(0,SURFACE_Y), (winSize[0],SURFACE_Y), 1)
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
        self.a=90*self.control
        self.v+=self.a * dt
        self.x += self.v * dt
        self.dalpha_d2t=0.9*self.alpha + 0.01*self.a
        self.dalpha_dt+=self.dalpha_d2t * dt
        self.alpha += self.dalpha_dt * dt
        self.alpha = min(MAX_ANG, max(-MAX_ANG, self.alpha))

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
                q, _=history.calcQ(sv, av)
                self.policy[f"{sv}+{av}"]=round(q, 2)
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
    def addEmptyRecord(self):
        self.records.append(None)
    def query(self, s, a):
        rr=[r for r in self.records if r and r[1]==s and r[2]==a]
        return rr
    def calcQ(self, s, a, horizon=70):
        rr=self.query(s, a)
        info = f"{len(rr)} matches"
        if len(rr)==0: return 0, info
        breaks=0
        qq=[]
        for r in rr:
            q, norm=0,0
            i0=r[0]
            discount0=0.99
            i1=min(i0+horizon, len(self.records))
            for i in range(i0, i1):
                if not self.records[i]:
                    breaks+=1
                    break
                discount=math.pow(discount0, i-i0)
                q += discount * self.records[i][-1]
                norm+=discount
            qq.append(q/norm)
        info+=f", {breaks} breaks"
        return float(np.mean(qq)), info
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(str(self.records))
    def read(self, filename):
        with open(filename, "r") as f:
            self.records=eval(f.read())
    def clear(self):
        self.records.clear()


qq=[]
rr=[]

def reset():
    cart.x = np.random.normal(400,50)
    cart.alpha = np.random.normal(0,0.1)
    cart.dalpha_dt = cart.dalpha_d2t = 0
    cart.v = cart.a = cart.control = 0
    qq.clear()
    rr.clear()


if __name__ == "__main__":
    cart=Cart()
    last_x, sel_action = cart.x, None

    fps=30
    dt=1/fps
    screen=pygame.display.set_mode(winSize)
    timer=pygame.time.Clock()

    history = History() #таблица исторических данных
    qtable = QTable() #таблица политики

    MODE="manual" #or "auto"

    while True:
        xDiscr=discretize(cart.x, [[0,350],[350,450],[450,800]], [0, 1, 2])
        vDiscr=discretize(cart.v, [[-500,-10],[-10,10],[10,500]], [0, 1, 2])
        alphaDiscr=discretize(cart.alpha, [[-MAX_ANG,-0.03],[-0.03,0.03],[0.03,MAX_ANG]], [0, 1, 2])
        dalphaDiscr=discretize(cart.dalpha_dt, [[-10*MAX_ANG,-0.1],[-0.1,0.1],[0.1,MAX_ANG*10]], [0, 1, 2])
        state = int(np.dot([1000,100,10,1],[xDiscr, vDiscr, alphaDiscr, dalphaDiscr]))
        action = discretize(cart.control, [[-5,-0.1],[-0.1,0.1],[0.1,5]], [0, 1, 2])
        reward = 2 / (5*abs(cart.alpha)+1) + 1 / (abs(400-cart.x)+1)

        estimated_q=0
        info=""
        if len(history.records):
            estimated_q, info=history.calcQ(state, action)

        DRAW=True

        if MODE=="manual":
            if cart.x!=last_x:
                history.addRecord(state, action, round(reward, 2))
                last_x=cart.x
        elif MODE=="auto":
            cart.controlExpert()
        elif MODE=="learn":
            history.addRecord(state, action, round(reward, 2))
            if sel_action==None or np.random.random()<0.1:
                sel_action=np.random.randint(3)
                print(f"Trying: {state:<04} -> {sel_action}")
            cart.control = [-1,0,1][sel_action]
        elif MODE=="qtable":
            sel_action=qtable.selectAction(state)
            print(f"Using: {state:<04} -> {sel_action}")
            cart.control = [-1,0,1][sel_action]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    cart.control=-1
                if event.key == pygame.K_d:
                    cart.control=1
                if event.key == pygame.K_z:
                    cart.control=0
                if event.key == pygame.K_m:
                    MODE="auto" if MODE=="manual" else "manual"
                if event.key == pygame.K_1: #тест запроса к исторической таблице по паре состояние-действие
                    historySubset=history.query(11, 2)
                    print(historySubset)
                if event.key == pygame.K_2: #тест расчета интегральной оценки эффективности пары состояние-действие
                    Q, _ =history.calcQ(11, 2)
                    print(Q)
                if event.key == pygame.K_3: #расчет оценок по всем комбинациям состояние-действие
                    #TODO: автоматизировать формирование комбинаций
                    from itertools import product, repeat
                    s0 = set((0, 1, 2))
                    s1 = product(s0, repeat=4)
                    state_variants=[np.dot(v, [1000,100,10,1]) for v in s1]
                    qtable.createPolicy(history, state_variants, [0, 1, 2])
                    print(qtable.policy)
                if event.key == pygame.K_4: #подвыборка действий, доступных для указанного состояния
                    actionsSubset=qtable.query(state)
                    print(actionsSubset)
                if event.key == pygame.K_5: #переключение в режим автоматического движения по выученной таблице оценок
                   MODE="qtable"
                if event.key == pygame.K_6: #переключение в режим автоматического обучения
                   MODE="learn"
                if event.key == pygame.K_r: #сбрасываем робота в удобное положение по центру экрана
                    reset()
                    history.addEmptyRecord()
                    DRAW=False
                if event.key == pygame.K_i: #вывод информации
                   print("Сперва отклоните тележку и дайте ей поездить в экспертном режиме через кнопку M")
                   print("Далее, когда накопится достаточно исторических записей, запустите формирование таблицы-политики через кнопку 3")
                   print("Переместите робота в центр экрана кнопеой R, и немного отклоните")
                   print("Запустите режим движения по таблице-политики кнопкой 5")
                if event.key == pygame.K_s: #сохранение истории движений робота в файл
                    history.save("history.txt")
                if event.key == pygame.K_l: #загрузка истории движений робота из файла
                    history.read("history.txt")
                if event.key == pygame.K_c: #очистка истории
                    history.clear()

        cart.sim(dt)

        if cart.x<=0 or cart.x>=800 or abs(cart.alpha)*1.01>MAX_ANG:
            reset()
            if MODE in ["manual", "learn"]:
                history.addEmptyRecord()
            DRAW=False

        if DRAW:
            screen.fill((255,255,255))
            #1 координата тележки
            drawText(screen, 5, 5, f"x={cart.x:.1f}")
            #2 скорость тележки
            drawText(screen, 5, 25, f"dx_dt={cart.v:.1f}")
            #3 угол балки (маятника)
            drawText(screen, 5, 45, f"alpha={cart.alpha:.2f}")
            #4 угловая скорость балки
            drawText(screen, 5, 65, f"dalpha_dt={cart.dalpha_dt:.2f}")
            #5 дискретизированное действие
            drawText(screen, 5, 85, f"action*={action}")
            #6 сиюминутное подкрепление
            drawText(screen, 5, 105, f"reward={reward:.2f}")
            #7 число записей в исторической таблице
            drawText(screen, 5, 125, f"numRecords={len(history.records)}")
            #8 обобщенное состояние, составленное из координаты тележки x и угла балки alpha
            drawText(screen, 5, 145, f"state (x, x',a, a') = {state:<04}")
            #9 оценка достоверности для выполняемого вручную или автоматически действия
            drawText(screen, 5, 165, f"estQ={estimated_q:.2f}")
            #10 информация об оценке
            drawText(screen, 5, 185, f"Q info = {info}")
            #11 информация о режиме работы
            drawText(screen, 5, 205, f"mode = {MODE}")
            qq.append(estimated_q)
            rr.append(reward)
            draw_plot(screen, qq, 0, 3, 600-SURFACE_Y, (0,0,255))
            draw_plot(screen, rr, 0, 3, 600-SURFACE_Y, (200,180,0))
            cart.draw(screen)
            pygame.display.flip()

        timer.tick(fps)

        # k = abs(self.alpha)
        # if self.alpha < -0.01:
        #     self.control = 100 + 0.1 * dxCart * k
        # elif self.alpha > 0.01:
        #     self.control = -100 + 0.1 * dxCart * k

#fix reward //account for alpha and x //dalpha_dt   !!!!!!!!
#fix horizon
#increase samples count in history
#+ filter samples count in history
#+ a = v? - better a=control   !!!!!!
#+ skip resets for calc Q
#+ random resets positions for variations in learning   !!!!!
#+ normailze Q
#+ не добавлять лишние записи при остановках   !!!!!!!!!!



