# https://flet.dev/docs/controls/elevatedbutton

import flet as ft
from datetime import datetime
import time
import binascii
import nfc
from functools import partial

#clf = nfc.ContactlessFrontend('usb')
#print(clf, "\n")

def main(page: ft.Page):
    
    # page(アプリ画面)の設定
    page.title = "NFC CHECK-IN APP"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.INDIGO_50
    page.padding = 50
    page.window_height = 800
    page.window_width = 800


    
    # buttonがクリックされたときのコールバック
    def change_text(e):
        text.value = "You Clicked!"     # textの文字を変更
        text.color = ft.colors.RED_700  # textの色を変更
        text.size = 40                  # textのサイズを変更
        button.visible = False          # ボタンを非表示
        page.update()                   # pageを更新

    # buttonがクリックされたときのコールバック
    def check_in(e):
        message_box.value = "IDカードをスキャンしてください"     # textの文字を変更
        message_box.update()
        id = read_nfc(timeout=5)
        if id is None:
            message_box.value = "タイムアウトしました"
        else:
            message_box.value = f"{id}さんチェックインしました"
            now_str = datetime.now().strftime("%m.%d %a %H:%M")
            log_box.value=log_box.value + f"{now_str}\t{id}さん\tチェックイン\n"
            page.update()
            time.sleep(2)
            message_box.value="Hello"
        page.update()

    def check_out(e):
        message_box.value = "IDカードをスキャンしてください"     # textの文字を変更
        message_box.update()
        id = read_nfc(timeout=5)
        if id is None:
            message_box.value = "タイムアウトしました"
        else:
            message_box.value = f"{id}さんチェックアウトしました"
            now_str = datetime.now().strftime("%m.%d %a %H:%M")
            log_box.value=log_box.value + f"{now_str}\t{id}さん\tチェックアウト\n"
            page.update()
            time.sleep(2)
            message_box.value="Hello"
        page.update()        


    def register_id(e):
        message_box.value = "IDカードをスキャンしてください"     # textの文字を変更
        message_box.update()
        id = read_nfc(timeout=5)
        if id is None:
            message_box.value = "タイムアウトしました"
        else:
            message_box.value = f"{id}を登録します"
            now_str = datetime.now().strftime("%m.%d %a %H:%M")
            log_box.value=log_box.value + f"{now_str}\t{id}\t登録\n"
            page.update()
            time.sleep(2)
            message_box.value="Hello"
        page.update()        
        
    ### NFCを読み取るときのタイムアウト処理
    ### https://www.kosh.dev/article/3/
    def measure_dt(n, t0):
        return time.time()-t0 > n
    
    def read_nfc(timeout=5):
        id = 0
        with nfc.ContactlessFrontend('usb') as clf:
            t0 = time.time()
            tag = clf.connect(
                rdwr={'targets': ['212F', '424F'], 'on-connect': lambda tag: False},
                terminate=partial(measure_dt, timeout, t0))
            if tag is None:
                id = None
            else:
                id=binascii.hexlify(tag.idm).decode()
        return id
    ###################

        

    
    
    # テキスト表示部分を作成
    message_box = ft.TextField(label="message", read_only=True, value="Hello", text_size=16)
    log_box = ft.TextField(label="log", value="", read_only=True, 
                        text_size=16, multiline=True, min_lines=10, max_lines=10)

    # テキスト表示部分を作成
    datetime_text = ft.Text("Date and Time", size=20, color=ft.colors.BLUE_500)
    
    # ボタンを作成
    # クリックされたときのコールバックとしてchenge_textを実行
    button_in = ft.ElevatedButton("チェックイン", width=120, height=40, on_click=check_in)
    button_out = ft.ElevatedButton("チェックアウト", width=120, height=40, on_click=check_out)
    button_regist = ft.ElevatedButton("ID登録", width=120, height=40, on_click=register_id)

    
    # コントロールを部品に追加
    page.add(ft.Row([datetime_text, button_in, button_out, button_regist]))
    page.add(message_box)
    page.add(log_box)


    # アプリ画面を更新    
    page.update()
    
    while True:
        # 時刻を表示
        now_str = datetime.now().strftime("%Y.%m.%d %a %H:%M:%S")
        datetime_text.value=now_str
        datetime_text.update()
        time.sleep(0.1)


# デスクトップアプリとして開く
ft.app(target=main)

# webアプリとして開く場合は任意のポート番号を指定し
# ブラウザでlocalhost:7777を開く
# ft.app(target=main, port=7777)