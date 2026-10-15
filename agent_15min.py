import time
import random
import pyautogui
import uiautomation as auto

# Import core modules
from cursor import human_curve_move, human_move_and_click
from Typing_2 import human_typing
from recognition import smart_click_link

# List of 10 designated URLs
TARGET_URLS = [
    "https://www.coinmarketcap.com",
    "https://www.coursera.org",
    "https://www.coinbase.com",
    "https://coingecko.com",
    "https://www.samsung.com",
    "https://aws.amazon.com",
    "https://www.amazon.com",
    "https://www.apple.com",
    "https://apnews.com",
    "https://www.dell.com"
]

# ==========================================
# Utility Functions
# ==========================================
def human_delay(min_sec=1.0, max_sec=3.0):
    """Random delay: 15% probability of triggering a long pause"""
    if random.random() < 0.15:
        time.sleep(random.uniform(5.0, 10.0))
    else:
        time.sleep(random.uniform(min_sec, max_sec))

def launch_app_via_win_search(app_name):
    """Use Win to search and start, ensuring parent process is clean (explorer.exe)"""
    print(f"\n[Launch] {app_name}...")
    pyautogui.press('win')
    human_delay(1.0, 1.5)
    human_typing(app_name)
    human_delay(0.8, 1.5)
    pyautogui.press('enter')
    human_delay(4.0, 6.0)

def move_cursor_to_safe_center():
    """Move cursor to the center to prevent invalid sliding outside the window"""
    screen_w, screen_h = pyautogui.size()
    safe_x = screen_w // 2 + random.randint(-200, 200)
    safe_y = screen_h // 2 + random.randint(-100, 100)
    start_x, start_y = pyautogui.position()
    print(f"    [Cursor] Move cursor to safe center ({safe_x}, {safe_y})")
    human_curve_move(start_x, start_y, safe_x, safe_y)
    human_delay(0.5, 1.0)

def close_browser_tab():
    """Closes the current browser tab safely without extra keypresses"""
    print("    [Exit] Closing browser tab...")
    pyautogui.hotkey('ctrl', 'w')
    human_delay(2.0, 3.0)

# ==========================================
# Page Validity Check
# ==========================================
def check_page_validity():
    """Reads window title to check if page loaded successfully."""
    try:
        win = auto.GetForegroundControl()
        if not win:
            return True

        title = win.Name or ""
        print(f"    [👁️] Current page title: '{title}'")

        # The three non-English entries match Chrome's error-page titles on a
        # Chinese-language Windows UI ("can't be reached", "connection failed",
        # "page can't be opened"), so they are kept as-is.
        error_keywords = ["error", "not found", "无法访问", "连接失败", "404", "timed out", "server not found", "can't be reached", "网页无法打开"]

        if any(keyword.lower() in title.lower() for keyword in error_keywords):
            print("    [!] Invalid page detected. Going back...")
            human_delay(0.5, 1.5)
            pyautogui.hotkey('alt', 'left')
            human_delay(2.0, 4.0)
            return False
        return True
    except Exception as e:
        print(f"    [-] Page validity check failed: {e}")
        return True

# ==========================================
# Task 1: OpenOffice Writer (Drafting an Email)
# ==========================================
def task_office_writer():
    print("\n=== Start office task: OpenOffice Writer (Email Draft) ===")
    launch_app_via_win_search("OpenOffice Writer")
    human_delay(5.0, 8.0)
    pyautogui.press('enter')
    human_delay(3.0, 5.0)

    pyautogui.hotkey('ctrl', 'home')
    human_delay(0.5, 1.0)

    email_content = [
        "To: supervisor@example.invalid",
        "Subject: Weekly Office Activity Report",
        " ",
        "Hello,",
        " ",
        "The weekly office activity report is ready for review.",
        "Please review the attached metrics by Friday.",
        " ",
        "Regards,",
        "Analyst"
    ]

    print(f"    [Typing] Drafting email...")
    for line in email_content:
        if line == " ":
            pyautogui.press('enter')
            human_delay(0.5, 1.0)
        else:
            human_typing(line)
            pyautogui.press('enter')
            human_delay(1.0, 2.0)

    # Save logic
    print("    [Save] Saving document...")
    pyautogui.hotkey('ctrl', 's')
    human_delay(3.0, 5.0)
    human_typing(f"Email_Draft_{random.randint(100, 999)}.odt")
    human_delay(1.5, 3.0)
    pyautogui.press('enter')
    human_delay(2.5, 4.0)
    pyautogui.press('enter')
    human_delay(2.0, 3.0)

    # 🚨 Save finished: only send Ctrl+Q to quit, absolutely no extra keypresses!
    print("    [Exit] Quitting OpenOffice with Ctrl+Q...")
    pyautogui.hotkey('ctrl', 'q')
    human_delay(2.5, 4.0)

