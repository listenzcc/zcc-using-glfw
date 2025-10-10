"""
File: welcome.py
Author: Chuncheng Zhang
Date: 2025-10-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Welcome to my GLFW learning. 
    It shows the welcome window and basic features of the learning.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-09 ------------------------
# Requirements and constants
import glfw
import math
from util.easy_import import *
from util.glfw_window import GLFWWindow, TextAnchor


# %% ---- 2025-10-09 ------------------------
# Function and class


def key_callback(window, key, scancode, action, mods):
    print(key, chr(key), scancode, action, mods)
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)
    return


def cursor_pos_callback(window, x, y):
    wnd.cursor_pos = (x, y)
    return


def main_render():
    omega = 0.1 * 2 * math.pi
    t = glfw.get_time()
    c = (math.sin(t*omega) + 1)/2
    # c = min(c, 0.3)

    x, y = wnd.cursor_pos
    x /= wnd.width
    y /= wnd.height
    y = 1-y

    wnd.draw_text(f'{x=:0.3f}, {y=:0.3f}', x, y, scale=0.5)
    wnd.draw_rect(0, 0, x, y, c)
    wnd.draw_text(f'{t=:0.3f}', 0, 0, scale=0.5, color=(1, 0, 0, 1))
    pass


# %% ---- 2025-10-09 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('./font/msyh.ttc')
wnd.init_window()

glfw.set_key_callback(wnd.window, key_callback)
glfw.set_cursor_pos_callback(wnd.window, cursor_pos_callback)

# Run FOREVER
wnd.render_loop(main_render)

# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
