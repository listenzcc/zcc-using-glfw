#version 330 core

in vec4 iColor;
out vec4 oColor;

void main() {
    oColor = iColor;
    gl_FragColor = iColor;
}