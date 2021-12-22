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

class Draw_window(object):
    def __init__(self):
        self.is_valid = True
        # 定数
        GRAPH_SIZE = (100, 100)
        DATA_SIZE = (500, 500)
        
        
    # カラム設定
        col1 =  [   [sg.Button('Start', size=(10,2))],
                    [sg.Button('Stop', size=(10,2))]
                ]
        col2 =  [   [
                    # sg.T(size=(50,10), key='-M_BOX_1-', background_color='black')
                    sg.Multiline(size=(55,10), key='-M_BOX_1-',background_color='black',autoscroll=True)
                    ],
                        
                    [sg.T(size=(50,4), key='-M_BOX_1-2', background_color='black')]
                ]   
        col3 =  [   [
                    sg.Multiline(size=(65,14), key='-M_BOX_2-',autoscroll=True),
                    # sg.Canvas(size=(100, 100), key='-CANVAS_3-'),
                    sg.Canvas(size=(100, 100), key='-CANVAS_EN-')
                ]   ]
        layout = [            
                    # 下部カラム
                    [sg.Column(col1),sg.Column(col2),sg.Column(col3)]
                ]
    # Window設定  
        self.window = sg.Window(
                    '認識', # タイトルバーのタイトル
                    layout, # 採用するレイアウトの変数
                    finalize=True,
                    auto_size_text=True,
                    location=(0, 0),
                    # no_titlebar=True, # タイトルバー無しにしたい時はコメントアウトを解除
                    )
        # self.window.Maximize()   # フルスクリーン化したい時にはコメントアウトを解除
    
        # m_box_1 = self.window['-M_BOX_1-']   # 左下左メッセージボックス
        # m_box_2 = self.window['-M_BOX_2-']   # 左下右メッセージボックス
        canvas_4 = self.window['-CANVAS_EN-'].TKCanvas
    
    # 円グラフ
        self._data = [1, 1]
        fig = Figure(figsize=(1.5,1.5)) # create a figure object
        fig.patch.set_facecolor('C9')  # 図全体の背景色
        self._ax = fig.add_subplot(111) # add an Axes to the figure
        self._ax.xaxis.set_visible(False)
        self._ax.yaxis.set_visible(False)
        # ax.pie(data, labels=label,shadow=True,)
        # ax.patch.set_facecolor('green')  # subplotの背景色
        # figとCanvasを関連付ける
        self._fig_agg_4 = draw_figure(canvas_4, fig)

        # ------------------------------------------------------
        # プロット設定
        #-------------------
        #------------------------------------

        # matplotlibスタイル（'dark_background'）
        plt.style.use('dark_background') 
        # ------------------------------------------------------
        # 描画設定
        #-------------------------------------------------------
        sg.theme('Dark Teal8')   # GUIテーマの変更
        self._window()

    def pct_abs(self,pct, raw_data):
            absolute = int(np.sum(raw_data)*(pct/100.))
            return '{:d}\n({:.0f}%)'.format(absolute, pct) if pct > 5 else ''

    def _window(self):
        print("window")
        #別ファイルの GCP STT の呼び出し
        ttsMIC = stt.Listen_print(2,"MIC")
        ttsMIKISER = stt.Listen_print(1,"MIKISER")
        while True:
            # print("window")
            event, values = self.window.read(timeout=10)
            self._ax.cla()#描画のクリア
            self._ax.pie(
            self._data, 
            # labels=self.labels, 
            counterclock=False, 
            startangle=90, 
            autopct=lambda p: self.pct_abs(p, self._data), 
            pctdistance=0.9,
            textprops={'color': 'white', 'weight':'bold'}
            # labeldistance=None
            )
            # self._ax.Circle((0,0),0.4,color='white', fc='white',linewidth=1.25)
            # center_circle = plt.Circle((0,0),0.4,color='white', fc='white',linewidth=1.25) #中心(0,0)に40%の大きさで円を描画
            # fig = plt.gcf()
            # fig.gca().add_artist(center_circle)
            # self._ax.add_artist(center_circle)
            self._ax.pie([100],colors="C4", radius=0.5)
            self._fig_agg_4.draw()
            
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Start':
                # 両マイクで認識を開始させる
                print("Start1")
                threading.Thread(target=ttsMIC.start_recognize, daemon=True).start()
                time.sleep(3)#これを入れないとWindowがクラッシュする
                print("Start2")
                threading.Thread(target=ttsMIKISER.start_recognize, daemon=True).start()      
            elif event == 'Alarm':
                message = values[event]
                sg.popup_auto_close(message)
            else:# それぞれの認識時の状態（待機か認識結果出力後か）を判断し，認識結果出力後であればテキストエディタに情報を追加する
                if(ttsMIC.get_condition()):
                    self.window['-M_BOX_2-'].print(ttsMIC.get_deviceName()+":"+ttsMIC.get_date()+ "\r"+ttsMIC.get_result(), text_color='red')
                    # self.window['-M_BOX_2-'].print("MIC:"+ttsMIC.get_result(), text_color='green')
                    ttsMIC.set_condition() #待機状態に戻す
                    # 認識をはじめる
                    threading.Thread(target=ttsMIC.start_recognize, daemon=True).start()
                    self._data[1]=self._data[1]+ttsMIC.get_chrCount()
                if(ttsMIKISER.get_condition()):
                    self.window['-M_BOX_2-'].print(ttsMIKISER.get_deviceName()+":"+ttsMIKISER.get_date()+ "\r"+ttsMIKISER.get_result(), text_color='green')
                    ttsMIKISER.set_condition() #待機状態に戻す
                    # 認識をはじめる
                    threading.Thread(target=ttsMIKISER.start_recognize, daemon=True).start()
                    self._data[0]=self._data[1]+ttsMIKISER.get_chrCount()                
                # self.window['-M_BOX_2-'].update("aasa")
                self.window['-M_BOX_1-'].update(ttsMIKISER.get_deviceName()+":"+str(ttsMIKISER.get_chrCount()) +"\r"+ttsMIKISER.get_progress_result(),text_color='white')
                self.window['-M_BOX_1-2'].update(ttsMIC.get_deviceName()+":"+str(ttsMIC.get_chrCount())+"\r"+ttsMIC.get_progress_result(),text_color='white')
                # self.window['-M_BOX_2-'].Widget.clipboard_clear()
                # self.window['-M_BOX_2-'].print(ttsMIK.get_progress_result(), text_color='green')          
                # continue
            if event in ('Exit', None):
                exit(69)
        
        self.window.close()# ウィンドウの破棄と終了

if __name__ == '__main__':
    win = Draw_window()
    win.window()
