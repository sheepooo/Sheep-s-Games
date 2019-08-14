from tkinter import *
import random
import threading
from collections import deque
from tkinter import messagebox
import tkinter.font as tkFont
import os.path

GRID_LEN = 30 #格子边长
GRID_X = 20 #格子列数
GRID_Y = 20 #格子行数
BG_X = GRID_X * GRID_LEN #背景宽度
BG_Y = GRID_Y * GRID_LEN #背景高度
D_HEAD = 30 #头大小
D_BODY = 30 #身大小
D_FOOD = 24 #食物大小
#蛇身体循环三种色系
CL_HEAD_LIST = ('#fb405a','#4891dc','#7d5dc6')
CL_BODY_LIST = ('#ff838b','#60b0e6','#ac98db')
CL_FOOD_LIST = ('#00aed9','#52da3f','#ffe81a','#ff993a','#ff545b','#ff14a3','#7d5ccb')
#初始色系
CL_HEAD = '#fb405a'
CL_BODY = '#ff838b'
CL_FOOD = '#9192ce'

class Game:
	def __init__(self, master):
		#定义几种字体
		self.ft40 = tkFont.Font(family='幼圆', size=40, weight=tkFont.BOLD)
		self.ft30 = tkFont.Font(family='幼圆', size=30, weight=tkFont.BOLD)
		self.ft20 = tkFont.Font(family='幼圆', size=20, weight=tkFont.BOLD)
		self.master = master
		self.cl_no = 0 #颜色序号
		if os.path.isfile('snake_data.txt'): #读取最高分纪录
			self.f = open('snake_data.txt', 'r+')
			self.score_highest = int(self.f.read())
			self.f.close()
		else:
			self.score_highest = 0
		self.f = open('snake_data.txt', 'w+')
		self.title = Label(self.master, text = '小肥羊的贪吃蛇', foreground = '#ff009c', font = self.ft40)
		self.title.place(relx = 0.5, x = -400, y = 20, width = 800, height = 60)
		self.lb_highest = Label(self.master, text = '最高分：%d' %self.score_highest, foreground = '#00a2ff', font = self.ft20,  anchor = E)
		self.lb_highest.place(relx = 0.5, rely = 1, x = 0, y = -80, width = 300, height = 30)
		self.panel_start_show('开始')

	def panel_start_show(self, text_of_btn):
		#显示开始界面
		self.btn_start = Button(self.master, text = text_of_btn, font = self.ft30, background = '#ffc550', foreground = '#ff5400')
		self.btn_start.place(width = 200, height = 100, relx = 0.5, rely = 0.5, x = -100, y = -50)
		self.btn_start.bind('<Button-1>', self.initwidgets)

	def panel_start_hide(self):
		#隐藏开始界面
		self.btn_start.place_forget()

	def stop_btn_show(self):
		#显示暂停界面
		self.btn_start = Button(self.master, text = '继续', font = self.ft30, background = '#ffc550', foreground = '#ff5400')
		self.btn_start.place(width = 200, height = 100, relx = 0.5, rely = 0.5, x = -100, y = -50)
		self.btn_start.bind('<Button-1>', self.stop_btn_hide)

	def stop_btn_hide(self, event):
		#隐藏暂停界面
		self.btn_start.place_forget()
		self.is_stop = False
		self.move()

	def panel_end_show(self):
		#显示结束界面
		self.btn_start = Button(self.master, text = '再来一局', font = self.ft30, background = '#ffc550', foreground = '#ff5400')
		self.btn_start.place(width = 200, height = 100, relx = 0.5, rely = 0.5, x = -100, y = -50)
		self.btn_start.bind('<Button-1>', self.initwidgets)
		self.result = Label(self.master, text = '你输了！分数：%d' %self.score , foreground = '#ff5054', font = self.ft30)
		self.result.place(relx = 0.5, x = -400, y = 280, width = 800, height = 60)
		self.lb_score.place_forget()
		self.cv.place_forget()
		self.f.truncate()
		self.f.write(str(self.score_highest))

	def panel_end_hide(self):
		#隐藏结束界面
		self.panel_start_hide()
		self.result.place_forget()

	def draw_circle(self, x, y, d, color):
		'''
		x y 表示在第几个格子，d表示圆的直径
		'''
		return self.cv.create_oval(x * GRID_LEN + 17 - d / 2, y * GRID_LEN + 17 - d / 2, x * GRID_LEN + 17 + d / 2, y * GRID_LEN + 17 + d / 2, fill = color, width = 0)

	def new_body(self, x, y, color):
		#蛇身增加一个圆
		self.body.appendleft((x,y))
		self.body.appendleft(self.draw_circle(x,y,D_HEAD, color))

	def new_food(self):
		#增加一个食物
		global CL_FOOD
		self.food_no = (self.food_no + 1) % 7
		CL_FOOD = CL_FOOD_LIST[self.food_no]
		while 1:
			x = random.randint(0,GRID_X - 1)
			y = random.randint(0,GRID_Y - 1)
			if (x,y) not in self.body and (x,y) not in self.food:
				self.food.append((x,y))
				self.food.append(self.draw_circle(x,y,D_FOOD, CL_FOOD))
				break

	def initwidgets(self, event):
		#初始化控件
		self.is_lose = False
		self.is_stop = False
		self.v_count = 0
		self.score = 0
		self.panel_start_hide()
		self.cv = Canvas(self.master, width = BG_X, height = BG_Y, background = '#c2e770')
		self.cv.place(relx = 0.5, rely = 0.5, x = -BG_X / 2, y = -BG_Y / 2)
		self.cv.focus_set()
		self.lb_score = Label(self.master, text = '分数：%d' %self.score, foreground = '#00a2ff', font = self.ft20,  anchor = W)
		self.lb_score.place(relx = 0.5, rely = 1, x = -300, y = -80, width = 300, height = 30)
		self.v = 3
		self.cl_no = (self.cl_no + 1) % 3
		global CL_HEAD, CL_BODY
		CL_HEAD = CL_HEAD_LIST[self.cl_no]
		CL_BODY = CL_BODY_LIST[self.cl_no]
		self.body = deque() #第一个是脑袋
		self.new_body(0,0,CL_BODY)
		self.new_body(1,0,CL_BODY)
		self.new_body(2,0,CL_HEAD)
		self.food = []
		self.food_no = 0
		for i in range(6):
			self.new_food()

		self.direction = (1,0) #当前方向增量(x,y)
		self.direction_next = (1,0) #未来方向增量(x,y)
		self.cv.bind('<Left>', self.t_left)
		self.cv.bind('<Right>', self.t_right)
		self.cv.bind('<Up>', self.t_up)
		self.cv.bind('<Down>', self.t_down)
		self.cv.bind('<space>', self.stop)
		self.t = threading.Timer(1 / self.v, self.move) #计时线程
		self.t.daemon = True
		self.t.start()

	def t_left(self, event):
		if not self.direction == (1,0):
			self.direction_next = (-1,0)
	def t_right(self, event):
		if not self.direction == (-1,0):
			self.direction_next = (1,0)
	def t_up(self, event):
		if not self.direction == (0,1):
			self.direction_next = (0,-1)
	def t_down(self, event):
		if not self.direction == (0,-1):
			self.direction_next = (0,1)
	def stop(self, event):
		self.is_stop = True

	def move(self):
		#移动
		head = self.body[1]
		next_head = (self.body[1][0] + self.direction_next[0], self.body[1][1] + self.direction_next[1])
		self.direction = self.direction_next
		if next_head[0] < 0 or next_head[1] < 0 or next_head[0] >= GRID_X or next_head[1] >= GRID_Y:
			self.is_lose = True
			self.panel_end_show()
		elif next_head in self.body:
			self.is_lose = True
			self.panel_end_show()
		else: #把head换成body，newhead新建一个头（队列左边）
			self.cv.delete(self.body[0])
			self.body.popleft()
			self.body.popleft()
			self.new_body(head[0], head[1],CL_BODY)
			self.new_body(next_head[0], next_head[1], CL_HEAD)
			eat = False
			if next_head in self.food:
				eat = True
				self.score += self.v
				self.v_count += 1
				self.lb_score['text'] = '分数：%d' %self.score
				if self.score > self.score_highest:
					self.score_highest = self.score
					self.lb_highest['text'] = '最高分：%d' %self.score_highest
				if self.v_count == 3:
					self.v += 1
					self.v_count = 0
				a = self.food.index(next_head)
				self.cv.delete(self.food[a + 1])
				del self.food[a : a+2]
				self.new_food()

			if not eat: #如果没有吃到食物，要把最后一个body去掉
				self.cv.delete(self.body[-2])
				self.body.pop()
				self.body.pop()

		if self.is_stop:
			self.stop_btn_show()

		if not self.is_lose and not self.is_stop:
			self.t = threading.Timer(1 / self.v, self.move)
			self.t.daemon = True
			self.t.start()


root = Tk()
root.title('贪吃蛇')
root.geometry('800x800')
a = Game(root)
root.mainloop()
a.f.close()