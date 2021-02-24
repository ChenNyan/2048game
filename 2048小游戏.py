import pygame
import sys, time
import random
import threading
from pygame.locals import *

LENGTH = 130
SIZE = 4
SCORE_HEIGHT = 130


class Map(object):
    def __init__(self, size):
        self.size = size
        self.map = [[0 for i in range(size)] for i in range(size)]
        # 生成一个4*4的列表分别代表4行4列元素，初始值为0
        self.score = 0
        self.is_move = 0
        # 随机添加2个元素到列表中（下面列表同矩阵的意思）
        self.add()
        self.add()

    def add(self):
        """该函数用于添加一个随机元素2 or 4到列表的随机位置"""

        while True:
            pos = random.randint(0, self.size * self.size - 1)  # 随机出一个0-15（含）的数字
            flag = self.map[pos // self.size][pos % self.size]  # 取这个数对应位置的元素
            if flag == 0:  # 如果这个元素为0则分配一个随机数给该位置，否则继续生成随机位置
                num = random.randint(0, 3)  # 这4行的含义是随机出0代表产生4，如果是1 2 3则生成数为2
                n = 2
                if num == 0:
                    n = 4
                self.map[pos // self.size][pos % self.size] = n  # 赋值给该位置
                self.score += n  # 这里是根据随机生成的数据后马上进行加分，另外一种加分方式是在合并的时候才加分
                break

    def moveToLeft(self):  # 判断是否能够左移
        changed = False  # 保存移动成功结果，默认是不能移动的
        for a in self.map:  # 取每一行
            b = []
            last = 0
            for v in a:  # 取每一个元素
                if v != 0:  # 元素值不等于0就将元素添加到b中，修改last值，
                    # 下一个元素如果等于last就是代表这个元素跟上一个元素相等，
                    # 就要将b中的最后一个元素左移一位，代表乘以2
                    if v == last:
                        b.append(b.pop() << 1)
                        last = 0
                    else:
                        b.append(v)
                        last = v
            b += [0] * (self.size - len(b))  # 在结束了相加之后，需要在末尾补充0来达到4个元素
            for i in range(self.size):  # 如果有任意一行的值和原来的值不相等，则代表移动成功了
                if a[i] != b[i]:
                    changed = True
            a[:] = b
        return changed

    def change(self):  # 该函数实现矩阵逆时针旋转90度
        self.map = [[self.map[i][j] for i in reversed(range(self.size))] for j in range(self.size)]

    def check(self, num):  # 判断num是否在矩阵中
        for i in self.map:
            for j in i:
                if j == num:
                    return True
        return False

    def move_left(self):  # 左移
        if self.moveToLeft():
            self.is_move = 1
            self.add()

    def move_up(self):  # 上移，需要将矩阵逆时针旋转3次90度，然后向左移动就代表在原矩阵向上移动了。
        self.change()
        self.change()
        self.change()
        if self.moveToLeft():  # 左移然后添加元素
            self.is_move = 1
            self.add()
        self.change()  # 在左移完了之后再旋转90度进行还原

    def move_right(self):  # 右移就是矩阵旋转180度，操作完左移了之后再旋转180度
        self.change()
        self.change()
        if self.moveToLeft():
            self.is_move = 1
            self.add()
        self.change()
        self.change()

    def move_down(self):  # 向下移动就是旋转90度，左移后，再旋转270度
        self.change()
        if self.moveToLeft():
            self.is_move = 1
            self.add()
        self.change()
        self.change()
        self.change()

    def failed(self):  # 判断结束
        for i in self.map:  # 如果有元素为0则返回false，这里可以如果是一维列表保存的则更简单
            for j in i:
                if j == 0:
                    return False
        for i in range(0, self.size):  # 只要有相邻的元素在一起则没有结束
            for j in range(0, self.size):
                if i - 1 >= 0 and self.map[i][j] == self.map[i - 1][j] or j - 1 >= 0 and self.map[i][j] == self.map[i][
                    j - 1] \
                        or i + 1 < self.size and self.map[i][j] == self.map[i + 1][j] or j + 1 < self.size and \
                        self.map[i][j] == self.map[i][j + 1]:
                    return False
        return True  # 以上条件都不满足则游戏结束了


def getColor(n):  # 这里是设置背景颜色的，不同的值设置不同的颜色
    hh = 0
    for i in range(1, 12):
        if n >> i == 1:
            hh = i
    color = [(255, 255, 255), (255, 255, 200), (255, 255, 150), (255, 255, 100), (255, 255, 0) \
        , (255, 193, 37), (208, 255, 63), (255, 165, 0), (255, 127, 36), (222, 174, 0), (0xa2, 0xcd, 0x5a),
             (0x98, 0xFB, 0x98), (106, 90, 205)]
    return color[hh]


# 这里的详细Pygame知识参照 https://blog.csdn.net/fengf2017/article/details/79300801
def display(map, screen):  # 定义主界面显示
    map_font = pygame.font.Font(None, LENGTH * 2 // 3)  # 这里采用地板除保证得到整数，颜色要用整数
    score_font = pygame.font.Font(None, SCORE_HEIGHT * 2 // 3)
    screen.fill((255, 255, 255))  # 整个屏幕都用白色填充
    for i in range(map.size):
        for j in range(map.size):
            block = pygame.Surface((LENGTH, LENGTH))
            block.fill(getColor(map.map[i][j]))
            font_surf = map_font.render(str(map.map[i][j]), True, (106, 90, 205))
            font_rect = font_surf.get_rect()
            font_rect.center = (j * LENGTH + LENGTH / 2, LENGTH * i + LENGTH / 2)
            screen.blit(block, (j * LENGTH, i * LENGTH))
            if map.map[i][j] != 0:
                screen.blit(font_surf, font_rect)
    score_surf = score_font.render('score: ' + str(map.score), True, (106, 90, 205))
    score_rect = score_surf.get_rect()
    score_rect.center = (LENGTH * SIZE / 2, LENGTH * SIZE + SCORE_HEIGHT / 2)
    screen.blit(score_surf, score_rect)
    pygame.display.update()

def main():
    pygame.init() #界面初始化
    map = Map(SIZE) #设置地图
    screen = pygame.display.set_mode((LENGTH*SIZE,LENGTH*SIZE+SCORE_HEIGHT))#设置界面尺寸
    pygame.display.set_caption("2048")#设置界面标题
    clock = pygame.time.Clock() #控制帧速率
    display(map,screen)#显示界面
    while not map.failed(): #如果没有失败
        for event in pygame.event.get():  #获取事件类型事件
            if event.type == QUIT:  #处理键盘退出
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            elif event.type ==KEYDOWN: #按键按下，按键如果不释放则不更新界面
                keys = pygame.key.get_pressed()#获取键盘按键的值
                map.is_move=0
                if keys[K_UP]: #上键
                    map.move_up()
                elif keys[K_DOWN]: #下键
                    map.move_down()
                elif keys[K_RIGHT]:
                    map.move_right()
                elif keys[K_LEFT]:
                    map.move_left()
            elif event.type == KEYUP: #按键释放，启动一个线程来更新显示界面，界面更新一般都是放在子线程中进行的
                t = threading.Thread(target=display,args=(map,screen))
                t.setDaemon(True)
                t.start()
        if map.is_move==1: #如果移动了，则检测是否有单元格达到2048了
            if map.check(2048):
                break; #此处可以改写其他提示信息，但是在此没有写提示
            time.sleep(0.01)#稍微设置一下延迟来等待界面更新
    result = "You Failed"
    if map.check(2048):
       result="You Win"
    screen.fill((255,255,255))
    map_font = pygame.font.Font('myfont.ttf',LENGTH*2//3)
    font_surf = map_font.render(result,True,(106, 90, 205))
    font_rect = font_surf.get_rect()
    font_rect.center = (SIZE*LENGTH/2,SIZE*LENGTH/2)
    screen.blit(font_surf,font_rect)
    pygame.display.update()
    while True:
       clock.tick(5) #控制帧值为5
       for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    main()