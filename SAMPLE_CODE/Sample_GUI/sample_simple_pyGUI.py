# https://knt60345blog.com/pysimplegui_col1/

#!usr/bin/env python
# -*- coding: utf-8 -*-

import PySimpleGUI as sg      

sg.ChangeLookAndFeel('BlueMono')      

#　列要素レイアウト（1段目：テキスト、2段目：テキスト、テキスト入力欄、3段目：テキスト、テキスト入力欄）
col = [[sg.Text('列１', text_color='white', background_color='blue')],      
        [sg.Text('列２', text_color='white', background_color='blue'), sg.Input('列２に入力してください')],      
        [sg.Text('列３', text_color='white', background_color='blue'), sg.Input('列３に入力してください')]]      

#　レイアウト（1段目：リストボックス、列要素レイアウト、2段目：テキスト入力欄、3段目：ボタン）
layout = [
            [sg.Listbox(values=('Listbox Item 1', 'Listbox Item 2', 'Listbox Item 3'), size=(20,3)), sg.Column(col, background_color='blue')],      
            [sg.Input('なにかテキストを入力してください')],      
            [sg.OK()]
        ]

#　ウィンドウの生成と、入力待ち（二つの処理を一つにまとめて書いています）
event, values = sg.Window('　複数列を表示するサンプルアプリ', layout).Read()  

#　入力された値をポップアップで表示する。
sg.popup(event, values, line_width=200)  