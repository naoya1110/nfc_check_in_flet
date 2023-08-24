# https://flet.dev/docs/controls/elevatedbutton

import flet as ft
from datetime import datetime
import time
import binascii
import nfc
from functools import partial
import requests
import os
import random

import user_list
users = user_list.users

import line_notify_tokens
line_notify_token = line_notify_tokens.tokens["personal"]

## avators_dict = {"name":ft.CircleAvatar(content=ft.Text(name[:2]))"}
avators_dict = {}

class Avator:
    def __init__(self, username):
        self.username = username
    
    def create(self):
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        colorcode = f'#{r:02X}{g:02X}{b:02X}'
        avator = ft.CircleAvatar(content=ft.Text(self.username[:2]),
                                bgcolor=colorcode,
                                color="#FFFFFF",
                                radius=30)
        return avator
        

def main(page: ft.Page):
    
    # page(アプリ画面)の設定
    page.title = "NFC CHECK-IN APP"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.INDIGO_50
    page.padding = 50
    page.window_height = 800
    page.window_width = 800

    def send_line_notify(notification_message):
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {line_notify_token}'}
        data = {'message': f'\n{notification_message}'}
        requests.post(line_notify_api, headers = headers, data = data)
    
    def logging():
        now = datetime.now()
        now_str = now.strftime("%m.%d %a %H:%M:%S")
        today_str = now.strftime("%Y_%m_%d")
        filepath = f"log/{today_str}.txt"
        
        if os.path.exists(filepath):
            mode="a"
        else:
            mode="x"
        
        with open(filepath, mode, encoding="utf-8") as f:
            f.write(f"{now_str}\t{message_box.value}\n")
        
        log_box.value=log_box.value + f"{now_str} {message_box.value}\n"        
        page.update()
        time.sleep(2)
        message_box.value="Hello"
        page.update()

    # チェックインボタンがクリックされたときのコールバック
    def check_in(e):
        global avators_dict
        message_box.value = "IDカードをスキャンしてください"     # textの文字を変更
        message_box.update()
        id, username, now = read_nfc(timeout=5)
        if id is None:
            message_box.value = "IDカードの読み取りがタイムアウトしました"
        elif username is None:
            message_box.value = f"ID={id}は登録されていません"
        else:
            message_box.value = f"{username}さんがチェックインしました"
            send_line_notify(f"{now.strftime('%m/%d %H:%M')}\n{message_box.value}")
            #avators_dict[username]=ft.CircleAvatar(content=ft.Text(username[:2]))
            avators_dict[username]=Avator(username).create()
            update_avators(avators_dict)
        page.update()
        logging()

    # チェックアウトボタンがクリックされたときのコールバック
    def check_out(e):
        global avators_dict
        message_box.value = "IDカードをスキャンしてください"     # textの文字を変更
        message_box.update()
        id, username, now = read_nfc(timeout=5)
        if id is None:
            message_box.value = "IDカードの読み取りがタイムアウトしました"
        elif username is None:
            message_box.value = f"ID={id}は登録されていません"
        else:
            message_box.value = f"{username}さんがチェックアウトしました"
            send_line_notify(f"{now.strftime('%m/%d %H:%M')}\n{message_box.value}")
            if username in avators_dict.keys():
                avators_dict.pop(username)
                update_avators(avators_dict)
        page.update()
        logging()
    
    def update_avators(avators_dict):
        avators_list = []
        for avator in avators_dict.values():
            avators_list.append(avator)
        avators_row.controls=avators_list
        page.update

        
    ### NFCを読み取るときのタイムアウト処理
    ### https://www.kosh.dev/article/3/
    def measure_dt(n, t0):
        return time.time()-t0 > n
    
    def read_nfc(timeout=5):
        username = None
        with nfc.ContactlessFrontend('usb') as clf:
            t0 = time.time()
            tag = clf.connect(
                rdwr={'targets': ['212F', '424F'], 'on-connect': lambda tag: False},
                terminate=partial(measure_dt, timeout, t0))
            if tag is None:
                id = None
            else:
                id=binascii.hexlify(tag.idm).decode()
            
            if id in users.keys():
                username = users[id]
            now = datetime.now()
        return id, username, now
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


    
    avators_row = ft.Row([], wrap=True)
    
    # コントロールを部品に追加
    page.add(ft.Row([datetime_text, button_in, button_out]))
    page.add(message_box)
    page.add(ft.Container(content=avators_row,
                        height=150,
                        width=page.window_width-100,
                        border=ft.border.all(1, ft.colors.BLACK),
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.all(10)))
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