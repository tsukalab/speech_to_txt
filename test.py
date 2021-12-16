import speech_to_text_sample_toSaveAudio as stt
import threading

class Tts_Result(object):
    def __init__(self,devicename, deviceindex):
        self._DEVICE_INDEX =  deviceindex
        self._RETURN_VALUE = "aiu"
        self._date = "" 
        self.tts_FLAG = False

    # def get_tts_result(self,devicename, deviceindex):
    def get_tts_result(self):
        while True:
            print("Start recognize")
            text = stt.Listen_print(self._DEVICE_INDEX)
            text.main()
            tt = str(text.get_return_value())
            time = str(text.get_date())
            print(tt)
            self._RETURN_VALUE= time+tt
            self.tts_FLAG = True
            # if(devicename=="MIC"):
                # MIC_RESULT = time+tt 
                # MIC_FLAG = True
            # return MIC_RESULT
            # win.close_window()
            # win.add_result(MIC_RESULT)
            
    def get_result(self):
        return self._RETURN_VALUE

    def get_FLAG(self):
        return self.tts_FLAG
    
    def set_FLAG(self):
        self.tts_FLAG = False

    # return tt
    # window['-M_BOX_2-'].print(time+":"+tt, text_color='green')

if __name__ == '__main__':
    ttss = Tts_Result("MIC",2)
    ttss2 = Tts_Result("MIk",1)
    ttss.get_tts_result()
    # while True:
    # t2 = threading.Thread(target=ttss.get_tts_result)
    # t3 = threading.Thread(target=ttss2.get_tts_result)
    # # t2 = threading.Thread(Threadtarget=get_tts_result, args=("MIC",2,win))
    # # t3 = threading.(target=get_tts_result, args=("Mik",1,win))
    # t2.setDaemon(True)
    # t3.setDaemon(True)
    # t2.start()
    # t3.start()
    # t2.join()
    # t3.join() 