from itertools import count

import numpy as np

def replace_char(s, i, ch_new):
    return s[:i]+ch_new+s[i:]

def basics():
    s1="00000001"
    s2="00011001"
    print(s1.count("1"))
    print(s2.count("1"))
    test="a"*7
    print(test)
    print(replace_char(test, 7, "b"))
basics()


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
        return cr1, cr2

class GA:
    def __init__(self, num_creatures, str_len):
        self.population=[]
        self.num_creatures=num_creatures
        for i in range(num_creatures):
            cr=Creature(str_len)
            cr.mutate()
            self.population.append(cr)
    def print_all(self):
        for cr in self.population:
            print(f"{cr.s} = {cr.fitness:.2f}")
    def calc_fitness(self):
        for cr in self.population:
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

print("")
ga=GA(10,8)
for i in range(5):
    ga.calc_fitness()
    ga.print_all()
    ga.mutate_all()

ga.filter_best()
print("FILTERED:")
ga.print_all()
