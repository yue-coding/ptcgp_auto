"""---copyright---
Author: Andrew Hu
"""
import cv2
import pyautogui as pag
import pyperclip
import time
from datetime import datetime, timedelta
import datetime as dt_module
import numpy as np
import os
import sys
import threading
import pygetwindow as pgw
from pynput.mouse import Button, Controller
import pyscreeze

"""---Instruction---
The only thing this file does is to sending friend request until successfully sent 

"""



class TaskManager:
    # 类封装，脚本自动执行内容

    def __init__(self, program_start_time, current_path, pic_dir, log_dir, count_battle_solo, window_position,
                 window_size):
        self.program_start_time = program_start_time
        self.current_path = current_path
        self.pic_dir = pic_dir
        self.log_dir = log_dir
        self.count_battle_solo = count_battle_solo
        self.window_position = window_position
        self.window_size = window_size
        self.pause_event = threading.Event()
        self.pause_event.set()  # 初始化为非暂停状态
        self.event_not_in_battle = threading.Event()
        self.event_not_in_battle.set()  # 初始化为非暂停状态。设置为True。.clear()设置成False



    def task_keep_adding(self):
        # 点击 已选中的对战模式

        cordinate = self.get_xy('add_friend_button',returnEmpty=True)
        while (cordinate):
            auto_click(cordinate)
            print("hand indicator clicked")
            cordinate = self.get_xy('add_friend_button', returnEmpty=True)
        # endregion


    def get_xy(self, template, timeOut=timedelta(minutes=1, seconds=30), whole_screen=True, returnEmpty=False):

        start_time = datetime.now()

        while (datetime.now() - start_time) <= timeOut:

            thread_name = threading.current_thread().name
            if thread_name == "MainLoopThread":
                if not self.pause_event.is_set() and self.event_not_in_battle.is_set():
                    print("Paused during get_xy for MainLoopThread.")
                    return (pag.position())  # 原地点一下

            # 保存截图到当前目录的pic文件夹下
            screenshot_path = os.path.join(self.pic_dir, '[log]screenshot.png')
            pag.screenshot(screenshot_path)

            img_screenshot = cv2.imread(screenshot_path)

            template_path = os.path.join(self.pic_dir, f'{template}.png')
            img_template = cv2.imread(template_path)

            best_match_mid = self.img_match(img_screenshot, img_template, template)
            if best_match_mid:
                return best_match_mid
        if returnEmpty==True:
            return None
        log_str = f'超时，鼠标原地点击一次。寻找目标: {template}，当前时间' + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)
        return (pag.position())  # 原地点一下

    def img_match(self, img_screenshot, img_template, template):

        # 设定一个相似度阈值，比如0.8
        threshold = 0.4

        # 尝试多个缩放比例
        scale_factors = [1.0, 1.05, 1.1, 1.15, 0.95, 0.90, 0.85]  # 添加适当的缩放比例
        best_match_val = 0
        best_match_mid = None

        for scale in scale_factors:
            # 根据比例缩放模板

            scaled_template = cv2.resize(img_template, (0, 0), fx=scale, fy=scale)
            height, width, channel = scaled_template.shape

            # 进行模板匹配
            result = cv2.matchTemplate(img_screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_match_val:  # 更新最佳匹配结果
                best_match_val = max_val
                best_match_mid = (int(max_loc[0] + width / 2), int(max_loc[1] + height / 2))

            if best_match_val >= threshold:
                best_match_pic_log_path = os.path.join(self.pic_dir + "/log/" + datetime.now().strftime(
                    "%Y_%m_%d_%H_%M_%S_" + str(self.count_battle_solo + 1) + "run.png"))
                pag.screenshot(best_match_pic_log_path, (max_loc[0], max_loc[1], width, height))

                log_str = f"找到最佳相似度，当前最佳相似度为{best_match_val:.2f}，缩放比例为" + str(
                    scale) + f"。寻找目标: {template}，当前时间" + str(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
                print(log_str)
                return best_match_mid  # 找到满足阈值的匹配

        log_str = f"相似度不足，当前最佳相似度为{best_match_val:.2f}，寻找目标: {template}" + "。当前时间" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(log_dir, '.txt'), log_str + "\n")
        if threading.current_thread().name == 'DebugMissionThread':
            print(log_str)
        return None


def append_to_file(filename, content):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(content)


def auto_click(cordinate_click):
    if cordinate_click[0] > 0 and cordinate_click[1] > 0:
        pag.moveTo(cordinate_click[0], cordinate_click[1], duration=0.1)
    else:
        print("Invalid coordinates, skipping move.")
    pag.click()
    pag.moveTo(10, 10)
    time.sleep(1)


def scheduler(task_manager):
    # 调度器函数

    task_daily_check_in_done = False
    while True:
        now = datetime.now()

        if now.hour == 1 and now.minute == 5 and not task_daily_check_in_done:
            log_str = "Pausing main loop for daily task... 当前时间" + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            append_to_file(os.path.join(task_manager.log_dir, '.txt'), log_str + "\n")
            print(log_str)

            task_manager.pause_event.clear()
            task_manager.task_daily_check_in()
            task_manager.pause_event.set()
            task_daily_check_in_done = True

        if now.hour != 0 and now.minute == 25:
            print("Pausing main loop for temporary task...")
            task_manager.pause_event.clear()
            task_manager.task_daily_auto_battle()
            task_manager.task_auto_claim_gift()
            task_manager.pause_event.set()

        if now.hour == 0 and now.minute == 0:
            task_daily_check_in_done = False

        if now.minute == 20:
            print("Pausing main loop for Wonder Pick...")
            task_manager.pause_event.clear()
            task_manager.task_auto_check_free_wonder_pick()
            task_manager.pause_event.set()

        time.sleep(1)  # 每秒判断一次


def scheduler_versus(task_manager):
    # 调度器函数

    task_daily_check_in_done = False
    task_daily_auto_claim_gift = False
    while True:
        now = datetime.now()

        if now.hour == 1 and now.minute == 0 and not task_daily_check_in_done:
            log_str = "Pausing main loop for daily task... 当前时间" + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            append_to_file(os.path.join(task_manager.log_dir, '.txt'), log_str + "\n")
            print(log_str)

            task_manager.pause_event.clear()
            task_manager.task_daily_check_in_versus()
            task_manager.pause_event.set()
            task_daily_check_in_done = True

        if now.hour == 2 and now.minute == 25 and not task_daily_auto_claim_gift:
            print("Pausing main loop for temporary task...")
            task_manager.pause_event.clear()
            task_manager.task_auto_claim_gift_versus()
            task_manager.pause_event.set()
            task_daily_auto_claim_gift = True

        if now.hour == 0 and now.minute == 0:
            task_daily_check_in_done = False
            task_daily_auto_claim_gift = False

        if now.minute == 20:
            print("Pausing main loop for Wonder Pick...")
            task_manager.pause_event.clear()
            task_manager.task_auto_check_free_wonder_pick_versus()
            task_manager.pause_event.set()

        time.sleep(1)  # 每秒判断一次


def status_checker(task_manager):
    screenshot_path = os.path.join(task_manager.pic_dir, '[log]screenshot_status_checker.png')
    pag.screenshot(screenshot_path)
    img_screenshot = cv2.imread(screenshot_path)

    template_list = [
        'ptcgp_date_change_01',  # OK按钮
        'button_ptcgp_app',  # 未打开游戏
        'button_ptcgp_title_page',  # 标题页面
        'button_tap_to_proceed',  # 点击来继续
        'button_next']  # 继续按钮
    for template in template_list:
        template_path = os.path.join(task_manager.pic_dir, f'{template}.png')
        img_template = cv2.imread(template_path)

        best_match_mid = task_manager.img_match(img_screenshot, img_template, template)

        if best_match_mid:
            return template, best_match_mid

    return None, None


def get_window_position(log_dir):
    # 获取特定窗口
    window = pgw.getWindowsWithTitle('MuMu')[0]  # 以标题部分匹配，如'PCLM10'

    # 获取窗口的位置和大小
    log_str = "窗口左上角坐标: " + str(window.topleft)  # 左上角坐标
    append_to_file(os.path.join(log_dir, '.txt'), log_str + "\n")
    print(log_str)

    log_str = "窗口大小: " + str(window.size)  # 宽度和高度
    append_to_file(os.path.join(log_dir, '.txt'), log_str + "\n")
    print(log_str)

    log_str = "窗口右下角坐标: " + str(window.bottomright)  # 右下角坐标
    append_to_file(os.path.join(log_dir, '.txt'), log_str + "\n")
    print(log_str)

    return window.topleft, window.size


def debug_mission(task_manager):
    # task_manager.routine()
    # task_manager.task_daily_check_in()
    # task_manager.task_daily_auto_battle()
    # task_manager.task_auto_claim_gift(start_hour=2, start_minute=25, end_hour=3, end_minute=15)
    # task_manager.task_auto_check_free_wonder_pick()
    # task_manager.routine_versus()
    # task_manager.task_daily_check_in_versus()
    # task_manager.task_auto_claim_gift_versus()
    task_manager.task_auto_check_free_wonder_pick_versus()


if __name__ == "__main__":
    # 启动主线程和调度器线程

    # region---启动程序，初始化---

    # region ---路径---
    # 获取当前目录路径
    if getattr(sys, 'frozen', False):  # 检查是否为打包后的可执行文件
        current_path = os.path.dirname(sys.executable)
        current_path = sys._MEIPASS
    else:
        current_path = os.path.dirname(__file__)
    # 确保pic文件夹存在
    pic_dir = os.path.join(current_path, 'pic')
    if not os.path.exists(pic_dir):
        os.makedirs(pic_dir)
    # 确保log文件夹存在
    log_dir = os.path.join(pic_dir, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # endregion

    log_str = '程序启动-V011. ' + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    append_to_file(os.path.join(log_dir, '.txt'), "\n" + log_str + "\n")  # 添加log
    print(log_str)

    window_position, window_size = get_window_position(log_dir)

    program_start_time = datetime.now()

    count_battle_solo = 0  # 循环计数器

    # endregion ---初始化结束---

    task_manager = TaskManager(program_start_time, current_path, pic_dir, log_dir, count_battle_solo, window_position,
                               window_size)  # 代码实现了参数从全局范围传递到 class TaskManager 的过程

    # 启动主循环线程
    main_thread = threading.Thread(target=task_manager.task_keep_adding, name="MainLoopThread")
    main_thread.daemon = True
    main_thread.start()

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=scheduler_versus, args=(task_manager,), name="SchedulerThread")
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # 启动debug单任务线程
    # scheduler_thread = threading.Thread(target=debug_mission, args=(task_manager,), name="DebugMissionThread")
    # scheduler_thread.daemon = True
    # scheduler_thread.start()

    # 保持主程序运行
    while True:
        time.sleep(0.3)
