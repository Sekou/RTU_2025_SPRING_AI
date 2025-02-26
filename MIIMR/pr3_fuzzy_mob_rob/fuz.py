import matplotlib.pyplot as plt
import numpy as np

class Term:
    def __init__(self, name, x0, w):
        self.name=name
        self.x0=x0
        self.w=w
        self.left=False
        self.right=False
    def F(self, x):
        if self.left and x<=self.x0: return 1
        if self.right and x>=self.x0: return 1
        if x<self.x0-self.w/2: return 0
        elif x<self.x0: return -(2*self.x0 / self.w - 1) + 2/self.w*x
        elif x<self.x0+self.w/2: return (2*self.x0 / self.w + 1) - 2/self.w*x
        else: return 0
    def calc(self, x):
        self.last_input=x
        self.activation=self.F(x)
        return self.activation
    def draw(self, plt, xmin, xmax):
        N = 100
        dx = (xmax - xmin) / N
        xx = [i * dx for i in range(N)]
        yy = [self.F(x) for x in xx]
        plt.plot(xx, yy)

class FuzzyVar:
    def __init__(self, xmin, xmax):

        self.terms = []
        self.xmin = xmin
        self.xmax = xmax

    def addTerm(self, name, x0, w):
        self.terms.append(Term(name, x0, w))

    def draw(self, plt):
        for t in self.terms:
            t.draw(plt, self.xmin, self.xmax)

    def calc(self, x):
        return [t.calc(x) for t in self.terms]

    def defuzzMamdani(self, x, rules, fvOut, split=100):
        # активация входных термов
        aa = [t.calc(x) for t in self.terms]
        # применение правил и определение выходных термов
        terms2 = [fvOut.terms[rules[i][1]] for i in range(len(rules))]
        # дефаззификация выходного нечеткого множества
        J, M = 0, 0
        step=(fvOut.xmax - fvOut.xmin)/split
        for x_ in np.arange(fvOut.xmin, fvOut.xmax, step):
            v = max([min(a, t.calc(x_)) for a, t in zip(aa, terms2)])
            J += v * x_
            M += v
        return J / M

if __name__ == "__main__":
    fvInp = FuzzyVar(0, 100)
    fvInp.addTerm("DSmall", 0, 100)
    fvInp.addTerm("DMid", 50, 100)
    fvInp.addTerm("DBig", 100, 100)
    fvInp.draw(plt)
    plt.show()
    fvOut = FuzzyVar(0, 80)
    fvOut.addTerm("VSmall", 0, 80)
    fvOut.addTerm("VMid", 40, 80)
    fvOut.addTerm("VBig", 80, 80)
    fvOut.draw(plt)
    plt.show()

    # цикл активации термов при линейном изменении входной координаты
    for x in range(100):
        aa = fvInp.calc(x)
    print(aa)

    # тестовая база правил, отображающая нечеткие значения сами в себя
    rules = [[0, 0], [1, 1], [2, 2]]  # при наблюдении нечеткого значения i выдать нечеткое значение j
    xx = np.arange(0, 100, 1)
    yy = [fvInp.defuzzMamdani(x, rules, fvOut) for x in xx]
    plt.plot(xx, yy)
    plt.show()

#S. Diane, 2025