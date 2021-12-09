from __future__ import division

import re
import sys

from google.cloud import speech_v1 as speech

import pyaudio
import queue
import wave
import numpy as np

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
# 実行するとデバイスインデックスがプリントされるので，
# 自身の実行環境で以下のインデックス番号を変更すると良い(デフォルトは1)
# おそらくだが「既定のマイク」->　DEVICE_INDEX = 1
# 「既定の通信マイク」->　DEVICE_INDEX = 2
DEVICE_INDEX = 2

# pyAudiosample
FORMAT = pyaudio.paInt16
WAVE_OUTPUT_FILENAME = "./speech_to_txt/text_output.wav"


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

    # MicrofoneStreamが終わる時
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
                    # ★To Save Audio
                    self._frames.append(chunk)
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                   
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
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        print("0")
        if not response.results:
            print("1 "+ response)
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            print("2 "+ response)
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            print("3" + transcript)
            # print("3 "+ str(response))
            # sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
            # return True

        else:
            # 認識が一旦終わる（改行がかかるとここに来る）
            print("transcript + overwrite_chars "+ transcript + overwrite_chars)
            # break

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            return False
            break
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0
        print("listen_print_loop end")

def main():
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

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK, DEVICE_INDEX) as stream:
        stream.print_deviceList()
        audio_generator = stream.generator()
        # stream.save_audio()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        print("【何か話してください】")
        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        flag = listen_print_loop(responses)
        if(flag):
            print("end Recogniaze")
            # break

if __name__ == "__main__":
    main()
    