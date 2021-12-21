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
        # ttsMIC = Tts_Result("MIC",1)
        ttsMIC = stt.Listen_print(2)
        # ttsMIKISER = Tts_Result("MIKISER",1)  
        ttsMIKISER = stt.Listen_print(1)
        while True:
            event, values = self.window.read(timeout=10)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Start':
                # 両マイクで認識を開始させる
                print("Start1")
                # threading.Thread(target=ttsMIC.main, daemon=True).start()
                # threading.Thread(target=ttsMIC.get_tts_result, daemon=True).start()
                print("Start2")
                threading.Thread(target=ttsMIKISER.main, daemon=True).start()
                # threading.Thread(target=ttsMIKISER.get_tts_result, daemon=True).start()
        
            elif event == 'Alarm':
                message = values[event]
                sg.popup_auto_close(message)
                # self.on_closing()
            else:
            # それぞれの認識時の状態（待機か認識結果出力後か）を判断し，認識結果出力後であればテキストエディタに情報を追加する
                if(ttsMIC.get_condition()):
                    print("-M_BOX_2-'MIC")
                    self.window['-M_BOX_2-'].print("MIC:"+ttsMIC.get_result(), text_color='green')
                    # self.window['-M_BOX_2-'].print("MIC:"+ttsMIC.get_result(), text_color='green')
                    ttsMIC.set_condition() #待機状態に戻す
                    event == 'Start'
                if(ttsMIKISER.get_condition()):
                    print("-M_BOX_2-MIK")
                    self.window['-M_BOX_2-'].print("MIK:"+ttsMIKISER.get_result(), text_color='green')
                    ttsMIKISER.set_condition() #待機状態に戻す
                    event == 'Start'
                    print(event)
                # print(ttsMIKISER.get_progress_result())
                self.window['-M_BOX_1-'].update(ttsMIC.get_progress_result())
                self.window['-M_BOX_1-'].update(ttsMIKISER.get_progress_result())
                # self.window['-M_BOX_2-'].Widget.clipboard_clear()
                # self.window['-M_BOX_2-'].print(ttsMIK.get_progress_result(), text_color='green')          
                # continue
            if event in ('Exit', None):
                exit(69)
        
        self.window.close()# ウィンドウの破棄と終了
        
class Tts_Result(object):
    def __init__(self, devicename, deviceindex):        
        self._DEVICE_INDEX =  deviceindex
        self.sttPackage = stt.Listen_print(self._DEVICE_INDEX)
        self._RETURN_VALUE = self.sttPackage.get_result()
        self._POGRESS_RESULT = self.sttPackage.get_progress_result()
        self._date = self.sttPackage.get_date() 
        self.condition = False
        
    def get_tts_result(self):
        while True:
            # print("Start recognize")
            # text = stt.Listen_print(self._DEVICE_INDEX)
            self.sttPackage.main()
            self.sttPackage.get_progress_result()
            tt = str(self.sttPackage.get_result())
            time = str(self.sttPackage.get_date())
            self._RETURN_VALUE= time+tt
            self.condition = True
            # if(devicename=="MIC"):
                # MIC_RESULT = time+tt 
                # MIC_FLAG = True
            # return MIC_RESULT
            # win.close_window()
            # win.add_result(MIC_RESULT)
            # return self._RETURN_VALUE
            print("End recognize")
            break
            
    def get_result(self):
        return self._RETURN_VALUE
    
    def get_progress_result(self):
        return self.sttPackage.get_progress_result()

    def get_condition(self):
        return self.condition
    
    def set_condition(self):
        self.condition = False

if __name__ == '__main__':
    win = Draw_window()
    win.window()
