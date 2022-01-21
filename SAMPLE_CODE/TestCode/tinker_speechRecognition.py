
import tkinter 
from tkinter import ttk, messagebox
import threading
import keyboard
import speech_recognition as sr
import csv
import datetime

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

def work1(mm = sr.Microphone(),r = sr.Recognizer() ,num = 0):
    while True:
        global var, tflag, label2
        # ii = num
        now = datetime.datetime.now()
        AUDIO_FILE_NAME = now.strftime('%Y-%m-%d-%H.%M.%S')+".wav"
        if(num%2 == 0):
            print("ミキサー")
        else:
            print("マイク")
      
        print("Say something ...")
        with mm as source:          
            r.adjust_for_ambient_noise(source) #雑音対策
            if(num%2 == 0):
                audio = r.listen(source)
            else:
                r.dynamic_energy_adjustment_damping = 0.15
                # r.dynamic_energy_adjustment_ratio = 1.0
                audio = r.listen(source, timeout = 10)
        
        AUDIO_FILE_PATH = Bfolder+AUDIO_FILE_NAME
        
        
        with open(AUDIO_FILE_PATH, "wb") as f:
            f.write(audio.get_wav_data())
        
        try:
            def dictToList(dd):#
                try:
                    dd = contents["alternative"]
                    result = [d["transcript"] for d in dd]
                    # pySerial(flag = "s")
                    return result
                except Exception:
                    return [0]
            contents = r.recognize_google(audio, language='ja-JP', show_all=True)
            contents = dictToList(contents)
            print(contents)
            if(num%2 == 0):
                print ("Now to recognize ミキサー認識")
                tmp = "ミキサー認識"
                print(tmp)
                var.set(contents[0])
                # var2.set("s")
                addwriteCsvTwoContents(AUDIO_FILE_NAME,RList=[""],LList=contents, openFileName="./wtomo/"+csvfile, cut_time = "0")
            else:
                print ("Now to recognize マイク認識")
                tmp = "マイク認識"
                print(tmp)
                var2.set(contents[0])
                addwriteCsvTwoContents(AUDIO_FILE_NAME,RList=contents,LList=[[""]], openFileName="./wtomo/"+csvfile, cut_time = "0")
            
            file = open("tinker.csv", 'a', newline="")
            w = csv.writer(file)
            # w = w.writerow(tmp+','+contents[0])
            file.close()
            label2.place(x=0+label.winfo_reqwidth(), y=(wh-num_comment*h-alpha))#.winfo_reqheight())
    
            # print(result)
            # "ストップ" と言ったら音声認識を止める
            if r.recognize_google(audio, language='ja-JP') == "ストップ" :
                print("end")
                
        # 以下は認識できなかったときに止まらないように。
        except sr.UnknownValueError:
            print("could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
def btn_clicked():
    # subf.destroy()
    root.wm_attributes("-topmost", True)
    # 背景を透過させる
    root.wm_attributes("-transparentcolor", "snow")
    root.attributes("-fullscreen", True)
    
    t1 = threading.Thread(target=work1,args=(mikiser,rmikiser,1))
    # t2 = threading.Thread(target=work1,args=(mic,rmic,1))
    t1.setDaemon(True)
    # t2.setDaemon(True)
    t1.start()
    # t2.start()

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

    #root.wm_attributes("-topmost", True)
    ttk.Style().configure("TP.TFrame", background="snow")
    root.title("TranScriptoWindow")
    root.protocol("WM_DELETE_WINDOW", "bbbbbbbbbbbbbbbbbbbbbbb")
    f = ttk.Frame(master=root, style="TP.TFrame", width=ww, height=wh)
    f.pack()
    
    var = tkinter.StringVar()
    tmp = "ミキサー"
    var.set(tmp)
    label = ttk.Label(root, textvariable=var,
                      wraplength=ww, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="white")
    # ★
    var2 = tkinter.StringVar()
    tmp2 = "装着者マイク"
    var2.set(tmp2)
    label2 = ttk.Label(root, textvariable=var2,
                      wraplength=ww+20, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="red")

    # label = ttk.Label(root, textvariable=var,
                    #   wraplength=ww, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="snow")                  
    w = label.winfo_reqwidth()/len(tmp)
    h = label.winfo_reqheight()
    
    # ★
    label.place(x=0, y=(wh-num_comment*h-alpha))  # -αは下のタスクバーの分
    label2.place(x=0+label.winfo_reqwidth(), y=(wh-num_comment*h-alpha))  # -αは下のタスクバーの分

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
        label = ttk.Label(root, textvariable=var,
                          wraplength=ww, font=("メイリオ", fontsize, bold), foreground=fontcolour, background="white")
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