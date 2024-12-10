import cv2
import pyautogui as pag
import time
from datetime import datetime, timedelta
import pyperclip
import os
import sys

# ---自动打开cmd启动scrcpy
pag.hotkey('win','r')
text = 'cmd'
pyperclip.copy(text)
pag.hotkey('ctrl','v')
time.sleep(0.2)
pag.press('enter')
time.sleep(2)
text = 'cd C:\\Users\\Andre\\Downloads\\scrcpy-win64-v2.7'
pyperclip.copy(text)
pag.hotkey('ctrl','v')
time.sleep(0.2)
pag.press('enter')
time.sleep(0.2)
text = 'scrcpy --turn-screen-off --always-on-top'
pyperclip.copy(text)
pag.hotkey('ctrl','v')
time.sleep(0.2)
pag.press('enter')
time.sleep(10)




# ---滑动进入解锁界面---


# 获取当前目录路径
if getattr(sys, 'frozen', False):  # 检查是否为打包后的可执行文件
    current_path = os.path.dirname(sys.executable)
    # print(current_path)
    current_path = sys._MEIPASS
    # print(current_path)
else:
    current_path = os.path.dirname(__file__)
# 确保pic文件夹存在
pic_dir = os.path.join(current_path, 'pic')
if not os.path.exists(pic_dir):
    os.makedirs(pic_dir)
# 保存截图到当前目录的pic文件夹下
screenshot_path = os.path.join(pic_dir, '[log]oppo_unlock.png')
pag.screenshot(screenshot_path)


# pag.screenshot('./pic/oppo_unlock.png')
# img = cv2.imread('./pic/oppo_unlock.png', cv2.IMREAD_GRAYSCALE)
img = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
template_path = os.path.join(pic_dir, '[oppo_unlock]_v2.png')
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
height, width = template.shape
result = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
# pag.screenshot('./pic/oppo_test.png',(max_loc[0],max_loc[1],width,height))


screenshot_log_path = os.path.join(pic_dir, '[log]oppo_unlock_log.png')
pag.screenshot(screenshot_log_path,(max_loc[0],max_loc[1],width,height))


pag.moveTo(x=int(max_loc[0]+width/2), y=(max_loc[1]+height*0.75),duration=0.1)
pag.mouseDown()
time.sleep(0.2)
pag.moveTo(x=int(max_loc[0]+width/2), y=(max_loc[1]+height*0.3),duration=0.5)
pag.mouseUp()
time.sleep(2)

# ---输入密码---
"""第二次识别可以省略
pag.screenshot('./pic/oppo_unlock.png')
img = cv2.imread('./pic/oppo_unlock.png', cv2.IMREAD_GRAYSCALE)
template = cv2.imread("./pic/oppo_unlock_page_2.png", cv2.IMREAD_GRAYSCALE)
height, width = template.shape

result = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED) # 换了这个方法后识别成功
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
"""

# pag.screenshot('./pic/oppo_test.png',(max_loc[0],max_loc[1],width,height))
pag.moveTo(x=int(max_loc[0]+width/2), y=(max_loc[1]+height*0.9),duration=0.1)
pag.click(clicks=6,interval=0.2)


