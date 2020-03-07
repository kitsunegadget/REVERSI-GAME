import numpy as np
import tkinter as tk
import tkinter.messagebox as tkMsg

class Reversi:
    """ リバーシゲーム """

    """ Game Status """
    BLACK = 1
    WHITE = 0
    PLACEABLE = -1
    BLANK = -2


    def __init__(self):
        self.__boardInit()
        self.__windowInit()

    def __boardInit(self):
        self.__board = np.full((8, 8), -2)
        for i in range(2):
            self.__board[i+3, 3] = i % 2
            self.__board[i+3, 4] = (i+1) % 2
        
        self.__board_Button = []
        self.__playerorder = True # Trueなら黒（先手）

    def __windowInit(self):
        """新規ゲームウインドウ作成
        """
        self.__root = tk.Tk()
        self.__root.title("リバーシ：")
        frame = tk.Frame(self.__root)
        #frame["height"] = 200
        #frame["width"] = 300
        #frame["relief"] = "sunken"
        #frame["borderwidth"] = 5
        frame.grid()

        for i, l1 in enumerate(self.__board):
            for j, val in enumerate(l1):
                bt = tk.Button(frame, height=5, text=str(i) + "," + str(j))
                bt["width"] = 10
                self.__board_Button.append(bt)
                bt.grid(row=j, column=i)
                bt.bind("<1>", (lambda e: self.__putKoma(e)))
        
        self.__board_Button = np.array(self.__board_Button).reshape((8, 8))
        self.__searchCalc(self.__playerorder)
        self.__StatusUpdate()

    def Start(self):
        """ ゲームスタート """
        print("Reversi Start!")
        self.__root.title("リバーシ: 黒の番です")
        self.__root.mainloop()


    def __StatusUpdate(self):
        """ 状態をGUIに反映します """
        #print("update!")
        for i, l1 in enumerate(self.__board):
            for j, val in enumerate(l1):
                if val == self.BLANK:
                    self.__board_Button[i][j].configure(
                        state=tk.DISABLED, 
                        background="#2E8B57",
                        disabledforeground="#2E8B57"
                    )
                    self.__board_Button[i][j].unbind("<1>")

                elif val == self.PLACEABLE:
                    self.__board_Button[i][j].configure(
                        state=tk.NORMAL, 
                        fg="#4DC482", 
                        bg="#4DC482"
                    )
                    self.__board_Button[i][j].bind("<1>", (lambda e: self.__putKoma(e)))

                elif val == self.WHITE:
                    self.__board_Button[i][j].configure(
                        state=tk.DISABLED, 
                        background="#FFFFFF",
                        disabledforeground="#FFFFFF"
                    )
                    self.__board_Button[i][j].unbind("<1>")

                elif val == self.BLACK:
                    self.__board_Button[i][j].configure(
                        state=tk.DISABLED, 
                        background="#000000",
                        disabledforeground="#000000"
                    )
                    self.__board_Button[i][j].unbind("<1>")
                    
    def __putKoma(self, event):
        """ コマを置いたときの動作 """
        text = event.widget["text"].split(",")
        i = int(text[0])
        j = int(text[1])
        self.__board[i][j] = int(self.__playerorder)
        self.__reverseCalc(player=self.__playerorder, y=i, x=j)
        self.__playerChange()
    
    def __playerChange(self, passCount=0):
        """ プレイヤーの交代\n
        passCount: ゲーム内連続パスカウント、2連続したらお互いに置ける場所がないのでゲーム終了
        """
        self.__playerorder = not self.__playerorder
        self.__searchCalc(self.__playerorder)
        #print("clicked!!")

        count_black = np.sum(self.__board == self.BLACK)
        count_white = np.sum(self.__board == self.WHITE)

        if self.__playerorder:
            player = "黒"
            strings = f"リバーシ: {player}の番です　黒: {count_black}　白: {count_white}"
            self.__root.title(strings)
        else:
            player = "白"
            strings = f"リバーシ: {player}の番です　黒: {count_black}　白: {count_white}"
            self.__root.title(strings)
        
        if np.sum(self.__board == self.BLANK) == 0 \
                and np.sum(self.__board == self.PLACEABLE) == 0:
            self.__endGame(black=count_black, white=count_white)
            return
        
        elif np.sum(self.__board == self.PLACEABLE) == 0:
            if passCount == 1:
                self.__endGame(black=count_black, white=count_white)
                return

            tkMsg.showinfo(
                f"{player} Pass", 
                "置ける場所がないためパスします", 
                parent=self.__root
            )
            self.__playerChange(passCount=1)
        
    def __endGame(self, black, white):
        """ ゲーム終了処理 """
        if black > white:
            winner = "黒"
        elif white > black:
            winner = "白"
        else:
            tkMsg.showinfo("ゲーム終了", "同点です", parent=self.__root)
            strings = f"リバーシ: 同点です　黒: {black}　白: {white}"
            self.__root.title(strings)
            print("Game End.")
            return

        tkMsg.showinfo("ゲーム終了", f"{winner} の勝ちです", parent=self.__root)
        strings = f"リバーシ: {winner} の勝ちです　黒: {black}　白: {white}"
        self.__root.title(strings)
        print("Game End.")
        

    def __searchCalc(self, player):
        """ 現在のプレイヤーのコマの置ける位置を探索します
        """
        # PLACEABLEの部分をリセット
        for i, l1 in enumerate(self.__board):
            for j, val in enumerate(l1):
                if val == self.PLACEABLE:
                    self.__board[i][j] = self.BLANK

        for i, l1 in enumerate(self.__board):
            for j, val in enumerate(l1):
                # 現在のプレイヤーと逆の色を探索
                if val == int(not player):
                    # その位置から周囲8方向の探索
                    for v in range(-1, 2):
                        for u in range(-1, 2):
                            if i+v >= 0 and i+v <= 7 and j+u >= 0 and j+u <= 7:
                                # 周囲に空白があれば、傾き方向を逆にして更に探索
                                if self.__board[i+v][j+u] == self.BLANK:
                                    self.__extendCalc(player, i+v, j+u, -v, -u)
        
        self.__StatusUpdate()
        
    def __extendCalc(self, player, y, x, ty, tx, changing=False):
        """ x,y 位置からの傾きで直線を探索\n
        player: 現在のプレイヤー
        y: 探索始点 y
        x: 探索始点 x
        ty: y 方向傾き
        tx: x 方向傾き
        changing: コマの入れ替えをするときにTrue
        """
        py = ty
        px = tx
        for i in range(8): # 盤面の最大値まで
            if y+ty < 0 or y+ty > 7 or x+tx < 0 or x+tx > 7:
                # 盤面の外に出たら探索終了
                return
            
            elif self.__board[y+ty][x+tx] == int(player):
                # プレイヤー色と同じ色に当たったら置ける場所
                if changing:
                    # コマの入れ替え時、戻りながら入れ替える
                    for j in range(i):
                        ty -= py
                        tx -= px
                        self.__board[y+ty][x+tx] = int(player)
                        
                    return

                self.__board[y][x] = self.PLACEABLE
                return

            elif self.__board[y+ty][x+tx] == int(not player):
                # プレイヤーと逆の色が当たったら続ける
                ty += py
                tx += px

    def __reverseCalc(self, player, y, x):
        """ コマの入れ替え """
        # 置いた駒から8方向の探索
        for v in range(-1, 2):
            for u in range(-1, 2):
                if y+v >= 0 and y+v <= 7 and x+u >= 0 and x+u <= 7:
                    if self.__board[y+v][x+u] == int(not player):
                        self.__extendCalc(player, y, x, v, u, True)
        
        self.__StatusUpdate()


if __name__ == "__main__":
    game = Reversi()
    game.Start()
    