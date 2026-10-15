import time
import random
import pyautogui

def human_typing(text, clear_first=False):
    """
    📝 Typing Module

    :param text: text content to be typed (str)
    :param clear_first: whether to select all and clear existing content first (Ctrl+A -> Backspace)
    """
    if clear_first:
        print("    [⌨️] Simulating human selecting all and clearing input box...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(random.uniform(0.1, 0.3))
        pyautogui.press('backspace')
        time.sleep(random.uniform(0.3, 0.8))

    print(f"    [⌨️] Start simulating humantyping: {text[:20]}...")

    for char in text:
        # 1. Simulate typo with backspace (5% probability)
        if random.random() < 0.05 and char.isalpha():
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            pyautogui.write(wrong_char)
            time.sleep(random.uniform(0.1, 0.3))

            # Notice the typo and delete it with backspace
            pyautogui.press('backspace')
            print(f"      [x] Typo and backspace: {wrong_char}")
            time.sleep(random.uniform(0.2, 0.5)) # Correction pause

        # 2. Input character
        pyautogui.write(char)


        # 3. Small random delay between characters (0.06 - 0.25 s)
        time.sleep(random.uniform(0.06, 0.25))

        # 4. Occasional "thinking" pauses
        if random.random() < 0.08:
            # 8%: short pause (deciding what to type next)
            think_delay = random.uniform(0.8, 2.0)
            print(f"      [~] Short pause while typing: {think_delay:.2f}s")
            time.sleep(think_delay)
        elif random.random() < 0.03:
            # 3%: long pause (2-5 s)
            long_delay = random.uniform(2.0, 5.0)
            print(f"      [~] Long pause while typing: {long_delay:.2f}s")
            time.sleep(long_delay)

    print("    [+] Typing finished.")
