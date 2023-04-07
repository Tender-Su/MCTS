from copy import deepcopy
from math import log, sqrt
from random import choice
from time import time

from numpy import unique


class 蒙特卡洛树:

    偏移 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    重复次数 = 1000
    持续时间 = 1
    c = 2
    开始时间 = 0
    def __init__(self, 棋盘, 轮次状态):
        self.探测次数 = 0
        self.价值 = 0
        self.棋盘 = 棋盘
        self.轮次状态 = 轮次状态
        self.父 = None
        self.子 = []
        self.坐标 = None


    def 给出决定(self):
        """
        根据某个局面
        返回下棋坐标
        """

        次数 = 0
        蒙特卡洛树.立场 = self.轮次状态
        开始时间 = time()

        #for i in range(蒙特卡洛树.重复次数):
        while(time() - 开始时间 < 蒙特卡洛树.持续时间):
            次数 += 1
            操作节点 = 蒙特卡洛树.找UCB最大叶节点(self)
            if 操作节点.探测次数:
                # 探测过
                if 蒙特卡洛树.判定胜者(操作节点.棋盘, 操作节点.轮次状态) == '未结束':
                    # 可扩展 / 未结束 -> 扩展节点
                    操作节点 = 蒙特卡洛树.节点拓展(操作节点)
            # 模拟
            操作节点.探测次数 += 1
            操作节点.价值 = 蒙特卡洛树.随机下棋(操作节点)
            # 反向传播
            蒙特卡洛树.反向传播(操作节点)
            
        # 决策
        最多次 = 0
        决定 = None
        for 子 in self.子:
            if 子.探测次数 > 最多次:
                最多次 = 子.探测次数
                决定 = 子.坐标
        蒙特卡洛树.开始时间 += time() - 开始时间
        print('本次模拟用时',round(time() - 开始时间, 2), '秒',end = ',')
        print('模拟',次数,'次',end = ',')
        print('总用时',round(蒙特卡洛树.开始时间, 2), '秒')
        return 决定



    @classmethod
    def 反向传播(self, 操作节点):
        '''
        次数++
        价值++
        '''
        价值 = 操作节点.价值
        while 操作节点.父 != None:
            操作节点 = 操作节点.父
            操作节点.探测次数 += 1
            操作节点.价值 += 价值
    
    @classmethod
    def 找UCB最大叶节点(self, 结果):
        全局次数 = 结果.探测次数
        while not 蒙特卡洛树.判叶节点(结果):
            结果 = 蒙特卡洛树.找UCB最大子(结果, 全局次数)
        return 结果

    @classmethod
    def 判叶节点(self, 节点):
        if len(节点.子):
            return False
        return True

    
    @classmethod
    def 找UCB最大子(self, 当前节点, 全局次数):
        最大UCB = -9999999999
        最大子 = 当前节点.子[0]
        for 子 in 当前节点.子:
            if 子.探测次数 == 0:
                return 子
            UCB = 蒙特卡洛树.UCB(子, 全局次数)
            if(UCB > 最大UCB):
                最大UCB = UCB
                最大子 = 子
        return 最大子

    @classmethod
    def UCB(self, 节点, 全局次数):
        return 节点.价值 / 节点.探测次数 + 蒙特卡洛树.c * sqrt(log(全局次数) / 节点.探测次数)

    @classmethod
    def 节点拓展(self, 操作节点):
        合法位置 = 蒙特卡洛树.算可下位置(操作节点.棋盘, 操作节点.轮次状态)
        if 合法位置:
            for 位置 in 合法位置:
                模拟棋盘 = deepcopy(操作节点.棋盘)
                模拟轮次状态 = deepcopy(操作节点.轮次状态)
                模拟轮次状态 = 操作节点.尝试下棋(位置[0], 位置[1], 模拟棋盘, 模拟轮次状态, True)
                子 = 蒙特卡洛树(模拟棋盘, 模拟轮次状态)
                子.父 = 操作节点
                子.坐标 = 位置
                操作节点.子.append(子)
            return 操作节点.子[0]
        else:
            操作节点.轮次状态 = -操作节点.轮次状态
            return 蒙特卡洛树.节点拓展(操作节点)

    @classmethod
    def 随机下棋(self, 操作节点):

        模拟棋盘 = deepcopy(操作节点.棋盘)
        模拟轮次状态 = deepcopy(操作节点.轮次状态)

        while True:
            # 结束则返回
            胜者 = 蒙特卡洛树.判定胜者(模拟棋盘, 模拟轮次状态)
            if type(胜者) == int:
                return 胜者 * 蒙特卡洛树.立场

            # 未结束
            合法位置 = 蒙特卡洛树.算可下位置(模拟棋盘, 模拟轮次状态)
            if 合法位置:
                位置 = choice(合法位置)
                模拟轮次状态 = 蒙特卡洛树.尝试下棋(位置[0], 位置[1], 模拟棋盘, 模拟轮次状态, True)
            else:
                模拟轮次状态 = -模拟轮次状态

    @classmethod
    def 算可下位置(self, 棋盘, 轮次状态):
        合法位置 = []
        for i in range(8):
            for j in range(8):
                已经结束咧 = False
                if 棋盘[i][j]:
                    continue
                for 方向 in 蒙特卡洛树.偏移:
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

    @classmethod
    def 翻面吃子(self, 棋盘, i, j, 轮次状态):
        for 方向 in 蒙特卡洛树.偏移:
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
        return 棋盘

    @classmethod
    def 判定胜者(self, 棋盘, 轮次状态):
        '''
        黑 1
        白 -1
        平局 0 
        未结束 '未结束'
        '''
        种类, 数量 = unique(棋盘, return_counts=True)
        统计值 = dict(zip(种类, 数量))
        if(len(蒙特卡洛树.算可下位置(棋盘, 轮次状态)) == 0 and len(蒙特卡洛树.算可下位置(棋盘, -轮次状态)) == 0 or 统计值.get(0,0) == 0):
            return int(统计值.get(1, 0) - 统计值.get(-1,0))
        return '未结束'

    @classmethod
    def 尝试下棋(self, i, j, 棋盘, 轮次状态, 保证合法位置):
        # 下棋失败：有子
        if 棋盘[i][j]:
            if 保证合法位置:
                print('意外错误,需要修正')
            return

        棋盘[i][j] = 轮次状态
        蒙特卡洛树.翻面吃子(棋盘, i, j, 轮次状态)
        if(len(蒙特卡洛树.算可下位置(棋盘, -轮次状态)) == 0):
            return 轮次状态
        else:
            return -轮次状态

'''        合法位置 = 蒙特卡洛树.算可下位置(棋盘, 轮次状态)
        if (i, j) in 合法位置:
            棋盘[i][j] = 轮次状态
            蒙特卡洛树.翻面吃子(棋盘, i, j, 轮次状态)
            if(len(蒙特卡洛树.算可下位置(棋盘, -轮次状态)) == 0):
                return 轮次状态
            else:
                return -轮次状态
        else:
            # 下棋失败：不合法
            if 保证合法位置:
                print('意外错误,需要修正')
            return 轮次状态'''
