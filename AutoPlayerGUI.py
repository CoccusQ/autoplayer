from selenium import webdriver
from selenium.webdriver.common.by import By
import tkinter as tk
import time
import json
import re
import threading

with open('playlist.json', 'r') as f:
    video_links = json.load(f)

driver = webdriver.Edge()
driver.get('https://www.bilibili.com/')
driver.delete_all_cookies()
with open('jsoncookie.json', 'r') as f:
    ListCookies = json.loads(f.read())
for cookie in ListCookies:
    driver.add_cookie({
        'domain': '.bilibili.com',
        'name': cookie['name'],
        'value': cookie['value'],
        'path': '/',
        'expires': None,
        'httponly': False,
    })
driver.get('https://www.bilibili.com/')

win = tk.Tk()
win.title("AutoPlayer")
is_first_video = True
is_loop = True
is_pause = False
is_next = False
is_prev = False
i = 0
video_duration = 0
video = 0
num = len(video_links)
stop_thread = False  # 标志位，用于结束线程

def play_loop():
    global i
    global is_first_video
    global is_pause
    global video_duration
    global video
    global is_prev
    global is_next
    
    while not stop_thread:  # 检查是否需要结束
        if i >= num:
            if is_loop:
                i = 0
            else:
                break

        driver.get(video_links[i])
        time.sleep(2)
        video = driver.find_element(By.CSS_SELECTOR, "video")
        if is_first_video:
            driver.execute_script("arguments[0].pause()", video)
            driver.execute_script("arguments[0].currentTime = 0;", video)
            volume_button = driver.find_element(By.CLASS_NAME, "bpx-player-ctrl-btn.bpx-player-ctrl-volume")
            volume_button.click()
            switch_button = driver.find_element(By.CLASS_NAME, "continuous-btn")
            switch_button.click()
            is_first_video = False
        video_duration = driver.execute_script("return arguments[0].duration;", video)
        minutes = int(video_duration // 60)
        seconds = int(video_duration % 60)
        temp_song_name = driver.find_element(By.CLASS_NAME, "tag-txt")
        pattern = re.compile(re.escape("发现《"))
        song_name = pattern.sub('', temp_song_name.text)
        pattern = re.compile(r'》')
        song_name = pattern.sub('', song_name)
        driver.execute_script("arguments[0].play();", video)
        if song_name is not None:
            song_name_label.config(text=f"♫ {song_name}")
            current_time_label.config(text="00:00")
            duration_label.config(text=f"/ {minutes:02d}:{seconds:02d}")
        while True:
            if stop_thread:
                return
            if driver.execute_script("return arguments[0].ended;", video):
                break
            current_time = driver.execute_script("return arguments[0].currentTime;", video)
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)
            current_time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            if stop_thread:
                break  # 如果线程需要结束，则退出
            if is_next:
                is_next = False
                break
            if is_prev:
                is_prev = False
                break
            time.sleep(1)
        i += 1

def play_video():
    global video
    driver.execute_script("arguments[0].play();", video)

def pause_video():
    global video
    driver.execute_script("arguments[0].pause();", video)

def play_or_pause():
    global is_pause  # 声明is_pause为全局变量
    if is_pause:
        is_pause = False
        play_button.config(text="⏸️")  # 更新时间为暂停图标
        play_video()
    else:
        is_pause = True
        play_button.config(text="▶")  # 更新时间为播放图标
        pause_video()

def next_video():
    global i
    global video_duration
    global video
    global is_next 
    is_next = True
    #driver.execute_script(f"arguments[0].currentTime = {video_duration};", video)

def prev_video():
    global i
    global video
    global video_duration
    global is_prev
    i -= 2
    if i < 0 and is_loop:
        i = num - 1
    is_prev = True
    #driver.execute_script(f"arguments[0].currentTime = {video_duration};", video)

def fast_forward_video():
    global video
    global video_duration
    driver.execute_script(f"if (arguments[0].currentTime + 5 >= {video_duration}) arguments[0].currentTime = {video_duration}; else arguments[0].currentTime += 5;", video)

def fast_reverse_video():
    global video
    global video_duration
    driver.execute_script("if (arguments[0].currentTime - 5 <= 0) arguments[0].currentTime = 0; else arguments[0].currentTime -= 5;", video)

def toggle_loop():
    global is_loop
    if is_loop:
        is_loop = False
        loop_button.config(text="➡️")
    else:
        is_loop = True
        loop_button.config(text="🔁")

def on_closing():
    global stop_thread
    stop_thread = True  # 设置标志位为True，通知线程结束
    win.destroy()  # 销毁窗口
    driver.quit()  # 确保 WebDriver 正确关闭
    # 等待线程结束
    for thread in threading.enumerate():
        if thread != threading.current_thread():
            thread.join()


head_frame = tk.Frame(win)
song_name_label = tk.Label(head_frame, text="♫")
current_time_label = tk.Label(head_frame)
duration_label = tk.Label(head_frame)

# 创建按钮
button_frame = tk.Frame(win)
prev_button = tk.Button(button_frame, text="⏮️", command=prev_video)
fast_reverse_button = tk.Button(button_frame, text="⏪", command=fast_reverse_video)
play_button = tk.Button(button_frame, text="⏸️", command=play_or_pause)
fast_forward_button = tk.Button(button_frame, text="⏩", command=fast_forward_video)
next_button = tk.Button(button_frame, text="⏭️", command=next_video)
loop_button = tk.Button(button_frame, text="🔁", command=toggle_loop)

# 布局按钮为水平
song_name_label.pack(side="left")
current_time_label.pack(side="left")
duration_label.pack(side="left")
head_frame.pack()
prev_button.pack(side=tk.LEFT)
fast_reverse_button.pack(side=tk.LEFT)
play_button.pack(side=tk.LEFT)
fast_forward_button.pack(side=tk.LEFT)
next_button.pack(side=tk.LEFT)
loop_button.pack(side=tk.LEFT)
button_frame.pack()

# 绑定关闭事件
win.protocol("WM_DELETE_WINDOW", on_closing)

# 启动播放循环线程
threading.Thread(target=play_loop).start()

win.mainloop()

if not stop_thread:
    driver.quit()