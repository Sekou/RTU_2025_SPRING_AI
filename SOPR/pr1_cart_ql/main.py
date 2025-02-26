#S. Diane, 2025
import pygame, sys, math, numpy as np
from itertools import product, repeat

WIN_SIZE=(800, 600)
SURFACE_Y= WIN_SIZE[1] * 2 / 3
MAX_ANG = 1 #предельный угол отклонения маятника
DISCOUNT = 0.99 #коэффициент дисконтирования
HORIZON = 125 #горизонт учета награды
# HORIZON = 25

pygame.font.init()
def draw_text(screen, x, y, text, sz=25): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    screen.blit(font.render(text,  False, (0, 0, 0)), (x, y))

def draw_plot(screen, vals, vmin, vmax, scale, color=(0,0,255)): #отрисовка графика
    for i in range(1, len(vals)):
        v1, v2, k=vals[i-1], vals[i], -scale/(vmax-vmin)
        pygame.draw.line(screen, color, (i - 1, WIN_SIZE[1] + k * v1), (i, WIN_SIZE[1] + k * v2))

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
        # self.dalpha_d2t=0.9*self.alpha + 0.01*self.a
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
    def estimate_state_action_reward(self):
        xDiscr=discretize(self.x, [[0,350],[350,450],[450,800]], [0, 1, 2])
        vDiscr=discretize(self.v, [[-500,-10],[-10,10],[10,500]], [0, 1, 2])
        alphaDiscr=discretize(self.alpha, [[-MAX_ANG,-0.03],[-0.03,0.03],[0.03,MAX_ANG]], [0, 1, 2])
        dalphaDiscr=discretize(self.dalpha_dt, [[-10*MAX_ANG,-0.1],[-0.1,0.1],[0.1,MAX_ANG*10]], [0, 1, 2])
        state = int(np.dot([1000,100,10,1],[xDiscr, vDiscr, alphaDiscr, dalphaDiscr]))
        action = discretize(self.control, [[-5,-0.1],[-0.1,0.1],[0.1,5]], [0, 1, 2])
        reward = 2 / (5*abs(self.alpha)+1) + 1 / (0.005*abs(400-self.x)+1)
        return state, action, reward

class History:
    def __init__(self):
        self.records=[]
    def add_record(self, s, a, r):
        self.records.append([len(self.records), s, a, r])
    def add_empty_record(self):
        self.records.append(None)
    def save(self, filename):
        with open(filename, "w") as f:
            f.write(str(self.records))
    def read(self, filename):
        with open(filename, "r") as f:
            self.records=eval(f.read())
    def clear(self):
        self.records.clear()
    def query(self, s, a): #подвыборка записей с указанными состоянием и действием
        rr=[r for r in self.records if r and r[1]==s and r[2]==a]
        return rr
    def calc_q(self, s, a): #расчет интегральной оценки пары состояние-действие
        rr=self.query(s, a)
        info = f"{len(rr)} matches"
        if len(rr)==0: return 0, info
        breaks=0 #число неполных оценок ввиду обрыва эпизода обучения
        qq=[]
        for (i0, s, a, r) in rr:
            q, norm=0,0
            i1=min(i0+HORIZON, len(self.records))
            for i in range(i0, i1):
                if not self.records[i]:
                    breaks+=1
                    break
                discount=math.pow(DISCOUNT, i - i0)
                q += discount * self.records[i][-1]
                norm+=discount
            qq.append(q/norm)
        info+=f", {breaks} breaks"
        return float(np.mean(qq)), info

class QTable:
    def __init__(self):
        self.policy=dict()
    def create_policy(self, history, statesVariants, actionsVariants):
        for sv in statesVariants:
            for av in actionsVariants:
                q, _= history.calc_q(sv, av)
                self.policy[f"{sv}+{av}"]=round(q, 2)
    def query(self, s):
        res=[[key,self.policy[key]] for key in self.policy.keys() if key.startswith(str(s)+"+")]
        return res
    def select_action(self, s):
        variants=self.query(s)
        if len(variants)==0: return 1 #выбор среднего (нулевого) действия
        aa=[v[0] for v in variants]
        aa=[a[a.index("+")+1:] for a in aa]
        qq=[v[1] for v in variants]
        i = np.argmax(qq)
        return int(aa[i])

qq=[] #график интегральных оценок действий
rr=[] #график мгновенных наград
def reset():
    cart.x = np.random.normal(400,50)
    cart.alpha = np.random.normal(0,0.1)
    cart.dalpha_dt = cart.dalpha_d2t = 0
    cart.v = cart.a = cart.control = 0
    qq.clear()
    rr.clear()

