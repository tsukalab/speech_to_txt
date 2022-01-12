
import PySimpleGUI as sg

text = sg.popup_get_file('ファイルを指定してください。')

sg.popup('結果', '選択されたファイルは、以下です。', text)