import tkinter as tk
import numpy as np
import GameList

def reverseStart():
    game = GameList.ReverseGame()
    game.Start()

window = tk.Tk()
window.title("Test")
#window.geometry(("200x200"))

frame = tk.Frame(window)
frame["height"] = 200
frame["width"] = 200
#frame["relief"] = "sunken"
#frame["borderwidth"] = 5
#frame["padding"] = 5
frame.grid()

label1 = tk.Label(
    frame,
    text="ゲームを選択してください。",
    foreground="#0d0d0d",
    width=45,
    anchor=tk.N
)
label1.grid(row=1, column=1)

button1 = tk.Button(
    frame,
    text="リバーシ",
    command=reverseStart
)
button1.grid(row=2, column=1)

window.mainloop()