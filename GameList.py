import numpy as np
import tkinter as tk

class ReverseGame:
    """リバーシゲーム
    """

    def __init__(self):
        self.__boardInit()
        self.__windowInit()

    def __boardInit(self):
        self.board = np.full((8, 8), -2)
        for i in range(2):
            self.board[i+3, 3] = i % 2
            self.board[i+3, 4] = (i+1) % 2
        
        self.board_Button = []
        self.__playerorder = True # Trueなら黒（先手）

        
    def __windowInit(self):
        """新規ゲームウインドウ作成
        """
        self.root = tk.Tk()
        self.root.title("リバーシ：")
        frame = tk.Frame(self.root)
        #frame["height"] = 200
        #frame["width"] = 300
        #frame["relief"] = "sunken"
        #frame["borderwidth"] = 5
        frame.grid()

        for i, l1 in enumerate(self.board):
            for j, val in enumerate(l1):
                bt = tk.Button(frame, height=5, text=str(i) + "," + str(j))
                bt["width"] = 10
                self.board_Button.append(bt)
                bt.grid(row=j, column=i)
                bt.bind("<1>", (lambda e: self.__putKoma(e)))
        
        self.board_Button = np.array(self.board_Button).reshape((8, 8))
        self.__searchCalc(self.__playerorder)
        self.__StatusUpdate()
        #root.mainloop()

    def Start(self):
        """ゲームスタート
        """
        print("Reverse Start!")
        self.root.title("リバーシ: 黒の番です")
        return self.board

    def __StatusUpdate(self):
        """状態をGUIに反映します
        """
        print("update!")
        for i, l1 in enumerate(self.board):
            for j, val in enumerate(l1):
                if val == -2:
                    self.board_Button[i][j].configure(state=tk.DISABLED, background="#2E8B57")
                    self.board_Button[i][j].unbind("<1>")
                elif val == -1:
                    self.board_Button[i][j].configure(state=tk.NORMAL, fg="#3CB371", bg="#3CB371")
                    self.board_Button[i][j].bind("<1>", (lambda e: self.__putKoma(e)))
                elif val == 0:
                    self.board_Button[i][j].configure(state=tk.DISABLED, background="#FFFFFF")
                    self.board_Button[i][j].unbind("<1>")
                elif val == 1:
                    self.board_Button[i][j].configure(state=tk.DISABLED, background="#000000")
                    self.board_Button[i][j].unbind("<1>")
                    
    def __putKoma(self, event):
        """コマを置いたときの動作です
        """
        text = event.widget["text"].split(",")
        i = int(text[0])
        j = int(text[1])
        self.board[i][j] = int(self.__playerorder)
        self.__putCalc(order=self.__playerorder, y=i, x=j, reverse=True)

        self.__playerorder = not self.__playerorder
        self.__searchCalc(self.__playerorder)
        self.__StatusUpdate()
        #print("clicked!!")

        count_black = np.sum(self.board == 1)
        count_white = np.sum(self.board == 0)

        if self.__playerorder:
            player = "黒"
            strings = f"リバーシ: {player}の番です　黒: {count_black}　白: {count_white}"
            self.root.title(strings)
        else:
            player = "白"
            strings = f"リバーシ: {player}の番です　黒: {count_black}　白: {count_white}"
            self.root.title(strings)
    
    def __searchCalc(self, playerorder):
        """現在のプレイヤーのコマの置ける位置を探索します
        """
        # -1の部分をリセット
        for i, l1 in enumerate(self.board):
            for j, val in enumerate(l1):
                if val == -1:
                    self.board[i][j] = -2

        for i, l1 in enumerate(self.board):
            for j, val in enumerate(l1):
                if val == int(not playerorder):
                    # playerとは逆の色を探索
                    for h in range(-1, 2):
                        for w in range(-1, 2):
                            # その駒から8方向の探索
                            if i+h >= 0 and i+h <= 7 and j+w >= 0 and j+w <= 7:
                                if self.board[i+h][j+w] == -2:
                                    self.__putCalc(playerorder, i+h, j+w)
        
    def __putCalc(self, order, y, x, reverse=False):
        """その場所からコマが置けるか探索
        reverse: コマの入れ替えをするときにTrue
        """
        for h in range(-1, 2):
            for w in range(-1, 2):
                if y+h >= 0 and y+h <= 7 and x+w >= 0 and x+w <= 7:
                    if self.board[y+h][x+w] == -2 or (h==0 and w==0):
                        continue
                    elif self.board[y+h][x+w] == int(not order):
                        hd = h+h
                        wd = w+w
                        for delta in range(7):
                            # 傾きで直線上の配置を探索
                            if y+hd >= 0 and y+hd <= 7 and x+wd >= 0 and x+wd <= 7:
                                if self.board[y+hd][x+wd] == int(order):
                                    if reverse:
                                        self.__reverseKomaRender(order, y, x, h, w)
                                        continue
                                    else:
                                        self.board[y][x] = -1
                                        return
                                elif self.board[y+hd][x+wd] in [-1, -2]:
                                    break     
                            hd += h
                            wd += w

    def __reverseKomaRender(self, order, y, x, h, w):
        """コマの入れ替え
        """
        hd = h
        wd = w
        for alpha in range(7):
            if self.board[y+hd][x+wd] == int(order):
                break
            else:
                self.board[y+hd][x+wd] = int(order)

            hd += h
            wd += w
