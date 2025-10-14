import glfw

from OpenGL.GL import *
from tr import ModernTextRenderer, ModernTextRenderer1


def main():
    # 初始化 GLFW
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(800, 600, "文本渲染示例", None, None)
    glfw.make_context_current(window)

    # 初始化文本渲染器（指定字体文件路径）
    # text_renderer = ModernTextRenderer("c:\\windows\\fonts\\arial.ttf", 24)
    text_renderer = ModernTextRenderer1("c:\\windows\\fonts\\msyh.ttc", 24)
    text_renderer.window_width = 800
    text_renderer.window_height = 600

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 绘制3D场景...

        # 启用文本渲染状态
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 禁用深度测试（确保文本显示在最前面）
        glDisable(GL_DEPTH_TEST)

        # 清除颜色
        glClearColor(0.2, 0.3, 0.3, 1.0)  # 设置非黑色背景以便观察

        # 渲染文本
        text_renderer.render_text(
            "Hello, World!", 50, 550, 1.0, (1.0, 1.0, 1.0))
        text_renderer.render_text("OpenGL 文本渲染", 50, 520, 1.0, (0.0, 1.0, 1.0))
        text_renderer.render_text("FPS: 60", 50, 490, 0.8, (1.0, 0.5, 0.0))

        # 恢复状态
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        glfw.swap_buffers(window)
        glfw.poll_events()

    text_renderer.cleanup()
    glfw.terminate()


if __name__ == "__main__":
    main()
