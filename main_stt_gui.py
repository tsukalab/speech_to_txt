# https://www.odndo.com/posts/1627006679066/
import threading
import tkinter as tk
from tkinter.constants import FALSE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patch
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import datetime

import PySimpleGUI as sg

import speech_to_text_sample_toSaveAudio as stt
import mecab_txt as mcb

# 一階層上にLOGを保存
LOG_DIRECTORY = "../LOG_GUI/"
MIC_INDEX = 2
MIXER_INDEX = 1

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

# 図（円グラフ用）の描画関数
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
                    [sg.Button('Stop', size=(10,2))],
                    [sg.Button('Select Save', size=(10,2))],
                    [sg.Button('Load', size=(10,2))]
                ]
        col2 =  [   [
                    # 認識結果リアルタイム表示用のテキストボックス
                    # sg.T(size=(50,10), key='-M_BOX_1-', background_color='black')
                    sg.Multiline(size=(55,10), key='-M_BOX_1-',background_color='black',autoscroll=True)
                    ],
                    [sg.T(size=(50,4), key='-M_BOX_1-2', background_color='black')]
                ]   
        col3 =  [   [
                    # 確定認識結ログ果表示用のテキストボックス
                    sg.Multiline(size=(65,14), key='-M_BOX_2-',autoscroll=True, background_color="#00ced1"),
                    # sg.Canvas(size=(100, 100), key='-CANVAS_3-'),
                    sg.Canvas(size=(100, 100), key='-CANVAS_EN-')
                ]   ]
        layout = [            
                    # 下部カラム
                    [sg.Column(col1),sg.Column(col2),sg.Column(col3),sg.Multiline(size=(20,14), key='-M_BOX_3-',autoscroll=True),]
                    # 時系列折れ線グラフ
                    ,[sg.Canvas(size=(100, 100), key='-CANVAS_GR-'),]
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
        canvas_5 = self.window['-CANVAS_GR-'].TKCanvas
    # 折れ線グラフの設定
        self._xs = [0]
        self._ys = [0]
        self._y2s = [0]
        fig = Figure(figsize=(10,1.5)) # create a figure object
        fig.patch.set_facecolor('C9')  # 図全体の背景色
        self._ax5 = fig.add_subplot(111) # add an Axes to the figure
        self._ax5.xaxis.set_visible(False)
        self._ax5.yaxis.set_visible(False)
        self._ax5.set_facecolor('#00ced1')#グラフの背景色
        # figとCanvasを関連付け
        self._fig_agg_5 = draw_figure(canvas_5, fig) 

    # 円グラフの設定
        self._data = [1, 1]
        fig = Figure(figsize=(1.5,1.5)) # create a figure object
        fig.patch.set_facecolor('C9')  # 図全体の背景色
        self._ax = fig.add_subplot(111) # add an Axes to the figure
        # self._ax.xaxis.set_visible(False)
        # self._ax.yaxis.set_visible(False)
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
    # 図（円グラフ用）の描画関数
    def pct_abs(self,pct, raw_data):
            absolute = int(np.sum(raw_data)*(pct/100.))
            return '{:d}\n({:.0f}%)'.format(absolute, pct) if pct > 5 else ''

    def _window(self):
        
        print("window")
        #別ファイルの GCP Speech to Text を実行する関数の呼び出し

        ttsMIC = stt.Listen_print(MIC_INDEX,"MIC", 1)
        ttsMIXER = stt.Listen_print(MIXER_INDEX,"MIXER",0)
        # self._ax5.set_xlim(0, 100)
        while True:
            event, values = self.window.read(timeout=10)

        # 折れ線グラフ
            self._ax5.cla()  # Axes をクリアする。            
            self._ax5.set_ylim(-10, 110)
            self._ax5.plot(self._xs, self._ys, color = "#fafad2",lw=1.5)
            self._ax5.plot(self._xs, self._y2s, color = "darkcyan", linestyle = "-",lw=1.5)
            self._fig_agg_5.draw()  # 描画する。
        
        # 円グラフ
            # print("window")
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
            self._ax.pie([100],colors="C4", radius=0.5)
            self._fig_agg_4.draw()
            
        # 折れ線グラフに発話数のデータを追加する関数
            def append_graph_data(mic = 0, MIXER = 0):
                if mic!=0 or MIXER != 0:
                    self._xs.append(self._xs[len(self._xs)-1] + 0.5)
                    xlim,x2lim = self._ax5.get_xlim()
                    #リアルタイムでデータが増える度に，グラフの描画も追従するようにx軸の描画範囲を移動させる
                    xlim+=0.5
                    x2lim+=0.5
                    self._ax5.set_xlim(xlim, x2lim)
                    if self._ys:
                        # self._ys.append(mic/(mic+MIXER)*100) # 発話の割合を描画する際のデータ追加方法
                        # self._y2s.append(MIXER/(mic+MIXER)*100) # 発話の割合を描画する際のデータ追加方法
                        self._ys.append(mic)  # 発話数を描画するデータ追加方法
                        self._y2s.append(MIXER)  # 発話数を描画するデータ追加方法
                    else:
                        self._ys.append(0)  # 初期値

        # 右側のテキストボックスにログに表示する際，テキストを形態素->名詞・動詞テキストカラーを変えてログ表示（読みづらい）
            def change_text_color(ttsObject):
                mcbtxt = mcb.mecab_t(ttsObject.get_result())
                self.window['-M_BOX_2-'].print(ttsObject.get_deviceName()+":"+ttsObject.get_date())
                for key,result in mcbtxt:
                    if(key=="名詞"):
                        self.window['-M_BOX_2-'].print(result,text_color='red',end='')
                    elif(key=="動詞"):
                        self.window['-M_BOX_2-'].print(result,text_color='green',end='')
                    else:
                        self.window['-M_BOX_2-'].print(result,text_color='black',end='')
                self.window['-M_BOX_2-'].print("\r")
        #イベント設定
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Start':# スタートボタンを押したら
                # 両マイクで認識をスレッドで開始させる
                print("Start1")
                t1 = threading.Thread(target=ttsMIC.start_recognize, daemon=True)
                t1.start()
                time.sleep(5)#これを入れないとpysimpleGUIのWindowがクラッシュする
                print("Start2")
                t2 = threading.Thread(target=ttsMIXER.start_recognize, daemon=True)
                t2.start()
                ttsMIC.set_progress_result("【何か話してください】")
                ttsMIXER.set_progress_result("【何か話してください】")
            elif event == 'Alarm':
                message = values[event]
                sg.popup_auto_close(message)
            elif event == 'Stop':
                # テキスト形式でログの保存（使っていない）
                log_chat = self.window['-M_BOX_2-'].get()
                f = open(LOG_DIRECTORY+ttsMIC.get_date()+'log_chat.txt', 'w')
                f.write(log_chat)
                f.close()
                # 両マイクで認識をスレッドで終了させる（未実装）
                # t1.sleep()
                # t2.sleep()
            elif event == 'Select Save':
                # 右側のテキストボックスから任意の文字列をクリック＆ドラックで選択した状態で->Select Saveボタンを押すと，最も右のテキストボックスにログとして表示
                now = datetime.datetime.now()
                try:
                # Tkinterの場合 .TKText 経由でアクセス
                    selected = self.window["-M_BOX_2-"].TKText.selection_get()
                    # now.strftime('%Y-%m-%d-%H.%M.%S')
                    self.window['-M_BOX_3-'].print(now.strftime('%H.%M')+selected, text_color='k')
                    print(selected)
                    # SAVE LOGの保存（簡易）
                    log_chat = self.window['-M_BOX_3-'].get()
                    # f = open(LOG_DIRECTORY+ttsMIC.get_date()[:10]+'Select_log_chat.txt', 'w')
                    f = open(LOG_DIRECTORY+now.strftime('%m-%d')+'Select_log_chat.txt', 'w')
                    f.write(log_chat)
                    f.close()
                except tk._tkinter.TclError:
                    sg.popup('テキストが選択されていません')
                    # pass # 選択範囲がない場合のエラーを無視
                
            elif event == 'Load':
                text = sg.popup_get_file('ファイルを指定してください。')
                # sg.popup('結果', '選択されたファイルは、以下です。', text)
                # file = open(LOG_DIRECTORY+"log.csv", 'r')
                print()
                try:
                    file = open(text, 'r')
                    data = csv.reader(file)
                    load_txt = ""
                    for row in data:
                        if int(row[6]) ==0:#MIXER
                            "MIXSER"+ row[2][:-4]
                            # load_txt += "MIXSER: "+row[2][:19]+'\n'+row[3]
                            self.window['-M_BOX_2-'].print( "MIXSER: "+row[2][:19]+'\n'+row[3], text_color='#008080')
                        else:
                            load_txt +="MIC: "+row[2][:19]+'\n'+row[3]
                            self.window['-M_BOX_2-'].print("MIC: "+row[2][:19]+'\n'+row[3], text_color='#fafad2')

                        load_txt+='\n'
        
                    file.close()
                except:
                    sg.popup('指定されたファイルはありません', text)
                    # print("ad")


            else:# それぞれの認識時の状態（待機か認識結果出力後か）を判断し，認識結果確定後であれば右側のテキストボックスに情報を追加する
                append_graph_data(int(ttsMIC.get_monoChrCount()), int(ttsMIXER.get_monoChrCount()))
                
                def display_result_on_textbox(ttsObject, text_color):
                    if(ttsObject.get_result()!="【スタートボタンを押すと認識がはじまります】"):
                        ttsObject.set_progress_result("【何か話してください】")
                        if(ttsObject.get_result()!="【何か話してください】"):
                            self.window['-M_BOX_2-'].print(ttsObject.get_deviceName_or_number(0)+":"+ttsObject.get_date()+ "\r"+ttsObject.get_result(), text_color=text_color)
                    # change_text_color(ttsMIC)
                    ttsObject.set_condition() #待機状態に戻す
                    audiofilename = ttsObject.get_date()+".wav"; result = [ttsObject.get_result()]; num = ttsObject.get_chrCount();filename = LOG_DIRECTORY+datetime.datetime.now().strftime('%Y-%m-%d')+'log.csv'
                    # 再度認識スレッドを立てる
                    threading.Thread(target=ttsObject.start_recognize, daemon=True).start()
                    self._data[ttsObject.get_deviceName_or_number(1)]=self._data[ttsObject.get_deviceName_or_number(1)]+ttsObject.get_chrCount()
                    
                    # LOGの保存（CSV）
                    addwriteCsvTwoContents(audiofilename,  result, num, filename, ttsObject.get_deviceName_or_number(1))
                
                if(ttsMIC.get_condition()):
                    display_result_on_textbox(ttsMIC,'#fafad2')            
                if(ttsMIXER.get_condition()):
                    display_result_on_textbox(ttsMIXER,'#008080') 
                # 左黒色のテキストボックスに，リアルタイムの認識結果を表示させる
                self.window['-M_BOX_1-'].update(ttsMIXER.get_deviceName_or_number(0)+":"+str(ttsMIXER.get_chrCount()) +"\r"+ttsMIXER.get_progress_result(),text_color='white')
                self.window['-M_BOX_1-2'].update(ttsMIC.get_deviceName_or_number(0)+":"+str(ttsMIC.get_chrCount())+"\r"+ttsMIC.get_progress_result(),text_color='white')
            
            if event in ('Exit', None):
                log_chat = self.window['-M_BOX_2-'].get()
                f = open(LOG_DIRECTORY+ttsMIC.get_date()+'log_chat.txt', 'w')
                f.write(log_chat)
                f.close()
                # t1.sleeo()
                # t2.sleep()
                exit(69)
        
        self.window.close()# ウィンドウの破棄と終了

if __name__ == '__main__':
    win = Draw_window()
    win.window()
