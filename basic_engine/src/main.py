from window import Window
from texture import Texture
from material import Material
from shader_program import ShaderProgram
from cube import Cube
from quad import Quad
from camera import Camera
from scene import Scene, RayScene
import numpy as np



# Ventana
window = Window(800, 600, "Parcial 1  - Manolo")

# Shader
shader_program = ShaderProgram(window.ctx, '../shaders/basic.vert', '../shaders/basic.frag')
shader_program_skybox = ShaderProgram(window.ctx, '../shaders/sprite.vert', '../shaders/sprite.frag',)

skybox_texture = Texture(width=WIDTH, height=HEIGHT, channels_amount=3, color=(0,0,0))

material = Material(shader_program)
material_sprite = Material(shader_program_skybox, textures_data = [skybox_texture])

# Objetos
cube1 = Cube((-2, 0, 0), (0, 45, 0), (1, 1, 1), name="Cube1")
cube2 = Cube((2, 0, 0), (0, 45, 0), (1, 1, 1), name="Cube2")
quad = Quad((0, 0, 0), (0, 0, 0), (6, 5, 1), name="Sprite", hittable = False)


# Cámara
camera = Camera((0, 0, 6), (0, 0, 0), (0, 1, 0), 45, window.width / window.height, 0.1, 100.0)


# Escena
scene = RayScene(window.ctx, camera, WIDTH, HEIGHT)

scene.add_object(quad, material_sprite)
scene.add_object(cube1, material)
scene.add_object(cube2, material)


# Carga de la escena y ejecución del loop principal
window.set_scene(scene)
window.run()
