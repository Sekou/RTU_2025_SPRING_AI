import math

import numpy as np


arr1=["g", "o", "g", "g", "o", "o", "r", "g", "r", "g"] #3 разных цвета
arr2=["g", "g", "g", "g", "g", "g", "g", "g", "g", "g"] #1 цвет
arr3=["g", "r", "v", "o"] #4 разных цвета

#расчет энтропии по формуле Шеннона
def calcEntropy(arr):
    pp=[arr.count(el)/len(arr) for el in set(arr)]
    return -np.sum([p*math.log2(p) for p in pp])

H=calcEntropy(arr1)
H2=calcEntropy(arr2)
H3=calcEntropy(arr3)

print(H, H2, H3)

#https://habr.com/ru/articles/801515/
#разбиение по минимизации энтропии Шеннона
def splitArray(arr):
    i_best, (H_best, H0) = -1, [calcEntropy(arr)]*2
    for i in range(1, len(arr)):
        arr1, arr2 = arr[:i], arr[i:]
        h1, h2 = calcEntropy(arr1), calcEntropy(arr2)
        h = (h1*len(arr1)+h2*len(arr2))/len(arr)
        if h < H_best: i_best, H_best = i, h
    if i_best>=0:
        return i_best, H_best, arr[:i_best], arr[i_best:]
    return -1, H0, arr, []

i, H, a1, a2 = splitArray(arr1)
print(i, H, a1, a2)
i, H, a1, a2 = splitArray(arr2)
print(i, H, a1, a2)
i, H, a1, a2 = splitArray(arr3)
print(i, H, a1, a2)

arr1_=['g', 'o', 'g', 'g', 'o', 'o']
i, H, a1, a2 = splitArray(arr1_)
print(i, H, a1, a2)