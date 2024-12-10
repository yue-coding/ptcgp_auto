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

"""---Instruction---
# 初级-火系\n
# 每小时自动对战15次,以求增加pvp胜场数
# 其余时间自动刷初级-火系人机胜利。\n
# 每天到点会自动暂停刷人机主线程,执行新线程特殊任务。之后再继续刷人机主线程\n

# 每天1点5分,在当前人机对战结束后,自动重启游戏,重新登录。\n
# 每当时间为25分时,在当前人机对战结束后,自动进行15次pvp战斗。(0点25分除外。30次pvp大概耗时80分钟)\n
# 每天2点25分至3点15分时, 在pvp战斗后自动领取收到谢谢礼物,每日商店礼物,每日任务礼物。\n
# 每当时间为20分时,在当前人机对战结束后,检查一次免费得卡挑战。\n

TODO \n

检测从其他设备登录, 1小时后自动重登\n
困难:自动开包。每天2次\n
困难:自动使用得卡挑战。每天2次,需要判断当前能量,需要只开1能量挑战\n
判断是否要修改get_xy获得上次点击位置。\n

更新日志\n
010: 修改pvp战斗, 使用私人对战(Private Match) "Thanks"。这样可以增加获胜概率, 而且也能给对方点赞, 满足对方获得商店券的初衷。\n
009: 增加一种routine_pvp。自动开pvp,期待对方投降,来刷胜利场数。\n
008: 统一截图名称\n

"""

