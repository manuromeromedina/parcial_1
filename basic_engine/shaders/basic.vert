#version 330

// Inputs desde el VAO.
in vec3 in_pos;
in vec3 in_color;

// Output => lo recibe el Fragment Shader.
out vec3 v_color;

// Variable "global" que recibimos para aplicar transformaciones al objeto.
uniform mat4 Mvp;

void main() {
    gl_Position = Mvp * vec4(in_pos, 1.0);
    v_color = in_color;
}
