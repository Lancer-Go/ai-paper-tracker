# -*- coding: utf-8 -*-
"""
4399 美食大战老鼠 — 批量账号背包截图自动化工具

使用方式:
  1. 首次校准:       python game_screenshotter.py --calibrate
  2. 运行截图:       python game_screenshotter.py
  3. 从指定编号恢复:  python game_screenshotter.py --start 15
"""

import json
import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

import pyautogui
import pygetwindow as gw
from PIL import Image

# ═══════════════════════════════════════════════
#  常量配置
# ═══════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
ACCOUNTS_FILE = SCRIPT_DIR / "accounts.txt"
OUTPUT_DIR = SCRIPT_DIR / "game-screenshots"
CLIENT_EXE = r"C:\Users\Administrator\Desktop\4399美食大战老鼠.exe"

# 微端窗口标题关键字
LOGIN_WINDOW_TITLE = "微端登录页"
GAME_WINDOW_TITLE = "美食大战老鼠"

# 三个背包 Tab
BACKPACK_TABS = ["装备", "防御卡", "道具"]

# PyAutoGUI 安全设置
pyautogui.PAUSE = 0.3          # 每次操作间隔 0.3s
pyautogui.FAILSAFE = True      # 鼠标移到左上角紧急停止

# ═══════════════════════════════════════════════
#  工具函数
# ═══════════════════════════════════════════════

