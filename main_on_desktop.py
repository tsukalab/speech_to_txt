# https://www.odndo.com/posts/1627006679066/
# from logging import root
import threading
import tkinter 
from tkinter import ttk, messagebox
from tkinter.constants import FALSE
from click import progressbar

import csv
import time
import datetime
import speech_to_text_sample_toSaveAudio as stt

# 一階層上にLOGを保存
# Bfolder = "F:/wavtomo/wav_Befor_Recognize/"
LOG_DIRECTORY = "../LOG_GUI/"
MIC_INDEX = 2
MIXER_INDEX = 1
ttsMIC = stt.Listen_print(MIC_INDEX,"USER", 1)
ttsMIXER = stt.Listen_print(MIXER_INDEX,"PC",0)
class display_result():
# def draw_window():
    def __init__(self):
        fontsize = 15;fontcolour = "black"
        num_comment = 3;alpha = 50;bold = "bold"

        self.root = tkinter.Tk()
        ww = self.root.winfo_screenwidth()
        wh = self.root.winfo_screenheight()  
        self.root.wm_attributes("-topmost", True)            # ウインドウを最前面へ
        self.root.wm_attributes("-transparentcolor", "white")# ウインドウを設定
        self.root.attributes("-alpha",0.5)                   # 全オブジェクトの透過度を設定:1-0
        self.root.title("TranScriptoWindow")    
        # self.root.protocol("WM_DELETE_WINDOW",  lambda: on_closing(self.root))# windowを閉じれないようにする
        # backgroundカラーに設定されたオブジェクトを完全透過する
        ttk.Style().configure("TP.TFrame", background="white")
        f = ttk.Frame(master=self.root, style="TP.TFrame", width=ww, height=wh)
        f.pack()        
        self.mic_progres = tkinter.StringVar()
        self.mixer_progres = tkinter.StringVar()
        tmp = ttsMIC.get_progress_result()
        self.mic_progres.set(tmp)
        tmp = ttsMIXER.get_progress_result()
        self.mixer_progres.set(tmp)
        mic_label = ttk.Label(  self.root, 
                                textvariable=self.mic_progres,
                                wraplength=ww, 
                                font=("メイリオ", fontsize, bold),
                                foreground=fontcolour,
                                background="red" ) 
        mixer_label = ttk.Label(    self.root, 
                                    textvariable=self.mixer_progres,
                                    wraplength=ww, 
                                    font=("メイリオ", fontsize, bold),
                                    foreground=fontcolour,
                                    background="blue" ) 
        w = mic_label.winfo_reqwidth()/len(tmp)
        h = mic_label.winfo_reqheight()
        mixer_label.place(x=0, y=100) 
        mic_label.place(x=0, y=(wh-num_comment*h-alpha))  # -αは下のタスクバーの分
        # # labelmic.place(x=0, y=100) 
        # # labelmikiser.place(x=0+labelmic.winfo_reqwidth(), y=100)  # -αは下のタスクバーの分
    #option_windowの設定        
        option_window = tkinter.Tk()
        option_window.wm_attributes("-topmost", True)
        option_window.geometry("300x300+"+str(int(ww/2-300/2))+"+"+str(int(wh/2-300/2)))
        option_window.title("Settings")
        # # Scale（デフォルトで作成）
        # scaleV = tkinter.Scale(option_window)
        # scaleV.pack(side = tkinter.RIGHT)
        # # Scale（オプションをいくつか設定）
        # self.scale_var = tkinter.DoubleVar()
        # scaleH = tkinter.Scale(
        #             option_window, 
        #             variable = self.scale_var, 
        #             command = self.slider_scroll,
        #             orient=tkinter.HORIZONTAL,   # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
        #             length = 300,           # 全体の長さ
        #             width = 20,             # 全体の太さ
        #             sliderlength = 20,      # スライダー（つまみ）の幅
        #             from_ = 0,            # 最小値（開始の値）
        #             to = 1,               # 最大値（終了の値）
        #             resolution=0.1,         # 変化の分解能(初期値:1)
        #             tickinterval=0.2         # 目盛りの分解能(初期値0で表示なし)
        #             )
        # scaleH.pack()
        # lnumcomment = ttk.Label(option_window, text="Number of comments",wraplength=ww)
        # lnumcomment.pack()

        # # Scale（オプションをいくつか設定）
        # self.scale_var = tkinter.DoubleVar()
        # fontsiza_sv = tkinter.Scale(
        #             option_window, 
        #             variable = self.scale_var, 
        #             command = self.slider_scroll,
        #             orient=tkinter.HORIZONTAL,   # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
        #             length = 300,           # 全体の長さ
        #             width = 20,             # 全体の太さ
        #             sliderlength = 20,      # スライダー（つまみ）の幅
        #             from_ = 0,            # 最小値（開始の値）
        #             to = 20,               # 最大値（終了の値）
        #             resolution=0.5,         # 変化の分解能(初期値:1)
        #             tickinterval=5        # 目盛りの分解能(初期値0で表示なし)
        #             )
        # fontsiza_sv.pack()
        # lnumcomment = ttk.Label(option_window, text=str(self.scale_var),wraplength=ww)
        # lnumcomment.pack()

        lfontsize = ttk.Label(option_window, text="Fontsize",
                            wraplength=ww)
        lfontsize.pack()
        txt2 = tkinter.Entry(option_window, width=20)
        txt2.insert(tkinter.END, fontsize)
        txt2.pack()

        lfontcolour = ttk.Label(option_window, text="Font colour",
                                wraplength=ww)
        lfontcolour.pack()
        txt3 = tkinter.Entry(option_window, width=20)
        txt3.insert(tkinter.END, fontcolour)
        txt3.pack()

        label = tkinter.Label(
        self.root,
        text="0",
        font=("", 80),
            width=10,
            # textvariable=self.scale_var.get() # ウィジェット変数を設定
        )
        label.pack(padx=10, pady=10)

        lalpha = ttk.Label(option_window, text="y-axis correction(If positive,display above)",
                        wraplength=ww)
        lalpha.pack()
        txt4 = tkinter.Entry(option_window, width=20)
        txt4.insert(tkinter.END, alpha)
        txt4.pack()

        bl1 = tkinter.BooleanVar(option_window)
        bl1.set(True)
        CheckBox1 = tkinter.Checkbutton(
            option_window, text="Bold", variable=bl1)
        CheckBox1.pack()
        btn = ttk.Button(option_window, text="Start", command=self.start_btn)
        btn.pack(side="right")
        applybtn = ttk.Button(option_window, text="Stop", command=self.stop_btn)
        applybtn.pack(side="right")
        self.root.mainloop()
    def slider_scroll(self, event=None):
        '''スライダーを移動したとき'''
        # label.config(text=str(self.scale_var.get()))
        # print(str(self.scale_var.get()))

    def update_stt_result(self):
        tmp = ttsMIC.get_progress_result()
        self.mic_progres.set(tmp)
        tmp = ttsMIXER.get_progress_result()
        self.mixer_progres.set(tmp)
        self.root.after(10, self.update_stt_result)
    def stop_btn(self):
        ttsMIXER.set_stt_status(False)
        ttsMIC.set_stt_status(False)
        # global start_flag
        # start_flag = False
    def start_btn(self):
        ttsMIC.init_object()
        ttsMIXER.init_object()
        print("Start1")
        t1 = threading.Thread(target=ttsMIC.start_recognize, daemon=True)
        t1.start()
        time.sleep(5)#これを入れないとpysimpleGUIのWindowがクラッシュする
        print("Start2")
        t2 = threading.Thread(target=ttsMIXER.start_recognize, daemon=True)
        t2.start()
        ttsMIC.set_progress_result("【何か話してください】")
        ttsMIXER.set_progress_result("【何か話してください】")
        self.root.after(1, self.update_stt_result)

        # subf.destroy()
        device_INDEX_MIKISER = 0
        device_INDEX_MIC = 2

