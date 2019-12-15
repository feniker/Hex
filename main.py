# здесь подключаются модули
import pygame
from math import sin, cos, pi, inf
import sys
import numpy as np

sys.setrecursionlimit(10000)  # увеличиваю глубину рекурсии до 10000

# здесь определяются константы, классы и функции
FPS = 60
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
LIGHT_BLUE = (64, 128, 255)
GREEN = (0, 200, 64)
YELLOW = (225, 225, 0)
PINK = (230, 50, 230)
MY_PINK = (230, 100, 100)
COLOR = [RED, BLUE]
COLOR_GRID = [MY_PINK, LIGHT_BLUE]
SIZE_GECT = 30
X_SIZE_FIELD = 11
Y_SIZE_FIELD = 11
WIDTH_WINDOW = 1000
HEIGHT_WINDOW = 800


# Обьект шестиугольник, который может менять свой цвет
class Gect(object):
    def __init__(self, ent_coord, ent_color, ent_surf, ent_size, ent_color_shape=None):
        self.coordinate = ent_coord
        self.color = ent_color
        self.mark = -1
        self.surf = ent_surf
        self.size = ent_size
        self.color_shape = ent_color_shape
        self.x_pos, self.y_pos = 0, 0
        self.line = None  # в какой связной области находится клетка
        self.Touch = False
        for i in range(6):
            self.x_pos += self.coordinate[i][0]
        self.x_pos /= 6
        for i in range(6):
            self.y_pos += self.coordinate[i][1]
        self.y_pos /= 6
        pygame.draw.polygon(self.surf, self.color, self.coordinate)
        if not (self.color_shape is None):
            pygame.draw.polygon(self.surf, self.color_shape, self.coordinate, 5)

    def change_color(self, ent_color, who=None):
        self.color = ent_color
        pygame.draw.polygon(self.surf, self.color, self.coordinate)
        if not (self.color_shape is None):
            pygame.draw.polygon(self.surf, self.color_shape, self.coordinate, 5)

    def change_shape(self, num, who):  # 0 1 - нижние грани; 2 - левая; 3 4 - верхние; 5 - правая
        pygame.draw.line(self.surf, COLOR_GRID[who], self.coordinate[num], self.coordinate[(num + 1) % 6], 5)

    def toMark(self, who):
        if self.mark == -1:
            self.mark = who

    def isFirst(self):
        return self.mark == 0

    def isSecond(self):
        return self.mark == 1

    def isMarked(self):
        return self.isFirst() or self.isSecond()

    def dist_sqr(self, ent_x, ent_y):
        return (self.x_pos - ent_x) ** 2 + (self.y_pos - ent_y) ** 2


# Обьект цепочки шестиугольников, который может определять касается ли он границы
class GectLine(object):
    def __init__(self, ent_mark):
        self.line = set()
        self.mark = ent_mark
        self.touch = [False, False]  # левый и правый край или верхний и нижний

    def addGect(self, x_pos, y_pos):
        self.line.add((x_pos, y_pos))
        if self.mark == 0:
            if x_pos == 0: self.touch[0] = True
            if x_pos == X_SIZE_FIELD - 1: self.touch[1] = True
        if self.mark == 1:
            if y_pos == 0: self.touch[0] = True
            if y_pos == Y_SIZE_FIELD - 1: self.touch[1] = True

    def addLine(self, new_line):
        self.line.update(new_line.line)
        self.touch[0] = self.touch[0] or new_line.touch[0]
        self.touch[1] = self.touch[1] or new_line.touch[1]


