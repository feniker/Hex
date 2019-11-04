# здесь подключаются модули
import pygame
from math import sin, cos, pi, inf

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

#Обьект шестиугольник, который может менять свой цвет
class Gect(object):
    def __init__(self, ent_coord, ent_color, ent_surf, ent_size, ent_color_shape = None):
        self.coordinate = ent_coord
        self.color = ent_color
        self.mark = -1
        self.surf = ent_surf
        self.size = ent_size
        self.color_shape = ent_color_shape
        self.x_pos, self.y_pos = 0, 0
        self.line = None #в какой связной области находится клетка
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
    def change_color(self, ent_color, who = None):
        self.color = ent_color
        pygame.draw.polygon(self.surf, self.color, self.coordinate)
        if not (self.color_shape is None):
            pygame.draw.polygon(self.surf, self.color_shape, self.coordinate, 5)
    def change_shape(self, num, who):#0 1 - нижние грани; 2 - левая; 3 4 - верхние; 5 - правая
        pygame.draw.line(self.surf, COLOR_GRID[who], self.coordinate[num], self.coordinate[(num+1)%6], 5)
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
        return (self.x_pos - ent_x)**2 + (self.y_pos - ent_y)**2

#Обьект цепочки шестиугольников, который может определять касается ли он границы
class GectLine(object):
    def __init__(self, ent_mark):
        self.line = set()
        self.mark = ent_mark
        self.touch = [False, False] #левый и правый край или верхний и нижний
    def addGect(self, x_pos, y_pos):
        self.line.add((x_pos, y_pos))
        if self.mark == 0:
            if x_pos == 0: self.touch[0] = True
            if x_pos == X_SIZE_FIELD-1: self.touch[1] = True
        if self.mark == 1:
            if y_pos == 0: self.touch[0] = True
            if y_pos == Y_SIZE_FIELD-1: self.touch[1] = True
    def addLine(self, new_line):
        self.line.update(new_line.line)
        self.touch[0] = self.touch[0] or new_line.touch[0]
        self.touch[1] = self.touch[1] or new_line.touch[1]

#Обьект поля шестиугольников, который может определять куда нажата мышка, и менять цвета шестикугольников
class GectField(object):
    def _getCoord (self, centr_x, centr_y):
        points_coord = [[], [], [], [], [], []]
        for i in range(6):
            points_coord[i] = [self.size*cos(i * pi / 3 + pi / 6) + centr_x, self.size*sin(i * pi / 3 + pi / 6) + centr_y]
        return points_coord
    def change_abroad(self):
        for i in self.gects[0]:
            i.change_shape(1,0)
            i.change_shape(2,0)
        for i in range(X_SIZE_FIELD):
            self.gects[i][0].change_shape(3,1)
            self.gects[i][0].change_shape(4,1)
            self.gects[i][Y_SIZE_FIELD-1].change_shape(1,1)
            self.gects[i][Y_SIZE_FIELD-1].change_shape(0,1)
        for i in self.gects[X_SIZE_FIELD-1]:
            i.change_shape(4,0)
            i.change_shape(5,0)
    def __init__(self, ent_x_pos, ent_y_pos, ent_x_size, ent_y_size, ent_color, ent_surf, ent_size, ent_color_grid = None):
        self.surf = ent_surf
        self.x_pos = ent_x_pos
        self.y_pos = ent_y_pos
        self.x_size = ent_x_size
        self.y_size = ent_y_size
        self.color = ent_color
        self.size = ent_size
        self.gects = [[]]
        self.color_grid = ent_color_grid
        self.lines = [[], []] #массив цепей шестиугольников
        #self.firstLine = {}
       # self.secondLine = {}
        #self.FLleft = []
        #self.FLright = []
        r, R = 3**0.5*self.size/2, self.size
        for i in range(self.x_size):
            self.gects.append([])
            for j in range(self.y_size):
                if (j % 2 == 0):
                    buf = Gect(self._getCoord(self.x_pos + r + (j//2+i) * 2 * r, self.y_pos + R + j * 1.5 * R), self.color,
                               self.surf, self.size, ent_color_shape = self.color_grid)
                else:
                    buf = Gect(self._getCoord(self.x_pos + r + r + (j//2+i) * 2 * r, self.y_pos + R + j * 1.5 * R), self.color,
                               self.surf, self.size, ent_color_shape = self.color_grid)
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
    def neighbourhood(self, x_pos, y_pos):
        near = [(x_pos - 1, y_pos), (x_pos - 1, y_pos + 1), (x_pos, y_pos - 1), (x_pos, y_pos + 1),
                (x_pos + 1, y_pos - 1), (x_pos + 1, y_pos)]
        return list(filter(lambda s: 0 <= s[0] <= 10 and 0 <= s[1] <= 10, near))
    def touchLines(self, x_pos, y_pos, who):
        near = self.neighbourhood(x_pos, y_pos)
        list_touch_lines = []
        for i in near:
            j = 0
            while j < len(self.lines[who]):#сделать рзделение по игрокам
                if i in self.lines[who][j].line:
                    list_touch_lines.append(self.lines[who][j])
                    self.lines[who].pop(j)
                    j-=1
                j+=1
        return list_touch_lines
    def uniteTouchLines(self, x_pos, y_pos, who):
        list_touch_lines = self.touchLines(x_pos, y_pos, who)
        new_gect_line = GectLine(who)
        new_gect_line.addGect(x_pos, y_pos)
        for i in list_touch_lines:
            new_gect_line.addLine(i)
        self.lines[who].append(new_gect_line)
        for i in self.lines[0]:
            print(0, " -  ", i.touch[0]," - ", i.line)
        for i in self.lines[1]:
            print(1, " -  ", i.touch[0]," - ", i.line)
    def click_player(self, event, who):
        # 0 - первый игрок, 1 - второй игрок
        x_coord, y_coord = event.pos
        x_pos, y_pos = self.nearest_point(x_coord, y_coord)
        if not self.gects[x_pos][y_pos].isMarked():
            self.gects[x_pos][y_pos].change_color(COLOR[who])
            self.change_abroad()
            self.gects[x_pos][y_pos].toMark(who)
            self.uniteTouchLines(x_pos, y_pos, who)
            a = self.neighbourhood(x_pos, y_pos)
            print("coord ", x_pos, y_pos, "neig ", a)
            return True
        return False
    def isWin(self, who):
        for i in self.lines[who]:
            if i.touch[0] and i.touch[1]:
                return True
        return False

# здесь происходит инициация, создание объектов и др.
pygame.init()
r1 = pygame.Rect((150, 20, 100, 75))
sc = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))
f0 = pygame.font.Font(None, 36)
win0 = f0.render('ПОБЕДИЛИ КРАСНЫЕ', 1, RED, GREEN) #текст, сглаживание 0 - нет, 1 - есть; цвет текста; цвет фона
f1 = pygame.font.Font(None, 36)
win1 = f1.render('ПОБЕДИЛИ СИНИЕ', 1, BLUE, GREEN)
field = GectField(100, 100, X_SIZE_FIELD, Y_SIZE_FIELD, WHITE, sc, SIZE_GECT, ent_color_grid = BLACK)
count_turn = 0
win = -1 #-1 - идет игра, 0 - победа 1 игрока, 1 - победа второго игрока
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
                #0 - первый игрок, 1 - второй игрок
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
    sc.blit(win0, (0.3*WIDTH_WINDOW, 0.3*HEIGHT_WINDOW))
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