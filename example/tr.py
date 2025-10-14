import ctypes
import freetype
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import ctypes
# ... 其它 imports 保持不变 ...


class ModernTextRenderer:
    def __init__(self, font_path, font_size=48):
        self.characters = {}
        self.font_size = font_size
        self.setup_shaders()
        self.setup_buffers()
        self.load_font(font_path)

    def cleanup(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader_program)

    def setup_shaders(self):
        # （你原来的 shader 我保留片段输出红色的测试版）
        vertex_shader_source = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;
        out vec2 TexCoord;
        uniform mat4 projection;
        void main()
        {
            gl_Position = projection * vec4(aPos, 0.0, 1.0);
            TexCoord = aTexCoord;
        }
        """
        fragment_shader_source = """
        #version 330 core
        in vec2 TexCoord;
        out vec4 FragColor;
        uniform sampler2D textTexture;
        uniform vec3 textColor;
        void main()
        {
            // sampled alpha from red-channel
            float alpha = texture(textTexture, TexCoord).r;
            FragColor = vec4(textColor, alpha);
            // For debugging constant red block, 可改成:
            // FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        }
        """
        try:
            vertex_shader = compileShader(
                vertex_shader_source, GL_VERTEX_SHADER)
            fragment_shader = compileShader(
                fragment_shader_source, GL_FRAGMENT_SHADER)
            self.shader_program = compileProgram(
                vertex_shader, fragment_shader)
            print("着色器编译成功")
        except Exception as e:
            print(f"着色器编译失败: {e}")

    def setup_buffers(self):
        # 生成 VAO、VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # 使用 ctypes.sizeof(ctypes.c_float) 来取 float 字节数
        float_size = ctypes.sizeof(ctypes.c_float)
        # 预分配缓冲区大小（6 顶点 * 4 float * 100 个字符）
        total_bytes = 6 * 4 * 100 * float_size
        glBufferData(GL_ARRAY_BUFFER, total_bytes, None, GL_DYNAMIC_DRAW)

        # 设置顶点属性指针 (位置: vec2, 纹理: vec2)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE,
                              4 * float_size, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                              4 * float_size, ctypes.c_void_p(2 * float_size))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def load_font(self, font_path):
        """加载字体文件并预渲染 ASCII 字符集"""
        try:
            self.face = freetype.Face(font_path)
            self.face.set_pixel_sizes(0, self.font_size)

            # 预加载常用字符
            for char_code in range(32, 127):  # ASCII 可打印字符
                char = chr(char_code)
                self.load_char(char)

            print(f"成功加载字体: {font_path}, 大小: {self.font_size}")
        except Exception as e:
            print(f"字体加载失败: {e}")
            # 回退到默认字体或创建占位符

    def load_char(self, char):
        if char in self.characters:
            return

        self.face.load_char(char, freetype.FT_LOAD_RENDER)
        bitmap = self.face.glyph.bitmap
        glyph = self.face.glyph

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # 重要：单字节对齐，针对宽度不是4的情况
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        if bitmap.pixel_mode == freetype.FT_PIXEL_MODE_MONO:
            data = self.mono_to_grayscale(bitmap)
        else:
            # 直接构造 numpy array, 注意 shape/类型
            data = np.array(bitmap.buffer, dtype=np.ubyte)

        # 纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 上传纹理（单通道）
        if bitmap.width > 0 and bitmap.rows > 0:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, bitmap.width,
                         bitmap.rows, 0, GL_RED, GL_UNSIGNED_BYTE, data)
        else:
            empty_data = np.array([0], dtype=np.ubyte)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 1, 1, 0,
                         GL_RED, GL_UNSIGNED_BYTE, empty_data)

        # 解绑纹理
        glBindTexture(GL_TEXTURE_2D, 0)

        self.characters[char] = {
            'texture': texture,
            'size': (bitmap.width, bitmap.rows),
            'bearing': (glyph.bitmap_left, glyph.bitmap_top),
            'advance': glyph.advance.x >> 6
        }

    def render_text(self, text, x, y, scale=1.0, color=(1.0, 1.0, 1.0)):
        if not text:
            return

        glUseProgram(self.shader_program)
        # 设置文本颜色 uniform
        loc_color = glGetUniformLocation(self.shader_program, "textColor")
        glUniform3f(loc_color, color[0], color[1], color[2])

        # 设置投影： 用列主顺序并在上传时不转置（GL_FALSE）
        # 这里构造 column-major 矩阵（OpenGL 希望的内存布局）
        proj = np.array([
            [2.0/self.window_width, 0.0, 0.0, 0.0],
            [0.0, +2.0/self.window_height, 0.0, 0.0],
            [0.0, 0.0, -1.0, 0.0],
            [-1.0, -1.0, 0.0, 1.0]
        ], dtype=np.float32)  # 这样得到的内存是列主顺序（numpy 默认 row-major，但 OpenGL 读取是按列）
        # 注意：如果你感觉坐标反了，可以改用 transpose 或调整 sign（这里 Y 轴翻转以便屏幕坐标(0,0)在左上）

        loc_proj = glGetUniformLocation(self.shader_program, "projection")
        glUniformMatrix4fv(loc_proj, 1, GL_FALSE, proj)

        # 告诉 shader textTexture 使用纹理单元 0
        loc_sampler = glGetUniformLocation(self.shader_program, "textTexture")
        glUniform1i(loc_sampler, 0)

        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)

        vertices = []
        textures_used = []
        start_index = 0

        for ch in text:
            if ch not in self.characters:
                continue
            c = self.characters[ch]
            xpos = x + c['bearing'][0] * scale
            ypos = y - (c['size'][1] - c['bearing'][1]) * scale
            w = c['size'][0] * scale
            h = c['size'][1] * scale

            if w > 0 and h > 0:
                # 采用常见的顶点/uv 顺序 (x,y,s,t)
                # 三角形1
                vertices.extend([xpos,     ypos + h,   0.0, 0.0])  # 左上
                vertices.extend([xpos,     ypos,       0.0, 1.0])  # 左下
                vertices.extend([xpos + w, ypos,       1.0, 1.0])  # 右下
                # 三角形2
                vertices.extend([xpos,     ypos + h,   0.0, 0.0])  # 左上
                vertices.extend([xpos + w, ypos,       1.0, 1.0])  # 右下
                vertices.extend([xpos + w, ypos + h,   1.0, 0.0])  # 右上

                end_index = len(vertices) // 4
                textures_used.append(
                    {'texture': c['texture'], 'start': start_index, 'count': end_index - start_index})
                start_index = end_index

            x += c['advance'] * scale

        if vertices:
            arr = np.array(vertices, dtype=np.float32)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr)

            for info in textures_used:
                glBindTexture(GL_TEXTURE_2D, info['texture'])
                glDrawArrays(GL_TRIANGLES, info['start'], info['count'])

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)


class ModernTextRenderer1:
    def __init__(self, font_path, font_size=48):
        self.characters = {}
        self.font_size = font_size
        self.setup_shaders()
        self.setup_buffers()
        self.load_font(font_path)

    def cleanup(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader_program)

    def setup_shaders(self):
        # 顶点着色器
        vertex_shader_source = """
        #version 330 core
        layout (location = 0) in vec2 aPos;
        layout (location = 1) in vec2 aTexCoord;
        
        out vec2 TexCoord;
        
        uniform mat4 projection;
        
        void main()
        {
            gl_Position = projection * vec4(aPos, 0.0, 1.0);
            TexCoord = aTexCoord;
        }
        """

        # 片段着色器
        fragment_shader_source = """
        #version 330 core
        in vec2 TexCoord;
        out vec4 FragColor;
        
        uniform sampler2D textTexture;
        uniform vec3 textColor;
        
        void main()
        {
            // vec4 sampled = vec4(1.0, 1.0, 1.0, texture(textTexture, TexCoord).r);
            // FragColor = vec4(textColor, 1.0) * sampled;

            float alpha = texture(textTexture, TexCoord).r;
            FragColor = vec4(textColor, alpha);
        }
        """

        # 编译着色器
        try:
            vertex_shader = compileShader(
                vertex_shader_source, GL_VERTEX_SHADER)
            fragment_shader = compileShader(
                fragment_shader_source, GL_FRAGMENT_SHADER)
            self.shader_program = compileProgram(
                vertex_shader, fragment_shader)
            print("着色器编译成功")
        except Exception as e:
            print(f"着色器编译失败: {e}")

    def setup_buffers(self):
        # 生成 VAO、VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # 预分配缓冲区大小（6个顶点 * 4个float * 100个字符）
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 100 *
                     sizeof(GLfloat), None, GL_DYNAMIC_DRAW)

        # 设置顶点属性指针
        # 位置属性
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE,
                              4 * sizeof(GLfloat), ctypes.c_void_p(0))
        # 纹理坐标属性
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 *
                              sizeof(GLfloat), ctypes.c_void_p(2 * sizeof(GLfloat)))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def load_font(self, font_path):
        """加载字体文件并预渲染 ASCII 字符集"""
        try:
            self.face = freetype.Face(font_path)
            self.face.set_pixel_sizes(0, self.font_size)

            # 预加载常用字符
            for char_code in range(32, 127):  # ASCII 可打印字符
                char = chr(char_code)
                self.load_char(char)

            print(f"成功加载字体: {font_path}, 大小: {self.font_size}")
        except Exception as e:
            print(f"字体加载失败: {e}")
            # 回退到默认字体或创建占位符

    def load_char(self, char):
        """加载单个字符到纹理"""
        if char in self.characters:
            return

        # 加载字符字形
        self.face.load_char(char, freetype.FT_LOAD_RENDER)
        bitmap = self.face.glyph.bitmap
        glyph = self.face.glyph
        print(char)

        # 生成纹理
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # 重要：单字节对齐，针对宽度不是4的情况
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # 处理不同位图格式
        if bitmap.pixel_mode == freetype.FT_PIXEL_MODE_MONO:
            # 单色位图转换为灰度
            data = self.mono_to_grayscale(bitmap)
        else:
            # 灰度位图
            data = np.array(bitmap.buffer, dtype=np.ubyte)

        # 设置纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 上传纹理数据
        if bitmap.width > 0 and bitmap.rows > 0:
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RED,
                bitmap.width, bitmap.rows, 0,
                GL_RED, GL_UNSIGNED_BYTE, data
            )
        else:
            # 对于空格等无可见图形的字符，创建1x1的透明纹理
            empty_data = np.array([0], dtype=np.ubyte)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RED,
                1, 1, 0,
                GL_RED, GL_UNSIGNED_BYTE, empty_data
            )

        # 存储字符信息
        self.characters[char] = {
            'texture': texture,
            'size': (bitmap.width, bitmap.rows),
            'bearing': (glyph.bitmap_left, glyph.bitmap_top),
            'advance': glyph.advance.x >> 6  # 转换为像素
        }

        glBindTexture(GL_TEXTURE_2D, 0)

    def mono_to_grayscale(self, bitmap):
        """将单色位图转换为灰度"""
        width = bitmap.width
        rows = bitmap.rows
        pitch = bitmap.pitch

        # 创建灰度数据数组
        data = np.zeros((rows, width), dtype=np.ubyte)

        for y in range(rows):
            for x in range(width):
                byte_index = y * pitch + x // 8
                bit_index = 7 - (x % 8)  # FT 位图是 MSB 优先

                if byte_index < len(bitmap.buffer):
                    byte_val = bitmap.buffer[byte_index]
                    bit_val = (byte_val >> bit_index) & 1
                    data[y, x] = 255 if bit_val else 0

        return data.flatten()

    def get_text_size(self, text, scale=1.0):
        """计算文本的宽度和高度"""
        width = 0
        max_height = 0

        for char in text:
            if char in self.characters:
                ch = self.characters[char]
                width += ch['advance'] * scale
                max_height = max(max_height, ch['size'][1] * scale)

        return width, max_height

    def render_text(self, text, x, y, scale=1.0, color=(1.0, 1.0, 1.0)):
        """渲染文本"""
        if not text:
            return

        glUseProgram(self.shader_program)
        glUniform3f(glGetUniformLocation(self.shader_program, "textColor"),
                    color[0], color[1], color[2])

        # 设置投影矩阵
        projection = np.array([
            [2.0/self.window_width, 0.0, 0.0, 0.0],
            [0.0, 2.0/self.window_height, 0.0, 0.0],
            [0.0, 0.0, -1.0, 0.0],
            [-1.0, -1.0, 0.0, 1.0]
        ], dtype=np.float32)

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"),
                           1, GL_FALSE, projection)

        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)

        # 为整个文本准备顶点数据
        vertices = []
        textures_used = []  # 记录使用的纹理和对应的顶点范围

        start_index = 0

        for char in text:
            self.load_char(char)
            if char not in self.characters:
                continue  # 跳过未加载的字符

            ch = self.characters[char]

            # 计算位置
            xpos = x + ch['bearing'][0] * scale
            ypos = y - (ch['size'][1] - ch['bearing'][1]) * scale
            w = ch['size'][0] * scale
            h = ch['size'][1] * scale

            # 跳过完全透明的字符（如空格）
            if w > 0 and h > 0:
                # 每个字符的6个顶点（2个三角形）
                # 三角形1
                vertices.extend(
                    [xpos,     ypos + h,   0.0, 0.0])  # 左下
                vertices.extend([xpos + w, ypos,       1.0, 1.0])  # 右上
                vertices.extend([xpos,     ypos,       0.0, 1.0])  # 左上

                # 三角形2
                vertices.extend([xpos,     ypos + h,   0.0, 0.0])  # 左下
                vertices.extend([xpos + w, ypos + h,   1.0, 0.0])  # 右下
                vertices.extend([xpos + w, ypos,       1.0, 1.0])  # 右上

                # 记录这个字符使用的纹理和顶点范围
                end_index = len(vertices) // 4  # 每个顶点4个float
                textures_used.append({
                    'texture': ch['texture'],
                    'start': start_index,
                    'count': end_index - start_index
                })
                start_index = end_index

            x += ch['advance'] * scale

        if vertices:
            # 上传顶点数据
            vertices_array = np.array(vertices, dtype=np.float32)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0,
                            vertices_array.nbytes, vertices_array)

            # 按纹理分组绘制
            for texture_info in textures_used:
                # print(texture_info)
                glBindTexture(GL_TEXTURE_2D, texture_info['texture'])
                glDrawArrays(
                    GL_TRIANGLES, texture_info['start'], texture_info['count'])

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