# Обьект поля шестиугольников, который может определять куда нажата мышка, и менять цвета шестикугольников
class GectField(object):
    def _getCoord(self, centr_x, centr_y):
        points_coord = [[], [], [], [], [], []]
        for i in range(6):
            points_coord[i] = [self.size * cos(i * pi / 3 + pi / 6) + centr_x,
                               self.size * sin(i * pi / 3 + pi / 6) + centr_y]
        return points_coord

    def change_abroad(self):
        for i in self.gects[0]:
            i.change_shape(1, 0)
            i.change_shape(2, 0)
        for i in range(X_SIZE_FIELD):
            self.gects[i][0].change_shape(3, 1)
            self.gects[i][0].change_shape(4, 1)
            self.gects[i][Y_SIZE_FIELD - 1].change_shape(1, 1)
            self.gects[i][Y_SIZE_FIELD - 1].change_shape(0, 1)
        for i in self.gects[X_SIZE_FIELD - 1]:
            i.change_shape(4, 0)
            i.change_shape(5, 0)

    def __init__(self, ent_x_pos, ent_y_pos, ent_x_size, ent_y_size, ent_color, ent_surf, ent_size,
                 ent_color_grid=None):
        self.surf = ent_surf
        self.x_pos = ent_x_pos
        self.y_pos = ent_y_pos
        self.x_size = ent_x_size
        self.y_size = ent_y_size
        self.color = ent_color
        self.size = ent_size
        self.gects = [[]]
        self.color_grid = ent_color_grid
        self.lines = [[], []]  # массив цепей шестиугольников
        # self.firstLine = {}
        # self.secondLine = {}
        # self.FLleft = []
        # self.FLright = []
        r, R = 3 ** 0.5 * self.size / 2, self.size
        for i in range(self.x_size):
            self.gects.append([])
            for j in range(self.y_size):
                if (j % 2 == 0):
                    buf = Gect(self._getCoord(self.x_pos + r + (j // 2 + i) * 2 * r, self.y_pos + R + j * 1.5 * R),
                               self.color,
                               self.surf, self.size, ent_color_shape=self.color_grid)
                else:
                    buf = Gect(self._getCoord(self.x_pos + r + r + (j // 2 + i) * 2 * r, self.y_pos + R + j * 1.5 * R),
                               self.color,
                               self.surf, self.size, ent_color_shape=self.color_grid)
                self.gects[i].append(buf)
        self.change_abroad()

    def change_color_gect(self, x_pos, y_pos, new_color):
        self.gects[x_pos][y_pos].change_color(new_color)

    def nearest_point(self, x_pos, y_pos):
        ans_x, ans_y = 0, 0
        min_length = inf
        for i in range(self.x_size):
            for j in range(self.y_size):
                if self.gects[i][j].dist_sqr(x_pos, y_pos) < min_length:
                    min_length = self.gects[i][j].dist_sqr(x_pos, y_pos)
                    ans_x = i
                    ans_y = j
        return (ans_x, ans_y)

    def get_Matrix(self):
        ans = []
        for i in range(self.x_size):
            ans.append([])
            for j in range(self.y_size):
                if self.gects[i][j].mark == 0:  ans[i].append(0)
                if self.gects[i][j].mark == 1:  ans[i].append(1)
                if self.gects[i][j].mark == -1:  ans[i].append(-1)
        return ans

    def get_Cells(self, who):
        ans = set()
        for i in range(self.x_size):
            for j in range(self.y_size):
                if self.gects[i][j].mark == who:
                    ans.add((i,j))
        return ans

    def click_player(self, event, who):
        # 0 - первый игрок, 1 - второй игрок
        x_coord, y_coord = event.pos
        x_pos, y_pos = self.nearest_point(x_coord, y_coord)
        print("You push ", x_pos, y_pos)
        if not self.gects[x_pos][y_pos].isMarked():
            self.gects[x_pos][y_pos].change_color(COLOR[who])
            self.change_abroad()
            self.gects[x_pos][y_pos].toMark(who)
            wisest = GarryKasparov(self.get_Matrix())
            wisest.help_Garry_Kimovich((who+1)%2)
            return True
        return False

    def dfs(self, graph, start, who, visited=None, Matrix = None):
        #print(start)
        if visited is None:
            visited = set()
        if Matrix is None:
            Matrix = self.get_Matrix()
        if who == 0 and start[0] == X_SIZE_FIELD-1:
            return True
        if who == 1 and start[1] == Y_SIZE_FIELD-1:
            return True
        visited.add(start)
        #print(start)
        adding = self.neighbourhood(start[0], start[1], Arr=Matrix, who=who)
        graph.update(adding)
        for next in adding - visited:
            return self.dfs(graph, next, who, visited=visited, Matrix=Matrix)
        return False

    def isWin(self, who):#дебагерский вывод
        set_of_cells = self.get_Cells(who)
        if who == 0:
            check = False
            for i in range(Y_SIZE_FIELD):
                if self.gects[0][i].mark == who:
                    check = max(self.dfs(set_of_cells, (0, i), who), check)
            return check
        if who == 1:
            check = False
            for i in range(X_SIZE_FIELD):
                if self.gects[i][0].mark == who:
                    check = max(self.dfs(set_of_cells, (i, 0), who), check)
            return check
        return False

    def neighbourhood(self, x_pos, y_pos, Arr = None, who = None):
        near = [(x_pos - 1, y_pos), (x_pos - 1, y_pos + 1), (x_pos, y_pos - 1), (x_pos, y_pos + 1),
                (x_pos + 1, y_pos - 1), (x_pos + 1, y_pos)]
        if Arr is not None:
            return set(filter(lambda s: 0 <= s[0] <= X_SIZE_FIELD - 1 and 0 <= s[1] <= Y_SIZE_FIELD - 1 and Arr[s[0]][s[1]] == who, near))
        else:
            return set(filter(lambda s: 0 <= s[0] <= X_SIZE_FIELD - 1 and 0 <= s[1] <= Y_SIZE_FIELD - 1, near))

class GarryKasparov(object):
    def __init__(self, ent_matrix):
        self.matrix = np.asarray(ent_matrix)
        self.x_size = len(ent_matrix)
        self.y_size = len(ent_matrix[0])
        self.cwin = [0, 0]
    def to_Numpy(self, arr):
        ans = np.array([])
        for i in arr:
            buf = np.array([])
            for j in i:
                buf = np.append(buf, j)
            ans = np.append(ans, buf)
        return ans
    def neighbourhood(self, x_pos, y_pos, who = None):
        near = [(x_pos - 1, y_pos), (x_pos - 1, y_pos + 1), (x_pos, y_pos - 1), (x_pos, y_pos + 1),
                (x_pos + 1, y_pos - 1), (x_pos + 1, y_pos)]
        return set(filter(lambda s: 0 <= s[0] <= X_SIZE_FIELD - 1 and 0 <= s[1] <= Y_SIZE_FIELD - 1 and self.buf_matrix[s[0]][s[1]] == who, near))
    def dfs(self, graph, start, who, visited=None):
        if visited is None:
            visited = set()
        if who == 0 and start[0] == X_SIZE_FIELD-1:
            return True
        if who == 1 and start[1] == Y_SIZE_FIELD-1:
            return True
        visited.add(start)
        adding = self.neighbourhood(start[0], start[1], who=who)
        graph.update(adding)
        for next in adding - visited:
            return self.dfs(graph, next, who, visited=visited)
        return False
    def get_Cells(self, who):
        ans = set()
        for i in range(X_SIZE_FIELD):
            for j in range(Y_SIZE_FIELD):
                if self.buf_matrix[i][j] == who:
                    ans.add((i,j))
        return ans
    def isWin(self, who, Arr):#дебагерский вывод
        set_of_cells = self.get_Cells(who)
        if who == 0:
            check = False
            for i in range(Y_SIZE_FIELD):
                if self.buf_matrix[0][i] == who:
                    check = max(self.dfs(set_of_cells, (0, i), who), check)
            return check
        if who == 1:
            check = False
            for i in range(X_SIZE_FIELD):
                if self.buf_matrix[i][0] == who:
                    check = max(self.dfs(set_of_cells, (i, 0), who), check)
            return check
        return False
    def estimate(self, depth):
        cnt1 = 0
        cnt2 = 0
        buf_matrix = self.matrix.astype(np.int8) + 1
        buf_matrix = buf_matrix.reshape(1, buf_matrix.size)[0]
        cnz = np.count_nonzero(buf_matrix)
        cz = buf_matrix.size - cnz
        mask = np.append(np.ones(cz//2, dtype=np.int8), np.zeros(cz - (cz//2), dtype=np.int8))
        for i in range(depth):
            np.random.shuffle(mask)
            self.buf_matrix = self.matrix.astype(np.int8) + 1
            self.buf_matrix[self.buf_matrix == 0] = mask + 1
            self.buf_matrix = self.buf_matrix - 1
            if self.isWin(0, self.buf_matrix): cnt1+=1
            if self.isWin(1, self.buf_matrix): cnt2+=1
        return (cnt1, cnt2)

    def help_Garry_Kimovich(self, who):
        ans = (0,0)
        cnt = 0
        for i in range(X_SIZE_FIELD):
            for j in range(Y_SIZE_FIELD):
                if self.matrix[i][j] == -1:
                    self.matrix[i][j] = who
                    if who == 0:
                        buf,_ = self.estimate(10)
                        if buf>cnt:
                            cnt = buf
                            ans = (i,j)
                    if who == 1:
                        _, buf = self.estimate(10)
                        if buf>cnt:
                            cnt = buf
                            ans = (i,j)
                    self.matrix[i][j] = -1
        print(ans)
        return ans



# здесь происходит инициация, создание объектов и др.
pygame.init()
r1 = pygame.Rect((150, 20, 100, 75))
sc = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))
f0 = pygame.font.Font(None, 36)
win0 = f0.render('ПОБЕДИЛИ КРАСНЫЕ', 1, RED, GREEN)  # текст, сглаживание 0 - нет, 1 - есть; цвет текста; цвет фона
f1 = pygame.font.Font(None, 36)
win1 = f1.render('ПОБЕДИЛИ СИНИЕ', 1, BLUE, GREEN)
field = GectField(100, 100, X_SIZE_FIELD, Y_SIZE_FIELD, WHITE, sc, SIZE_GECT, ent_color_grid=BLACK)
count_turn = 0
win = -1  # -1 - идет игра, 0 - победа 1 игрока, 1 - победа второго игрока
clock = pygame.time.Clock()

# если надо до цикла отобразить объекты на экране
pygame.display.update()

# главный цикл
while win == -1:

    # задержка
    clock.tick(FPS)

    # цикл обработки событий
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            exit()
        if i.type == pygame.MOUSEBUTTONDOWN:
            if i.button == 1:
                # 0 - первый игрок, 1 - второй игрок
                if field.click_player(i, count_turn % 2):
                    count_turn += 1
                if field.isWin(0):
                    win = 0
                if field.isWin(1):
                    win = 1
    # --------
    # изменение объектов и многое др.
    # --------

    # обновление экрана
    pygame.display.update()
if win == 0:
    sc.blit(win0, (0.3 * WIDTH_WINDOW, 0.3 * HEIGHT_WINDOW))
    pygame.display.update()
if win == 1:
    sc.blit(win1, (0.3 * WIDTH_WINDOW, 0.3 * HEIGHT_WINDOW))
    pygame.display.update()

while True:

    # задержка
    clock.tick(FPS)

    # цикл обработки событий
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            exit()
    # --------
    # изменение объектов и многое др.
    # --------

    # обновление экрана
    pygame.display.update()
