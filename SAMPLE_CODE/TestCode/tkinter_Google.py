from __future__ import division
import tkinter 
from tkinter import ttk, messagebox
import threading
import keyboard
import speech_recognition as sr
import csv
import datetime
import textwrap
import wave

import re
import sys
from google.cloud import speech_v1 as speech
import pyaudio
import pyautogui


# from speechRecognitionReferenec import AUDIO_FILE_NAME
rmic = sr.Recognizer()
rmikiser = sr.Recognizer()
mic = sr.Microphone(device_index=2)
mikiser = sr.Microphone(device_index=1)
rmic.dynamic_energy_adjustment_damping = True
rmikiser.dynamic_energy_adjustment_damping = True
Bfolder = "F:/wavtomo/wav_Befor_Recognize/"
Afloder = "F:/wavtomo/wav_After_Recognize/"
csvfile = "tkintertes.csv"
ch = False

# from six.moves import queue
import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
FORMAT = pyaudio.paInt16
NAME_MIKISER = "ステレオ ミキサー (Realtek High Definit"
NAME_MIC = "マイク配列 (Realtek High Definition"

Bfolder = "F:/wavtomo/wav_Befor_Recognize/"
Afloder = "F:/wavtomo/wav_After_Recognize/"
WAVE_OUTPUT_FILENAME = "output.wav"

class MicrophoneStream(object):
    
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk, deviceindex):
        self._rate = rate
        self._chunk = chunk
        self._deviceindex  = deviceindex
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        # Save Audio Buff
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
            # ★デバイスのマイク取得する
            input_device_index=self._deviceindex,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        # print("PyAUDIO STREAM STOP")
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
        # print("PyAUDIO STREAM END")
    
    # save wav failes
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self._audio_interface.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("sudioStreamEnd")
        

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

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
                    self._frames.append(chunk)
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def addwriteCsvTwoContents(AUDIO_FILE_NAME, RList:list, LList:list, openFileName, cut_time = 0 , progressTime = "::"):

    month=AUDIO_FILE_NAME[5:7];day=AUDIO_FILE_NAME[8:10];hh=AUDIO_FILE_NAME[11:13];mm=AUDIO_FILE_NAME[14:16];ss=AUDIO_FILE_NAME[17:19]
    audioNameR=audioNameL=AUDIO_FILE_NAME
    CR0=CL0=CR=CL=""
    CR0Len=CL0Len=0
    file = open(openFileName, 'a', newline="")
    w = csv.writer(file)
    if not RList:
        print("R contents is not Recognize")
    else:
        CR0 = RList[0]
        CR = RList
        if(CR0 != 0):
            CR0Len = int(len(CR0))
    if not LList:
        print("L contents is not Recognize")
    else:
        CL0 = LList[0]
        CL = LList
        if(CL0 != 0):
            CL0Len = int(len(CL0))
        w = w.writerow([month+"/"+day,hh+":"+mm+":"+ss,audioNameR,CR0,CR,CR0Len,audioNameL,CL0,CL,CL0Len, cut_time,"NULL",progressTime])
        file.close()

def on_closing():
    global tflag
    try:
        subf.wm_attributes("-topmost", False)
    except:
        pass
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        tflag = False
        root.quit()
        try:
            subf.destroy()
        except:
            pass
    else:
        try:
            subf.wm_attributes("-topmost", True)
        except:
            pass

