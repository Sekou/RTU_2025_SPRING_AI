import math
import numpy as np
import matplotlib.pyplot as plt

xx=np.arange(0, 20, 0.1)

np.random.seed(0)
yy=[math.sin(x)+np.random.normal(0,0.1) for x in xx]

y=[]
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


