import MeCab
from sys import argv

#引数の取得
# input_file_name="face1direct.txt"
def mecab_t(text):
    # # inputname=input()
    # inputname=FILE_NAME
    # input_file_name="extscenario_recognizedWord/"+inputname

    # # 解析対象テキストファイルのインポート
    # f = open(input_file_name, 'r', newline="",encoding="utf-8")
    # # reader = csv.reader(f)
    # text=f.read()
    # print(text)
    # print(text)

    # 分かち書きのみ出力する設定にする
    # mecab = MeCab.Tagger("-Ochasen")
    # mecab = MeCab.Tagger("-Owakati")
    mecab = MeCab.Tagger("/b1017059/local/lib/mecab/dic/mecab-ipadic-neologd")
    result = mecab.parse(text)
    # print(result)
    mecab.parse('')

    lines = result.split('\n')
    nounAndVerb = []#「名詞」と「動詞」を格納するリスト
    hinshiList = []
    for line in  lines:
        feature = line.split('\t')
        # print(feature)
        if len(feature) != 1: #'EOS'と''を省く
            info = feature[1].split(',')
            hinshi = info[0]
            if hinshi in ('名詞'):
                hinshiList.append(["名詞",feature[0]])
                if info[6]=="*":
                    nounAndVerb.append(info[0])
                else:
                    nounAndVerb.append(info[6])
            elif hinshi in ('動詞'): 
                hinshiList.append(["動詞", feature[0]])
            else:
                hinshiList.append(["その他", feature[0]])
    return hinshiList

if __name__ == "__main__":
    text = input()
    print(mecab_t(text))

