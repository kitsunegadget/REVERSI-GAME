import numpy as np
import tkinter as tk
from tkinter.font import Font
import tkinter.messagebox as tkmsg

class MineSweep:
    """マインスイーパ
    """
    # 数字の色
    fgcolor = ["blue","green","red","yellow","purple","pink","white","black"]

    """ Game Status
        0:000: Closed
        1:001: Mine
        2:010: Flagged
        4:100: Unknowned
        -2:1110: Opened

        ex: 
        mine + flagged = 3
        mine + unknowned = 5
    """
    CLOSED = 0
    MINE = 1
    FLAG = 2
    UNKNOWN = 4
    OPEN = -2

    def __init__(self):
        # ゲームサイズ
        self.x = 9
        self.y = 9

        # Mine の数
        self.mine_num = 13

        self.__gameInit()
        self.__windowInit()


    def __gameInit(self):
        entire_size = self.x * self.y

        if self.mine_num < 1:
            self.mine_num = 1
        elif entire_size <= self.mine_num:
            self.mine_num = entire_size - 1

        mine = np.full(self.mine_num, 1) # mineの数列
        space = np.full(entire_size - self.mine_num, 0) # 空白の数列
        data = np.concatenate([mine, space]) # 配列結合
        np.random.shuffle(data) # シャッフル
        data = np.reshape(data, (self.y, self.x)) # 2次元化
        print(data)
        
        self.game = data
        self.game_button = []
    

    def __windowInit(self):
        self.root = tk.Tk()
        self.root.title("マインスイーパー：")
        frame = tk.Frame(self.root)
        frame.grid()

        # ボタンイベント作成
        for i, v in enumerate(self.game):
            for j, val in enumerate(v):
                bt = tk.Button(frame)
                bt["height"] = 2
                bt["width"] = 4
                bt["bg"] = "#ccc"
                bt["fg"] = "#eee"
                bt["relief"] = tk.RAISED
                bt["state"] = tk.DISABLED
                self.game_button.append(bt)
                bt.grid(row=i, column=j)
                bt.bind("<1>", (lambda e: self.__mainClick(e)))
                bt.bind("<3>", (lambda e: self.__subClick(e)))
        
        self.game_button = np.array(self.game_button).reshape((self.y, self.x))


    def Start(self):
        print("MineSweep Start!")
    

    # Left click event
    def __mainClick(self, event):
        for v, vals in enumerate(self.game_button):
            for u, val in enumerate(vals):
                if val == event.widget:
                    #print(u, v)
                    j = v
                    i = u
        
        if self.game[j][i] == self.MINE:
            event.widget.configure(text="x", foreground="#fff")
            self.__gameOver()
            return
        
        print(self.game);
        
        self.__search(j, i)

    # Right click event
    def __subClick(self, event):
        for v, vals in enumerate(self.game_button):
            for u, val in enumerate(vals):
                if val == event.widget:
                    #print(u, v)
                    j = v
                    i = u

        if self.game[j][i] == self.CLOSED or self.game[j][i] == self.MINE:
            event.widget.configure(text="F", foreground="#f00", state=tk.NORMAL)
            event.widget.unbind("<1>")
            self.game[j][i] += self.FLAG
            print(self.game[j][i])
        
        elif self.game[j][i] & self.FLAG == 0b10:
            event.widget.configure(text="❓", foreground="#f00", state=tk.NORMAL)
            self.game[j][i] += (self.UNKNOWN - self.FLAG) 
            print(self.game[j][i])
        
        elif self.game[j][i] & self.UNKNOWN == 0b100:
            event.widget.bind("<1>", (lambda e: self.__mainClick(e)))
            event.widget.configure(text="", foreground="#fff", state=tk.NORMAL)
            self.game[j][i] -= self.UNKNOWN
            print(self.game[j][i])

    
    def __gameClear(self):
        print("Game Clear")
        self.root.title("マインスイーパー：Game Clear")
        for v, vals in enumerate(self.game):
            for u, val in enumerate(vals):
                if val & self.MINE == 1:
                    self.game_button[v][u].configure(
                        state=tk.NORMAL, 
                        text="⭕", 
                        foreground="#f00")
        
        for v in self.game_button:
            for u in v:
                u.unbind("<1>")
                u.unbind("<3>")

    def __gameOver(self):
        print("Game Over")
        self.root.title("マインスイーパー：Game Over")
        for v, vals in enumerate(self.game):
            for u, val in enumerate(vals):
                if val & self.MINE == 1:
                    self.game_button[v][u].configure(
                        state=tk.NORMAL, 
                        text="❌", 
                        foreground="#f00")
        
        for v in self.game_button:
            for u in v:
                u.unbind("<1>")
                u.unbind("<3>")
        
        
        
    # 周囲8マス探索
    def __search(self, posY, posX):
        if self.game[posY][posX] & self.MINE == 1:
            return

        # 周囲のMine数を探索
        mines = 0
        for v in range(-1, 2):
            for u in range(-1, 2):
                # print(v, u)
                if posY + v < 0 or self.y - 1 < posY + v \
                        or posX + u < 0 or self.x - 1 < posX + u:
                    continue

                if self.game[posY + v][posX + u] & self.MINE == 1:
                    mines += 1
        
        # print(mines)
        if mines != 0:
            self.game_button[posY][posX].configure(
                text=str(mines), 
                foreground=self.fgcolor[mines-1],
                state=tk.NORMAL,
                background="#999",
                relief=tk.SUNKEN)
            self.game_button[posY][posX].unbind("<1>")
            self.game_button[posY][posX].unbind("<3>")
            self.game[posY][posX] = self.OPEN
        
        else:
            self.game_button[posY][posX].configure(
                text="",
                background="#999", 
                state=tk.DISABLED,
                relief=tk.SUNKEN)
            self.game_button[posY][posX].unbind("<1>")
            self.game_button[posY][posX].unbind("<3>")
            self.game[posY][posX] = self.OPEN
            
            # 0のときは更に周りのマスを中心に探索
            for v in range(-1, 2):
                for u in range(-1, 2):
                    if posY + v < 0 or self.y - 1 < posY + v \
                            or posX + u < 0 or self.x - 1 < posX + u:
                        continue

                    # 隣のマスにおいてのmineを更に探索
                    if self.game[posY + v][posX + u] != self.OPEN:
                        self.__search(posY + v, posX + u)
        
        self.__clearCheck()
        

    # クリアチェック
    def __clearCheck(self):
        openedCount = 0
        for vals in self.game:
            for val in vals:
                if val & self.MINE == 1 or val == self.OPEN:
                    openedCount += 1
        
        if openedCount == self.x * self.y:
            self.__gameClear()