def log(msg):
    """带时间戳的日志输出"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def find_window(title_keyword, timeout=10):
    """按标题关键字查找窗口，支持超时等待"""
    start = time.time()
    while time.time() - start < timeout:
        windows = gw.getWindowsWithTitle(title_keyword)
        # 过滤掉不相关的匹配（如cmd窗口）
        for w in windows:
            if title_keyword in w.title:
                return w
        time.sleep(0.5)
    return None


def activate_window(window):
    """激活并置顶窗口"""
    try:
        if window.isMinimized:
            window.restore()
        window.activate()
        time.sleep(0.3)
    except Exception as e:
        log(f"⚠️ 激活窗口失败: {e}")


def click_at(config, key, window=None):
    """点击配置中指定的相对坐标位置"""
    coords = config["coords"][key]
    if window:
        x = window.left + coords["x"]
        y = window.top + coords["y"]
    else:
        x, y = coords["x"], coords["y"]
    pyautogui.click(x, y)
    time.sleep(0.2)


def click_absolute(x, y):
    """点击绝对坐标"""
    pyautogui.click(x, y)
    time.sleep(0.2)


def clear_and_type(text):
    """清空输入框并输入文本"""
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("delete")
    time.sleep(0.1)
    # 使用 pyperclip 方式输入中文/特殊字符
    import pyperclip
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)


def type_text_safe(text):
    """安全输入文本（通过剪贴板，支持任意字符）"""
    try:
        import pyperclip
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
    except ImportError:
        # 降级：逐字符输入（仅支持 ASCII）
        pyautogui.typewrite(text, interval=0.05)
    time.sleep(0.2)


def screenshot_region(window, area):
    """根据给定的 area 截取该区域的相对像素"""
    left = window.left + area["x1"]
    top = window.top + area["y1"]
    width = area["x2"] - area["x1"]
    height = area["y2"] - area["y1"]
    return pyautogui.screenshot(region=(left, top, width, height))


def images_are_same(img1, img2, threshold=0.99):
    """比较两张图是否几乎相同（用于检测滚动到底）"""
    if img1.size != img2.size:
        return False
    
    # 转换为 numpy 数组进行快速比对
    import numpy as np
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    same = np.sum(arr1 == arr2)
    total = arr1.size
    return (same / total) >= threshold


# ═══════════════════════════════════════════════
#  坐标校准模块
# ═══════════════════════════════════════════════

def calibrate():
    """交互式坐标校准"""
    print("=" * 60)
    print("  坐标校准模式")
    print("=" * 60)
    print()

    # 尝试加载已有配置，避免全量覆盖
    config = {
        "client_exe": CLIENT_EXE,
        "server_id": "1",
        "game_load_wait": 15,
        "tab_load_wait": 10,
        "captcha_detect_timeout": 15
    }
    coords = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                config.update(loaded)
                coords = loaded.get("coords", {})
        except Exception as e:
            log(f"读取旧配置失败，将重新创建: {e}")

    # 分组定义校准项
    groups = {
        "1": {
            "name": "登录页面",
            "window": LOGIN_WINDOW_TITLE,
            "items": [
                ("username_field", "用户名输入框", ""),
                ("password_field", "密码输入框", ""),
                ("login_button", "登录按钮", "")
            ]
        },
        "2": {
            "name": "选服页面（有历史记录的布局）",
            "window": LOGIN_WINDOW_TITLE,
            "items": [
                ("server_input", "服务器编号输入框（右上角可以填数字的那个框）", ""),
                ("server_enter", "「进入」按钮", "")
            ]
        },
        "2b": {
            "name": "选服页面（无历史记录的布局）",
            "window": LOGIN_WINDOW_TITLE,
            "items": [
                ("view_all_servers", "「查看全部服务器>>」链接", "👉 右侧偏上的「查看全部服务器>>」文字"),
                ("server_input_alt", "展开后的服务器编号输入框", "👉 先点了查看全部服务器后，再指向输入框"),
                ("server_enter_alt", "展开后的「进入」按钮", "")
            ]
        },
        "3": {
            "name": "游戏内：背包与弹窗",
            "window": GAME_WINDOW_TITLE,
            "items": [
                ("popup_confirm", "系统弹窗「确定」按钮", "👉 进游戏后弹出的防沉迷/公告框的确定按钮"),
                ("popup_holiday_close", "假期特惠弹窗右上角 ✕ 关闭按钮", "👉 橙色圆形 X 按钮，在假期特惠页面右上角"),
                ("backpack_button", "底部「背包」按钮", ""),
                ("sort_button", "背包内「整理」按钮", "👉 背包右下角的“整理”按钮"),
                ("tab_equipment", "背包内「装备」Tab", ""),
                ("tab_defense", "背包内「防御卡」Tab", ""),
                ("tab_items", "背包内「道具」Tab", "")
            ]
        },
        "4": {
            "name": "游戏内：各分类背包独立区域校准",
            "window": GAME_WINDOW_TITLE,
            "items": [
                ("装备_area_topleft", "【装备】格子区域左上角", "截图区域左上角的那个角"),
                ("装备_area_bottomright", "【装备】格子区域右下角", "截图区域右下角的那个角"),
                ("装备_arrow", "【装备】向下滚动箭头或滑道", "滚动条下面那个空白骨架或者向下的箭头"),
                ("防御卡_area_topleft", "【防御卡】格子区域左上角", ""),
                ("防御卡_area_bottomright", "【防御卡】格子区域右下角", ""),
                ("防御卡_arrow", "【防御卡】向下滚动箭头或滑道", ""),
                ("道具_area_topleft", "【道具】格子区域左上角", ""),
                ("道具_area_bottomright", "【道具】格子区域右下角", ""),
                ("道具_arrow", "【道具】向下滚动箭头或滑道", ""),
            ] 
        }
    }

    print("请选择要重新校准的内容：")
    print("  0. 校准全部流程 (首次使用推荐)")
    for k, v in groups.items():
        print(f"  {k}. 仅校准 {v['name']}")
    print("  q. 退出校准")
    print()
    
    choice = input("👉 请输入序号后回车: ").strip().lower()
    if choice == 'q':
        return
        
    keys_to_process = []
    if choice == '0':
        keys_to_process = ["1", "2", "2b", "3", "4"]
    elif choice in groups:
        keys_to_process = [choice]
    else:
        print("❌ 无效的选项")
        return

    def record_point(wx, wy, key, label, hint=""):
        if hint:
            print(f"  💡 提示: {hint}")
        input(f"  👉 将鼠标移到【{label}】上，等待按 Enter 记录...")
        pos = pyautogui.position()
        rel_x = pos[0] - wx
        rel_y = pos[1] - wy
        coords[key] = {"x": rel_x, "y": rel_y}
        print(f"     ✅ 已记录: 相对坐标 ({rel_x}, {rel_y})")
        print()

    for k in keys_to_process:
        group = groups[k]
        print(f"─── {group['name']} ───")
        
        if k == "2":
            print("请手动登录一个账号，进入【选服页面】后再继续。")
            input("准备好后按 Enter ...")
            print()
        elif k in ["3", "4"]:
            print("请手动选服进入游戏，等待完全加载。")
            if k == "4":
                print("请务必【打开背包】后再继续。")
            input("准备好后按 Enter ...")
            print()
            
        # 查找窗口
        window_title = group['window']
        window = find_window(window_title, timeout=5)
        # 兼容选服页可能标题变了的情况
        if not window and window_title == LOGIN_WINDOW_TITLE:
            window = find_window(GAME_WINDOW_TITLE, timeout=2)
            
        if not window:
            print(f"❌ 未找到对应窗口 ({window_title})，请确认界面正确！")
            return
            
        activate_window(window)
        wx, wy = window.left, window.top
        print(f"✅ 定位到窗口，位置: ({wx}, {wy})")
        print()
        
        for item_key, label, hint in group['items']:
            record_point(wx, wy, item_key, label, hint)

    # 如果有截图区域的临时坐标，则合并转换
    for tab in ["装备", "防御卡", "道具"]:
        tl = f"{tab}_area_topleft"
        br = f"{tab}_area_bottomright"
        if tl in coords and br in coords:
            coords[f"{tab}_area"] = {
                "x1": coords[tl]["x"],
                "y1": coords[tl]["y"],
                "x2": coords[br]["x"],
                "y2": coords[br]["y"],
            }
            coords.pop(tl)
            coords.pop(br)

    # 保存配置
    config["coords"] = coords
    config["calibrated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"  ✅ 校准完成！配置已保存到 {CONFIG_FILE}")
    print("=" * 60)


# ═══════════════════════════════════════════════
#  账号解析
# ═══════════════════════════════════════════════

def load_accounts(filepath, start_from=1):
    """
    解析账号文件
    支持格式：
      号1：xj1234312 312312313
      号2：abc999 777666555
    """
    accounts = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 解析 "号N：账号 密码"
            try:
                # 分离编号和其余部分
                if "：" in line:
                    num_part, rest = line.split("：", 1)
                elif ":" in line:
                    num_part, rest = line.split(":", 1)
                else:
                    log(f"⚠️ 跳过格式异常行: {line}")
                    continue

                # 提取编号数字
                num = int("".join(filter(str.isdigit, num_part)))

                # 分离账号和密码
                parts = rest.strip().split()
                if len(parts) < 2:
                    log(f"⚠️ 跳过格式异常行（缺少密码）: {line}")
                    continue

                username = parts[0]
                password = parts[1]

                if num >= start_from:
                    accounts.append({
                        "num": num,
                        "username": username,
                        "password": password,
                    })
            except (ValueError, IndexError) as e:
                log(f"⚠️ 跳过格式异常行: {line} ({e})")
                continue

    return accounts


# ═══════════════════════════════════════════════
#  核心流程
# ═══════════════════════════════════════════════

def launch_client(exe_path):
    """启动微端"""
    log("🚀 启动微端...")
    subprocess.Popen(exe_path, shell=True)
    time.sleep(3)  # 等待客户端启动


def kill_client():
    """关闭微端进程"""
    log("🔄 关闭微端...")
    os.system('taskkill /f /im "4399美食大战老鼠.exe" >nul 2>&1')
    # 同时尝试关闭可能的子进程
    os.system('taskkill /f /im "MsdsClient.exe" >nul 2>&1')
    os.system('taskkill /f /im "msds_client.exe" >nul 2>&1')
    time.sleep(2)


def login_account(config, window, username, password):
    """在登录页填入账号密码"""
    activate_window(window)
    wx, wy = window.left, window.top

    # 点击并切换到"账号密码登录" Tab（确保在正确的登录方式）
    time.sleep(0.5)

    # 点击用户名框
    click_at(config, "username_field", window)
    time.sleep(0.2)
    clear_and_type(username)

    # 点击密码框
    click_at(config, "password_field", window)
    time.sleep(0.2)
    clear_and_type(password)

    # 点击登录
    click_at(config, "login_button", window)
    log(f"   已填入账号并点击登录")


def wait_for_captcha():
    """等待用户手动处理验证码"""
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  ⏸️  如有验证码，请手动处理               ║")
    print("  ║  完成后按 Enter 继续...                  ║")
    print("  ║  输入 skip 跳过该账号                    ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    response = input("  >>> ").strip().lower()
    return response != "skip"


def select_server(config, window):
    """选择服务器，自动适配“有历史记录”和“无历史记录”两种布局"""
    activate_window(window)
    server_id = config.get("server_id", "1")

    # 用图像识别判断当前是哪种布局
    # 需要在脚本目录放 view_all_servers.png（"查看全部服务器>>"的特征截图）
    view_all_template = SCRIPT_DIR / "view_all_servers.png"
    is_no_history_layout = False

    if view_all_template.exists():
        try:
            region = (window.left, window.top, window.width, window.height)
            template_img = Image.open(view_all_template)
            pos = pyautogui.locateOnScreen(template_img, region=region, confidence=0.8)
            if pos is not None:
                is_no_history_layout = True
                log("   🔍 检测到无历史布局，点击「查看全部服务器」展开...")
                center = pyautogui.center(pos)
                pyautogui.click(center)
                time.sleep(1.5)
        except Exception:
            pass

    if is_no_history_layout and "server_input_alt" in config["coords"]:
        input_key = "server_input_alt"
        enter_key = "server_enter_alt" if "server_enter_alt" in config["coords"] else "server_enter"
        log("   📋 使用无历史布局坐标")
    else:
        input_key = "server_input"
        enter_key = "server_enter"
        log("   📋 使用有历史布局坐标")

    # 点击服务器输入框
    click_at(config, input_key, window)
    time.sleep(0.3)
    clear_and_type(server_id)

    # 点击进入
    click_at(config, enter_key, window)
    log(f"   已选择 {server_id} 服并点击进入")


def wait_for_game_load(timeout=60):
    """等待游戏加载完成"""
    log("   ⏳ 等待游戏加载...")
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  游戏加载中，请等道具图标全部显示后      ║")
    print("  ║  按 Enter 继续...                       ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    input("  >>> ")


import os
import cv2
import numpy as np

def has_loading_icon_color_hist(screen_img, template_path, threshold_ratio=0.15):
    """基于色彩直方图反向投影检测转圈动画（免疫旋转、变形、背景干扰和 DPI 缩放）"""
    try:
        template_bgra = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
        if template_bgra is None or template_bgra.shape[2] != 4:
            return False # 无 Alpha 通道无法提取纯净颜色特征
            
        # 1. 提取非透明模板的纯净特征颜色
        mask = template_bgra[:,:,3] > 128
        template_hsv = cv2.cvtColor(template_bgra[:,:,:3], cv2.COLOR_BGR2HSV)
        roihist = cv2.calcHist([template_hsv], [0, 1], mask.astype(np.uint8), [180, 256], [0, 180, 0, 256])
        cv2.normalize(roihist, roihist, 0, 255, cv2.NORM_MINMAX)
        
        # 2. 在屏幕截图中寻找相似颜色
        screen_bgr = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)
        screen_hsv = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([screen_hsv], [0, 1], roihist, [0, 180, 0, 256], 1)
        
        # 3. 形态学滤波聚集色块
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        cv2.filter2D(dst, -1, disc, dst)
        _, thresh = cv2.threshold(dst, 50, 255, 0)
        
        # 4. 统计匹配像素
        match_pixels = cv2.countNonZero(thresh)
        template_pixels = np.sum(mask)
        
        # 只要屏幕上标志性颜色像素超过模板非透明部的 15%，就认为转圈依然存在
        if match_pixels > template_pixels * threshold_ratio:
            return True
        return False
    except Exception as e:
        return False

def wait_for_area_to_stabilize(config, window, area, timeout=15, check_interval=0.5):
    """
    智能等待区域加载：优先使用多尺度图像识别查找加载转圈，解决背景融合与缩放问题。
    """
    left = window.left + area["x1"]
    top = window.top + area["y1"]
    width = area["x2"] - area["x1"]
    height = area["y2"] - area["y1"]
    region = (left, top, width, height)

    start = time.time()
    loading_icon = "loading_icon.png"
    
    if os.path.exists(loading_icon):
        log("   👁️ 使用图像识别检测加载图标...")
        while time.time() - start < timeout:
            curr_img = pyautogui.screenshot(region=region)
            if not has_loading_icon_color_hist(curr_img, loading_icon):
                time.sleep(0.5)  # Double check
                curr_img2 = pyautogui.screenshot(region=region)
                if not has_loading_icon_color_hist(curr_img2, loading_icon):
                    log("   ✅ 图标加载完毕（转圈图标已消失）")
                    return True
            time.sleep(check_interval)
        log(f"   ⚠️ 图标加载超时 ({timeout}s)，强行继续！")
        return False
        
    # 如果没有转圈图文件，降级为像素变化比对
    prev_img = pyautogui.screenshot(region=region)
    while time.time() - start < timeout:
        time.sleep(check_interval)
        curr_img = pyautogui.screenshot(region=region)
        
        if images_are_same(prev_img, curr_img, threshold=1.0):
            time.sleep(0.5) 
            final_img = pyautogui.screenshot(region=region)
            if images_are_same(curr_img, final_img, threshold=1.0):
                log("   ✅ 图标加载完毕（画面已稳定）")
                return True
        prev_img = curr_img

    log(f"   ⚠️ 等待图标加载超时 ({timeout}s)，直接强行截图")
    return False


def take_backpack_screenshots(config, window, account_num):
    """截取背包三个 Tab 的截图"""
    activate_window(window)

    # 点击背包按钮
    click_at(config, "backpack_button", window)
    log("   📦 打开背包")
    time.sleep(1)

    # 防御性尝试关闭“假期特惠”弹窗（可能在打开背包时突然弹出）
    try_dismiss_holiday_popup(config, window)

    # 重新获取游戏窗口（标题可能不同）
    game_window = find_window(GAME_WINDOW_TITLE, timeout=5)
    if game_window:
        window = game_window
        activate_window(window)

    tab_keys = ["tab_equipment", "tab_defense", "tab_items"]
    # 留作兜底超时时间
    tab_load_wait = config.get("tab_load_wait", 10)

    for tab_key, tab_name in zip(tab_keys, BACKPACK_TABS):
        log(f"   📸 截图: {tab_name}")

        # 点击对应 Tab
        click_at(config, tab_key, window)
        
        # 移开鼠标到安全区(窗口顶部)防干扰浮窗出现
        pyautogui.moveTo(window.left + 150, window.top + 10)

        # 防御性尝试关闭“假期特惠”弹窗（可能在切换 Tab 时突然弹出）
        try_dismiss_holiday_popup(config, window)

        # 点击「整理」按钮，让道具排列紧凑无空缺
        if "sort_button" in config["coords"]:
            log("   🧹 点击「整理」按钮...")
            click_at(config, "sort_button", window)
            time.sleep(1)
            # 整理后移开鼠标
            pyautogui.moveTo(window.left + 150, window.top + 10)

        # 智能等待画面不再产生新变化（即加载转圈结束并出图）
        # 检查是否配置文件缺少按类分组的参数(兼容旧文件提醒)
        if f"{tab_name}_area" not in config["coords"]:
            log(f"   ❌ 配置文件缺少对【{tab_name}】的独立高低坐标记录！")
            log("   ⚠️ 请运行命令 `python game_screenshotter.py --calibrate` 并在菜单中选 4 重新校准！")
            return
            
        area = config["coords"][f"{tab_name}_area"]
        arrow = config["coords"][f"{tab_name}_arrow"]
        rows = config["coords"].get(f"{tab_name}_rows", 7)
        # 切换Tab后的等待和翻页后的等待分开控制
        tab_load_wait = config.get("tab_load_wait", 60)
        scroll_wait = config.get("scroll_wait", 0)
        
        log(f"   ⏳ 切换到【{tab_name}】Tab，强制等待 {tab_load_wait} 秒加载图标...")
        time.sleep(tab_load_wait)

        # 全景拼接切割法（CV Stitching）
        import cv2
        import numpy as np
        import math
        
        stitched_img = None
        prev_img_cv = None
        template_h = 100 # 用底部 100 像素作为模板匹配
        
        # 封面直接截取全屏，作为商品展示的第一张
        cover_img = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        cover_filename = f"号{account_num}_{tab_name}_封面.png"
        cover_img.save(OUTPUT_DIR / cover_filename)
        log(f"   ✅ 已保存: {cover_filename}")

        for roll_idx in range(20): # 最多滚 20 次防死循环
            pyautogui.moveTo(window.left + 150, window.top + 10)
            time.sleep(0.5)
            
            curr_pil = screenshot_region(window, area)
            curr_cv = cv2.cvtColor(np.array(curr_pil), cv2.COLOR_RGB2BGR)
            
            if stitched_img is None:
                stitched_img = curr_cv
                prev_img_cv = curr_cv
            else:
                # 取上一张图底部作为模板
                template = prev_img_cv[-template_h:, :, :]
                res = cv2.matchTemplate(curr_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
                if max_val > 0.8:
                    match_y = max_loc[1]
                    new_slice = curr_cv[match_y + template_h:, :, :]
                    if new_slice.shape[0] > 0:
                        stitched_img = np.vstack((stitched_img, new_slice))
                    else:
                        log("   🏁 画面不再出新内容，判定已翻到底部！")
                        break
                else:
                    log("   ⚠️ 翻页幅度过大或画面巨变导致断层，强制拼接")
                    stitched_img = np.vstack((stitched_img, curr_cv))
                    
                prev_img_cv = curr_cv
                
            # 点击向下箭头或滑块下方空白处进行翻页
            scroll_x = window.left + arrow["x"]
            scroll_y = window.top + arrow["y"]
            pyautogui.moveTo(scroll_x, scroll_y)
            time.sleep(0.1)
            # 随意点 3 次，保证有滚动但绝不超过一整页，以确保有重叠供CV识别
            pyautogui.click(clicks=3, interval=0.1)
            
            # 【强制等待】翻页后死等固定秒数，绝对不缩减，给游戏加载图标的时间
            log(f"   ⏳ 翻页后强制等待 {scroll_wait} 秒...")
            time.sleep(scroll_wait)

        # 拼接完成后，直接保存为无缝大全景长图！不再强行切割
        if stitched_img is not None:
            out_pil = Image.fromarray(cv2.cvtColor(stitched_img, cv2.COLOR_BGR2RGB))
            filename = f"号{account_num}_{tab_name}_全景长图.png"
            out_pil.save(OUTPUT_DIR / filename)
            log(f"   ✅ 已保存大全景长图: {filename}")

        # 回到顶部（为下一个 Tab 准备）
        # 将鼠标移到该背包内容区内，向上狂滚回顶
        pyautogui.moveTo(window.left + area["x1"] + 50, window.top + area["y1"] + 50)
        for _ in range(3):
            pyautogui.scroll(5000)
            
        # 移开鼠标到安全区防干扰
        pyautogui.moveTo(window.left + 150, window.top + 10)
        time.sleep(0.3)


def wait_for_page_change(window, timeout=30, poll_interval=1):
    """
    自动等待页面变化（通过截取窗口小区域对比像素变化）。
    用于检测 登录→选服、选服→游戏 等页面跳转。
    返回 True 表示检测到变化，False 表示超时。
    """
    cx = window.left + window.width // 2
    cy = window.top + window.height // 2
    region = (cx - 50, cy - 50, 100, 100)

    baseline = pyautogui.screenshot(region=region)
    start = time.time()

    while time.time() - start < timeout:
        time.sleep(poll_interval)
        current = pyautogui.screenshot(region=region)
        if not images_are_same(baseline, current, threshold=0.95):
            log("   ✅ 检测到页面变化")
            time.sleep(1.5)  # 额外再等让新页面稳定
            return True

    return False


def popup_alert(title, message):
    """
    弹出一个始终置顶的 tkinter 提示框。
    用户点击"确定"后返回 True，点击"跳过"返回 False。
    不阻塞其他窗口，用户可以继续做其他事。
    """
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes("-topmost", True)  # 弹框置顶

    result = messagebox.askyesno(
        title,
        message + "\n\n点「是」继续，点「否」跳过该账号",
        parent=root
    )
    root.destroy()
    return result


def try_dismiss_holiday_popup(config, window):
    """
    尝试关闭"假期特惠"弹窗。
    使用图像识别确认弹窗确实存在后才点击，避免误触其他按钮。
    需要在脚本目录放一张 holiday_popup.png（假期特惠弹窗的局部特征截图）。
    """
    holiday_template = SCRIPT_DIR / "holiday_popup.png"
    if not holiday_template.exists():
        return  # 没有特征图就跳过，不盲点

    activate_window(window)
    try:
        region = (window.left, window.top, window.width, window.height)
        template_img = Image.open(holiday_template)
        pos = pyautogui.locateOnScreen(template_img, region=region, confidence=0.8)
        if pos is not None:
            log("   🔲 检测到假期特惠弹窗，正在关闭...")
            if "popup_holiday_close" in config["coords"]:
                click_at(config, "popup_holiday_close", window)
            else:
                # 没配置精确坐标时，点击识别到的模板中心
                center = pyautogui.center(pos)
                pyautogui.click(center)
            time.sleep(1)
    except Exception:
        pass  # 识别失败就静默跳过，不影响主流程


def close_game_popup(config, window):
    """关闭游戏内的系统提示弹窗和假期特惠弹窗"""
    # 第一层：关闭“系统提示”弹窗（点确定）
    if "popup_confirm" in config["coords"]:
        log("   🔲 关闭系统提示弹窗...")
        click_at(config, "popup_confirm", window)
        time.sleep(1)
    else:
        log("   🔲 尝试关闭系统弹窗（按 Enter）...")
        activate_window(window)
        pyautogui.press("enter")
        time.sleep(1)

    # 第二层：关闭“假期特惠”弹窗（点右上角 ✕）
    try_dismiss_holiday_popup(config, window)


def process_account(config, account):
    """处理单个账号的完整流程"""
    num = account["num"]
    username = account["username"]
    password = account["password"]

    # 从配置读取等待时间（秒），可在 config.json 中调整
    game_load_wait = config.get("game_load_wait", 15)
    captcha_detect_timeout = config.get("captcha_detect_timeout", 15)

    log(f"{'═' * 50}")
    log(f"  开始处理: 号{num} (账号: {username})")
    log(f"{'═' * 50}")

    # ── 步骤 1: 启动微端 ──
    launch_client(config.get("client_exe", CLIENT_EXE))

    # ── 步骤 2: 等待登录窗口出现 ──
    log("   ⏳ 等待微端启动...")
    login_window = find_window(LOGIN_WINDOW_TITLE, timeout=20)
    if not login_window:
        log(f"❌ 号{num}: 未找到登录窗口，跳过")
        kill_client()
        return False

    time.sleep(3)
    activate_window(login_window)
    time.sleep(1)

    # ── 步骤 3: 输入账号密码 ──
    login_account(config, login_window, username, password)

    # ── 步骤 4: 自动检测验证码 ──
    # 点击登录后，轮询等待页面变化
    # 如果页面在 captcha_detect_timeout 秒内跳转 → 没有验证码，自动继续
    # 如果超时没跳转 → 可能有验证码，弹窗提示用户处理
    log(f"   ⏳ 检测是否有验证码 (等待 {captcha_detect_timeout}s)...")
    page_changed = wait_for_page_change(login_window, timeout=captcha_detect_timeout)

    if not page_changed:
        log("   ⚠️ 页面未跳转，可能有验证码")
        # 弹出置顶提示框，用户可以在做其他事时看到
        should_continue = popup_alert(
            f"号{num} 需要验证码",
            f"账号 {username} 登录时可能遇到验证码。\n请手动处理验证码，处理完后点击「是」。"
        )
        if not should_continue:
            log(f"⏭️ 号{num}: 用户跳过")
            kill_client()
            return False
        # 用户处理完验证码后，再等一下页面跳转
        time.sleep(3)
    else:
        log("   ✅ 无验证码，自动继续")

    # ── 步骤 5: 自动等待选服页面加载 ──
    log("   ⏳ 等待选服页面加载...")
    server_window = find_window(LOGIN_WINDOW_TITLE, timeout=10)
    if not server_window:
        server_window = find_window(GAME_WINDOW_TITLE, timeout=5)
    if not server_window:
        log(f"❌ 号{num}: 未找到选服窗口，跳过")
        kill_client()
        return False

    time.sleep(3)
    activate_window(server_window)
    time.sleep(1)

    # ── 步骤 6: 选服进入 ──
    select_server(config, server_window)

    # ── 步骤 7: 自动等待游戏加载 ──
    log(f"   ⏳ 等待游戏加载...")
    game_window = find_window(GAME_WINDOW_TITLE, timeout=30)
    if not game_window:
        log(f"❌ 号{num}: 未找到游戏窗口，跳过")
        kill_client()
        return False

    activate_window(game_window)

    # 智能等待功能：如果目录有 ready_flag.png，则一直等到它出现；否则固定等待
    ready_flag_path = "ready_flag.png"
    if os.path.exists(ready_flag_path):
        log("   👁️ 智能等待：已启用 ready_flag.png 检测，正在等待界面出现...")
        start_wait = time.time()
        is_ready = False
        while time.time() - start_wait < 120: # 最长等 120 秒
            time.sleep(1)
            try:
                region = (game_window.left, game_window.top, game_window.width, game_window.height)
                # 使用相对宽容的 0.8 置信度
                pos = pyautogui.locateOnScreen(ready_flag_path, region=region, confidence=0.8)
                if pos is not None:
                    log("   ✅ 识别到界面已就绪 (ready_flag)，进入下一步！")
                    is_ready = True
                    time.sleep(2) # 缓冲一下
                    break
            except Exception:
                pass
        if not is_ready:
            log("   ⚠️ 智能等待超时，强行继续")
    else:
        # 降级：走原有的固定等待配置
        log(f"   ⏳ 固定等待加载 ({game_load_wait}s)... (提示: 放一张 ready_flag.png 到本目录可开启智能等待)")
        time.sleep(game_load_wait)
        log("   ✅ 固定等待结束")

    # ── 步骤 8: 关闭系统提示弹窗 ──
    activate_window(game_window)
    time.sleep(0.5)
    close_game_popup(config, game_window)

    # ── 步骤 9: 截取背包截图 ──
    take_backpack_screenshots(config, game_window, num)

    # ── 步骤 10: 关闭微端 ──
    kill_client()

    log(f"✅ 号{num} 处理完成!")
    return True


# ═══════════════════════════════════════════════
#  主程序
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="4399美食大战老鼠 批量账号背包截图工具")
    parser.add_argument("--calibrate", action="store_true", help="进入坐标校准模式")
    parser.add_argument("--start", type=int, default=1, help="从指定编号开始 (默认: 1)")
    args = parser.parse_args()

    # 校准模式
    if args.calibrate:
        calibrate()
        return

    # 检查配置文件
    if not CONFIG_FILE.exists():
        print("❌ 未找到配置文件！请先运行校准：")
        print("   python game_screenshotter.py --calibrate")
        return

    # 检查账号文件
    if not ACCOUNTS_FILE.exists():
        print(f"❌ 未找到账号文件: {ACCOUNTS_FILE}")
        print("请创建 accounts.txt，格式如下：")
        print("  号1：xj1234312 312312313")
        print("  号2：abc999 777666555")
        return

    # 加载配置
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 加载账号
    accounts = load_accounts(ACCOUNTS_FILE, start_from=args.start)
    if not accounts:
        print(f"❌ 未找到编号 >= {args.start} 的账号")
        return

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 开始处理
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  4399 美食大战老鼠 — 批量背包截图工具            ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  待处理账号: {len(accounts)} 个")
    print(f"║  起始编号:   号{args.start}")
    print(f"║  输出目录:   {OUTPUT_DIR}")
    print("╠══════════════════════════════════════════════════╣")
    print("║  ⚠️  运行中请勿手动操作鼠标（验证码除外）       ║")
    print("║  🛑  紧急停止：快速移动鼠标到屏幕左上角         ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    input("按 Enter 开始...")

    # 先关闭可能存在的客户端
    kill_client()
    time.sleep(1)

    # 统计
    success = 0
    failed = 0
    failed_list = []

    for i, account in enumerate(accounts):
        log(f"📊 进度: {i + 1}/{len(accounts)}")

        try:
            result = process_account(config, account)
            if result:
                success += 1
            else:
                failed += 1
                failed_list.append(account["num"])
        except KeyboardInterrupt:
            log("⚡ 用户中断，正在退出...")
            kill_client()
            break
        except Exception as e:
            log(f"❌ 号{account['num']} 异常: {e}")
            failed += 1
            failed_list.append(account["num"])
            kill_client()
            time.sleep(1)

    # 汇总报告
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  执行完成                                       ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  ✅ 成功: {success} 个")
    print(f"║  ❌ 失败: {failed} 个")
    if failed_list:
        nums = ", ".join(f"号{n}" for n in failed_list)
        print(f"║  失败编号: {nums}")
    print(f"║  截图目录: {OUTPUT_DIR}")
    print("╚══════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
