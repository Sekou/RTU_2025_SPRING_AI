import math

import numpy as np

arr1=["g", "o", "g", "g", "o", "o", "r", "g", "r", "g"] #3 разных цвета
arr2=["g", "g", "g", "g", "g", "g", "g", "g", "g", "g"] #1 цвет
arr3=["g", "r", "v", "o"] #4 разных цвета

#расчет энтропии по формуле Шеннона
def calc_entropy(arr):
    pp=[arr.count(el)/len(arr) for el in set(arr)]
    return -np.sum([p*math.log2(p) for p in pp])

H=calc_entropy(arr1)
H2=calc_entropy(arr2)
H3=calc_entropy(arr3)

print(H, H2, H3)

#https://habr.com/ru/articles/801515/
#разбиение по минимизации энтропии Шеннона
def split_array(arr):
    i_best, (H_best, H0) = -1, [calc_entropy(arr)] * 2
    for i in range(1, len(arr)):
        arr1, arr2 = arr[:i], arr[i:]
        h1, h2 = calc_entropy(arr1), calc_entropy(arr2)
        h = (h1*len(arr1)+h2*len(arr2))/len(arr)
        if h < H_best: i_best, H_best = i, h
    if i_best>=0:
        return i_best, H_best, arr[:i_best], arr[i_best:]
    return -1, H0, arr, []

i, H, a1, a2 = split_array(arr1)
print(i, H, a1, a2)
i, H, a1, a2 = split_array(arr2)
print(i, H, a1, a2)
i, H, a1, a2 = split_array(arr3)
print(i, H, a1, a2)

arr1_=['g', 'o', 'g', 'g', 'o', 'o']
i, H, a1, a2 = split_array(arr1_)
print(i, H, a1, a2)


class Node:
    def __init__(self, parent, parent_split_ind, parent_split_H, arr):
        self.parent = parent
        self.parent_split_H=parent_split_H #суммарная энтропия родителдьского разбиения
        self.own_H=calc_entropy(arr) #собственная энтропия (по массиву arr)
        self.parent_split_ind=parent_split_ind
        self.arr=arr
        self.childs=None
        self.level=parent.level+1 if parent else 0

    def split_childs(self):
        i, H, a1, a2 = split_array(self.arr)
        if a2:
            self.childs=[Node(self, i, H, a1), Node(self, i, H, a2)]
            for ch in self.childs:
                ch.split_childs()
    def print_struct(self):
        indent = "-  "*self.level
        print(f"{indent} ({self.level} {self.parent_split_ind} {self.own_H:.2f} {self.arr}) ")
        if self.childs:
            for ch in self.childs:
                ch.print_struct()

#https://habr.com/ru/articles/171759/
class Graph:
    def __init__(self, arr):
        self.arr=arr
        self.root_node=Node(None, -1, 0, arr)

    def split_childs(self):
        self.root_node.split_childs()

    def print_struct(self):
        print("CLASSIFICATION TREE:")
        self.root_node.print_struct()


tree = Graph(arr1)
tree.split_childs()
tree.print_struct()