# ==========================================
# Task 2: OpenOffice Calc
# ==========================================
def task_office_calc():
    print("\n=== Start office task: OpenOffice Calc ===")
    launch_app_via_win_search("OpenOffice Calc")
    human_delay(5.0, 8.0)
    pyautogui.press('enter')
    human_delay(3.0, 5.0)

    pyautogui.hotkey('ctrl', 'home')
    human_delay(0.5, 1.0)

    table_data = [
        ["Name", "Q1", "Q2", "Q3", "Total"],
        ["Alice", "120", "150", "130", "400"],
        ["Bob", "90", "110", "100", "300"],
        ["Charlie", "200", "210", "190", "600"]
    ]

    print("    [Typing] Entering data cell by cell...")
    for row in table_data:
        for cell in row:
            human_typing(cell)
            human_delay(0.2, 0.5)
            pyautogui.press('tab')
            human_delay(0.1, 0.3)
        pyautogui.press('enter')
        human_delay(0.8, 1.5)

    # Save logic
    print("    [Save] Saving spreadsheet...")
    pyautogui.hotkey('ctrl', 's')
    human_delay(3.0, 5.0)
    human_typing(f"Data_{random.randint(100, 999)}.ods")
    human_delay(1.5, 3.0)
    pyautogui.press('enter')
    human_delay(2.5, 4.0)
    pyautogui.press('enter')
    human_delay(2.0, 3.0)

    # 🚨 Save finished: only send Ctrl+Q to quit, absolutely no extra keypresses!
    print("    [Exit] Quitting OpenOffice with Ctrl+Q...")
    pyautogui.hotkey('ctrl', 'q')
    human_delay(2.5, 4.0)

# ==========================================
# Web Task (Interleaved Scroll & Click)
# ==========================================
def task_web_surfing(url):
    print(f"\n=== Start web task: {url} ===")
    launch_app_via_win_search("chrome")
    move_cursor_to_safe_center()

    pyautogui.hotkey('ctrl', 'l')
    human_delay(0.3, 0.8)
    human_typing(url)
    human_delay(0.3, 0.8)
    pyautogui.press('enter')
    human_delay(4.0, 8.0)

    check_page_validity()

    print("    [Vision] Interleaved scrolling and clicking...")
    clicked = False
    total_scrolls = 0
    max_scrolls = random.randint(8, 14)

    while total_scrolls < max_scrolls:
        scroll_batch = random.randint(1, 3)
        for _ in range(scroll_batch):
            pyautogui.scroll(random.randint(-700, -400))
            total_scrolls += 1
            human_delay(1.0, 2.5)

        if random.random() < 0.6:
            print(f"    [Vision] After {total_scrolls} scrolls, looking for links...")
            if smart_click_link(human_move_and_click):
                clicked = True
                print("    [+] Successfully clicked a real link!")
                human_delay(2.0, 4.0)

                if check_page_validity():
                    human_delay(3.0, 5.0)
                else:
                    break

                if random.random() < 0.5:
                    pyautogui.hotkey('alt', 'left')
                    human_delay(3.0, 5.0)

                if random.random() < 0.6:
                    print("    [Vision] Ending browsing early.")
                    break
            else:
                print("    [-] No links found, continue scrolling...")
                human_delay(1.5, 3.0)

    if not clicked:
        print("    [!] No links clicked, performing fallback...")
        screen_w, screen_h = pyautogui.size()
        for _ in range(random.randint(1, 2)):
            human_move_and_click(random.randint(int(screen_w*0.2), int(screen_w*0.8)),
                                 random.randint(int(screen_h*0.3), int(screen_h*0.8)))
            human_delay(2.0, 4.0)
            if random.random() < 0.3:
                pyautogui.hotkey('alt', 'left')
                human_delay(2.0, 4.0)

    close_browser_tab()

# ==========================================
# Main Controller (Strict 15 Minutes)
# ==========================================
def run_agent():
    print("========================================")
    print(" Agent start (strict 15 minutes)")
    print(" Goal: Guarantee Word and Excel are executed")
    print("========================================")
    print("Warning: Ensure switching to English input method.")
    print("Warning: Please click the virtual machine desktop in 5 seconds.")
    time.sleep(5)

    start_time = time.time()
    total_duration = 15 * 60

    url_pool = TARGET_URLS.copy()
    random.shuffle(url_pool)

    mandatory_tasks = ["word", "excel"]
    random.shuffle(mandatory_tasks)
    print(f"[*] Mandatory task order: {mandatory_tasks}")

    task_count = 0

    while time.time() - start_time < total_duration:
        task_count += 1
        elapsed = (time.time() - start_time) / 60
        remain = (total_duration - (time.time() - start_time)) / 60
        print(f"\n>>>>>>> Task {task_count}: has run {elapsed:.1f} mins (Remaining: {remain:.1f} mins) <<<<<<<")

        if mandatory_tasks and (task_count % 3 == 0 or remain < 4.0):
            task_name = mandatory_tasks.pop(0)
            print(f"    [System] Triggering mandatory task: {task_name}")
            if task_name == "word":
                task_office_writer()
            elif task_name == "excel":
                task_office_calc()
        else:
            if not url_pool:
                url_pool = TARGET_URLS.copy()
                random.shuffle(url_pool)

            next_url = url_pool.pop(0)
            task_web_surfing(next_url)

        print(f"\n[*] Rest between tasks...")
        human_delay(2.0, 5.0)

    # Final cleanup after 15 minutes: again only Ctrl+Q and Ctrl+W, never press 'y'
    print("\n=== 15-minute runtime complete. Performing final cleanup... ===")
    for _ in range(3):
        pyautogui.hotkey('ctrl', 'q')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)
        pyautogui.press('esc')
        time.sleep(0.5)

    print("========================================")
    print(" All tasks finished. Screen cleaned up.")
    print("========================================")

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    run_agent()
