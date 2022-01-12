
from queue import Queue
from threading import Thread
import time

import PySimpleGUI as sg

ui_que = Queue()
data_que = Queue()

def show_time():
    jikan = time.strftime('%p %I:%M:%S')
    return jikan

def worker(data_que,ui_que):
    result = data_que.get()
    time.sleep(1)
    ui_que.put(result[0])

def worker_do(data_que,ui_que):
    result_do = data_que.get()
    time.sleep(0.5)
    ui_que.put(len(result_do))


sg.theme('Dark')
layout = [
          [sg.Text(size=(15, 1), font=('Helvetica', 20),justification='center', key='-jikan-')],
          [sg.Text('Data', size=(8, 1)),sg.Input(key='-data-')],
          [sg.Submit()],
          [sg.Text('Data2', size=(8, 1)),sg.Input(key='-data2-')],
          [sg.Button('DO',key='-do-'), sg.Cancel()],
          [sg.Text('Status:', size=(8, 1)),sg.Text('',size=(8,1), key='-status-')],
          [sg.Output(size=(70, 2))]
          ]

window = sg.Window('template',layout)

while True:
    event, values = window.read(timeout=10,timeout_key='-timeout-')
    print(event+"ddd")

    # event, values = window.read()
    #timeoutを指定することで、timeoutイベントが起こります。timeoutの単位ms
    # print(event,values)
    #↑コメントアウトを外すと、どんなイベントが起こっているか確かめることができます。
    if event in (None,'Cancel'):
        break
    elif event in 'Submit':
        print('Input data: {}'.format(values['-data-']))
        # デーモンスレッドはデーモンスレッド以外のスレッドがなくなった時点で全て自動終了する
        thread = Thread(target=worker, args=(data_que,ui_que), daemon=True).start()
        data_que.put(values['-data-'])

    elif event in '-do-':
        print('do somthing: {}'.format(values['-data2-']))
        thread_do = Thread(target=worker_do, args=(data_que,ui_que), daemon=True).start()
        data_que.put(values['-data2-'])

    elif event in '-timeout-':
        jikan = show_time()
        window['-jikan-'].update(jikan)

        try:
            ui_data=ui_que.get_nowait()
        except :
            ui_data = None
        if ui_data:
            print(ui_data)   
            window['-status-'].update(ui_data)


window.close()