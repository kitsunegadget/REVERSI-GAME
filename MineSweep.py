import numpy as np
import tkinter as tk
import threading
import time

class MineSweep:
    """
    マインスイーパ
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
        self.mine_num = 12
        self.mine_remain = self.mine_num

        # time
        self.time_count = 0
        self.GAMEEND = False

        self.game_button = []
        self.thread = None
        self.opened_count = 0

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
    
    def __windowInit(self):
        self.root = tk.Tk()
        self.root.wm_minsize(342, 418)
        self.root.wm_resizable(False, False)
        self.root.title("マインスイーパー")

        # create info label
        infoframe = tk.Frame(self.root)
        self.lb_time = tk.Label(infoframe, width=21)
        self.lb_time["text"] = "Time: " + str(self.time_count) + "s"
        self.lb_time.grid(row=0, column=1)

        bt_restart = tk.Button(infoframe)
        bt_restart["text"] = "Re"
        bt_restart["height"] = 2
        bt_restart["width"] = 4
        bt_restart.bind("<1>", (lambda e: self.__restart()))
        bt_restart.grid(row=0, column=2)

        self.lb_remain = tk.Label(infoframe, width=21)
        self.lb_remain["text"] = "Remain: " + str(self.mine_remain)
        self.lb_remain.grid(row=0, column=3)

        infoframe.place(x=0, y=0)

        # ボタンイベント作成
        gridframe = tk.Frame(self.root)
        for i, v in enumerate(self.game):
            for j, val in enumerate(v):
                bt = tk.Button(gridframe)
                bt["height"] = 2
                bt["width"] = 4
                bt["bg"] = "#ccc"
                bt["fg"] = "#eee"
                bt["relief"] = tk.RAISED
                bt["state"] = tk.NORMAL
                bt["disabledforeground"] = "#eee"
                # print(bt.keys())
                self.game_button.append(bt)
                bt.grid(row=i, column=j)
                bt.bind("<1>", (lambda e: self.__mainClick(e)))
                bt.bind("<3>", (lambda e: self.__subClick(e)))
        
        gridframe.place(x=0, y=49)
        self.game_button = np.array(self.game_button).reshape((self.y, self.x))

    def Start(self):
        """ Start MineSweeper """
        print("MineSweep Start!")
        self.click_count = 0
        self.root.mainloop()
    
    def __restart(self):
        """ Restart Game """
        print("Restart!")
        self.GAMEEND = True
        for v in self.game_button:
            for u in v:
                u["text"] = ""
                u["bg"] = "#ccc"
                u["fg"] = "#eee"
                u["relief"] = tk.RAISED
                u["state"] = tk.NORMAL
                u["disabledforeground"] = "#eee"
                u.bind("<1>", (lambda e: self.__mainClick(e)))
                u.bind("<3>", (lambda e: self.__subClick(e)))
        
        self.time_count = 1
        self.__changeTime()
        self.mine_remain = self.mine_num
        self.__changeRemain()
        self.__changeTitle("")
        self.__gameInit()
        self.click_count = 0
        self.opened_count = 0

    def __countTime(self):
        """ 時間計測 (スレッド呼び出し専用) """
        while not self.GAMEEND:
            self.__changeTime()
            # print(self.time_count)
            self.time_count += 1
            time.sleep(1)
            

    def __mainClick(self, event):
        """ Left click event """
        # set time thread
        if self.click_count == 0:
            self.GAMEEND = False
            self.thread = threading.Thread(target=self.__countTime)
            self.thread.daemon = True
            self.thread.start()
        
        self.click_count += 1

        for v, vals in enumerate(self.game_button):
            for u, val in enumerate(vals):
                if val == event.widget:
                    # print(u, v)
                    j = v
                    i = u
        
        if self.game[j][i] == self.MINE:
            self.__gameOver()
            return
        
        print(self.game)
        
        self.__search(j, i)

    def __subClick(self, event):
        """ Right click event """
        for v, vals in enumerate(self.game_button):
            for u, val in enumerate(vals):
                if val == event.widget:
                    # print(u, v)
                    j = v
                    i = u

        if self.game[j][i] == self.CLOSED or self.game[j][i] == self.MINE:
            event.widget.configure(
                text="▼", 
                foreground="#333", 
            )
            event.widget.unbind("<1>")
            self.game[j][i] += self.FLAG
            self.mine_remain -= 1
            self.__changeRemain()
            # print(self.game[j][i])
        
        elif self.game[j][i] & self.FLAG == 0b10:
            event.widget.configure(
                text="❔", 
                foreground="#333",
            )
            self.game[j][i] += (self.UNKNOWN - self.FLAG)
            self.mine_remain += 1
            self.__changeRemain()
            # print(self.game[j][i])
        
        elif self.game[j][i] & self.UNKNOWN == 0b100:
            event.widget.bind("<1>", (lambda e: self.__mainClick(e)))
            event.widget.configure(
                text="", 
            )
            self.game[j][i] -= self.UNKNOWN
            # print(self.game[j][i])

    
    def __gameClear(self):
        self.GAMEEND = True
        print("Game Clear")
        self.__changeTitle("： Game Clear!")
        for v, vals in enumerate(self.game):
            for u, val in enumerate(vals):
                if val & self.MINE == 1:
                    self.game_button[v][u].configure(
                        text="✔", 
                        foreground="#0a0"
                    )
        
        for v in self.game_button:
            for u in v:
                u.unbind("<1>")
                u.unbind("<3>")

    def __gameOver(self):
        self.GAMEEND = True
        print("Game Over")
        self.__changeTitle("： Game Over!")
        for v, vals in enumerate(self.game):
            for u, val in enumerate(vals):
                if val & self.MINE == 1:
                    self.game_button[v][u].configure(
                        text="❌", 
                        foreground="#e00"
                    )
        
        for v in self.game_button:
            for u in v:
                u.unbind("<1>")
                u.unbind("<3>")
    
    def __changeTitle(self, state):
        self.root.title("マインスイーパー" + state)
    
    def __changeTime(self):
        """ time changes """
        if (self.GAMEEND):
            self.time_count -= 1
        
        self.lb_time["text"] = "Time: " + str(self.time_count) + "s"
    
    def __changeRemain(self):
        """ remain current flags """
        self.lb_remain["text"] = "Remain: " + str(self.mine_remain)
        

    def __search(self, posY, posX):
        """ 周囲8マス探索 """
        if self.game[posY][posX] & self.MINE == 1:
            return

        # 周囲のMine数を探索
        mines = 0
        for v in range(-1, 2):
            for u in range(-1, 2):
                # print(v, u)
                if (posY + v < 0) or (self.y - 1 < posY + v) \
                        or (posX + u < 0) or (self.x - 1 < posX + u):
                    continue

                if self.game[posY + v][posX + u] & self.MINE == 1:
                    mines += 1
        
        # print(mines)
        if mines != 0:
            self.game_button[posY][posX].configure(
                text=str(mines), 
                disabledforeground=self.fgcolor[mines-1],
                background="#999",
                state=tk.DISABLED,
                relief=tk.SUNKEN
            )
            self.game_button[posY][posX].unbind("<1>")
            self.game_button[posY][posX].unbind("<3>")
            self.game[posY][posX] = self.OPEN
        
        else:
            self.game_button[posY][posX].configure(
                text="",
                disabledforeground=self.fgcolor[mines-1],
                background="#999",
                state=tk.DISABLED,
                relief=tk.SUNKEN
            )
            self.game_button[posY][posX].unbind("<1>")
            self.game_button[posY][posX].unbind("<3>")
            self.game[posY][posX] = self.OPEN
            
            # 0のときは更に周りのマスを中心に探索
            for v in range(-1, 2):
                for u in range(-1, 2):
                    if (posY + v < 0) or (self.y - 1 < posY + v) \
                            or (posX + u < 0) or (self.x - 1 < posX + u):
                        continue

                    # 隣のマスにおいてのmineを更に探索
                    if self.game[posY + v][posX + u] != self.OPEN:
                        self.__search(posY + v, posX + u)
        
        # クリアチェック
        self.opened_count += 1
        if self.opened_count + self.mine_num == self.x * self.y:
            self.__gameClear()


# 単体テスト用
if __name__ == "__main__":
    game = MineSweep()
    game.Start()
