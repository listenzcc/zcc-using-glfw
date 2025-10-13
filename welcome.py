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
import time
import glfw
import math
import random

from queue import Queue
from threading import Thread, RLock

from util.easy_import import *
from util.glfw_window import GLFWWindow, TextAnchor
from color_manager import WowColors, MyColors

FONT_SIZE = 48
WC = WowColors()
MC = MyColors()
PROMPT_COLOR = random.choice(WC.class_colors['hex'])
TEXT_QUEUE = Queue(maxsize=50)

WELCOME_MSG = '''
Welcome to my GLFW window.

The blinking square's NE corner is on cursor.
And press key for popping and lifting texts.
It also changes the text color.
'''

# %% ---- 2025-10-09 ------------------------
# Function and class


class BasicAnimatingText:
    text = 'BasicText'  # content
    ta = TextAnchor.B  # text anchor
    scale = 0.5  # text scale
    rgb = '#efe529'  # text color
    alpha = 1  # text alpha

    x = 0  # xpos in 0 ~ 1
    y = 0  # xpos in 0 ~ 1

    tic = 0  # now in seconds
    age = 0  # seconds since tic
    lifetime = 1  # how old it can be
    expired = False  # tells if it is expired
    rlock = RLock()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.tic = time.time()
        Thread(target=self._getting_old, daemon=True).start()

    def _getting_old(self):
        with self.rlock:
            self.age = (time.time() - self.tic) / self.lifetime
            if self.age > 1:
                self.expired = True
                return
        time.sleep(0.005)
        self._getting_old()

    def _get_age(self):
        with self.rlock:
            return self.age


class LiftingText(BasicAnimatingText):
    y_lift = 0.2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.y1 = self.y
        self.rgb = random.choice(MC.damage_colors['hex'])

    def update(self):
        age = self._get_age()
        self.alpha = math.exp(-age*2)
        self.y = self.y1 + self.y_lift * age
        return age


class PoppingText(BasicAnimatingText):
    scale_enlarge = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale1 = self.scale
        self.lifetime = 0.2
        self.rgb = random.choice(MC.damage_colors['hex'])

    def update(self):
        age = self._get_age()
        self.scale = self.scale1 + self.scale_enlarge * (1-math.exp(-age*2))
        return age


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

    # Get where the cursor is.
    # And convert into (0, 1) scale.
    x, y = wnd.cursor_pos
    x /= wnd.width
    y /= wnd.height
    y = 1-y

    # Start a animation text.
    if random.random() > 0.5:
        TEXT_QUEUE.put_nowait(LiftingText(x=x, y=y, text=f'{key}, {chr(key)}'))
    else:
        TEXT_QUEUE.put_nowait(PoppingText(x=x, y=y, text=f'{key}, {chr(key)}'))

    # Choose another PROMPT_COLOR
    global PROMPT_COLOR
    PROMPT_COLOR = random.choice(WC.class_colors['hex'])

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

    # Draw the welcome message
    x = 1.0
    y = 0.8
    for text in WELCOME_MSG.split('\n'):
        if len(text) == 0:
            text = '\n'
        w, _, h = wnd.draw_text(text, x, y, scale=0.5,
                                anchor=TextAnchor.BR, color=PROMPT_COLOR)
        y -= h/wnd.height

    # Draw the top right corner prompt
    x, y = wnd.cursor_pos
    text = f'{x=: 4.0f}, {y=: 4.0f}'
    x /= wnd.width
    y /= wnd.height
    y = 1-y
    wnd.draw_rect(0, 0, x, y, face_color)
    w, _, h = wnd.draw_text(text, x, y, scale=0.5,
                            anchor=TextAnchor.TR, color=PROMPT_COLOR)
    w /= wnd.width
    h /= wnd.height
    wnd.draw_rect(x-w, y-h, w, 1/wnd.height, (0, 0, 0, 1))
    wnd.draw_rect(x-w, y-h, 1/wnd.width, h, (0, 0, 0, 1))

    # Draw the center prompt
    text = f'{t=:0.3f} | {TEXT_QUEUE.qsize()=}'
    wnd.draw_text(text, x/2, y/2, scale=1,
                  anchor=TextAnchor.C, color=PROMPT_COLOR)

    # Draw the animation texts
    for _ in range(TEXT_QUEUE.qsize()):
        dt: LiftingText = TEXT_QUEUE.get_nowait()
        dt.update()
        if not dt.expired:
            TEXT_QUEUE.put_nowait(dt)
        wnd.draw_text(dt.text, dt.x, dt.y, dt.scale,
                      TextAnchor.B, color=(dt.rgb, dt.alpha))

    return


# %% ---- 2025-10-09 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('c:\\windows\\fonts\\stliti.ttf', FONT_SIZE)
wnd.init_window()

glfw.set_key_callback(wnd.window, key_callback)
glfw.set_cursor_pos_callback(wnd.window, cursor_pos_callback)

# Run FOREVER
wnd.render_loop(main_render)

# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
