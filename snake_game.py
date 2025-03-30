import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

class SnakeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 游戏参数
        self.grid_size = 20  # 网格大小
        self.cell_size = 20  # 单元格大小
        self.game_speed = 100  # 游戏速度（毫秒）
        
        # 初始化游戏状态
        self.snake = [(5, 5), (4, 5), (3, 5)]  # 蛇的身体，列表中的每个元素是一个坐标元组
        self.direction = (1, 0)  # 初始方向：向右
        self.food = self.generate_food()  # 生成食物
        self.score = 0  # 分数
        self.game_over = False  # 游戏是否结束
        
        # 设置窗口
        self.setWindowTitle("贪吃蛇游戏")
        self.setFixedSize(self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(self.game_speed)
        
        # 显示窗口
        self.show()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制背景
        painter.fillRect(0, 0, self.width(), self.height(), QColor(220, 220, 220))
        
        if not self.game_over:
            # 绘制食物
            painter.fillRect(
                self.food[0] * self.cell_size,
                self.food[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
                QColor(255, 0, 0)  # 红色
            )
            
            # 绘制蛇
            for i, (x, y) in enumerate(self.snake):
                color = QColor(0, 128, 0) if i == 0 else QColor(0, 200, 0)  # 蛇头深绿色，身体浅绿色
                painter.fillRect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                    color
                )
        else:
            # 游戏结束显示
            painter.setPen(QColor(255, 0, 0))
            painter.setFont(QFont('Arial', 15))
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                f"游戏结束!\n得分: {self.score}\n按空格键重新开始"
            )
        
        # 显示分数
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Arial', 10))
        painter.drawText(10, 20, f"得分: {self.score}")
    
    def keyPressEvent(self, event):
        # 处理按键事件
        key = event.key()
        
        if self.game_over:
            if key == Qt.Key_Space:
                self.restart_game()
            return
        
        # 改变方向
        if key == Qt.Key_Up and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key == Qt.Key_Down and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key == Qt.Key_Left and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key == Qt.Key_Right and self.direction != (-1, 0):
            self.direction = (1, 0)
        elif key == Qt.Key_P:
            # 暂停/继续游戏
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start(self.game_speed)
    
    def update_game(self):
        if self.game_over:
            return
        
        # 获取蛇头位置
        head_x, head_y = self.snake[0]
        
        # 计算新的蛇头位置
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 检查是否撞墙
        if (new_head[0] < 0 or new_head[0] >= self.grid_size or
            new_head[1] < 0 or new_head[1] >= self.grid_size):
            self.game_over = True
            self.update()
            return
        
        # 检查是否撞到自己
        if new_head in self.snake:
            self.game_over = True
            self.update()
            return
        
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            # 增加游戏速度
            if self.game_speed > 50:
                self.game_speed -= 2
                self.timer.setInterval(self.game_speed)
        else:
            # 如果没有吃到食物，移除蛇尾
            self.snake.pop()
        
        # 更新界面
        self.update()
    
    def generate_food(self):
        # 生成食物，确保不在蛇身上
        while True:
            food = (random.randint(0, self.grid_size - 1), 
                   random.randint(0, self.grid_size - 1))
            if food not in self.snake:
                return food
    
    def restart_game(self):
        # 重置游戏状态
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.game_speed = 100
        self.timer.start(self.game_speed)
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = SnakeGame()
    sys.exit(app.exec_())
