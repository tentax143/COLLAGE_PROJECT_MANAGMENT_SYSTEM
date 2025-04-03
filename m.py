import pyautogui
import time

try:
    while True:
        pyautogui.typewrite('?')
        pyautogui.press('enter')
        time.sleep(1)  # Adjust the delay if needed
except KeyboardInterrupt:
    print("Program stopped by user.")
