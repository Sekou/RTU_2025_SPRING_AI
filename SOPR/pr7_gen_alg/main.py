from itertools import count

import numpy as np

def replace_char(s, i, ch_new):
    if i>=len(s): return str(s)
    s2=ch_new+s[1:] if i==0 else s[:i]+ch_new+s[i+1:]
    assert len(s2)==len(s), f"str len mismatch {len(s2)}!={len(s)}, repl at {i}"
    return s2

def some_tests():
    s1="00000001"
    s2="00011001"
    print(s1.count("1"))
    print(s2.count("1"))
    test="a"*8
    print(test)
    print(replace_char(test, 7, "b"))
some_tests()


class Creature:
    def __init__(self, str_len):
        self.str_len=str_len
        self.s="0"*str_len
        self.fitness=0
    def mutate(self):
        ind=np.random.randint(self.str_len)
        ch_new=str(1-int(self.s[ind]))
        self.s=replace_char(self.s, ind, ch_new)
    def crossover(self, other, i):
        cr1=Creature(self.str_len)
        cr2=Creature(self.str_len)
        cr1.s = self.s[:i]+other.s[i:]
        cr2.s = other.s[:i]+self.s[i:]
        assert len(cr1.s)==self.str_len
        assert len(cr2.s)==self.str_len
        return cr1, cr2

class GA:
    def __init__(self, num_creatures, str_len):
        self.population=[]
        self.num_creatures=num_creatures
        for i in range(num_creatures):
            cr=Creature(str_len)
            cr.mutate()
            self.population.append(cr)
        self.calc_fitness()
    def print_all(self):
        for cr in self.population:
            print(f"{cr.s} = {cr.fitness:.2f}")
    def calc_fitness(self):
        for cr in self.population:
            # ЭТОТ ФУНКЦИОНАЛ МОЖНО ИЗМЕНИТЬ ДЛЯ РЕШЕНИЯ ДРУГОЙ ЗАДАЧИ
            cr.fitness=cr.s.count("1")
    def mutate_all(self):
        for cr in self.population:
            cr.mutate()
    def filter_best(self):
        self.population=sorted(self.population, key=lambda cr: cr.fitness, reverse=True)
        self.population=self.population[:len(self.population)//2]
    def repopulate(self):
        while len(self.population)<self.num_creatures:
            i1=np.random.randint(len(self.population)-1)
            i2=np.random.randint(i1, len(self.population))
            a, b=self.population[i1], self.population[i2]

            ic=np.random.randint(a.str_len) #индекс кроссовера
            c, d = a.crossover(b, ic)
            self.population.append(c)
            if len(self.population)<self.num_creatures:
                self.population.append(d)
    def get_solution(self):
        return sorted(self.population, key=lambda cr: cr.fitness, reverse=True)[0]

print("")
ga=GA(10,8)

ii=[]
ff=[]
for i in range(1000):
    print(f"ALL CREATURES ({i}):")
    ga.print_all()
    ga.filter_best()
    print("FILTERED:")
    ga.print_all()
    ga.repopulate()
    ga.mutate_all()
    ga.calc_fitness()
    solution = ga.get_solution()
    ii.append(i)
    ff.append(solution.fitness)
    if solution.fitness==8:
        print(f"Found solution on {i}-th iteration")
        print(f"SOLUTION: {solution.s}, fitness={solution.fitness}")
        break

import matplotlib.pyplot as plt

plt.title("Fitness")
plt.plot(ii, ff)
plt.show()