if __name__ == "__main__":
    fps=30; dt=1/fps
    screen=pygame.display.set_mode(WIN_SIZE)
    timer=pygame.time.Clock()
    mode= "manual" #режим программы

    cart=Cart() #робот-балансир
    last_x, sel_action = cart.x, None
    history = History() #таблица исторических данных
    qtable = QTable() #таблица интегральных оценок

    while True:
        state, action, reward= cart.estimate_state_action_reward()

        estimated_q, info=0, "" #ожидаемая оценка - отличается от текущей награды
        if len(history.records):
            estimated_q, info= history.calc_q(state, action)

        if mode== "manual":# режим ручного управления
            if cart.x!=last_x:
                history.add_record(state, action, round(reward, 2))
                last_x=cart.x
        elif mode== "auto":# режим экспертного управления
            cart.control_expert()
        elif mode== "learn": # режим обучения
            history.add_record(state, action, round(reward, 2))
            if sel_action==None or np.random.random()<0.1:
                sel_action=np.random.randint(3)
                print(f"Trying: {state:<04} -> {sel_action}")
            cart.control = [-1,0,1][sel_action]
        elif mode== "qtable": # режим обученного управления
            sel_action= qtable.select_action(state)
            print(f"Using: {state:<04} -> {sel_action}")
            cart.control = [-1,0,1][sel_action]

        need_draw=True

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                manual_control={pygame.K_a: -1,pygame.K_d: 1,pygame.K_z: 0}
                if event.key in manual_control: cart.control=manual_control[event.key]
                elif event.key == pygame.K_m: mode= "auto" if mode == "manual" else "manual"
                elif event.key == pygame.K_1: #тест запроса к исторической таблице по паре состояние-действие
                    historySubset=history.query(11, 2)
                    print(historySubset)
                elif event.key == pygame.K_2: #тест расчета интегральной оценки эффективности пары состояние-действие
                    Q, _ = history.calc_q(11, 2)
                    print(Q)
                elif event.key == pygame.K_3: #расчет оценок по всем комбинациям состояние-действие
                    s0 = set((0, 1, 2))
                    s1 = product(s0, repeat=4)
                    state_variants=[np.dot(v, [1000,100,10,1]) for v in s1]
                    qtable.create_policy(history, state_variants, [0, 1, 2])
                    print(qtable.policy)
                elif event.key == pygame.K_4: #подвыборка действий, доступных для указанного состояния
                    actionsSubset=qtable.query(state)
                    print(actionsSubset)
                elif event.key == pygame.K_5: mode= "learn" #переключение в режим автоматического Q-обучения
                elif event.key == pygame.K_6: mode= "qtable" #переключение в режим автоматического движения по выученной таблице оценок
                elif event.key == pygame.K_r: #сбрасываем робота в удобное положение по центру экрана
                    reset()
                    history.add_empty_record()
                    need_draw=False
                elif event.key == pygame.K_i: #вывод информации
                   print("Кнопка 5 - авто-обучение тележки (накопление исторических записей)")
                   print("Кнопка 3 - расчет таблицы политики Q(s, a)")
                   print("Кнопка 6 - режим движения по таблице-политики")
                elif event.key == pygame.K_s: history.save("history.txt") #сохранение истории движений робота в файл
                elif event.key == pygame.K_l: history.read("history.txt") #загрузка истории движений робота из файла
                elif event.key == pygame.K_j: history.read("history5000.txt") #загрузка истории движений робота из файла
                elif event.key == pygame.K_c: history.clear() #очистка истории


        cart.simulate(dt)

        if cart.x<=0 or cart.x>=800 or abs(cart.alpha)*1.01>MAX_ANG:
            reset()
            if mode in ["manual", "learn"]:
                history.add_empty_record()
            need_draw=False

        if need_draw:
            screen.fill((255,255,255))

            #отрисовка тележки с маятником
            cart.draw(screen)

            # вывод текстовой информации
            #1 горизонт прогноза
            draw_text(screen, 5, 5, f"horizon = {HORIZON}")
            #2 фактор дисконтирования
            draw_text(screen, 5, 25, f"discount = {DISCOUNT:.3f}")
            #3 координата и скорость тележки
            draw_text(screen, 5, 45, f"x={cart.x:.1f}, dx_dt={cart.v:.1f}")
            #4 угол и угловая скорость балки
            draw_text(screen, 5, 65, f"alpha={cart.alpha:.2f}, dalpha_dt={cart.dalpha_dt:.2f}")
            #5 дискретизированное действие
            draw_text(screen, 5, 85, f"action*={action}")
            #6 сиюминутное подкрепление
            draw_text(screen, 5, 105, f"reward={reward:.2f}")
            #7 число записей в исторической таблице
            draw_text(screen, 5, 125, f"num_records={len(history.records)}")
            #8 обобщенное состояние, составленное из координаты тележки x и угла балки alpha
            draw_text(screen, 5, 145, f"state = (x, x', a, a') = {state:<04}")
            #9 оценка целесообразности для выполняемого вручную или автоматически действия
            draw_text(screen, 5, 165, f"estQ={estimated_q:.2f}")
            #10 информация об оценке
            draw_text(screen, 5, 185, f"Q info = {info if info else 'None'}")
            #11 информация о режиме работы
            draw_text(screen, 5, 205, f"mode = {mode}")

            #отрисовка графиков
            qq.append(estimated_q)
            rr.append(reward)
            draw_plot(screen, qq, 0, 3, 600-SURFACE_Y, (0,0,255))
            draw_plot(screen, rr, 0, 3, 600-SURFACE_Y, (200,180,0))
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
#скважность расчета, оценка полезности записей,
# добавление только полезных (когда мало воспоминаний) или удаление лишних


