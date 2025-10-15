#version 330

// inputs desde el vao
in vec3 in_pos;
in vec3 in_color;

// output --> lo que recibe el fragment
out vec3 v_color;

// variable global que recibimos para aplicar al objeto
uniform mat4 Mvp;
uniform float pos_x;

void main(){
    gl_Position = Mvp * vec4(in_pos, 1.0);
    v_color = in_color + vec3(1.0, 0.3, 0.0) * pos_x; // azul
    
}
