from __future__ import division
import datetime

import re
import sys

from google.cloud import speech_v1 as speech

import pyaudio
import queue
import wave
from pykakasi import kakasi

# Bfolder = "F:/wavtomo/wav_Befor_Recognize/"
# Afloder = "F:/wavtomo/wav_After_Recognize/"

# 一階層上にオーディオを保存
AUDIO_DIRECTORY = "../Audio_GUI/"
DEVICE_INDEX  = 2

# 使用可能なデバイスインデックスがプリントする方法
# line180e前後の stream._print_deviceList() のコメントアウトを外す
# 自身の実行環境で以下のインデックス番号を変更すると良い(デフォルトは1)
# おそらくだが「既定のマイク」->　DEVICE_INDEX = 1
# 「既定の通信マイク」->　DEVICE_INDEX = 2
# DEVICE_INDEX = 2

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
# pyAudiosample
FORMAT = pyaudio.paInt16
kakasi = kakasi()

class _MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk, device_index):
        self._rate = rate 
        self._chunk = chunk
        self._DEVICE_INDEX  = device_index
        self._WAVE_OUTPUT_FILENAME = AUDIO_DIRECTORY+"output.wav"

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        # Save Audio Buff
        self._frames = []

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        # 接続されたデバイスの表示
        for x in range(0, self._audio_interface.get_device_count()):
            if x==self._DEVICE_INDEX:
                print("接続デバイス【index"+str(x)+":"+self._audio_interface.get_device_info_by_index(x).get("name")+"】")
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # デバイスのマイク設定する
            input_device_index=self._DEVICE_INDEX,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        print("Start Save Audio: "+self._WAVE_OUTPUT_FILENAME)
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

        # save wav failes
        # """
        wf = wave.open(self._WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self._audio_interface.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        # """
        print("End Save Audio")

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
                    # Add Audio file
                    self._frames.append(chunk)
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
    
    def _set_audio_file_path(self, file_name):
        self._WAVE_OUTPUT_FILENAME = file_name

    def clear_audio_file(self):
        # 発話前の無音部分をカットしておく
        if(len(self._frames)-7>0):
            del self._frames[:len(self._frames)-7]
        else:
            self._frames.clear()
        
    def print_connected_deviceList(self):# 音声デバイスを一覧表示する
        audio = pyaudio.PyAudio()
        print("【オーディオデバイス一覧】")
        for x in range(0, audio.get_device_count()):
            print("index"+str(x)+":"+audio.get_device_info_by_index(x).get("name"))

class Listen_print(object):
    def __init__(self, deviceindex, deviceNAME, deviceNumber):
        self._DEVICE_INDEX =  deviceindex
        self._DEVICENAME_AND_NUMBER = (deviceNAME, deviceNumber)
        self._return_result = "【スタートボタンを押すと認識がはじまります】"
        self._date = "00/00/00"
        self._progress_result = "【スタートボタンを押すと認識がはじまります】"
        self.condition = False
        self._chrCount = 0
        self._monoChrCount = 0

    def start_recognize(self):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        # 認識の言語は日本語に変更している
        language_code = "ja-JP" # a BCP-47 language tag

        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        _streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        now = datetime.datetime.now()
        AUDIO_FILE_NAME = now.strftime('%Y-%m-%d-%H.%M.%S')+self._DEVICENAME_AND_NUMBER[0]+".wav"

        with _MicrophoneStream(RATE, CHUNK, self._DEVICE_INDEX) as stream:
            count = 0
            num_chars_printed = 0
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            print("【何か話してください】")
            try:
                responses = client.streaming_recognize(config=_streaming_config, requests=requests)

                for response in responses:
                                            
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
                    # print("overwrite_chars"+overwrite_chars)

                    if not result.is_final:                                               
                        # print("transcript" + transcript)
                        sys.stdout.write(transcript + overwrite_chars + "\r")
                        sys.stdout.flush()
                        if(count==0): # 発話開始時のみ実行する
                            stream.clear_audio_file()   
                            now = datetime.datetime.now()
                            AUDIO_FILE_NAME = now.strftime('%Y-%m-%d-%H.%M.%S')+self._DEVICENAME_AND_NUMBER[0]+".wav"
                            self._date = now.strftime('%Y-%m-%d-%H.%M.%S')
                            # AUDIO_FILE_PATH = Bfolder+AUDIO_FILE_NAME
                            AUDIO_FILE_PATH = AUDIO_DIRECTORY+AUDIO_FILE_NAME
                            stream._set_audio_file_path(AUDIO_FILE_PATH)
                            print(AUDIO_FILE_PATH)
                            count+=1
                        
                        num_chars_printed = len(transcript)
                        # txtlist = textwrap.wrap(transcript, int(ww/w))
                        # print(txtlist)
                        self._progress_result = transcript
                        self._monoChrCount = len(transcript)

                    else:
                        # 認識結果が確定したら
                        print("確定認識結果："+transcript + overwrite_chars)
                        self._return_result = transcript + overwrite_chars
                        self._progress_result = transcript + overwrite_chars
                        kakasi.setMode('J', 'H') #漢字からひらがなに変換
                        # kaka.setMode("K", "H") #カタカナからひらがなに変換
                        conv = kakasi.getConverter()
                        self._chrCount += len(conv.do(transcript))
                        # 認識文字数を保存
                        self._monoChrCount = len(conv.do(transcript))
                        
                        break
                        if re.search(r"\b(exit|quit)\b", transcript, re.I):
                            print("Exiting..")
                            break

                        num_chars_printed = 0        
            except BaseException as e:
                print("Exception occurred - {}".format(str(e)))
                AUDIO_FILE_PATH = AUDIO_DIRECTORY+AUDIO_FILE_NAME
                stream._set_audio_file_path(AUDIO_FILE_PATH)
                self._return_result = "【sst内に問題が発生しました】"
                self._progress_result = "【sst内に問題が発生しました】"

        self.condition = True

    def get_result(self):# 認識確定した文字起こしデータ
        return self._return_result
    def get_progress_result(self):# リアルタイムに認識されている文字起こしデータ
        return self._progress_result 
    def set_progress_result(self, contents):# リアルタイムに認識されている文字起こしデータ
        self._progress_result = contents
    def get_date(self):
        return self._date
    def get_condition(self):
        return self.condition
    def set_condition(self):
        self.condition = False
        self._monoChrCount = 0
    def get_deviceName_or_number(self,int):#デバイスの名前の取り出し：MIC or MIXER
        return self._DEVICENAME_AND_NUMBER[int]
    def get_chrCount(self):#円グラフ用：総発話文字数の取り出し用
        return self._chrCount
    def get_monoChrCount(self):#棒グラフ用：都度発話数の取り出し用
        return self._monoChrCount
if __name__ == "__main__":
    # Listen_print()は 以下のどちらかを使用
        # deviceNAMEが"mixer"ならdeviceNumber = 0
        # deviceNAMEが"mic"ならdeviceNumber = 1
    # deviceindex=1
    # 使用可能なデバイスの表示するには以下2行のコメントアウトを消す
    b=_MicrophoneStream(RATE, CHUNK, device_index = DEVICE_INDEX)
    b.print_connected_deviceList()
    a = Listen_print(deviceindex = DEVICE_INDEX , deviceNAME = "deviceNAME", deviceNumber = 0)
    a.start_recognize()
    