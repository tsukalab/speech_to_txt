# https://www.odndo.com/posts/1627006679066/
import threading
from tkinter.constants import FALSE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patch
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg

import re
import sys


import speech_to_text_sample_toSaveAudio as stt

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
DEVICE_INDEX = 1
# pyAudiosample
WAVE_OUTPUT_FILENAME = "./speech_to_text/text_output.wav"

# 図の描画関数
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

MIC_RESULT = "saisyo"
MIC_FLAG  = False

def draw_window():
    global MIC_FLAG

    # カラム設定
    layout = [            
                # 下部カラム
                [
                    sg.T(size=(50,5), key='-M_BOX_1-', background_color='black'),
                    sg.Multiline(size=(65,5), key='-M_BOX_2-'),
                    sg.Canvas(size=(640, 480), key='-CANVAS_3-')
                ]
            ]

    # Window設定
    sg.theme('Dark Teal8')   # GUIテーマの変更
    window = sg.Window(
                'テスト', # タイトルバーのタイトル
                layout, # 採用するレイアウトの変数
                finalize=True,
                auto_size_text=True,
                location=(0, 0),
                # no_titlebar=True, # タイトルバー無しにしたい時はコメントアウトを解除
                )
    # window.Maximize()   # フルスクリーン化したい時にはコメントアウトを解除
    canvas_elem_3 = window['-CANVAS_3-'] # CANVAS_3 = 円の回転アニメーショングラフ    
    m_box_1 = window['-M_BOX_1-']   # 左下左メッセージボックス
    m_box_2 = window['-M_BOX_2-']   # 左下右メッセージボックス
    canvas_3 = canvas_elem_3.TKCanvas

    # ------------------------------------------------------
    # プロット設定
    #-------------------------------------------------------

    # matplotlibスタイル（'dark_background'）
    plt.style.use('dark_background') 

    # グラフサイズ変更（figsize=(横インチ ,縦インチ)
    fig_3 = Figure(figsize=(1, 1)) 

    # axesオブジェクト設定（1行目・1列・1番目）

    ax_3 = fig_3.add_subplot(111)
    ax_3.xaxis.set_visible(False)
    ax_3.yaxis.set_visible(False)

    # グラフの描画
    fig_agg_3 = draw_figure(canvas_3, fig_3)

    # ランダム数値データの用意
    NUM_DATAPOINTS = 10000 # ランダムデータ用の数値ポイント最大値
    dpts = [np.sqrt(1-np.sin(x)) for x in range(NUM_DATAPOINTS)] # ランダム数値リスト

    # ------------------------------------------------------
    # 描画設定
    #-------------------------------------------------------
    
    # 描画ループ
    while True:
        event, values = window.read(timeout=10)
        if event in ('Exit', None):
            exit(69)
        if(MIC_FLAG):
            MIC_FLAG = True
            window['-M_BOX_2-'].print(MIC_RESULT, text_color='green')
            print("aa")

        # window['-M_BOX_1-'].Update("aaa")        
        # fig_agg_3.draw()

        # text = stt.Listen_print(2)
        # text.main()
        # tt = str(text.get_return_value())
        # time = str(text.get_date())
        # print(tt)
        # 
        
        # for i in range(len(dpts)):
        #     event, values = window.read(timeout=10)
        #     if event in ('Exit', None):
        #         exit(69)

        #     # グラフ描画のクリア
        #     ax_3.cla()
        #     # グラフ3の描画
        #     # 円-楕円 描画
        #     ellipse = patch.Ellipse(xy=(0.5, 0.5), width=np.sin(i/3), height=1, fill=False, ec='yellow')
        #     ax_3.add_patch(ellipse)
        #     # グラフの描画        
        #     fig_agg_3.draw()
        
        # with open('./Sample_GUI/message.txt',encoding="utf-8") as message_file: # メッセージボックス入力
        #     window['-M_BOX_1-'].Update(message_file.read())
        
# class Tts_Result(object):
#     def __init__(self,_deviceindex):
#         self._DEVICE_INDEX =  _deviceindex
#         self._RETURN_VALUE = "aiu"
#         self._date = "" 

def get_tts_result(devicename, deviceindex):
    global MIC_RESULT
    while True:
        print("arara")
        text = stt.Listen_print(deviceindex)
        text.main()
        tt = str(text.get_return_value())
        time = str(text.get_date())
        print(tt)
        if(devicename=="MIC"):
            MIC_RESULT = time+tt 
            MIC_FLAG = True

    # return tt
    # window['-M_BOX_2-'].print(time+":"+tt, text_color='green')

if __name__ == '__main__':
    t1 = threading.Thread(target=draw_window)
    t2 = threading.Thread(target=get_tts_result, args=("MIC",2))
    t3 = threading.Thread(target=get_tts_result, args=("Mik",1))
    t1.setDaemon(True)

# t1.join()
    t2.setDaemon(True)
    t3.setDaemon(True)
    t1.start()
    t2.start()

    # t3.start()
    t1.join()
    t2.join()

#
    #  if(ch):
        # break
    # get_tts_result(2)
    # draw_window()



    # main()