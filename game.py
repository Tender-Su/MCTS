from time import sleep
from tkinter import messagebox

import pygame
from numpy import unique, zeros

from mcts import 蒙特卡洛树

方格数 = 8
棋子尺寸 = 20
棋盘界面距 = 棋子尺寸 * 3
界面窗口距 = 30
真棋盘距离 = 棋盘界面距 + 界面窗口距
网格尺寸 = 2 * 棋子尺寸 + 5
线宽 = 2
棋盘长度 = 方格数 * 网格尺寸 + 线宽 * (网格尺寸 + 1)
界面长度 = 棋盘长度 + 棋子尺寸
窗口长度 = 界面长度 + 2 * 界面窗口距
# 棋子标记
翻译官 = {1: 'black', -1: 'white'}
黑子 = 1
白子 = -1
空位置 = 0

偏移 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
temp = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]

棋盘 = zeros((方格数, 方格数))
棋盘[3][3] = 黑子
棋盘[3][4] = 白子
棋盘[4][3] = 白子
棋盘[4][4] = 黑子


def 初始化窗口():
    pygame.init()
    pygame.display.set_caption('黑白棋')
    return pygame.display.set_mode((窗口长度, 窗口长度))


def 初始化局面():
    global 棋盘
    棋盘 = zeros((方格数, 方格数))
    棋盘[3][3] = 黑子
    棋盘[3][4] = 白子
    棋盘[4][3] = 白子
    棋盘[4][4] = 黑子


def xy2ij(x, y):
    '''
    界面坐标映射为棋盘矩阵坐标
    '''
    (i, j) = ((x - 真棋盘距离) // 网格尺寸, (y - 真棋盘距离) // 网格尺寸)
    (i, j) = (max(i, 0), max(j, 0))
    (i, j) = (min(i, 方格数 - 1), min(j, 方格数 - 1))
    return (i, j)


def ij2xy(i, j):
    return (i * 网格尺寸 + 真棋盘距离, j * 网格尺寸 + 真棋盘距离)


def ij2xy棋子(i, j):
    return (i * 网格尺寸 + 真棋盘距离 + (网格尺寸+线宽)/2, j * 网格尺寸 + 真棋盘距离 + (网格尺寸+线宽)/2)


def 绘制(轮次状态):
    # 画界面
    pygame.draw.rect(游戏窗口, 'grey', 界面)
    # 画轮次状态
    pygame.draw.circle(游戏窗口, 翻译官[轮次状态], (棋子尺寸*3, 棋子尺寸*3), 棋子尺寸)
    # 画可下位置
    for (i, j) in 可下位置(轮次状态):
        pygame.draw.circle(游戏窗口, 翻译官[轮次状态], ij2xy棋子(i, j), 棋子尺寸/3)
    # 画方格线
    for i in range(方格数 + 1):
        pygame.draw.line(游戏窗口, 'black', ij2xy(i, 0), ij2xy(i, 方格数), 线宽)
        pygame.draw.line(游戏窗口, 'black', ij2xy(0, i), ij2xy(方格数, i), 线宽)
    for i, line in enumerate(棋盘):
        for j, color in enumerate(line):
            # 画下棋状态
            if color:
                pygame.draw.circle(游戏窗口, 翻译官[color], ij2xy棋子(i, j), 棋子尺寸)
    pygame.display.update()


def 游戏结束(胜者):
    pygame.display.update()
    判定词 = {1: '黑方胜', -1: '白方胜', 2: '平局'}
    messagebox.showinfo('游戏结束', 判定词[胜者])
    初始化局面()


def 可下位置(轮次状态):
    合法位置 = []
    for i in range(8):
        for j in range(8):
            已经结束咧 = False
            if 棋盘[i][j]:
                continue
            for 方向 in 偏移:
                有敌人 = False
                newi = i
                newj = j
                while True:
                    newi += 方向[0]
                    newj += 方向[1]
                    if newi < 0 or newi > 7 or newj < 0 or newj > 7:
                        break
                    if not 棋盘[newi][newj]:
                        break
                    if 棋盘[newi][newj] == -轮次状态:
                        有敌人 = True
                    elif 棋盘[newi][newj] == 轮次状态 and 有敌人:
                        合法位置.append((i, j))
                        已经结束咧 = True
                        break
                    else:
                        break
                if(已经结束咧):
                    break

    return 合法位置


def 翻面吃子(i, j, 轮次状态):
    for 方向 in 偏移:
        newi = i
        newj = j
        待反转列表 = []
        while True:
            newi += 方向[0]
            newj += 方向[1]
            if newi < 0 or newi > 7 or newj < 0 or newj > 7:
                break
            if not 棋盘[newi][newj]:
                break
            if 棋盘[newi][newj] == -轮次状态:
                待反转列表.append((newi, newj))
            elif 棋盘[newi][newj] == 轮次状态 and len(待反转列表):
                for i2, j2 in 待反转列表:
                    棋盘[i2][j2] = 轮次状态
                break
            else:
                break


def 判定胜者(轮次状态):
    '''
    黑1
    白-1
    未结束0
    平局2
    '''
    种类, 数量 = unique(棋盘, return_counts=True)
    统计值 = dict(zip(种类, 数量))
    if(len(可下位置(轮次状态)) == 0 and len(可下位置(-轮次状态)) == 0 or 统计值[0] == 0):
        if 统计值.get(1,0) > 统计值.get(-1,0):
            return 1
        if 统计值.get(1,0) == 统计值.get(-1,0):
            return 2
        if 统计值.get(1,0) < 统计值.get(-1,0):
            return -1
    return 0


def 尝试下棋(i, j, 轮次状态):
    # 下棋失败：有子
    if 棋盘[i][j] != 空位置:
        return 轮次状态

    合法位置 = 可下位置(轮次状态)
    if (i, j) in 合法位置:
        棋盘[i][j] = 轮次状态
        翻面吃子(i, j, 轮次状态)
        if(len(可下位置(-轮次状态)) == 0):
            return 轮次状态
        else:
            return -轮次状态
    else:
        # 下棋失败：不合法
        return 轮次状态


def main():
    游戏窗口.fill('white')
    轮次状态 = 黑子
    绘制(轮次状态)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 退出
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 按下左键
                    (i, j) = (xy2ij(event.pos[0], event.pos[1]))
                    轮次状态 = 尝试下棋(i, j, 轮次状态)
                    绘制(轮次状态)
                    胜者 = 判定胜者(轮次状态)
                    if(胜者):
                        游戏结束(胜者)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    树 = 蒙特卡洛树(棋盘, 轮次状态)
                    决定 = 树.给出决定()
                    轮次状态 = 尝试下棋(决定[0], 决定[1], 轮次状态)
                    绘制(轮次状态)
                    胜者 = 判定胜者(轮次状态)
                    if(胜者):
                        游戏结束(胜者)


游戏窗口 = 初始化窗口()
界面 = pygame.Rect(界面窗口距, 界面窗口距, 界面长度, 界面长度)
main()