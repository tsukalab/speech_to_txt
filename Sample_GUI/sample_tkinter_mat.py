# https://www.python-beginners.com/entry/20210720/1626710254
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np


#スケール用関数
def change(value):
    t = int(value)
    y = np.sin(t * x)
    line.set_ydata(y)
    canvas.draw()
    
root = tkinter.Tk()
root.title("matplotlib 埋め込み")

#グラフデータ
x = np.linspace(0, 2*np.pi, 400)
y = np.sin(x)

#グラフ用オブジェクト生成
fig = Figure(figsize=(3, 3))   #Figure
ax = fig.add_subplot(1, 1, 1)           #Axes
line, = ax.plot(x, y)                   #2DLine

#Figureを埋め込み
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()

#ツールバーを表示
toolbar=NavigationToolbar2Tk(canvas, root)

#スケール
s = tkinter.Scale(
    root,
    orient="horizontal",    #方向
    command=change,         #調整時に実行
    )
s.pack()

root.mainloop()