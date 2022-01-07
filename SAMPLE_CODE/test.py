from pykakasi import kakasi

kakasi = kakasi()
kakasi.setMode('J', 'H') #漢字からひらがなに変換
kakasi.setMode("K", "H") #カタカナからひらがなに変換
conv = kakasi.getConverter()

str = '何してんのどうも皆さんの生活23日目棚どうぶつの森全然やってな'
a = (1,0)
print(a)

print(conv.do(str))
