#по материалам статьи
#https://cyberleninka.ru/article/n/odnomernyy-filtr-kalmana-v-algoritmah-chislennogo-resheniya-zadachi-optimalnogo-dinamicheskogo-izmereniya

import math
import numpy as np
import matplotlib.pyplot as plt

xx=np.arange(0, 20, 0.1)

np.random.seed(0)
yy=[math.sin(x)+np.random.normal(0,0.1) for x in xx]

yy_mes=[5, 5, 5, 5] #измерения сигнала
yy_est=[4, 5, 6, 7] #оценки сигнала
def dev_avg(i, N): #среднее отклонение сигнала по ретроспективному окну N
    i0, i1 = i-N+1, i+1
    yy_mes_, yy_est_=yy_mes[i0:i1], yy_est[i0:i1]
    return np.mean([a-b for (a, b) in zip(yy_mes_, yy_est_)])

d=dev_avg(3, 3)
print(d)

def dev_dev_avg(i, N):
    dd=[dev_avg(i-N+1+j, N) for j in range(N)]
    return np.sum(dd)/(len(dd)+1)

#метод экспоненциального среднего
def get_kalman_filter_value(yy, i, win_size):
    P=0.1 #if i==0 else
    K=P/(P+0.1)
    res=K*yy[i] + (1-K)*yy[ max(0, i-1) ]
    return res

yy1=[get_kalman_filter_value(yy, i, 5) for i in range(len(yy))]

plt.plot(xx, yy)
plt.plot(xx, yy1)
plt.show()