def work1(device_name = "MIC",device_index = 0):
    
    mikiserCount = 1
    micCount = 1
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "ja-JP"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
      
    with MicrophoneStream(RATE, CHUNK, device_index) as stream:
        now = datetime.datetime.now()
        AUDIO_FILE_NAME = now.strftime('%Y-%m-%d-%H.%M.%S')+".wav"
        AUDIO_FILE_PATH = Bfolder+AUDIO_FILE_NAME
        audio_generator = stream.generator()
            # f.write(audio_generator)
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        ) 
    
        responses = client.streaming_recognize(streaming_config, requests)
        
        num_chars_printed = 0
        for response in responses:
            nowt = now.strftime('%Y.%m.%d-%H.%M.%S')
            # print(nowt)
            mikx  = mikiserCount/(micCount+mikiserCount)
            micx  = micCount/(micCount+mikiserCount)
            # print(1000*mikx,micCount/1000*micx)    
            if not response.results:
                continue
            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript
            overwrite_chars = " " * (num_chars_printed - len(transcript))
            # print("transcript"+transcript )
            # print("overwrite_chars"+ overwrite_chars)

            if not result.is_final:
                # with open(AUDIO_FILE_PATH, "wb") as f:
                #   f.write(audio_generator)
                num_chars_printed = len(transcript)
                txtlist = transcript
                # txtlist = textwrap.wrap(transcript, int(ww/w))
                print(txtlist)
                if(device_name=="MIC"):         
                    var2.set(txtlist)
                    lis = [txtlist,0]
                    # addwriteCsvTwoContents(AUDIO_FILE_NAME = "null", RList = lis, LList = lis, openFileName = "mik.csv", cut_time = 0 , progressTime = mikx)
                    micCount = micCount+1
                else:
                    var.set(txtlist) 
                    lis = [txtlist,0]
                    # addwriteCsvTwoContents(AUDIO_FILE_NAME = "null", RList = lis, LList = lis, openFileName = "mic.csv", cut_time = 0 , progressTime =  micx)
                    mikiserCount = mikiserCount+1 
            else:
                print("end ddd"+nowt)
                print( transcript + overwrite_chars)
                break


                    
            #     setxt = ""
            #     if(len(txtlist) <= num_comment):
            #         for i in range(len(txtlist)):
            #             setxt += txtlist[i]
            #         if(device_name=="MIC"):
            #             var2.set(setxt)
            #         else:
            #             var.set(setxt)
                            
            #     else:
            #         for i in range(num_comment):
            #             setxt += txtlist[len(txtlist)-num_comment+i]
            #         if(device_name=="MIC"):
            #             var2.set(setxt)
            #         else:
            #             var.set(setxt)          

            # else:
            #     # Exit recognition if any of the transcribed phrases could be
            #     # one of our keywords.
            #     if re.search(r'\b(exit|quit)\b', transcript, re.I):
            #         on_closing()
                        
        # with open(AUDIO_FILE_PATH, "wb") as f:
        # for content in audio_generator:
        #     print("content"+ content)
        #     with open(AUDIO_FILE_PATH, "wb") as f:
        #         f.write(content)

        # Now, put the transcription responses to use.
        # listen_print_loop(responses)

def btn_clicked():
    # ch = True
    # subf.destroy()
    root.wm_attributes("-topmost", True)
    # 背景を透過させる
    root.wm_attributes("-transparentcolor", "snow")
    root.attributes("-alpha",0.5)
    root.attributes("-fullscreen", True)
    print("【使用可能なマイクのリスト】");print("index:name")
    device_INDEX_MIKISER = 0
    device_INDEX_MIC = 2
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        # print(str(i)+":"+microphone_name)
        if NAME_MIC == microphone_name:
            device_INDEX_MIC = i
            # print("MIC" + str(device_INDEX_MIC))
        if NAME_MIKISER == microphone_name:
            device_INDEX_MIKISER = i
            # print("MIKISER" + str(device_INDEX_MIKISER))

    t1 = threading.Thread(target=work1,args=("MIC", int(device_INDEX_MIC)))
    t2 = threading.Thread(target=work1,args=("MIKISER", int(device_INDEX_MIKISER)))
    t2 = threading.Thread(target=work1,args=("MIKISER", int(device_INDEX_MIKISER)))   
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    if(ch):
        t1.join()
        t2.join()   

