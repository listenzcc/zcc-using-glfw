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
from util.easy_import import *
from util.glfw_window import GLFWWindow, TextAnchor

import glfw


# %% ---- 2025-10-09 ------------------------
# Function and class
def key_callback(window, key, scancode, action, mods):
    print(key, chr(key), scancode, action, mods)
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)
        return


def main_render():
    pass


# %% ---- 2025-10-09 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('./font/msyh.ttc')
wnd.render_loop(key_callback, main_render)

# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
