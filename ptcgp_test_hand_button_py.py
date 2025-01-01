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
# 纯versus_private \n
# 每小时自动进行versus_private对战,以求增加pvp胜场数\n
# 每天到点会自动暂停刷pvp主线程,执行新线程特殊任务。之后再继续刷pvp主线程\n

pvp
检查得卡挑战

每天一次检查礼物

# 每天1点整, 进入刷新模式, 当前对战结束后, 自动重启游戏, 重新登录。\n
# 每天2点25分, 在pvp战斗后自动领取收到谢谢礼物,每日商店礼物,每日任务礼物。\n
# 每当时间为20分时,在当前pvp对战结束后,检查一次免费得卡挑战。\n

TODO \n

检测从其他设备登录, 1小时后自动重登\n
困难:自动开包。每天2次\n
困难:自动使用得卡挑战。每天2次,需要判断当前能量,需要只开1能量挑战\n
判断是否要修改get_xy获得上次点击位置。\n

更新日志\n
011: 修改为纯pvp战斗,不进行pve战斗了
010: 修改pvp战斗, 使用私人对战(Private Match) "Thanks"。这样可以增加获胜概率, 而且也能给对方点赞, 满足对方获得商店券的初衷。\n
009: 增加一种routine_pvp。自动开pvp,期待对方投降,来刷胜利场数。\n
008: 统一截图名称\n

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



    def routine(self):
        # 点击 已选中的对战模式
        cordinate_click = self.get_xy('hand_indicator')
        auto_click(cordinate_click)
        print("hand indicator clicked")
        # 进单人模式
        cordinate_click = self.get_xy('button_battle_solo')
        auto_click(cordinate_click)

        # 点击初级对战
        cordinate_click = self.get_xy('button_battle_solo_beginner')
        auto_click(cordinate_click)

        # 完成，等待刷刷刷脚本自动运行

        # region ---自动刷人机
        timer_main_loop = 0
        while True:
            if self.pause_event.is_set():
                # print(f"[{self.program_start_time}] Main loop is running... Count: {self.count_battle_solo}, LogDir: {self.log_dir}")

                # region ---自动运行主要开刷部分---

                loop_start_time = datetime.now()

                """---识别并滚动屏幕---
                # ---识别并滚动屏幕---
                cordinate_scroll_start = self.get_xy('solo_expert_water') 
                if not self.pause_event.is_set():
                    continue 
                cordinate_scroll_end = self.get_xy('solo_expert_grass') 
                if not self.pause_event.is_set():
                    continue 
                pag.moveTo(cordinate_scroll_start)
                pag.mouseDown()
                pag.moveTo(cordinate_scroll_end,duration=1)
                pag.mouseUp()
                time.sleep(1) # 滚动后可能还有滑动动画
                """

                cordinate_click = self.get_xy('solo_beginner_fire')
                if not self.pause_event.is_set():
                    continue  # 如果在 `get_xy` 后 pause_event 被设置，跳过后续操作
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_auto_on')
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_battle')
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)
                self.event_not_in_battle.clear()  # 进入战斗状态
                time.sleep(150)  # 对战时间，停2分30秒。

                cordinate_click = self.get_xy('button_tap_to_proceed',
                                              timeOut=timedelta(minutes=2, seconds=30))  # 胜利页面。若失败，则没有此次点击，不论是投降还是被击败。
                # print('战斗状态结束') # debug
                auto_click(cordinate_click)
                time.sleep(1)
                self.event_not_in_battle.set()  # 战斗状态结束
                if not self.pause_event.is_set():
                    continue

                cordinate_click = self.get_xy('button_tap_to_proceed')  # 己方MVP
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_tap_to_proceed')  # 敌方MVP。若开局直接投降，则没有此次点击。
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_next')  # 奖励页面
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                self.count_battle_solo += 1
                current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                loop_end_time = datetime.now()

                log_str = "循环" + str(self.count_battle_solo) + "次。当前时间" + str(
                    current_time_str) + "。本次循环用时" + str(loop_end_time - loop_start_time)
                append_to_file(os.path.join(self.log_dir, '.txt'), log_str + '\n')  # 添加log
                print(log_str)
                # endregion

            else:
                if np.mod(timer_main_loop, 60) == 0:
                    log_str = "Main loop paused... Current time:" + str(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
                    print(log_str)
                timer_main_loop += 1
                time.sleep(1)
        # endregion

    def task_daily_check_in(self):
        log_str = "Starting the Daily Check In task... Current time:" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)

        while not self.event_not_in_battle.is_set():
            time.sleep(1)

        time.sleep(1)
        # region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.98 * self.window_size[1],
                   duration=0.1)
        pag.middleClick()  # 先回主页，确保多任务顺利打开
        time.sleep(1)
        pag.mouseDown(button='left')
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.5 * self.window_size[1],
                   duration=0.2)
        time.sleep(0.1)
        pag.mouseUp(button='left')

        # 手动划掉任务栏，关闭程序
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.75 * self.window_size[1])
        pag.mouseDown()
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.2 * self.window_size[1],
                   duration=0.1)
        pag.mouseUp()

        # 等待10秒
        time.sleep(2)

        # 打开游戏
        cordinate_click = self.get_xy('button_ptcgp_app')
        auto_click(cordinate_click)

        # 点击标题页面
        time.sleep(1)
        cordinate_click = self.get_xy('button_ptcgp_title_page')
        auto_click(cordinate_click)
        # endregion

        # region ---进单人对战-初级---

        cordinate_click = self.get_xy('button_page_battle')  # 进对战页面
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_battle_solo')  # 单人模式
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_battle_solo_beginner')  # 初级对战
        auto_click(cordinate_click)
        # endregion

        # time.sleep(200)
        log_str = "Daily Check In task completed. Current time:" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)

    def task_daily_auto_battle(self, auto_battle_num=15):
        log_str = "Starting the Daily Auto Battle task... Current time:" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)

        while not self.event_not_in_battle.is_set():
            time.sleep(1)

        # region ---步骤说明---
        # 单击侧键进多任务 # 似乎并不方便多平台实现，win32是可以
        # 手动划掉任务栏，关闭程序
        # 等待20秒
        # 打开游戏
        # 点击标题页面
        # 进对战页面
        # 进多人模式
        # 进私人对战模式 -- 输入Thanks --
        # 点击对战
        # 等待10秒
        # 点击更多
        # 点击投降
        # 点击确认投降
        # 点击“点击以继续”
        # 点击 继续按钮
        # 点击 谢谢按钮
        # 点击 ×按钮
        # 重复回点击对战按钮
        # 点击 已选中的对战模式
        # 进单人模式
        # 点击初级对战
        # 完成，等待刷刷刷脚本自动运行
        # endregion

        # region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.98 * self.window_size[1],
                   duration=0.1)
        pag.middleClick()  # 先回主页，确保多任务顺利打开
        time.sleep(1)
        pag.mouseDown(button='left')
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.5 * self.window_size[1],
                   duration=0.2)
        time.sleep(0.1)
        pag.mouseUp(button='left')

        # 手动划掉任务栏，关闭程序
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.75 * self.window_size[1])
        pag.mouseDown()
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.2 * self.window_size[1],
                   duration=0.1)
        pag.mouseUp()

        # 等待10秒
        time.sleep(2)

        # 打开游戏
        cordinate_click = self.get_xy('button_ptcgp_app')
        auto_click(cordinate_click)

        # 点击标题页面
        time.sleep(1)
        cordinate_click = self.get_xy('button_ptcgp_title_page')
        auto_click(cordinate_click)
        # endregion

        # region ---进入多人活动对战
        # 进对战页面
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进多人模式
        cordinate_click = self.get_xy('button_battle_versus')
        auto_click(cordinate_click)

        # 进活动模式
        # cordinate_click = self.get_xy('button_battle_versus_event') # 活动对战
        # cordinate_click = self.get_xy('button_battle_versus_random') # 随机对战

        cordinate_click = self.get_xy('button_battle_versus_private')  # 私人对战
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_01')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_02')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_03')
        auto_click(cordinate_click)
        paste_text = 'Thanks'
        pyperclip.copy(paste_text)
        pag.hotkey('ctrl', 'v')
        cordinate_click = self.get_xy('button_battle_versus_private_04')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)
        # endregion

        # region ---自动进行多人活动对战
        count_battle_versus = 0
        while count_battle_versus < auto_battle_num:
            # 点击对战
            cordinate_click = self.get_xy('button_battle')
            auto_click(cordinate_click)
            self.event_not_in_battle.clear()  # 进入战斗状态

            # 等待15秒
            time.sleep(15)  # 15秒应该足够对面投降了，不投也不会投

            # 点击更多
            cordinate_click = self.get_xy('button_concede_01', timeOut=timedelta(seconds=15))
            if not cordinate_click == (pag.position()):
                # 找到的情况下
                auto_click(cordinate_click)

                # 点击投降
                cordinate_click = self.get_xy('button_concede_02', timeOut=timedelta(seconds=15))
                auto_click(cordinate_click)

                # 点击确认投降
                cordinate_click = self.get_xy('button_concede_03', timeOut=timedelta(seconds=15))
                auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_ok', timeOut=timedelta(seconds=5))
            auto_click(cordinate_click)

            # 点击“点击以继续”
            cordinate_click = self.get_xy('button_tap_to_proceed')
            auto_click(cordinate_click)

            self.event_not_in_battle.set()

            # 点击可能存在的“点击以继续”，若随机模式pvp胜利，则有个3个点击以继续。大部分时候没有，所以时间限制设置短一些
            cordinate_click = self.get_xy('button_tap_to_proceed', timeOut=timedelta(seconds=15))
            auto_click(cordinate_click)

            # 点击可能存在的“点击以继续”，若pvp胜利，则有个3个点击以继续。大部分时候没有，所以时间限制设置短一些
            cordinate_click = self.get_xy('button_tap_to_proceed', timeOut=timedelta(seconds=15))
            auto_click(cordinate_click)

            # 点击 继续按钮
            cordinate_click = self.get_xy('button_next')
            auto_click(cordinate_click)

            # 点击 谢谢按钮
            cordinate_click = self.get_xy('button_thanks')
            auto_click(cordinate_click)

            # 点击 ×按钮
            time.sleep(5)
            cordinate_click = self.get_xy('button_close')
            auto_click(cordinate_click)

            count_battle_versus += 1

            log_str = '自动对战' + str(count_battle_versus) + '次' + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
            print(log_str)
        # endregion

        # time.sleep(200) # debug
        log_str = f"Daily Auto Battle task completed. Battled {auto_battle_num} times. Current time:" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)

    def task_auto_claim_gift(self, start_hour=2, start_minute=25, end_hour=3, end_minute=15):
        """
        # 自动领取收到谢谢礼物
        # 仅在凌晨2点25分至3点15分之间时执行该程序。

        起点: 非主页+非战斗状态。(通常在自动pvp后, 多人对战准备页面)\n
        终点: 单人对战-初级页面。(后接自动刷人机)\n
        """

        auto_claim_indicator = False
        now = datetime.now()
        if now.hour == start_hour and now.minute >= start_minute:
            auto_claim_indicator = True
        elif now.hour == end_hour and now.minute <= end_minute:
            auto_claim_indicator = True

        while not self.event_not_in_battle.is_set():
            time.sleep(1)

        if auto_claim_indicator:
            time.sleep(3)  # 只有在固定时间内才领礼物，其他时候不领礼物，直接进单人对战-初级

            # region ---自动领取收到的谢谢礼物
            cordinate_click = self.get_xy('button_page_home')
            auto_click(cordinate_click)

            time.sleep(10)
            cordinate_click = self.get_xy('button_gifts_01')
            auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_gifts_02')
            auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_ok')
            auto_click(cordinate_click)

            time.sleep(15)
            # print('cross') # debug
            cordinate_click = self.get_xy('button_close')
            auto_click(cordinate_click)
            # endregion

            # 领取每日奖励
            # region ---自动领取每日商店礼品
            cordinate_click = self.get_xy('button_daily_gifts_01')
            auto_click(cordinate_click)

            time.sleep(3)
            cordinate_click = self.get_xy('button_daily_gifts_02')
            auto_click(cordinate_click)

            time.sleep(3)
            cordinate_click = self.get_xy('button_ok')
            auto_click(cordinate_click)

            time.sleep(10)
            cordinate_click = self.get_xy('button_close')
            auto_click(cordinate_click)
            # endregion

            # region ---自动领取每日任务礼品
            cordinate_click = self.get_xy('button_daily_missions_01')
            auto_click(cordinate_click)

            time.sleep(3)
            cordinate_click = self.get_xy('button_daily_missions_02')
            auto_click(cordinate_click)

            time.sleep(3)
            cordinate_click = self.get_xy('button_daily_missions_03')
            auto_click(cordinate_click)

            time.sleep(3)
            cordinate_click = self.get_xy('button_ok')
            auto_click(cordinate_click)

            time.sleep(10)
            cordinate_click = self.get_xy('button_close')
            auto_click(cordinate_click)

            # endregion

        # region ---进单人对战-初级
        # 点击 对战模式
        time.sleep(5)
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进单人模式
        cordinate_click = self.get_xy('button_battle_solo')
        auto_click(cordinate_click)

        # 点击初级对战
        cordinate_click = self.get_xy('button_battle_solo_beginner')
        auto_click(cordinate_click)

        # 完成，等待刷刷刷脚本自动运行
        # endregion

    def task_auto_check_free_wonder_pick(self):
        """
        # 自动检查免费得卡挑战

        得卡挑战 wonder pick\n
        免费挑战 Bonus Pick\n
        幸运挑战 Chansey Pick\n
        稀有挑战 Rare Pick\n
        """

        # 判断是否仍在战斗，若是，则等待到结束为止。
        while not self.event_not_in_battle.is_set():
            # print('def task_auto_check_free_wonder_pick(self)函数判断',not self.event_not_in_battle.is_set()) # debug
            # print('应该是在战斗中，应该为True') # debug
            time.sleep(1)

        # print('开始重启') # debug

        time.sleep(1)
        # region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.98 * self.window_size[1],
                   duration=0.1)
        pag.middleClick()  # 先回主页，确保多任务顺利打开
        time.sleep(1)
        pag.mouseDown(button='left')
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.5 * self.window_size[1],
                   duration=0.2)
        time.sleep(0.1)
        pag.mouseUp(button='left')

        # 手动划掉任务栏，关闭程序
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.75 * self.window_size[1])
        pag.mouseDown()
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.2 * self.window_size[1],
                   duration=0.1)
        pag.mouseUp()

        # 等待10秒
        time.sleep(2)

        # 打开游戏
        cordinate_click = self.get_xy('button_ptcgp_app')
        auto_click(cordinate_click)

        # 点击标题页面
        time.sleep(1)
        cordinate_click = self.get_xy('button_ptcgp_title_page')
        auto_click(cordinate_click)
        # endregion

        # region ---检查得卡挑战---
        time.sleep(3)
        cordinate_click = self.get_xy('button_wonder_pick_01')
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_wonder_pick_02_bonus', timeOut=timedelta(seconds=30))
        if not cordinate_click == (pag.position()):
            auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_ok')
            auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_wonder_pick_03')
            auto_click(cordinate_click)

            # time.sleep(20)
            cordinate_click = self.get_xy('button_tap_to_proceed')
            auto_click(cordinate_click)

            # 不一定有添加新卡环节
            cordinate_click = self.get_xy('button_wonder_pick_04', timeOut=timedelta(seconds=30))
            if not cordinate_click == (pag.position()):
                # 有添加新卡的部分
                pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0],
                           task_manager.window_position[1] + 0.7 * task_manager.window_size[1],
                           duration=0.1)
                pag.mouseDown(button='left')
                pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0],
                           task_manager.window_position[1] + 0.4 * task_manager.window_size[1],
                           duration=0.2)
                time.sleep(0.1)
                pag.mouseUp(button='left')

                time.sleep(15)
                cordinate_click = self.get_xy('button_next')
                auto_click(cordinate_click)

            # time.sleep(15)
            cordinate_click = self.get_xy('button_tap_to_proceed')
            auto_click(cordinate_click)

        # endregion

        # region ---进单人对战-初级
        # 点击 对战模式
        time.sleep(5)
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进单人模式
        cordinate_click = self.get_xy('button_battle_solo')
        auto_click(cordinate_click)

        # 点击初级对战
        cordinate_click = self.get_xy('button_battle_solo_beginner')
        auto_click(cordinate_click)

        # 完成，等待刷刷刷脚本自动运行
        # endregion

    def routine_versus(self):
        # region ---进pvp私人对战Thanks---
        # 点击 已选中的对战模式
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进pvp模式
        cordinate_click = self.get_xy('button_battle_versus')
        auto_click(cordinate_click)

        # 点击私人对战并输入密码
        cordinate_click = self.get_xy('button_battle_versus_private')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_01')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_02')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_03')
        auto_click(cordinate_click)
        paste_text = 'Thanks'
        pyperclip.copy(paste_text)
        pag.hotkey('ctrl', 'v')
        cordinate_click = self.get_xy('button_battle_versus_private_04')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)
        # 完成，等待刷刷刷脚本自动运行
        # endregion

        # region ---自动刷pvp---
        timer_main_loop = 0
        while True:
            if self.pause_event.is_set():
                # region ---自动运行主要开刷部分---
                loop_start_time = datetime.now()

                cordinate_click = self.get_xy('button_battle')  # 点击对战按钮
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)
                self.event_not_in_battle.clear()  # 进入战斗状态

                # 等待15秒
                time.sleep(20)  # 15秒应该足够对面投降了，不投也不会投

                # 点击更多
                cordinate_click = self.get_xy('button_concede_01', timeOut=timedelta(seconds=15))
                if not cordinate_click == (pag.position()):
                    # 找到的情况下
                    auto_click(cordinate_click)

                    # 点击投降
                    cordinate_click = self.get_xy('button_concede_02', timeOut=timedelta(seconds=15))
                    auto_click(cordinate_click)

                    # 点击确认投降
                    cordinate_click = self.get_xy('button_concede_03', timeOut=timedelta(seconds=15))
                    auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_ok', timeOut=timedelta(seconds=5))
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_tap_to_proceed', timeOut=timedelta(seconds=30))
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_tap_to_proceed',
                                              timeOut=timedelta(seconds=15))  # 失败的话只有1次，versus_private
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_next', timeOut=timedelta(seconds=30))  # 奖励页面
                auto_click(cordinate_click)

                # 点击 谢谢按钮
                cordinate_click = self.get_xy('button_thanks', timeOut=timedelta(seconds=30))
                auto_click(cordinate_click)

                # 点击 ×按钮
                time.sleep(5)
                cordinate_click = self.get_xy('button_close', timeOut=timedelta(seconds=30))
                auto_click(cordinate_click)

                time.sleep(1)
                self.event_not_in_battle.set()  # 战斗状态结束

                self.count_battle_solo += 1
                current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                loop_end_time = datetime.now()

                log_str = "自动战斗" + str(self.count_battle_solo) + "次。当前时间" + str(
                    current_time_str) + "。本次循环用时" + str(loop_end_time - loop_start_time)
                append_to_file(os.path.join(self.log_dir, '.txt'), log_str + '\n')  # 添加log
                print(log_str)
                # endregion

            else:
                if np.mod(timer_main_loop, 60) == 0:
                    log_str = "Main loop paused... Current time:" + str(
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
                    print(log_str)
                timer_main_loop += 1
                time.sleep(1)
        # endregion

    def task_daily_check_in_versus(self):
        log_str = "Starting the Daily Check In task... Current time:" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)

        while not self.event_not_in_battle.is_set():
            time.sleep(1)

        time.sleep(1)
        # region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.98 * self.window_size[1],
                   duration=0.1)
        pag.middleClick()  # 先回主页，确保多任务顺利打开
        time.sleep(1)
        pag.mouseDown(button='left')
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.5 * self.window_size[1],
                   duration=0.2)
        time.sleep(0.1)
        pag.mouseUp(button='left')

        # 手动划掉任务栏，关闭程序
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.75 * self.window_size[1])
        pag.mouseDown()
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.2 * self.window_size[1],
                   duration=0.1)
        pag.mouseUp()

        # 等待10秒
        time.sleep(2)

        # 打开游戏
        cordinate_click = self.get_xy('button_ptcgp_app')
        auto_click(cordinate_click)

        # 点击标题页面
        time.sleep(1)
        cordinate_click = self.get_xy('button_ptcgp_title_page')
        auto_click(cordinate_click)
        # endregion

        # region ---进pvp私人对战Thanks---
        # 点击 已选中的对战模式
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进pvp模式
        cordinate_click = self.get_xy('button_battle_versus')
        auto_click(cordinate_click)

        # 点击私人对战并输入密码
        cordinate_click = self.get_xy('button_battle_versus_private')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_01')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_02')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_03')
        auto_click(cordinate_click)
        paste_text = 'Thanks'
        pyperclip.copy(paste_text)
        pag.hotkey('ctrl', 'v')
        cordinate_click = self.get_xy('button_battle_versus_private_04')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)
        # 完成，等待刷刷刷脚本自动运行
        # endregion

        log_str = "Daily Check In task completed. Current time:" + str(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'), log_str + "\n")
        print(log_str)

    def task_auto_claim_gift_versus(self):
        """
        # 自动领取收到谢谢礼物
        """

        while not self.event_not_in_battle.is_set():
            time.sleep(1)

        time.sleep(1)

        # region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.98 * self.window_size[1],
                   duration=0.1)
        pag.middleClick()  # 先回主页，确保多任务顺利打开
        time.sleep(1)
        pag.mouseDown(button='left')
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.5 * self.window_size[1],
                   duration=0.2)
        time.sleep(0.1)
        pag.mouseUp(button='left')

        # 手动划掉任务栏，关闭程序
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.75 * self.window_size[1])
        pag.mouseDown()
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.2 * self.window_size[1],
                   duration=0.1)
        pag.mouseUp()

        # 等待10秒
        time.sleep(2)

        # 打开游戏
        cordinate_click = self.get_xy('button_ptcgp_app')
        auto_click(cordinate_click)

        # 点击标题页面
        time.sleep(1)
        cordinate_click = self.get_xy('button_ptcgp_title_page')
        auto_click(cordinate_click)
        # endregion

        # region ---自动领取收到的谢谢礼物
        cordinate_click = self.get_xy('button_gifts_01')
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_gifts_02')
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)

        time.sleep(10)
        # print('cross') # debug
        cordinate_click = self.get_xy('button_close')
        auto_click(cordinate_click)
        # endregion

        # region ---自动领取每日商店礼品
        cordinate_click = self.get_xy('button_daily_gifts_01')
        auto_click(cordinate_click)

        time.sleep(3)
        cordinate_click = self.get_xy('button_daily_gifts_02')
        auto_click(cordinate_click)

        time.sleep(3)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)

        time.sleep(10)
        cordinate_click = self.get_xy('button_close')
        auto_click(cordinate_click)
        # endregion

        # region ---自动领取每日任务礼品
        cordinate_click = self.get_xy('button_daily_missions_01')
        auto_click(cordinate_click)

        time.sleep(3)
        cordinate_click = self.get_xy('button_daily_missions_02')
        auto_click(cordinate_click)

        time.sleep(3)
        cordinate_click = self.get_xy('button_daily_missions_03')
        auto_click(cordinate_click)

        time.sleep(3)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)

        time.sleep(10)
        cordinate_click = self.get_xy('button_close')
        auto_click(cordinate_click)

        # endregion

        time.sleep(5)
        # region ---进pvp私人对战Thanks---

        # 点击 已选中的对战模式
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进pvp模式
        cordinate_click = self.get_xy('button_battle_versus')
        auto_click(cordinate_click)

        # 点击私人对战并输入密码
        cordinate_click = self.get_xy('button_battle_versus_private')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_01')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_02')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_03')
        auto_click(cordinate_click)
        paste_text = 'Thanks'
        pyperclip.copy(paste_text)
        pag.hotkey('ctrl', 'v')
        cordinate_click = self.get_xy('button_battle_versus_private_04')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)
        # 完成，等待刷刷刷脚本自动运行
        # endregion

    def task_auto_check_free_wonder_pick_versus(self):
        """
        # 自动检查免费得卡挑战

        得卡挑战 wonder pick\n
        免费挑战 Bonus Pick\n
        幸运挑战 Chansey Pick\n
        稀有挑战 Rare Pick\n
        """

        # 判断是否仍在战斗，若是，则等待到结束为止。
        while not self.event_not_in_battle.is_set():
            # print('def task_auto_check_free_wonder_pick(self)函数判断',not self.event_not_in_battle.is_set()) # debug
            # print('应该是在战斗中，应该为True') # debug
            time.sleep(1)

        time.sleep(1)
        # region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.98 * self.window_size[1],
                   duration=0.1)
        pag.middleClick()  # 先回主页，确保多任务顺利打开
        time.sleep(1)
        pag.mouseDown(button='left')
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.5 * self.window_size[1],
                   duration=0.2)
        time.sleep(0.1)
        pag.mouseUp(button='left')

        # 手动划掉任务栏，关闭程序
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.75 * self.window_size[1])
        pag.mouseDown()
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0],
                   self.window_position[1] + 0.2 * self.window_size[1],
                   duration=0.1)
        pag.mouseUp()

        # 等待10秒
        time.sleep(2)

        # 打开游戏
        cordinate_click = self.get_xy('button_ptcgp_app')
        auto_click(cordinate_click)

        # 点击标题页面
        time.sleep(1)
        cordinate_click = self.get_xy('button_ptcgp_title_page')
        auto_click(cordinate_click)
        # endregion

        # region ---检查得卡挑战---
        time.sleep(3)
        cordinate_click = self.get_xy('button_wonder_pick_01')
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_wonder_pick_02_bonus', timeOut=timedelta(seconds=30))
        if not cordinate_click == (pag.position()):
            auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_ok')
            auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_wonder_pick_03')
            auto_click(cordinate_click)

            # time.sleep(20)
            cordinate_click = self.get_xy('button_tap_to_proceed')
            auto_click(cordinate_click)

            # 不一定有添加新卡环节
            cordinate_click = self.get_xy('button_wonder_pick_04', timeOut=timedelta(seconds=30))
            if not cordinate_click == (pag.position()):
                # 有添加新卡的部分
                pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0],
                           task_manager.window_position[1] + 0.7 * task_manager.window_size[1],
                           duration=0.1)
                pag.mouseDown(button='left')
                pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0],
                           task_manager.window_position[1] + 0.4 * task_manager.window_size[1],
                           duration=0.2)
                time.sleep(0.1)
                pag.mouseUp(button='left')

                time.sleep(15)
                cordinate_click = self.get_xy('button_next')
                auto_click(cordinate_click)

            # time.sleep(15)
            cordinate_click = self.get_xy('button_tap_to_proceed')
            auto_click(cordinate_click)

        # endregion

        # region ---进pvp私人对战Thanks---
        # 点击 已选中的对战模式
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进pvp模式
        cordinate_click = self.get_xy('button_battle_versus')
        auto_click(cordinate_click)

        # 点击私人对战并输入密码
        cordinate_click = self.get_xy('button_battle_versus_private')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_01')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_02')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_03')
        auto_click(cordinate_click)
        paste_text = 'Thanks'
        pyperclip.copy(paste_text)
        pag.hotkey('ctrl', 'v')
        cordinate_click = self.get_xy('button_battle_versus_private_04')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)
        # 完成，等待刷刷刷脚本自动运行
        # endregion

    def get_xy(self, template, timeOut=timedelta(minutes=1, seconds=30), whole_screen=True):

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
    main_thread = threading.Thread(target=task_manager.routine, name="MainLoopThread")
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
        time.sleep(1)
