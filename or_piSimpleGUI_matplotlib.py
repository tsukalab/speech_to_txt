# https://www.odndo.com/posts/1627006679066/
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patch
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg

import re
import sys
from google.cloud import speech_v1 as speech
import pyaudio
import queue
import wave

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
DEVICE_INDEX = 1
# pyAudiosample
FORMAT = pyaudio.paInt16
WAVE_OUTPUT_FILENAME = "./speech_to_text/text_output.wav"

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk, device_index):
        self._rate = rate 
        self._chunk = chunk
        self._deviceindex  = device_index

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        self._frames = []

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # デバイスのマイク設定する
            input_device_index=self._deviceindex,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
        # save wav failes
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self._audio_interface.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue
    
    def save_audio(self):
        print("save0")
        while True:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    # ★
                    self._frames.append(data)
                    if chunk is None:
                        print("saveNone")
                        return
                except queue.Empty:
                    break

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    # ★
                    self._frames.append(data)
                    print("aa")
                except queue.Empty:
                    break

            yield b"".join(data)
     
    # 音声デバイスを一覧表示する
    def print_deviceList(self):
        audio = pyaudio.PyAudio()
        print("【オーディオデバイス一覧】")
        for x in range(0, audio.get_device_count()): 
            print("index"+str(x)+":"+audio.get_device_info_by_index(x).get("name"))

def listen_print_loop(responses):
    # サーバーのレスポンスを繰り返し処理し、それらをプリントします。
    # 渡されたレスポンスは、サーバーからレスポンスが提供されるまでブロックする
    # ジェネレーターです。がサーバーから提供されるまでブロックします。
    # 
    # 各レスポンスには複数の結果が含まれ、各結果には複数の選択肢が含まれます。
    # 詳細は、https://goo.gl/tjCPAU を参照してください。
    # ここでは、一番上の結果の一番上の選択肢の転写のみを印刷します。
    # 
    # この場合、中間の結果に対してもレスポンスが提供されます。
    # もし レスポンスが暫定的なものであれば，その最後に改行を印字して，
    # 次の結果がそのレスポンスを 次の結果で上書きできるようにするため、
    # 最終的な回答になるまで 最終結果の場合 最終的なものに対しては、改行を印字して最終的な転写を保存します。
    num_chars_printed = 0
    for response in responses:
        print("0")
        if not response.results: #何も認識されなければスルー
            print("1")
            continue
        # results`のリストは連続しています。ストリーミングでは、
        # 最初の結果が検討されることだけを気にします。
        # というのも、それが `is_final` になると、次の発話の検討に移るからです。
        result = response.results[0]
        if not result.alternatives:
            print("2")
            continue
        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        # 中間の結果を表示しますが、行末にキャリッジリターンを付けて、
        # 後続の行がそれらを上書きするようにします。
        # 前の結果が今回の結果よりも長かった場合は、前の結果を上書きするために、
        # いくつかの余分なスペースを表示する必要があります
    
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            print("3")
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            print("result trans")
            print(transcript + overwrite_chars)

            # 転写されたフレーズの中にキーワードになりそうなものがあれば、出口認識を行います。
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break
            num_chars_printed = 0
        print("end")

# 図の描画関数
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def main():
    # カラム設定
    layout = [            
                # 下部カラム
                [
                    sg.T(size=(45,5), key='-M_BOX_1-', background_color='black'),
                    sg.Multiline(size=(45,5), key='-M_BOX_2-'),
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
    fig_1 = Figure(figsize=(2, 2))    
    fig_2 = Figure(figsize=(6, 4)) 
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

    
    # 認識の言語は日本語に変更している
    language_code = "ja-JP" # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK, DEVICE_INDEX) as stream:
        stream.print_deviceList()
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        print("【何か話してください】")
        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)

    # ------------------------------------------------------
    # 描画設定
    #-------------------------------------------------------

    # 描画ループ
    while True:
        
        for i in range(len(dpts)):

            event, values = window.read(timeout=10)
            if event in ('Exit', None):
                exit(69)

            # グラフ描画のクリア
        
            ax_3.cla()

        # ax_1のグリッド描画

            # グラフ1の描画
            # 黄色折れ線グラフのアニメーション
            

            # グラフ2の描画
            
            
            # グラフ3の描画
            # 円-楕円 描画
            ellipse = patch.Ellipse(xy=(0.5, 0.5), width=np.sin(i/3), height=1, fill=False, ec='yellow')
            ax_3.add_patch(ellipse)


            # グラフの描画
        
            fig_agg_3.draw()


            # ------------------------------------------------------
            # メッセージ内容設定
            # ------------------------------------------------------

            # iが各数字の倍数であるときに色を変更しながらメッセージとして表示する
            if i % 5 == 0:
                window['-M_BOX_2-'].print(str(i)+' は 5 の倍数です。', text_color='green')
            if i % 7 == 0:
                window['-M_BOX_2-'].print(str(i)+' は 7 の倍数です。', text_color='black')
            if i % 13 == 0:
                window['-M_BOX_2-'].print(str(i)+' は 13 の倍数です。', text_color='red')

            # message.txtに書かれている内容を表示する
            with open('./matplotlib/message.txt',encoding="utf-8") as message_file: # メッセージボックス入力
                window['-M_BOX_1-'].Update(message_file.read())

    window.close()

    

if __name__ == '__main__':
    main()