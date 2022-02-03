
## 「GCP_Speech_To_TXT _SAMPLE_CODE」
このディレクトリ内のコードは単体で実行することができます．  

### speech_to_text_sample_audioFile.py  
[GCPのサンプルコード](https://cloud.google.com/speech-to-text/docs/streaming-recognize?hl=ja)
内の「ローカルファイルでストリーミング音声認識を実行する」のコードです．  
1行目の下記の行を任意の認識させたいファイル名に変更すると，認識結果を表示してくれます
~~~python
AUIDO_FILENAME = "test.wav"　　
~~~

### speech_to_text_sample_streming.py

同じく[GCPのサンプルコード](https://cloud.google.com/speech-to-text/docs/streaming-recognize?hl=ja)
内の「音声ストリームでストリーミング音声認識を実行する」のコードを改変したものになります．  

このコードは任意の入力デバイスを設定し音声認識することができます．  
入力デバイスの設定は`DEVICE_INDEX`で制御しています．（defolt：0）

実行すると`【オーディオデバイス一覧】`が表示されたのち，現在接続されている入力デバイスが`接続デバイス【indexhoge:hogehoge】`として表示されます．  
その後`【何か話してください】`と表示された後，音声認識をはじめることができます．<br>

実行例
~~~
【オーディオデバイス一覧】
index0:Microsoft Sound Mapper - Input
index1:ステレオ ミキサー (Realtek High Definit
index2:マイク配列 (Realtek High Definition 
index3:Microsoft Sound Mapper - Output
index4:スピーカー (Realtek High Definition 
index5:hoge
index6:hogehoge
...
接続デバイス【index0:Microsoft Sound Mapper - Input】
【何か話してください】
~~~~~

<br><br><br>
## speech_to_text_sample_toSaveAudio.py
単体で実行することができます．<br>
挙動は[speech_to_text_sample_streming.py](###speech_to_text_sample_streming.py)とほぼ一緒ですが，認識された音声を録音できます．<br>
認識結果をひらがな変換するために`pykakasi`のライブラリを使用しているため，新たにインストールする必要があります．<br>

~~~
pip install pykakasi
~~~
[インストール参考方法](https://office54.net/python/module/pykakasi-kanji-convert)

単体で実行後，pykakasiのバージョンに関して警告がでるかもしれません．

### 音声ファイルの保存場所
録音した音声は以下のように一階層上のローカルディレクトリに保存されるようになっています（ディレクトリは自動で作成されません）<br>
~~~python
AUDIO_DIRECTORY = "../Audio_GUI/"
~~~
以下のように書き換えるとおそらくすぐ実行できます．
~~~python
AUDIO_DIRECTORY = ""
~~~



<br><br><br>
## main_sst_gui.py
メインファイルです．<br>

使用ライブラリ
- PySimpleGUI
~~~
pip install PySimpleGUI
~~~
<br>
おそらく上記以外はpythonの標準モジュールとして使用できると思います．

### 実行前の書き換え

#### ログの保存場所
ログは以下のように一階層上のローカルディレクトリに保存されるようになっています（ディレクトリは自動で作成されません）<br>
~~~python
LOG_DIRECTORY = "../LOG_GUI/"
~~~
以下のように書き換えるとおそらくすぐ実行できます．
~~~python
LOG_DIRECTORY = ""
~~~

#### 2つのDEVICE_INDEX
PCの内部音声（`MIXER_INDEX`）と，外部マイクからの入力（`MIC_INDEX`）を同時に取得するために，それぞれの`DEVICE_INDEX`を割り当てる必要があります．<br>
デフォルトでは以下のように設定されています．
~~~python
MIC_INDEX = 2
MIXER_INDEX = 1
~~~
入力デバイスのインデックス番号が分からない場合は[speech_to_text_sample_streming.py](###speech_to_text_sample_streming.py)を実行してください．デバイスの一覧が表示されます．

### 実行後
Startボタンを押すと設定したで入力デバイスで認識が始まります．<br>
※この時スタートボタンを複数回押さないでください（認識が開始するまでに数秒かかります）

その他にボタンなどがありますが，複雑なので一度説明を終わります．

<br><br><br>
## main_on_desktop.py
実験用ファイルです．<br>

使用ライブラリ:tkinter

認識結果のみが逐一表示されます．

<br><br><br>
## mecab_txt.py
現在はどのファイルとも依存関係は無いので無視して大丈夫です．<br>
ライブラリのインポートや設定に書き換えが必要になりますが，単体で実行できます．<br>
実行後ターミナルにテキストを入力すると形態素解析してくれます．<br>

実行例
~~~~~
本日は晴天なり
[['名詞', '本日'], ['その他', 'は'], ['名詞', '晴天'], ['その他', 'なり']]
~~~~~


<br><br><br>
## 「SAMPLE_CODE」
このディレクトリは無視してください



