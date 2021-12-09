import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

# r.energy_threshold = 4000
# マイクの閾値を設定できる（ただ動的に変化するものなのであまり設定する必要はない，周囲の雑音が予想できない時は設定すとよい）
# 基本Falseの設定がよい

r.dynamic_energy_threshold = True
# Type:bool, Defolt:True
# 音の閾値の調整を自動的に行うか設定できる
# 周囲の周辺環境が厳密に設定されているときに有効

r.dynamic_energy_adjustment_damping
# Type:float, Defolt:True, Limit:0~1
# 動的な閾値設定の時有効（余りいじらないほうが良い）
# 低いと調整が速くなる（特定のフレーズを見逃しやすい）

r.pause_threshold = 0.8
# Type:float, Defolt:..., Unit:ss
# フレーズの終わり（無音）の基準　小さいと細切れになる

r.operation_timeout =None
# type: Union[float, None]
# APIのタイムアウトまでの時間を変更できる（秒単位）


#マイクを開いて録音を開始する．以下に認識などの処理をする
with mic as source:    
    """
    # 音を聞いているマイクの状態を表すそうだが，mic.list_working_microphones()がないと言われる
    for device_index in mic.list_working_microphones():
        m = mic(device_index=device_index)
        break
    else:
        print("No working microphones found!")
    """

    r.adjust_for_ambient_noise(source) 
    """
    # r.adjust_for_ambient_noise(source: AudioSource, 
    #                            duration: float = 1)
    #雑音対策 閾値を動的に変化させる
    # durationは最小0，5で　閾値を動的に変化させてから復帰させるまでの秒数
    """

    audio = r.listen(source)
    """
    # r.listen(source: AudioSource, 
    #          timeout: Union[float, None] = None, 
    #          phrase_time_limit: Union[float, None] = None, 
    #          snowboy_configuration: Union[Tuple[str, Iterable[str]], None] = None)
    # ユーザが話始めるまで待機している
    # （だからAUDIOdataは無音の部分がカットされてしまっている）
    # timeout：ユーザが話はじめるまで待つ時間（speech_recognition.WaitTimeoutError）
    # phrase_time_limit：フレーズの最大秒数（Noneに時間制限はない）
    # snowboy_configuration：ホットワード検出？
    """

    # callable = r.listen_in_background(source)
    """
    # ★★★★★★★★★★★★
    # listen_in_background(source: AudioSource, 
    #                      callback: Callable[[Recognizer, AudioData], Any])
    # ソース(AudioSourceインスタンス)からのフレーズをAudioDataインスタンスに繰り返し録音し、
    # 各フレーズが検出されるとすぐにそのAudioDataインスタンスでコールバックを行うスレッドを生成します。
    # 呼び出されると，バックグラウンドリススレッドが強制停止する
    """

    """
    AudioData(frame_data: bytes, 
              sample_rate: int, 
              sample_width: int)
    # モノラルオーディオデータのインスタンス生成
    # 通常、このクラスのインスタンスは、直接インスタンス化するのではなく、
    # recognizer_instance.record
    # recognizer_instance.listen
    # recognizer_instance.listen_in_background
    # のコールバックで取得します。
    """
    
    """
    audiodata_instance.get_segment(start_ms: Union[float, None] = None, 
                                    end_ms: Union[float, None] = None)
    # 指定された時間間隔に切り詰められた新しい AudioData インスタンスを返します。
    # 言い換えれば、同じオーディオデータを持つ AudioData インスタンスですが、開始点が start_ms ミリ秒、終了点が end_ms ミリ秒となります。
    """
    
    """
    audiodata_instance.get_raw_data(convert_rate: Union[int, None] = None,
                                     convert_width: Union[int, None] = None) -> bytes
    # AudioData インスタンスが表すオーディオの生のフレームデータを表すバイト文字列を返します。
    # convert_rateが指定され、オーディオのサンプルレートがconvert_rate Hz以外の場合、結果として得られるオーディオは一致するようにリサンプルされます。
    # convert_widthが指定され、オーディオサンプルのサイズがconvert_width bytes以外であれば、結果として得られるオーディオは適合するように変換されます。
    # これらのバイトを直接ファイルに書き込むと、有効なRAW/PCMオーディオファイルが作成されます。
    """
    
    with open("speechRecognitionReference.wav", "wb") as f:
        f.write(audio.get_wav_data())
    """
    audiodata_instance.get_wav_data(convert_rate: Union[int, None] = None, 
                                    convert_width: Union[int, None] = None) -> bytes
    
    """
    pass

# オーディオファイルを開く
AUDIO_FILE_NAME = "empathtes.wav"
with sr.AudioFile(AUDIO_FILE_NAME) as source: 
    

    

    audio = r.record(source)  # read the entire audio file
    """
    r.record(source: AudioSource, 
             duration: Union[float, None] = None, 
             offset: Union[float, None] = None)
    durationはAudioの入力の長さ
    offsetは基準点からの距離または長さ
    """

    print("【オーディオの長さ：秒 】")  
    print(source.DURATION)              
    """
    これは、recognizer_instance.recordのoffsetパラメータと組み合わせることで、チャンク単位で音声認識を行うことができるので便利です。
    ただし、複数のチャンクで音声を認識することは、全体を一度に認識することと同じではないことに注意してください。
    音声をチャンクに分割した境界線上に話し言葉が現れた場合、各チャンクでは単語の一部しか認識されず、不正確な結果になる可能性があります。   
    """

    print("【"+AUDIO_FILE_NAME +"を認識中】") 
    print(r.recognize_google(audio, language='ja-JP'))
    """
    r.recognize_google(audio_data: AudioData, 
                       key: Union[str, None] = None, 
                       language: str = "en-US", 
                       pfilter: Union[0, 1], 
                       show_all: bool = False)
    # APIのキーなどが無くても使用できる認識エンジン
    # スピーチが理解できない場合は、speech_recognition.UnknownValueError
    # インターネットに接続されていない場合は、speech_recognition.RequestError
    """

    """
    # r.recognize_google_cloud(audio_data: AudioData, 
    #                          credentials_json: Union[str, None] = None, 
    #                          language: str = "en-US", 
    #                          preferred_phrases: Union[Iterable[str], None] = None, 
    #                          show_all: bool = False)
    # Google Cloud Platform アカウントが必要
    """
    pass      

# 使用可能なすべてのマイクの名前のリストを返す
print("【使用可能なマイクのリスト】");print("index:name")
for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
    if microphone_name == "HDA Intel HDMI: 0 (hw:0,3)":
        m = sr.Microphone(device_index=i)
    print(str(i)+":"+microphone_name)

"""
"AudioSource"
オーディオソースを表す基本クラスです。インスタンス化しないでください。
MicrophoneやAudioFileなど、このクラスのサブクラスのインスタンスは、
recognizer_instance.recordやrecognizer_instance.listenなどに渡すことができます。
これらのインスタンスは、コンテキストマネージャーのように動作し、with文で使用するように設計されています。

"""

