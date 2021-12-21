# https://www.odndo.com/posts/1627006679066/
import threading
from tkinter.constants import FALSE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patch
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg
import time

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
    # def on_closing(self):
    #     global is_valid
    #     is_valid = False
        
    #     self.window.close() # Windowを破棄

    def add_result(self, MIC_RESULT):
        # while is_valid:
        self.is_valid = False
        self.window['-M_BOX_2-'].print(MIC_RESULT, text_color='green')
            # is_valid = False
            # break

    def _window(self):
        print("window")
        #別ファイルの GCP STT の呼び出し
        ttsMIC = stt.Listen_print(2,"MIC")
        ttsMIKISER = stt.Listen_print(1,"MIKISER")
        while True:
            event, values = self.window.read(timeout=10)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Start':
                # 両マイクで認識を開始させる
                print("Start1")
                threading.Thread(target=ttsMIC.start_recognize, daemon=True).start()
                time.sleep(2)#これを入れないとWindowがクラッシュする
                print("Start2")
                threading.Thread(target=ttsMIKISER.start_recognize, daemon=True).start()      
            elif event == 'Alarm':
                message = values[event]
                sg.popup_auto_close(message)
            else:
            # それぞれの認識時の状態（待機か認識結果出力後か）を判断し，認識結果出力後であればテキストエディタに情報を追加する
                if(ttsMIC.get_condition()):
                    self.window['-M_BOX_2-'].print(ttsMIC.get_deviceName()+":"+ttsMIC.get_date()+ "\r"+ttsMIC.get_result(), text_color='red')
                    # self.window['-M_BOX_2-'].print("MIC:"+ttsMIC.get_result(), text_color='green')
                    ttsMIC.set_condition() #待機状態に戻す
                    # 認識をはじめる
                    threading.Thread(target=ttsMIC.start_recognize, daemon=True).start()
                if(ttsMIKISER.get_condition()):
                    self.window['-M_BOX_2-'].print(ttsMIKISER.get_deviceName()+":"+ttsMIKISER.get_date()+ "\r"+ttsMIKISER.get_result(), text_color='green')
                    ttsMIKISER.set_condition() #待機状態に戻す
                    # 認識をはじめる
                    threading.Thread(target=ttsMIKISER.start_recognize, daemon=True).start()
                self.window['-M_BOX_1-'].update(ttsMIC.get_progress_result())
                self.window['-M_BOX_1-'].update(ttsMIKISER.get_progress_result())
                # self.window['-M_BOX_2-'].Widget.clipboard_clear()
                # self.window['-M_BOX_2-'].print(ttsMIK.get_progress_result(), text_color='green')          
                # continue
            if event in ('Exit', None):
                exit(69)
        
        self.window.close()# ウィンドウの破棄と終了

if __name__ == '__main__':
    win = Draw_window()
    win.window()