if __name__ == '__main__':
    fontsize = 15
    fontcolour = "black"
    num_comment = 3
    alpha = 50
    tflag = True
    bold = "bold"
    root = tkinter.Tk()
    ww = root.winfo_screenwidth()
    wh = root.winfo_screenheight()
    # print(ww/2)

    #root.wm_attributes("-topmost", True)
    ttk.Style().configure("TP.TFrame", background="snow")
    root.title("TranScriptoWindow")
    root.protocol("WM_DELETE_WINDOW", "bbbbbbbbbbbbbbbbbbbbbbb")
    f = ttk.Frame(master=root, style="TP.TFrame", width=ww, height=wh)
    f.pack()
    
    var = tkinter.StringVar()
    tmp = "ミキサー"
    var.set(tmp)
    labelmic = ttk.Label(root, width=100, background="red")
    labelmikiser =  ttk.Label(root, width=100, background="blue")
            #         #   tkinter.Label(root,text="label",width=10,height=5)
    label = ttk.Label(root, textvariable=var,
                      wraplength=ww, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="white")
    # ★
    var2 = tkinter.StringVar()
    tmp2 = "装着者マイク"
    var2.set(tmp2)
    label2 = ttk.Label(root, textvariable=var2,
                      wraplength=ww+20, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="red")
    root.attributes("-alpha",0.5)

    # label = ttk.Label(root, textvariable=var,
                    #   wraplength=ww, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="snow")                  
    w = label.winfo_reqwidth()/len(tmp)
    h = label.winfo_reqheight()
    
    # ★
    label.place(x=0, y=(wh-num_comment*h-alpha))  # -αは下のタスクバーの分
    label2.place(x=0+label.winfo_reqwidth(), y=(wh-num_comment*h-alpha)-100)
    # labelmic.place(x=0, y=100) 
    # labelmikiser.place(x=0+labelmic.winfo_reqwidth(), y=100)  # -αは下のタスクバーの分

    subf = tkinter.Tk()
    subf.protocol("WM_DELETE_WINDOW", "aaaaaaaaaaaaaaaaaaaaaaaaaaa")
    subf.wm_attributes("-topmost", True)
    subf.geometry("300x300+"+str(int(ww/2-300/2))+"+"+str(int(wh/2-300/2)))
    subf.title("Settings")

    lnumcomment = ttk.Label(subf, text="Number of comments",
                            wraplength=ww)
    lnumcomment.pack()
    txt1 = tkinter.Entry(subf, width=20)
    txt1.insert(tkinter.END, num_comment)
    txt1.pack()

    lfontsize = ttk.Label(subf, text="Fontsize",
                          wraplength=ww)
    lfontsize.pack()
    txt2 = tkinter.Entry(subf, width=20)
    txt2.insert(tkinter.END, fontsize)
    txt2.pack()

    lfontcolour = ttk.Label(subf, text="Font colour",
                            wraplength=ww)
    lfontcolour.pack()
    txt3 = tkinter.Entry(subf, width=20)
    txt3.insert(tkinter.END, fontcolour)
    txt3.pack()

    lalpha = ttk.Label(subf, text="y-axis correction(If positive,display above)",
                       wraplength=ww)
    lalpha.pack()
    txt4 = tkinter.Entry(subf, width=20)
    txt4.insert(tkinter.END, alpha)
    txt4.pack()

    bl1 = tkinter.BooleanVar(subf)
    bl1.set(True)
    CheckBox1 = tkinter.Checkbutton(
        subf, text="Bold", variable=bl1)
    CheckBox1.pack()

    
    
    def apply():
        ch = True
        global label,label2, w, h, num_comment, alpha
        label.place_forget()
        num_comment = int(txt1.get())
        fontsize = int(txt2.get())
        fontcolour = txt3.get()
        alpha = float(txt4.get())
        if(bl1.get()):
            bold = "bold"
        else:
            bold = "normal"
        if(fontcolour == "snow"):
            fontcolour = "white"
        # label = ttk.Label(root, textvariable=var,
                        #   wraplength=ww, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="white")
        w = label.winfo_reqwidth()/(len(tmp))
        h = label.winfo_reqheight()
        label.place(x=0, y=(wh-num_comment*h-alpha))
        #★bel2
        label2.place(x=0+label.winfo_reqwidth(), y=(wh-num_comment*h-alpha)-100) 
    btn = ttk.Button(subf, text="Start", command=btn_clicked)
    btn.pack(side="right")
    applybtn = ttk.Button(subf, text="Apply", command=apply)
    applybtn.pack(side="right")
    root.mainloop()
    # ch = True
    # work1("MIC", int(2))
    # work1("MIKISER", int(1))