class TaskManager: 
    # 类封装，脚本自动执行内容

    def __init__(self, program_start_time, current_path, pic_dir, log_dir, count_battle_solo, window_position, window_size):
        self.program_start_time = program_start_time
        self.current_path = current_path
        self.pic_dir = pic_dir
        self.log_dir = log_dir
        self.count_battle_solo = count_battle_solo
        self.window_position = window_position
        self.window_size = window_size
        self.pause_event = threading.Event()
        self.pause_event.set() # 初始化为非暂停状态
        self.event_not_in_battle = threading.Event()
        self.event_not_in_battle.set() # 初始化为非暂停状态。设置为True。.clear()设置成False

    def routine(self):
        # 点击 已选中的对战模式
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进单人模式
        cordinate_click = self.get_xy('button_battle_solo')
        auto_click(cordinate_click)

        # 点击初级对战
        cordinate_click = self.get_xy('button_battle_solo_beginner')
        auto_click(cordinate_click)

        # 完成，等待刷刷刷脚本自动运行

        #region ---自动刷人机
        timer_main_loop = 0
        while True:
            if self.pause_event.is_set():
                # print(f"[{self.program_start_time}] Main loop is running... Count: {self.count_battle_solo}, LogDir: {self.log_dir}")

                #region ---自动运行主要开刷部分---

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
                self.event_not_in_battle.clear() # 进入战斗状态
                time.sleep(150) # 对战时间，停2分30秒。

                cordinate_click = self.get_xy('button_tap_to_proceed', timeOut = timedelta(minutes=2, seconds=30)) # 胜利页面。若失败，则没有此次点击，不论是投降还是被击败。
                # print('战斗状态结束') # debug
                auto_click(cordinate_click)
                time.sleep(1)
                self.event_not_in_battle.set() # 战斗状态结束
                if not self.pause_event.is_set():
                    continue
                

                cordinate_click = self.get_xy('button_tap_to_proceed') # 己方MVP
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_tap_to_proceed') # 敌方MVP。若开局直接投降，则没有此次点击。
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                cordinate_click = self.get_xy('button_next') # 奖励页面
                if not self.pause_event.is_set():
                    continue
                auto_click(cordinate_click)

                self.count_battle_solo += 1
                current_time_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                
                loop_end_time = datetime.now()


                # log_str = "循环",count_battle_solo,"次。当前时间",current_time_str,"。本次循环用时",loop_end_time-loop_start_time,'\n' #tuple
                log_str = "循环"+str(self.count_battle_solo)+"次。当前时间"+str(current_time_str)+"。本次循环用时"+str(loop_end_time-loop_start_time)
                append_to_file(os.path.join(self.log_dir, '.txt'),log_str+'\n') # 添加log
                print(log_str)
                #endregion
                
            else:
                if np.mod(timer_main_loop,60) == 0:
                    log_str = "Main loop paused... Current time:"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n")
                    print(log_str)
                timer_main_loop += 1
                time.sleep(1)
        #endregion

    def task_daily_check_in(self):
        log_str = "Starting the Daily Check In task... Current time:"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n")
        print(log_str)

        while not self.event_not_in_battle.is_set():
            time.sleep(1)

        time.sleep(1)
        #region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0], 
                self.window_position[1] + 0.98 * self.window_size[1], 
                duration=0.1)
        pag.middleClick() # 先回主页，确保多任务顺利打开
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
        #endregion

        #region ---进单人对战-初级---

        cordinate_click = self.get_xy('button_page_battle') # 进对战页面
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_battle_solo') # 单人模式
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_battle_solo_beginner') # 初级对战
        auto_click(cordinate_click)
        #endregion

        # time.sleep(200)
        log_str = "Daily Check In task completed. Current time:"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n")
        print(log_str)

    def task_daily_auto_battle(self, auto_battle_num=15):
        log_str = "Starting the Daily Auto Battle task... Current time:"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n")
        print(log_str)

        while not self.event_not_in_battle.is_set():
            time.sleep(1)
        
        #region ---步骤说明---
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
        #endregion

        #region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0], 
                self.window_position[1] + 0.98 * self.window_size[1], 
                duration=0.1)
        pag.middleClick() # 先回主页，确保多任务顺利打开
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
        #endregion

        #region ---进入多人活动对战
        # 进对战页面
        cordinate_click = self.get_xy('button_page_battle')
        auto_click(cordinate_click)

        # 进多人模式
        cordinate_click = self.get_xy('button_battle_versus')
        auto_click(cordinate_click)

        # 进活动模式
        # cordinate_click = self.get_xy('button_battle_versus_event') # 活动对战
        # cordinate_click = self.get_xy('button_battle_versus_random') # 随机对战
        
        cordinate_click = self.get_xy('button_battle_versus_private') # 私人对战
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_01')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_02')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_battle_versus_private_03')
        auto_click(cordinate_click)
        paste_text = 'Thanks'
        pyperclip.copy(paste_text)
        pag.hotkey('ctrl','v')
        cordinate_click = self.get_xy('button_battle_versus_private_04')
        auto_click(cordinate_click)
        cordinate_click = self.get_xy('button_ok')
        auto_click(cordinate_click)
        #endregion


        #region ---自动进行多人活动对战
        count_battle_versus = 0
        while count_battle_versus < auto_battle_num:
            # 点击对战
            cordinate_click = self.get_xy('button_battle')
            auto_click(cordinate_click)
            self.event_not_in_battle.clear() # 进入战斗状态

            # 等待15秒
            time.sleep(15) # 15秒应该足够对面投降了，不投也不会投

            # 点击更多
            cordinate_click = self.get_xy('button_concede_01', timeOut = timedelta(seconds=15))
            if not cordinate_click == (pag.position()):
                # 找到的情况下
                auto_click(cordinate_click)

                # 点击投降
                cordinate_click = self.get_xy('button_concede_02', timeOut = timedelta(seconds=15))
                auto_click(cordinate_click)

                # 点击确认投降
                cordinate_click = self.get_xy('button_concede_03', timeOut = timedelta(seconds=15))
                auto_click(cordinate_click)

            cordinate_click = self.get_xy('button_ok', timeOut = timedelta(seconds=5))
            auto_click(cordinate_click)

            # 点击“点击以继续”
            cordinate_click = self.get_xy('button_tap_to_proceed')
            auto_click(cordinate_click)

            self.event_not_in_battle.set() 

            # 点击可能存在的“点击以继续”，若pvp胜利，则有个3个点击以继续。大部分时候没有，所以时间限制设置短一些
            cordinate_click = self.get_xy('button_tap_to_proceed', timeOut = timedelta(seconds=15))
            auto_click(cordinate_click)

            # 点击可能存在的“点击以继续”，若pvp胜利，则有个3个点击以继续。大部分时候没有，所以时间限制设置短一些
            cordinate_click = self.get_xy('button_tap_to_proceed', timeOut = timedelta(seconds=15))
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

            log_str = '自动对战'+str(count_battle_versus)+'次'+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
            append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n")
            print(log_str)
        #endregion


        # time.sleep(200) # debug
        log_str = f"Daily Auto Battle task completed. Battled {auto_battle_num} times. Current time:"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n")
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
            time.sleep(3) # 只有在固定时间内才领礼物，其他时候不领礼物，直接进单人对战-初级

            #region ---自动领取收到的谢谢礼物
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
            #endregion

            # 领取每日奖励
            #region ---自动领取每日商店礼品
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
            #endregion

            #region ---自动领取每日任务礼品
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

            #endregion

        #region ---进单人对战-初级
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
        #endregion

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
        #region ---重启游戏---
        # 进多任务
        pag.moveTo(self.window_position[0] + 0.5 * self.window_size[0], 
                self.window_position[1] + 0.98 * self.window_size[1], 
                duration=0.1)
        pag.middleClick() # 先回主页，确保多任务顺利打开
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
        #endregion

        #region ---检查得卡挑战---
        time.sleep(3)
        cordinate_click = self.get_xy('button_wonder_pick_01')
        auto_click(cordinate_click)

        cordinate_click = self.get_xy('button_wonder_pick_02_bonus', timeOut = timedelta(seconds=30))
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
                #有添加新卡的部分
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
        
        #endregion

        #region ---进单人对战-初级
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
        #endregion

    def get_xy(self, template, timeOut = timedelta(minutes=1, seconds=30), whole_screen=True):

        start_time = datetime.now()
        # current_time = datetime.now()
        # time_delta = current_time - start_time
        # print(time_delta,current_time)

        # while time_delta <= timedelta(minutes=2,seconds=30):
        while (datetime.now() - start_time) <= timeOut:

            # if pause_event.is_set():
            #     print("Paused during get_xy.")
            #     return (pag.position())  # 原地点一下
            # 不能在get_xy中暂停，不然daily task就不会去点了
            
            thread_name = threading.current_thread().name
            if thread_name == "MainLoopThread":
                # 主线程中需要判断是否暂停
                # print(f"Thread: {threading.current_thread().name}, pause_event: {self.pause_event.is_set()}, event_not_in_battle: {self.event_not_in_battle.is_set()}") # debug
                if not self.pause_event.is_set() and self.event_not_in_battle.is_set():
                    # and not event_not_in_battle.is_set()
                    print("Paused during get_xy for MainLoopThread.")
                    # print(not self.pause_event.is_set()) # debug
                    # print(not self.event_not_in_battle.is_set()) # debug
                    # print(not self.pause_event.is_set() and not self.event_not_in_battle.is_set()) # debug
                    return (pag.position())  # 原地点一下


            # current_time = datetime.now()
            # time_delta = current_time - start_time
            # print(time_delta,current_time)

            """ 旧获取路径方法，已经不需要了。
            # 获取当前目录路径
            if getattr(sys, 'frozen', False):  # 检查是否为打包后的可执行文件
                current_path = os.path.dirname(sys.executable)
                # print(current_path,'current_path = os.path.dirname(sys.executable)')
                current_path = sys._MEIPASS
                # print(current_path,'current_path = sys._MEIPASS')
            else:
                current_path = os.path.dirname(__file__)
                # print(current_path,'current_path = os.path.dirname(__file__)')
            # 确保pic文件夹存在
            pic_dir = os.path.join(current_path, 'pic')
            if not os.path.exists(pic_dir):
                os.makedirs(pic_dir)
            """
            # 保存截图到当前目录的pic文件夹下
            screenshot_path = os.path.join(self.pic_dir, '[log]screenshot.png')
            pag.screenshot(screenshot_path)


            # pag.screenshot("./pic/screenshot.png")
            # screenshot
            # img_screenshot = cv2.imread("./pic/screenshot.png")
            img_screenshot = cv2.imread(screenshot_path)

            # get match object
            # img_template = cv2.imread("./pic/"+template+".png")
            # img_template = cv2.imread(f"./pic/{template}.png")
            template_path = os.path.join(self.pic_dir, f'{template}.png')
            img_template = cv2.imread(template_path)

            """---debug部分---
            # print(f"Current Working Directory: {os.getcwd()}") 
            # 输出结果为
            # C:\\Users\\Andre\\Desktop\\ptcg_auto

            # 因为启动终端自动输入的命令为
            
            # PS C:\\Users\\Andre\\Desktop\\ptcg_auto>  c:; cd 'c:\\Users\\Andre\\Desktop\\ptcg_auto'; & 'c:\\Users\\Andre\\AppData\\Local\\Programs\\Python\\Python39\\python.exe' 'c:\\Users\\Andre\\.vscode\\extensions\\ms-python.debugpy-2024.12.0-win32-x64\\bundled\\libs\\debugpy\\adapter/../..\debugpy\\launcher' '7889' '--' 'C:\\Users\\Andre\\Desktop\\ptcg_auto\\auto-test\\test_ptcgp_006.py' 
            
            # 所以前面代码
            # print(current_path,'current_path = os.path.dirname(__file__)')
            # 输出的结果为 C:\\Users\\Andre\\Desktop\\ptcg_auto\\auto-test

            # 这两个地址是有区别的，因为控制台cd的位置的问题，进入git的页面，而不是py文件所在的路径。

            # 你在脚本中打印的路径之一是基于 os.getcwd()，而另一个是基于 os.path.dirname(__file__) 或 sys.executable。两者代表的路径含义不同：
            # os.getcwd() 是程序启动时的工作目录。
            # os.path.dirname(__file__) 或 sys.executable 是代码文件或解释器的实际所在路径。
            # 1. os.getcwd() 是当前工作目录
            # 2. os.path.dirname(__file__) 或 sys.executable 是脚本所在路径


            #---debug部分结束---

            #---测试match结果---
            # get match object's height and width
            height, width, channel = img_template.shape
            
            # get result
            result = cv2.matchTemplate(img_screenshot,img_template,cv2.TM_CCOEFF_NORMED)

            # 获取匹配的最大值（相似度最高的位置）
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # 如果相似度达到或超过阈值，执行程序A
                # print("相似度足够高，执行程序A")
                # 程序A的代码

                # get upper left and lower right
                # match_upper_left = cv2.minMaxLoc(result)[3]
                match_upper_left = max_loc # 一样的

                match_mid = (int(match_upper_left[0]+width/2),int(match_upper_left[1]+height/2))

                # break # 相似度足够高，退出循环
                return match_mid
                
            else:
                # 如果相似度不足，执行程序B
                print("相似度不足，执行程序B")
                # 程序B的代码
                # 程序B的代码（这里重新加载已经在循环内完成）
                time.sleep(1)
                current_time = datetime.now()
                time_delta = current_time - start_time
            
            #---测试match结果结束---

            #---额外多行注释字符转译bug---
            即便是在多行注释内，出现\\U是不行的。直接杠U会被识别为特殊字符，然后就bug了。
            您的代码中发生了 SyntaxError: (unicode error) 的问题，通常是因为字符串中包含了类似 \\U 的字符序列，Python 误将其解释为 Unicode 转义序列，但后续字符不足以形成有效的 Unicode 转义。
            

            # for thread in threading.enumerate():
            #     print(thread)
            """

            best_match_mid = self.img_match(img_screenshot, img_template, template)
            if best_match_mid:
                return best_match_mid

        
        # print('超时，鼠标原地点击一次',datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # log_dir = os.path.join(pic_dir,'log')
        # if not os.path.exists(log_dir):
        #     os.makedirs(log_dir)
        # log_str = '超时，鼠标原地点击一次。时间：'+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_str = f'超时，鼠标原地点击一次。寻找目标: {template}，当前时间'+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        append_to_file(os.path.join(self.log_dir, '.txt'),log_str+"\n") # 添加log    
        print(log_str)
        return (pag.position()) # 原地点一下

    def img_match(self, img_screenshot, img_template, template):
    # def img_match(self, img_screenshot, img_template, pic_dir, log_dir, template, count):

        #region ---debug部分---
        # # 检查图像是否加载成功
        # if img_screenshot is None:
        #     raise ValueError(f"Screenshot image could not be loaded from the provided path.")
        # if img_template is None:
        #     raise ValueError(f"Template image could not be loaded for template: {template}")

        # # 确保图像类型一致（转换为灰度图）
        # if len(img_screenshot.shape) == 3:  # 彩色图像
        #     img_screenshot = cv2.cvtColor(img_screenshot, cv2.COLOR_BGR2GRAY)
        # if len(img_template.shape) == 3:  # 彩色图像
        #     img_template = cv2.cvtColor(img_template, cv2.COLOR_BGR2GRAY)

        # # 打印图像信息（调试用）
        # print(f"Screenshot shape: {img_screenshot.shape}, dtype: {img_screenshot.dtype}")
        # print(f"Template shape: {img_template.shape}, dtype: {img_template.dtype}")
        #endregion

        # 设定一个相似度阈值，比如0.8
        threshold = 0.8
        
        # 尝试多个缩放比例
        scale_factors = [1.0, 1.05, 1.1, 1.15, 0.95, 0.90, 0.85]  # 添加适当的缩放比例
        best_match_val = 0
        best_match_mid = None

        for scale in scale_factors:
            # 根据比例缩放模板
            # img_template = cv2.imread(f"./pic/{template}.png")
            scaled_template = cv2.resize(img_template, (0, 0), fx=scale, fy=scale)
            # print(threading.current_thread().name, scaled_template.shape) # debug
            height, width, channel = scaled_template.shape
            # height, width = scaled_template.shape # debug，不知道为什么有的时候3个报错，有的时候2个报错。彩色图像是3，灰白图像是2个参数。因为前面debug把彩色图像转成灰白了，所以3个报错。但是应该是一般是彩色图像所以是3个。
            
            # 进行模板匹配
            result = cv2.matchTemplate(img_screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_match_val:  # 更新最佳匹配结果
                best_match_val = max_val
                best_match_mid = (int(max_loc[0] + width / 2), int(max_loc[1] + height / 2))

            if best_match_val >= threshold:
                best_match_pic_log_path = os.path.join(self.pic_dir+"/log/"+datetime.now().strftime("%Y_%m_%d_%H_%M_%S_第"+str(self.count_battle_solo+1)+"次循环.png"))
                pag.screenshot(best_match_pic_log_path,(max_loc[0],max_loc[1],width,height))
                
                log_str = f"找到最佳相似度，当前最佳相似度为{best_match_val:.2f}，缩放比例为"+str(scale)+f"。寻找目标: {template}，当前时间"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                append_to_file(os.path.join(self.log_dir, '.txt'), log_str+"\n")
                print(log_str)
                return best_match_mid  # 找到满足阈值的匹配

        
        log_str = f"相似度不足，当前最佳相似度为{best_match_val:.2f}，寻找目标: {template}"+"。当前时间"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        append_to_file(os.path.join(log_dir, '.txt'),log_str+"\n")
        if threading.current_thread().name == 'DebugMissionThread':
            print(log_str)
        # print(log_str)
        return None

def append_to_file(filename, content):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(content)

def auto_click(cordinate_click):
    if cordinate_click[0] > 0 and cordinate_click[1] > 0:
        pag.moveTo(cordinate_click[0], cordinate_click[1], duration=0.1)
    else:
        print("Invalid coordinates, skipping move.")
    # pag.moveTo(cordinate_click[0],cordinate_click[1],duration=0.1)
    pag.click()
    pag.moveTo(10,10)
    time.sleep(1)

def scheduler(task_manager):
    # 调度器函数

    task_daily_check_in_done = False
    task_daily_auto_battle_done = False
    while True:
        now = datetime.now()
        # print(now.hour, now.minute, now.second) # debug
        
        if now.hour == 1 and now.minute == 5 and not task_daily_check_in_done:
            log_str = "Pausing main loop for daily task... 当前时间"+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
            append_to_file(os.path.join(task_manager.log_dir, '.txt'),log_str+"\n")
            print(log_str)

            task_manager.pause_event.clear()
            task_manager.task_daily_check_in() # TODO
            task_manager.pause_event.set()
            task_daily_check_in_done = True
            # time.sleep(60) # 确保时间进到下一分钟，而不会再次执行此程序 # 不需要了，因为一定会过这个时间

        if now.hour != 0 and now.minute == 25:
            print("Pausing main loop for temporary task...")
            task_manager.pause_event.clear()
            task_manager.task_daily_auto_battle()
            task_manager.task_auto_claim_gift()
            task_manager.pause_event.set()
            # task_daily_auto_battle_done = True 
            # time.sleep(60) # 不需要了，因为一定会过这个时间

        if now.hour == 0 and now.minute == 0:
            task_daily_check_in_done = False
            task_daily_auto_battle_done = False
        
        if now.minute == 20:
            print("Pausing main loop for Wonder Pick...")
            task_manager.pause_event.clear()
            task_manager.task_auto_check_free_wonder_pick()
            task_manager.pause_event.set()

            # time.sleep(60) # 不需要了，因为一定会过这个时间

        #region ---特殊状态检测+重启---
        # current_status, button_mid = status_checker(task_manager)
        # print(current_status, button_mid) # debug
        # if current_status:
        #     # TODO 改成另外两个特殊状态时不检测是否卡住
        #     time.sleep(180) # 等待一会，以便double check确实是卡住了
        #     current_status_double_check, button_mid_double_check = status_checker(task_manager)
        #     if current_status_double_check:
        #         task_manager.pause_event.clear()
        #         log_str = '检测到特殊状态：'+current_status+' 再次检测：'+current_status_double_check
        #         append_to_file(os.path.join(task_manager.log_dir, '.txt'),log_str+"\n")
        #         print(log_str)
        #         time.sleep(10)

        #         # print(current_status, button_mid) # debug
        #         # auto_click(button_mid_double_check) # 直接改成重启软件好了。或者是写多个if状态，根据template_list来判断当前到底卡哪里了

        #         #region ---重启游戏---
        #         # 进多任务
        #         pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0], 
        #                 task_manager.window_position[1] + 0.98 * task_manager.window_size[1], 
        #                 duration=0.1)
        #         pag.middleClick() # 先回主页，确保多任务顺利打开
        #         time.sleep(1)
        #         pag.mouseDown(button='left')
        #         pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0], 
        #                 task_manager.window_position[1] + 0.5 * task_manager.window_size[1], 
        #                 duration=0.2)
        #         time.sleep(0.1)
        #         pag.mouseUp(button='left')

        #         # 手动划掉任务栏，关闭程序
        #         pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0], 
        #                 task_manager.window_position[1] + 0.75 * task_manager.window_size[1])
        #         pag.mouseDown()
        #         pag.moveTo(task_manager.window_position[0] + 0.5 * task_manager.window_size[0], 
        #                 task_manager.window_position[1] + 0.2 * task_manager.window_size[1], 
        #                 duration=0.1)
        #         pag.mouseUp()

        #         # 等待10秒
        #         time.sleep(10)

        #         # 打开游戏
        #         start_time = datetime.now()
        #         cordinate_click = get_xy('button_ptcgp_app',start_time,  task_manager.current_path, task_manager.pic_dir, task_manager.log_dir, task_manager.count_battle_solo, task_manager.pause_event)
        #         auto_click(cordinate_click)

        #         # 点击标题页面
        #         time.sleep(3)
        #         start_time = datetime.now()
        #         cordinate_click = get_xy('button_ptcgp_title_page',start_time,  task_manager.current_path, task_manager.pic_dir, task_manager.log_dir, task_manager.count_battle_solo, task_manager.pause_event)
        #         auto_click(cordinate_click)
        #         #endregion

        #         #region ---进单人对战-初级
        #         # 点击 对战模式
        #         time.sleep(15)
        #         start_time = datetime.now()
        #         cordinate_click = get_xy('button_page_battle',start_time,  task_manager.current_path, task_manager.pic_dir, task_manager.log_dir, task_manager.count_battle_solo, task_manager.pause_event)
        #         auto_click(cordinate_click)

        #         # 进单人模式
        #         start_time = datetime.now()
        #         cordinate_click = get_xy('button_battle_solo',start_time,  task_manager.current_path, task_manager.pic_dir, task_manager.log_dir, task_manager.count_battle_solo, task_manager.pause_event)
        #         auto_click(cordinate_click)

        #         # 点击初级对战
        #         start_time = datetime.now()
        #         cordinate_click = get_xy('button_battle_solo_beginner',start_time,  task_manager.current_path, task_manager.pic_dir, task_manager.log_dir, task_manager.count_battle_solo, task_manager.pause_event)
        #         auto_click(cordinate_click)

        #         # 完成，等待刷刷刷脚本自动运行
        #         #endregion
                
        #         task_manager.pause_event.set()
        #     else:
        #         print('误判！')

        #endregion

        time.sleep(1) # 每秒判断一次

def status_checker(task_manager):      
    screenshot_path = os.path.join(task_manager.pic_dir, '[log]screenshot_status_checker.png')
    pag.screenshot(screenshot_path)
    img_screenshot = cv2.imread(screenshot_path)
    # print(img_screenshot)
    
    template_list = [
        'ptcgp_date_change_01', # OK按钮
        'button_ptcgp_app', # 未打开游戏
        'button_ptcgp_title_page', # 标题页面
        'button_tap_to_proceed', # 点击来继续
        'button_next'] # 继续按钮
    for template in template_list:
        template_path = os.path.join(task_manager.pic_dir, f'{template}.png')
        img_template = cv2.imread(template_path)
        
        best_match_mid = task_manager.img_match(img_screenshot, img_template, template)


        if best_match_mid:
            return template, best_match_mid
    
    return None, None

def get_window_position(log_dir):
    # # 获取所有窗口标题
    # windows = pgw.getAllTitles()
    # print("所有窗口标题:", windows)

    # 获取特定窗口
    window = pgw.getWindowsWithTitle('PCLM10')[0]  # 以标题部分匹配，如'PCLM10'

    # 获取窗口的位置和大小
    log_str = "窗口左上角坐标: "+str(window.topleft) # 左上角坐标
    append_to_file(os.path.join(log_dir, '.txt'),log_str+"\n")
    print(log_str)

    log_str = "窗口大小: "+str(window.size) # 宽度和高度
    append_to_file(os.path.join(log_dir, '.txt'),log_str+"\n")
    print(log_str)

    log_str = "窗口右下角坐标: "+str(window.bottomright) # 右下角坐标
    append_to_file(os.path.join(log_dir, '.txt'),log_str+"\n")
    print(log_str)

    return window.topleft,window.size

def debug_mission(task_manager):
    # task_manager.routine()
    # task_manager.task_daily_check_in()
    task_manager.task_daily_auto_battle()
    # task_manager.task_auto_claim_gift(start_hour=2, start_minute=25, end_hour=3, end_minute=15)
    # task_manager.task_auto_check_free_wonder_pick()

if __name__ == "__main__":
    # 启动主线程和调度器线程


    #region---启动程序，初始化---


    # 获取当前目录路径
    if getattr(sys, 'frozen', False):  # 检查是否为打包后的可执行文件
        current_path = os.path.dirname(sys.executable)
        # print(current_path,'current_path = os.path.dirname(sys.executable)')
        current_path = sys._MEIPASS
        # print(current_path,'current_path = sys._MEIPASS')
    else:
        current_path = os.path.dirname(__file__)
        # print(current_path,'current_path = os.path.dirname(__file__)')
        # current_path = os.getcwd()
        # TODO 需要确认这几个获得current_path方法有什么区别。
    # 确保pic文件夹存在
    pic_dir = os.path.join(current_path, 'pic')
    if not os.path.exists(pic_dir):
        os.makedirs(pic_dir)
    # 确保log文件夹存在
    log_dir = os.path.join(pic_dir,'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_str = '程序启动. '+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
    append_to_file(os.path.join(log_dir, '.txt'),"\n"+log_str+"\n") # 添加log
    print(log_str)

    window_position, window_size = get_window_position(log_dir)
    
    program_start_time = datetime.now()


    
    count_battle_solo = 0 #循环计数器
    
    # return program_start_time,current_path,pic_dir,log_dir
    # routine(program_start_time,log_dir,count_battle_solo) # 开始进routine循环 # 更新多线程后不需要直接进循环。

    #endregion ---初始化结束---

    # 用于控制主线程的暂停和恢复.初始化 pause_event
    # pause_event = threading.Event()
    

    task_manager = TaskManager(program_start_time, current_path, pic_dir, log_dir, count_battle_solo, window_position, window_size) # 代码实现了参数从全局范围传递到 class TaskManager 的过程 


    # 设置暂停事件为未暂停
    # task_manager.pause_event.set() 



    # 启动主循环线程
    main_thread = threading.Thread(target=task_manager.routine, name="MainLoopThread")
    main_thread.daemon = True
    main_thread.start()
    

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=scheduler, args=(task_manager,), name="SchedulerThread")
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # 启动debug单任务线程
    # scheduler_thread = threading.Thread(target=debug_mission, args=(task_manager,), name="DebugMissionThread")
    # scheduler_thread.daemon = True
    # scheduler_thread.start()




    # 保持主程序运行
    while True:
        time.sleep(1)

#region ---备注

#region python输入点击鼠标侧键

# 使用 pynput 模拟鼠标侧键

# from pynput.mouse import Button, Controller

# mouse = Controller()

# # 模拟点击 XBUTTON1（后退键）
# mouse.press(Button.xbutton1)
# mouse.release(Button.xbutton1)

# # 模拟点击 XBUTTON2（前进键）
# mouse.press(Button.xbutton2)
# mouse.release(Button.xbutton2)


#endregion

#region 为什么我的调度器函数内，用pause_event.set()来表示暂停主程序，用.clear()表示恢复主程序呢? (已修改)

# 你的代码中用 pause_event.set() 表示暂停主程序、用 pause_event.clear() 表示恢复主程序的逻辑其实是反常的。原因在于 threading.Event 的语义：

# set(): 将事件标记为“已触发”。在wait()时不会阻塞，线程会继续运行。
# clear(): 将事件标记为“未触发”。在wait()时会阻塞，线程暂停。
# 因此，在通常的用法中：

# 使用 clear() 来暂停线程。
# 使用 set() 来恢复线程。
#endregion

#region 为什么当到时间点，执行其他task之后，routine会从头开始循环呢？

# 在你的代码中，当到达时间点时，调度器会通过 pause_event.set() 暂停 routine() 的执行，并在完成其他任务后通过 pause_event.clear() 恢复执行。这会导致 routine() 的循环从检查点继续，而不是从中断的位置接着执行。如果看起来是从头开始循环，那是因为 routine() 的循环结构和逻辑使其在恢复后重新开始一个完整的循环。

# 以下是为什么会出现这种现象的原因分析：

# 1. routine() 的循环结构设计
# routine() 是一个 while True 的无限循环：

# python
# 复制代码
# def routine(self):
#     start_time = self.program_start_time
#     while True:
#         if not self.pause_event.is_set():
#             # 主任务逻辑
#         else:
#             print("Main loop paused...")
#             time.sleep(1)
# pause_event.is_set() 的状态控制：
# 在调度器中，pause_event.set() 暂停主循环。
# routine() 发现 pause_event.is_set() 为 True，进入 else 分支执行 print("Main loop paused...") 和 time.sleep(1)。
# 调度器完成任务后，调用 pause_event.clear()，routine() 重新进入 if not self.pause_event.is_set() 的分支，开始下一次完整的循环。

# 2. 调度器与 pause_event 的控制逻辑
# 调度器通过设置和清除 pause_event 来通知 routine() 暂停或继续，但 routine() 的循环并没有中断，而是等待信号恢复。

# python
# 复制代码
# def scheduler(task_manager):
#     if now.hour == 20 and now.minute == 47:
#         task_manager.pause_event.set()  # 暂停主循环
#         task_manager.task_daily_check_in()
#         task_manager.pause_event.clear()  # 恢复主循环
# 当 pause_event.clear() 被调用后，routine() 的无限循环继续从头开始新一轮检查。
# 这并非真正的“从头开始”，而是循环的自然特性——它的每次迭代都是独立的。

#endregion

#region ---旧routine方法---

# def routine(program_start_time,log_dir,count):
#     start_time = program_start_time
#     while True:
#         loop_start_time = datetime.now()

#         """---识别并滚动屏幕---
#         # ---识别并滚动屏幕---
#         cordinate_scroll_start = get_xy('ptcgp_001_master_water',start_time,count) 
#         start_time = datetime.now()
#         cordinate_scroll_end = get_xy('ptcgp_001_1',start_time,count) 
#         pag.moveTo(cordinate_scroll_start)
#         pag.mouseDown()
#         pag.moveTo(cordinate_scroll_end,duration=1)
#         pag.mouseUp()
#         time.sleep(1) # 滚动后可能还有滑动动画
#         """

#         start_time = datetime.now()
#         cordinate_click = get_xy('ptcgp_002_start_fire',start_time,count) 
#         auto_click(cordinate_click)

#         start_time = datetime.now()
#         cordinate_click = get_xy('button_auto_on',start_time,count) 
#         auto_click(cordinate_click)
        
#         start_time = datetime.now()
#         cordinate_click = get_xy('button_battle',start_time,count)
#         auto_click(cordinate_click)
#         time.sleep(150) # 对战时间，停2分30秒。

#         start_time = datetime.now()
#         cordinate_click = get_xy('button_tap_to_proceed',start_time,count) # 胜利页面。若失败，则没有此次点击，不论是投降还是被击败。
#         auto_click(cordinate_click)

#         start_time = datetime.now()
#         cordinate_click = get_xy('button_tap_to_proceed',start_time,count) # 己方MVP
#         auto_click(cordinate_click)

#         start_time = datetime.now()
#         cordinate_click = get_xy('button_tap_to_proceed',start_time,count) # 敌方MVP。若开局直接投降，则没有此次点击。
#         auto_click(cordinate_click)

#         start_time = datetime.now()
#         cordinate_click = get_xy('button_next',start_time,count) # 奖励页面
#         auto_click(cordinate_click)

#         count += 1
#         current_time_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        
#         loop_end_time = datetime.now()
#         print("循环",count,"次。当前时间",current_time_str,"。本次循环用时",loop_end_time-loop_start_time)

#         # log_str = "循环",count,"次。当前时间",current_time_str,"。本次循环用时",loop_end_time-loop_start_time,'\n' #tuple
#         log_str = "循环"+str(count)+"次。当前时间"+str(current_time_str)+"。本次循环用时"+str(loop_end_time-loop_start_time)+'\n'
        
#         append_to_file(os.path.join(log_dir, '.txt'),log_str) # 添加log

#endregion


"""---旧版本---
# 用于控制主线程的暂停和恢复
pause_event = threading.Event()

# 主线程的任务（模拟主循环）
def main_loop():
    while True:
        if not pause_event.is_set():
            print("Main loop is running...")
            time.sleep(1)  # 模拟工作
        else:
            print("Main loop paused...")
            time.sleep(1)  # 暂停时等待恢复信号

# 需要在凌晨 1:05 执行的任务
def daily_task():
    print("Starting the daily task...")
    time.sleep(10)  # 模拟耗时任务
    print("Daily task completed.")

# 定时检查是否需要暂停主线程
def scheduler():
    while True:
        now = datetime.datetime.now()
        # 如果当前时间是凌晨 1:05
        if now.hour == 1 and now.minute == 5:
            print("Pausing main loop for daily task...")
            pause_event.set()  # 暂停主循环
            daily_task()       # 执行每日任务
            pause_event.clear()  # 恢复主循环
            print("Main loop reset and restarted.")
            time.sleep(60)  # 确保不会重复触发
        time.sleep(1)  # 每秒检查一次时间
"""


#region 我的程序只有一个<_MainThread(MainThread, started 2492)>线程，我将其称之为主线程。主线程主要任务就是一个while True循环。

# 现在我希望，每到每天凌晨1点5分时，暂停主线程的while循环，执行另外一个程序。并且在另外一个程序执行完毕后，不论原本主线程的while循环执行到哪里，都从头开始重新执行while循环。

# 怎么写？



# 要实现你的需求，可以通过以下步骤完成：

# 主线程持续运行 while True 循环。
# 在每天凌晨 1:05 时，主线程暂停执行，并运行另一个程序。
# 另一个程序执行完毕后，主线程的循环从头开始。
# 可以通过条件控制和事件机制实现。这是一种典型的“暂停-恢复”操作，以下是实现方案：
#endregion


#region 如果我需要额外在早上8点执行第三个临时程序，应该怎么写？



# 如果需要额外在早上 8 点执行一个第三个程序（称为 temporary_task），你可以在 scheduler 函数中添加一个额外的时间检查逻辑。以下是修改的完整代码：
#endregion


#region 如果我的main_loop需要传入参数program_start_time,log_dir,count。daily_task和temporary_task也需要传入log_dir怎么办



# 方法 3：通过类封装共享参数
# 使用类将共享参数封装成属性，让各个方法访问这些参数。
#endregion


#region 初始化的参数，是怎么传到class TaskManager中的呢？



# 总结
# 构造方法（__init__）是参数传递的关键：
# 它在类实例化时被调用，初始化实例变量。
# 全局变量传递：
# 全局定义的 program_start_time、log_dir 和 count 被传递给 TaskManager 的构造方法。
# 类内访问：
# 通过 self.<变量名>，类的其他方法可以随时访问这些参数。
#endregion


#region 这个程序，if __name__ == "__main__":最后的time.sleep(1)，如果改成time.sleep(100000)会怎么样呢？主线程会也跟着停吗



# 是的，如果你将程序末尾的 `time.sleep(1)` 改成 `time.sleep(100000)`，主线程也会进入长时间的休眠状态，但这并不会影响你的程序中运行的守护线程（`main_loop` 和 `scheduler`）。以下是原因和影响的详细解释：

# ---

# ### **1. 主线程的行为**

# 在你的程序中，`time.sleep(1)` 的作用是保持主线程的运行，而守护线程则在后台持续工作。如果你改成 `time.sleep(100000)`：

# - **主线程行为**：主线程进入休眠状态，执行到 `time.sleep(100000)` 后，会暂停，直到 100,000 秒（约 27.8 小时）后才会继续执行后续代码。
# - **守护线程行为**：由于守护线程独立于主线程，它们会继续运行 `main_loop` 和 `scheduler`，不受主线程休眠的影响。

# 主线程的休眠只是防止程序退出，并不阻止其他线程的执行。

# ---

# ### **2. 守护线程的运行**

# 你的 `main_loop` 和 `scheduler` 被设置为**守护线程**：

# ```python
# main_thread.daemon = True
# scheduler_thread.daemon = True
# ```

# - **守护线程的特性**：
#   - 守护线程会在主线程运行期间持续工作。
#   - 一旦主线程结束，所有守护线程会被立即终止。

# 因此，只要主线程未退出，无论主线程在做什么（如休眠），守护线程都可以正常运行。

# ---

# ### **3. 为什么不建议用 `time.sleep(100000)`？**

# 虽然程序可以正常运行，但这种设置存在以下问题：

# 1. **可维护性差**：
#    - 一个显而易见的逻辑问题是，`time.sleep(100000)` 并不直观，未来维护代码的人可能无法理解这个数字的意义。
#    - 如果需要更改程序逻辑，比如需要终止主线程，修改这个值会很不方便。

# 2. **不灵活**：
#    - 如果你的程序需要动态调整主线程的运行状态（如增加新的功能），主线程正在休眠可能会导致调试和控制困难。

# 3. **无法响应中断**：
#    - 主线程在休眠时无法立即响应外部中断（如信号、用户输入等）。

# ---

# ### **推荐的替代方案**

# 为了更灵活地保持主线程运行，可以使用以下方法：

# #### 方法 1：无限循环 + 短时间休眠
# 保持 `time.sleep(1)`，因为它是常见的“阻塞主线程”方式，且每秒允许主线程有机会响应外部事件。

# ```python
# while True:
#     time.sleep(1)
# ```

# - **优点**：主线程在每秒钟可被中断（例如通过 `KeyboardInterrupt` 或外部信号）。
# - **适用场景**：程序需要长时间运行，并可能需要调试或扩展。

# ---

# #### 方法 2：使用 `thread.join()` 等待守护线程

# 你可以将 `main_loop` 和 `scheduler` 设置为**非守护线程**，然后使用 `thread.join()` 主动等待它们完成任务。

# ```python
# main_thread = threading.Thread(target=task_manager.main_loop, name="MainLoopThread")
# scheduler_thread = threading.Thread(target=scheduler, args=(task_manager,), name="SchedulerThread")

# # 不设置为守护线程
# main_thread.start()
# scheduler_thread.start()

# # 主线程等待子线程完成
# main_thread.join()
# scheduler_thread.join()
# ```

# - **优点**：更加明确地表达主线程依赖于子线程的运行状态。
# - **缺点**：如果子线程包含无限循环（如你的程序），主线程也会永远等待，仍需外部终止信号。

# ---

# #### 方法 3：使用条件变量（`threading.Condition`）

# 如果希望主线程更灵活地运行并等待某些事件，可以使用 `threading.Condition` 或其他同步机制代替简单的 `time.sleep`。

# ---

# ### **总结**

# - 如果你改成 `time.sleep(100000)`，程序仍然会正常运行，但主线程将长时间进入休眠状态。
# - 守护线程（`main_loop` 和 `scheduler`）不会受到主线程休眠的影响，它们会继续正常运行。
# - **最佳实践**是使用 `time.sleep(1)` 或其他循环机制，保持主线程的灵活性和可维护性。
#endregion


#region 如果修改成time.sleep(100000)，会不会减小性能损耗呢？毕竟程序停止了？



# 将 time.sleep(1) 修改为 time.sleep(100000) 对性能的影响是极小的，但可能会略微减少主线程的资源消耗，因为主线程在休眠期间不需要频繁地被唤醒。不过，这种优化通常是微不足道的，因为 time.sleep 本身是一种阻塞调用，不占用 CPU 资源。

# 性能分析：为什么变化很小？
# time.sleep 的工作机制

# 当调用 time.sleep 时，线程进入休眠状态，操作系统将该线程标记为“非活动”。
# 被标记为非活动的线程不会占用 CPU 时间，直到设定的时间到了才会重新变为“活动”。
# 因此，无论是 sleep(1) 还是 sleep(100000)，线程都不会消耗 CPU。
# 主要性能损耗来自守护线程

# 在你的程序中，真正的工作是由两个守护线程完成的：main_loop 和 scheduler。
# 守护线程的任务（如定时检查和循环运行）才会对 CPU 和内存产生主要负担。
# 主线程的 time.sleep 只用于阻塞主线程，不会显著影响性能。
# 时间精度与资源消耗

# 使用较短的 sleep（如 time.sleep(1)) 时，主线程会更频繁地被操作系统唤醒。
# 这种频繁唤醒对 CPU 的额外消耗通常是微不足道的，尤其是在现代多核系统中。
# 会减少性能损耗的场景
# 修改 time.sleep(1) 为 time.sleep(100000) 的确可以在以下特定场景下减少一些性能损耗：

# 程序的频繁调度

# 如果程序中有大量线程，频繁唤醒主线程可能稍微增加线程切换的开销。
# 将 time.sleep 的间隔变长可以减少线程调度的频率，从而优化资源使用。
# 资源竞争激烈的环境

# 在资源竞争激烈的环境中（例如许多程序同时运行），减少主线程被唤醒的次数可能有助于释放更多 CPU 时间给其他线程。
# 减少性能损耗的更优策略
# 如果关注性能，以下策略可能更加有效：

# 1. 让主线程退出而不是休眠
# 如果主线程的唯一目的是阻止程序退出，可以让主线程在子线程完成任务后自动退出。
# 修改方法：
# 将守护线程改为非守护线程。
#endregion





#endregion