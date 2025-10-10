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
import random
from queue import Queue
from util.easy_import import *
from util.glfw_window import GLFWWindow, TextAnchor
from color_manager import WowColors, MyColors

FONT_SIZE = 48
WC = WowColors()
MC = MyColors()
text_color = random.choice(WC.class_colors['hex'])

# %% ---- 2025-10-09 ------------------------
# Function and class


class DancingText:
    text = 'DancingText'
    x = 0  # range 0~1
    y = 0  # range 0~1
    y_lift = 0.2
    scale = 0.5
    tic = 0  # now seconds
    lifetime = 1  # seconds
    rgb = '#efe529'
    alpha = 1
    age = 0  # range 0~1

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.y1 = self.y
        self.y2 = self.y + self.y_lift
        self.rgb = random.choice(MC.damage_colors['hex'])

    def update(self, t):
        age = (t-self.tic) / self.lifetime
        if age > 1:
            return False

        self.alpha = math.exp(-age*2)
        self.y = self.y1 + (self.y2-self.y1) * age

        return True


myqueue = Queue(maxsize=50)


def key_callback(window, key, scancode, action, mods):
    if not action == glfw.PRESS:
        return

    print(key, chr(key), scancode, action, mods)

    if key == glfw.KEY_ESCAPE:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)

    x, y = wnd.cursor_pos
    x /= wnd.width
    y /= wnd.height
    y = 1-y
    myqueue.put_nowait(DancingText(
        x=x, y=y, text=f'{key}, {chr(key)}', tic=glfw.get_time()))

    global text_color
    text_color = random.choice(WC.class_colors['hex'])

    return


def cursor_pos_callback(window, x, y):
    wnd.cursor_pos = (x, y)
    return


def main_render():
    omega = 0.2 * 2 * math.pi
    t = glfw.get_time()
    c = (math.sin(t*omega) + 1) * 0.5
    c *= 0.5
    face_color = (c, c, c, 0.5)

    x, y = wnd.cursor_pos
    x /= wnd.width
    y /= wnd.height
    y = 1-y

    wnd.draw_rect(0, 0, x, y, face_color)
    w, _, h = wnd.draw_text(f'{x=:0.3f}, {y=:0.3f}', x, y,
                            scale=0.5, anchor=TextAnchor.TR, color=text_color)
    w /= wnd.width
    h /= wnd.height
    wnd.draw_rect(x-w, y-h, w, 1/wnd.height, (0, 0, 0, 1))
    wnd.draw_rect(x-w, y-h, 1/wnd.width, h, (0, 0, 0, 1))
    wnd.draw_text(f'{t=:0.3f}', x/2, y/2, scale=1, color=text_color)

    for _ in range(myqueue.qsize()):
        dt: DancingText = myqueue.get_nowait()
        if dt.update(t):
            myqueue.put_nowait(dt)
        wnd.draw_text(dt.text, dt.x, dt.y, dt.scale,
                      TextAnchor.B, color=(dt.rgb, dt.alpha))

    return


# %% ---- 2025-10-09 ------------------------
# Play ground
wnd = GLFWWindow()
# wnd.load_font('./font/msyh.ttc', FONT_SIZE)
# wnd.load_font('c:\\windows\\fonts\\harngton.ttf', FONT_SIZE)
wnd.load_font('c:\\windows\\fonts\\alger.ttf', FONT_SIZE)
wnd.init_window()

glfw.set_key_callback(wnd.window, key_callback)
glfw.set_cursor_pos_callback(wnd.window, cursor_pos_callback)

# Run FOREVER
wnd.render_loop(main_render)

# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
