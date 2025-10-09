"""
File: text_render.py
Author: Chuncheng Zhang
Date: 2025-10-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    TextRender

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-09 ------------------------
# Requirements and constants
from .easy_import import *

import freetype
from OpenGL.GL import *
from collections import OrderedDict


# %% ---- 2025-10-09 ------------------------
# Function and class
class TextRenderer:
    def __init__(self, max_cache_size=1024):
        self.face = None
        self.characters = OrderedDict()  # 使用有序字典实现LRU缓存
        self.max_cache_size = max_cache_size  # 最大缓存字符数

    def load_font(self, font_path, size):
        """初始化字体"""
        self.face = freetype.Face(font_path)
        self.face.set_char_size(size << 6)
        logger.info(f'Using font: {font_path} ({size})')

    def load_char(self, char):
        """动态加载单个字符（支持中文字符）"""
        # 如果字符已在缓存中，移到最前面表示最近使用
        if char in self.characters:
            self.characters.move_to_end(char)
            return True

        # 如果缓存已满，移除最久未使用的字符
        if len(self.characters) >= self.max_cache_size:
            oldest_char = next(iter(self.characters))
            glDeleteTextures([self.characters[oldest_char]['texture']])
            del self.characters[oldest_char]
            logger.warning(
                f'Characters cache exceeds limit, removed: {oldest_char}')

        # 加载新字符
        self.face.load_char(char, freetype.FT_LOAD_RENDER |
                            freetype.FT_LOAD_TARGET_LIGHT)
        bitmap = self.face.glyph.bitmap

        # 将单通道位图转换为RGBA格式

        # -------------------------
        # It is Slow.
        # for i in range(bitmap.rows):
        #     for j in range(bitmap.width):
        #         value = bitmap.buffer[i * bitmap.width + j]
        #         rgba_data.extend([255, 255, 255, value])  # 白色+alpha
        # -------------------------

        buffer = np.array(bitmap.buffer, dtype=np.uint8).reshape(
            (bitmap.rows, bitmap.width))
        rgba_data = np.zeros((bitmap.rows, bitmap.width, 4), dtype=np.uint8)
        rgba_data[..., :3] = 255  # 设置RGB为白色
        rgba_data[..., 3] = buffer  # 设置Alpha通道
        rgba_data = rgba_data.flatten()

        # 生成纹理
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            bitmap.width, bitmap.rows,
            0, GL_RGBA, GL_UNSIGNED_BYTE,
            rgba_data
        )

        # 设置纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 存储字符信息
        self.characters[char] = {
            'texture': texture,
            'size': (bitmap.width, bitmap.rows),
            'bearing': (self.face.glyph.bitmap_left, self.face.glyph.bitmap_top),
            'advance': self.face.glyph.advance.x >> 6
        }

        # 将新字符移到最前面
        self.characters.move_to_end(char, last=False)
        logger.info(f'Loaded character: {char}, {self.characters[char]}')
        return True

    def bounding_box(self, text, scale=1.0):
        """计算文本的边界框"""
        width = 0
        height = 0
        for char in text:
            if char not in self.characters:
                self.load_char(char)

            ch = self.characters[char]
            width += ch['advance'] * scale
            height = max(height, ch['size'][1] * scale)

        return width, height

    def render_text(self, text, x, y, scale=1.0, color=(1.0, 1.0, 1.0, 1.0)):
        '''
        Draw the text at its SW corner.
        '''
        # 启用必要的OpenGL状态
        # glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)

        # 设置颜色（包含alpha通道）
        glColor4f(*color)

        # 获取视口尺寸用于坐标转换
        viewport = glGetIntegerv(GL_VIEWPORT)
        screen_width = viewport[2]
        screen_height = viewport[3]

        # 设置正交投影
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, screen_width, 0, screen_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        for char in text:
            self.load_char(char)

            ch = self.characters[char]
            xpos = x + ch['bearing'][0] * scale
            ypos = y - (ch['size'][1] - ch['bearing'][1]) * scale

            w = ch['size'][0] * scale
            h = ch['size'][1] * scale

            # 绑定字符纹理
            glBindTexture(GL_TEXTURE_2D, ch['texture'])

            # 绘制字符
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(xpos, ypos + h)  # 左下角

            glTexCoord2f(1, 0)
            glVertex2f(xpos + w, ypos + h)  # 右下角

            glTexCoord2f(1, 1)
            glVertex2f(xpos + w, ypos)  # 右上角

            glTexCoord2f(0, 1)
            glVertex2f(xpos, ypos)  # 左上角
            glEnd()

            x += ch['advance'] * scale

        # 恢复矩阵状态
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        # 禁用状态
        glDisable(GL_TEXTURE_2D)
        # glDisable(GL_BLEND)

# %% ---- 2025-10-09 ------------------------
# Play ground


# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
