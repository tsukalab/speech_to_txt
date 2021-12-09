import tkinter as tk 
from tkinter import ttk, messagebox
root = tk.Tk()
ttk.Style().configure("TP.TFrame", background="snow")
# subf.destroy()
root.wm_attributes("-topmost", True)
# 背景を透過させる
root.wm_attributes("-transparentcolor", "snow")
root.attributes("-fullscreen", True)
txt = tk.Text(height=1, width=10, wrap="none", background="snow")
txt.pack()

txt.tag_configure("r", foreground="#FF0000")
txt.tag_configure("g", foreground="#00FF00")
txt.tag_configure("b", foreground="#0000FF")

txt.insert("end", 'abc', 'r')
txt.insert("end", 'def', 'g')
txt.insert("end", 'ghi', 'b')

txt.configure(state="disabled") # 読取専用に

root.mainloop()