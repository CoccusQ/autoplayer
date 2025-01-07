from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import keyboard
import time
import json
import re

with open('playlist.json', 'r') as f:
    video_links = json.load(f)        

driver = webdriver.Edge()
driver.get('https://www.bilibili.com/')
# 删除本次打开网页时的所有cookie
driver.delete_all_cookies()
with open('jsoncookie.json','r') as f:
    ListCookies = json.loads(f.read())
# 将jsoncookie.json里的cookie写入本次打开的浏览器中。
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

print("键盘操作  下一首：↓ 上一首：↑ 快进：→ 快退：← 按键锁定: ctrl+0 列表循环：1\n")
print(">  按键锁定：关闭 |")
print(">  列表循环：关闭 |")
is_first_video = True
is_lock = False
is_loop = False
is_back = False
is_exit = False
num = len(video_links)
i = 0
while i < num:
    if is_back:
        i -= 2
        is_back = False
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
        print(f"                  | ♫ {song_name}    {minutes:02d}:{seconds:02d}")
    while not driver.execute_script("return arguments[0].ended;", video):
        if keyboard.is_pressed('ctrl+0'):
            if is_lock:
                is_lock = False
                print(">  按键锁定：关闭 |")
            else:
                is_lock = True
                print(">  按键锁定：开启 |")
            time.sleep(0.1)
        if not is_lock:
            if keyboard.is_pressed('right'):
                driver.execute_script(f"if (arguments[0].currentTime + 5 >= {video_duration}) arguments[0].currentTime = {video_duration}; else arguments[0].currentTime += 5;", video)
                print(">> 快进5秒        |")
            elif keyboard.is_pressed('left'):
                driver.execute_script("if (arguments[0].currentTime - 5 <= 0) arguments[0].currentTime = 0; else arguments[0].currentTime -= 5;", video)
                print("<< 后退5秒        |")
            elif i >0 and keyboard.is_pressed('up') :
                is_back = True
                print("<<<上一首         |")
                break
            elif keyboard.is_pressed('down'):
                print(">>>下一首         |")
                break
            elif keyboard.is_pressed('esc'):
                is_exit = True
                print("[!]    退出       |")
                break
            elif not is_loop and keyboard.is_pressed('1'):
                is_loop = True
                print(">  列表循环：开启 |")
            elif is_loop and keyboard.is_pressed('1'):
                is_loop = False
                print(">  列表循环：关闭 |")
        time.sleep(0.1)
    if is_exit:
        break
    i += 1
    if i >= num and is_loop:
        i = 0

driver.quit()
