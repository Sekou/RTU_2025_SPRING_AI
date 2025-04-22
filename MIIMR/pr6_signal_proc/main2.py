import math
import numpy as np
import matplotlib.pyplot as plt

xx=np.arange(0, 20, 0.1)

np.random.seed(0)
yy=[math.sin(x)+np.random.normal(0,0.1) for x in xx]

#метод экспоненциального среднего
def get_exponential_average(yy, i, win_size):
    i0=max(0, i-win_size)
    subset=yy[i0:i+1]
    gamma=0.7
    s, cnt=0,0
    for j in range(win_size):
        j_=i-j
        if j_>=0:
            s+=yy[j_]*math.pow(gamma, j)
            cnt+=math.pow(gamma, j)
    return s/cnt

yy1=[get_exponential_average(yy, i, 5) for i in range(len(yy))]

plt.plot(xx, yy)
plt.plot(xx, yy1)
plt.show()

