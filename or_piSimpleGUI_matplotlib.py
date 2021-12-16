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

class Draw_window(object):
    def __init__(self):
        self.is_valid = True
        # カラム設定
        layout = [            
                    # 下部カラム
                    [
                        sg.Button('Start', size=(10,2)),
                        # sg.Text('', size=(30, 2)), sg.Text('Press "Start" button', size=(55, 12), key='-MAIN-'),
                        sg.T(size=(50,5), key='-M_BOX_1-', background_color='black'),
                        sg.Multiline(size=(65,5), key='-M_BOX_2-'),
                        sg.Canvas(size=(640, 480), key='-CANVAS_3-')
                    ]
                ]
        # Window設定
        sg.theme('Dark Teal8')   # GUIテーマの変更
        self.window = sg.Window(
                    'テスト', # タイトルバーのタイトル
                    layout, # 採用するレイアウトの変数
                    finalize=True,
                    auto_size_text=True,
                    location=(0, 0),
                    # no_titlebar=True, # タイトルバー無しにしたい時はコメントアウトを解除
                    )
        # window.Maximize()   # フルスクリーン化したい時にはコメントアウトを解除
        canvas_elem_3 = self.window['-CANVAS_3-'] # CANVAS_3 = 円の回転アニメーショングラフ    
        m_box_1 = self.window['-M_BOX_1-']   # 左下左メッセージボックス
        m_box_2 = self.window['-M_BOX_2-']   # 左下右メッセージボックス
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
        self.window['-M_BOX_2-'].print("tesy", text_color='green')
        self._window()
    # コールバック関数
    def on_closing(self):
        global is_valid
        is_valid = False
        
        self.window.close() # Windowを破棄

    def add_result(self, MIC_RESULT):
        # while is_valid:
        self.is_valid = False
        self.window['-M_BOX_2-'].print(MIC_RESULT, text_color='green')
            # is_valid = False
            # break

    def _window(self):
        print("window")
        ttss = Tts_Result("MIC",2)  
        while True:
            event, values = self.window.read(timeout=10)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Start':
                print("Start")
                ttss.get_tts_result()
                threading.Thread(target=ttss.get_tts_result, daemon=True).start()
            elif event == 'Alarm':
                message = values[event]
                sg.popup_auto_close(message)
                # self.on_closing()
            else:
                if(ttss.get_FLAG()):
                    self.window['-M_BOX_2-'].print(ttss.get_result(), text_color='green')
                    ttss.set_FLAG()
                # print(event)
                continue
            if event in ('Exit', None):
                exit(69)
        
        self.window.close()# ウィンドウの破棄と終了
        
class Tts_Result(object):
    def __init__(self,devicename, deviceindex):
        self._DEVICE_INDEX =  deviceindex
        self._RETURN_VALUE = "aiu"
        self._date = "" 
        self.tts_FLAG = False

    def get_tts_result(self):
        while True:
            print("Start recognize")
            text = stt.Listen_print(self._DEVICE_INDEX)
            text.main()
            tt = str(text.get_return_value())
            time = str(text.get_date())
            self._RETURN_VALUE= time+tt
            self.tts_FLAG = True
            # if(devicename=="MIC"):
                # MIC_RESULT = time+tt 
                # MIC_FLAG = True
            # return MIC_RESULT
            # win.close_window()
            # win.add_result(MIC_RESULT)
            return self._RETURN_VALUE
            break
    def get_result(self):
        return self._RETURN_VALUE

    def get_FLAG(self):
        return self.tts_FLAG
    
    def set_FLAG(self):
        self.tts_FLAG = False

if __name__ == '__main__':
    win = Draw_window()
    win.window()
