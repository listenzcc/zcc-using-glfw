"""
File: rolling-text.py
Author: Chuncheng Zhang
Date: 2025-10-20
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    The demo of rolling text rendering.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-20 ------------------------
# Requirements and constants
import glfw

from util.easy_import import *
from util.glfw_window import GLFWWindow


# %% ---- 2025-10-20 ------------------------
# Function and class

def key_callback(window, key, scancode, action, mods):
    '''
    Key press callback.
    '''

    # Only be interested in PRESS event.
    if not action == glfw.PRESS:
        return

    print(key, chr(key), scancode, action, mods)

    # Close the window if ESC is pressed.
    if key == glfw.KEY_ESCAPE:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)

    return


def main_render():
    wnd.draw_rect(0, 0, 0.2, 0.3, color=0.5)
    wnd.draw_rect(0, -0.3, 0.9, 0.3, color=0.5)
    pass


# %% ---- 2025-10-20 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('c:\\windows\\fonts\\stxinwei.ttf')
wnd.init_window()

glfw.set_key_callback(wnd.window, key_callback)

wnd.render_loop(main_render)
wnd.cleanup()

# %% ---- 2025-10-20 ------------------------
# Pending


# %% ---- 2025-10-20 ------------------------
# Pending
