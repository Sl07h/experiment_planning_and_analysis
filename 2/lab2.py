import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.linalg import det, inv


pd.set_option('precision', 2)
n = 25  # число точек сетки
m = 6   # число параметров a + b*x + c*y + d*x*y + e*x^2 + f*y^2 
k = 2   # число переменных 2: (x,y)

def f(theta, x):
    return  theta[0] + \
            theta[1]*x[0] + \
            theta[2]*x[1] + \
            theta[3]*x[0]*x[1] + \
            theta[4]*x[0]**2 + \
            theta[5]*x[1]**2

def f_vector(x):
    return np.array([
        [1],
        [x[0]],
        [x[1]],
        [x[0]*x[1]],
        [x[0]**2],
        [x[1]**2]
    ])

def f_vector_T(x):
    return np.array([
        1,
        x[0],
        x[1],
        x[0]*x[1],
        x[0]**2,
        x[1]**2
    ])


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Lab2():
    '''
    Класс для 2 лабораторной работы
    Для стандартизации все критерии ищут минимальное значение
    '''
    def __init__(self):
        ''' Выделение памяти под массивы '''
        self.x = np.ndarray((n, k))
        self.p = np.ndarray(n)
        self.new_x = np.ndarray((n, k))
        self.new_p = np.ndarray(n)
        self.M = np.ndarray((m, m))
        self.alpha = 1 / n
        self.gamma = 2
        self.max_iter_s = 30
        self.max_iter_alpha = 20

    def generate_initial_guess(self):
        ''' Задаём начальное приближение '''
        t = np.linspace(-1, 1, 5)
        i = 0
        for x1 in t:
            for x2 in t:
                self.x[i] = np.array([x1, x2])
                i+=1
        self.p = np.full(n, 1/n)

    def fi(self, x):
        ''' Значение функции fi в точке x '''
        return f_vector_T(x) @ self.D @ f_vector(x)

    def max_fi(self):
        ''' Поиск максимального значения fi '''
        max_fi = -9000
        for point in self.x:
            fi = self.fi(point)
            if fi > max_fi:
                max_fi = fi
        return max_fi

    def is_plan_optimal(self):
        '''
        Проверяем выполнение необходимых и достаточных
        условий оптимальности планов
        '''
        max_fi = self.max_fi()
        delta = 0.01 * abs(max_fi)
        if abs(-max_fi + np.trace(self.M @ self.D)) <= delta:
            return True
        else:
            return False

    def clear_plan(self):
        ''' Процедура очистки плана '''
        global n
        
        t = np.linspace(-1, 1, 5)
        i = 0
        for x1 in t:
            for x2 in t:
                self.new_x[i] = np.array([x1, x2])
                i+=1
        self.new_p = np.zeros(25)

        for point, weigth in zip(self.x, self.p):
            for i in range(5):
                for j in range(5):
                    a = point
                    b = self.new_x[i*5+j]
                    if a[0]==b[0] and a[1]==b[1]:
                        self.new_p[i*5+j] += weigth
        self.x = np.copy(self.new_x)
        self.p = np.copy(self.new_p)
        n = 25
        
    def calc_new_point(self):
        ''' Выбираем новую точку плана '''
        max_fi = -9000
        new_point = self.x[0]
        for point in self.x:
            fi = self.fi(point)
            if fi > max_fi:
                max_fi = fi
                new_point = point
        return new_point

    def add_new_point(self):
        ''' Добавляем в план новую точку x_s '''
        global n
        n += 1
        x_s = self.calc_new_point()
        self.x = np.append(self.x, [x_s], axis=0)
        self.p = np.append(self.p * (1 - self.alpha), self.alpha) 
        
    def draw_plan(self, iteration):
        ''' Отрисовка весов плана эксперимента '''
        x, y = np.hsplit(self.x, 2)
        plt.scatter(x, y)
        for i, txt in enumerate(self.p):
            plt.annotate(str(int(txt*100)), (x[i], y[i]))
        plt.title('План на шаге: ' + str(iteration), fontsize=19)
        # plt.xlabel('X', fontsize=10)
        # plt.ylabel('Y', fontsize=10)
        # plt.tick_params(axis='both', labelsize=8)
        plt.grid(alpha=0.4)
        plt.savefig('report/plan' + str(iteration) + '.png')
        plt.clf()

    def sequential_algorithm(self):
        '''
        Последовательный алгоритм синтеза непрерывного
        оптимального плана эксперимента
        '''
        self.generate_initial_guess()
        do_calc = True
        i = 0

        while do_calc == True and i < self.max_iter_s:
            flag = 0
            self.alpha = 1 / n
            self.build_matrix_M()
            self.build_matrix_D()
            psi = self.calc_D()
            self.add_new_point()
            psi_next = self.calc_D()

            # Уменьшаем шаг, если метод расходится
            while psi_next >= psi and flag < self.max_iter_alpha:
                flag += 1
                self.alpha /= self.gamma
                psi = psi_next
                self.add_new_point()
                psi_next = self.calc_D()
            print(i+1, flag)
            self.clear_plan()
            self.draw_plan(i+1)
            do_calc = not self.is_plan_optimal()
            # if i % 21 == 0:
            #     pass
            i += 1

    def build_matrix_M(self):
        ''' Построение информационной матрицы M '''
        # print(self.x)
        # print(self.p)
        self.M = np.zeros((m, m))
        for i in range(n):
            self.M += self.p[i] * f_vector(self.x[i]) * f_vector_T(self.x[i])

    def build_matrix_D(self):
        ''' Построение дисперсионной матрицы D '''
        self.D = inv(self.M)

    def calc_D(self):
        ''' 
        Критерий D - оптимальности. (D - determinant)
        Эллипсоид рассеивания имеет минимальный объём
        '''
        return np.log(det(self.M))


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

l2 = Lab2()
l2.sequential_algorithm()