# CSV形式でLOG保存関数
#引数(AUDIO_FILE_NAME:nameFormat【2021-01-01-10.10.55】, ResultList:認識結果, num:認識結果文字数, saveFileName:保存するファイルの名前, deviceNUM :MIXER=0,MIC=1)
def addwriteCsvTwoContents(AUDIO_FILE_NAME, ResultList:list, num, saveFileName, deviceNUM = 0):
    month=AUDIO_FILE_NAME[5:7];day=AUDIO_FILE_NAME[8:10];hh=AUDIO_FILE_NAME[11:13];mm=AUDIO_FILE_NAME[14:16];ss=AUDIO_FILE_NAME[17:19]
    audioNameR=audioNameL=AUDIO_FILE_NAME
    CR0=CL0=CR=CL=""
    CR0Len=CL0Len=0
    file = open(saveFileName, 'a', newline="")
    w = csv.writer(file)
    if not ResultList:
        print("R contents is not Recognize")
    else:
        CR0 = ResultList[0]
        CR = ResultList
        if(CR0 != 0):
            # print(conv.do(CR0))
            # CR0Len = int(len(CR0))
            CR0Len = num

    # w = w.writerow([month+"/"+day,hh+":"+mm+":"+ss,audioNameR,CR0,CR,CR0Len,audioNameL,CL0,CL,CL0Len, cut_time,"NULL",progressTime])
    w = w.writerow([month+"/"+day, hh+":"+mm+":"+ss, audioNameR, CR0, CR, CR0Len, deviceNUM])
    file.close()

if __name__ == '__main__':
    # draw_window()
    display_result()
