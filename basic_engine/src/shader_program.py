#carga de shaders
from moderngl import Attribute, Uniform
import numpy as np
import glm

class ShaderProgram:
    def __init__(self, ctx, vertex_shader_path, fragment_shader_path):
        with open(vertex_shader_path) as file:
            vertex_shader = file.read()
        with open(fragment_shader_path) as file:
            fragment_shader = file.read()

        self.prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        attributes = []
        uniforms = []

        for name in self.prog:
            member = self.prog[name]
            if type(member) is Attribute:
                attributes.append(name)
            if type(member) is Uniform:
                uniforms.append(name)
        
        self.attributes = list(attributes)
        self.uniforms = uniforms
   
   
   
   
    def set_uniform(self, name, value):
        if name  in self.uniforms:
            uniform = self.prog[name]
            # Caso matriz (ej: glm.mat4 convertido a np.array)
            if isinstance(value, glm.mat4):
                uniform.write(value.to_bytes())
            # Caso float
            elif hasattr(uniform, "value"):
                uniform.value = value


        # Caso glm (ej: glm.mat4 o glm.vec3)
        else:
            try:
                arr = np.array(value, dtype='f4')
                self.prog[name].write(arr.tobytes())
            except Exception as e:
                print(f"Could not set uniform {name}: {e}")

# carga el compute shader en el contexto de OpenGL
# no proceso vertices ni fragmentos
# trabaja sobre buffers y texturas arbitrarias
class ComputeShaderProgram:

    # cargamos un shader 
    def __init__(self,  ctx, compute_shader_path):
        with open(compute_shader_path) as file:
            compute_source = file.read()
        self.prog = ctx.compute_shader(compute_source)

        uniforms = []
        for name in self.prog:
            member = self.prog[name]
            if type(member) is Uniform:
                uniforms.append(name)

        self.uniforms = uniforms
    # lo asociamos al programa
    def set_uniform(self, name, value):
        if name in self.uniforms:
            uniform = self.prog[name]
            if isinstance(value, glm.mat4):
                uniform.write(value.to_bytes())
            elif hasattr(uniform, "value"):
                uniform.value = value

    def run(self, groups_x, groups_y, groups_z=1):
        self.prog.run(group_x=groups_x, group_y=groups_y, group_z=groups_z)

