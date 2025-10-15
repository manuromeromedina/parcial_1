from texture import Texture
from bvh import BVH
from shader_program import ComputeShaderProgram
#  generar un frame del raytracing en CPU y 
# depositarlo en una textura que luego visualizará un Quad

class RayTracer:
    def __init__(self, camera, width, height):
        self.camera = camera
        self.width = width
        self.height = height
        self.framebuffer = Texture(width=width, height=height, channels_amount=3)

        self.camera.set_sky_colors(top=(16,150,222), bottom=(181, 224, 247))

   
   # recorre los objetos comprobando si el rayo los intersecta
    def trace_ray(self, ray, objects):
        for obj in objects:
            if obj.check_hit(ray.origin, ray.direction):
                return (255, 0, 0)
         # Si no hay intersección 
         # devuelve el color del cielo calculado por camera.get_sky_gradient(height).   
        height = ray.direction.y
        return self.camera.get_sky_gradient(height)
    

    def render_frame(self, objects):
        #En cada iteración generamos un rayo que parte desde la cámara hacia la dirección correspondiente al píxel,
        #  luego trazamos ese rayo y finalmente pintamos la textura asignando el color resultante en la posición
        for y in range(self.height):
            for x in range(self.width):
                u = x / (self.width -1)
                v = y / (self.height -1)
                ray = self.camera.raycast(u,v)
                color = self.trace_ray(ray, objects)
                self.framebuffer.set_pixel(x, y, color)
   
    # leer la info generada en el framebuffer para usar en el render de quad
    def get_texture(self):
        return self.framebuffer.image_data
    
# inicializa y maneja el compute shader de raytracing
# crear una textura de salida en la que se escribira el resultado
# actualizar dicha textura en los graficos de salida


class RayTracerGPU:
    def __init__(self, ctx, camera, width, height, output_graphics):
        self.ctx = ctx
        self.width, self.height = width, height
        self.camera = camera
        self.width = width
        self.height = height
        self.compute_shader = ComputeShaderProgram(self.ctx, "shaders/raytracing.comp")
        self.output_graphics = output_graphics

        # seleccionamos una unidad de imagen
        self.texture_unit = 0
        # crear la textura de salida con el tamaño pedido y el formato
        self.output_texture = Texture("u_texture", self.width, self.height, 4, None, (255,255,255,255))
       # enviarr textura a graphics para que el quad la tenga disponible
        self.output_graphics.update_texture("u_texture", self.output_texture.image_data)
       # vincular la textura como la imagen para el compute shader
        self.output_graphics.bind_to_image("u_texture", self.texture_unit, read=False, write=True)

        # incializamos los valores de la posicón, target y fov
        self.compute_shader.set_uniform('cameraPosition', self.camera.position)
        self.compute_shader.set_uniform('inverseViewMatrix', self.camera.get_inverse_view_matrix())
        self.compute_shader.set_uniform('fieldOfView', self.camera.fov)

    def resize(self, width, height):
        self.width, self.height = width, height
        self.output_texture = Texture("u_texture", width, height, 4, None, (255,255,255,255))
        self.output_graphics.update_texture("u_texture", self.output_texture.image_data)

    # convierte un arreglo en un buffer de GPU y lo vincula a un índice (binding) específico
    def matrix_to_ssbo(self, matrix, binding=0):
        buffer = self.ctx.buffer(matrix.tobytes())
        # se usa para que el compute shader pueda escribir directamente en una textura.
        buffer.bind_to_storage_buffer(binding = binding)

    # divide el espacio en cajas que contienen primitivas, 
    # reduciendo drásticamente el número de chequeos de colisión que debe hacer cada rayo.
    def primitives_to_ssbo(self, primitives, binding = 3):
        self.bvh_nodes = BVH(primitives)
        self.bvh_ssbo = self.bvh_nodes.pack_to_bytes()
        buf_bvh = self.ctx.buffer(self.bvh_ssbo);
        buf_bvh.bind_to_storage_buffer(binding=binding)

    # divide en bloques y asigna un work group por bloque
    def run(self):
        groups_x = (self.width + 15 ) // 16
        groups_y = (self.height + 15 ) // 16

        self.compute_shader.run(groups_x=groups_x, groups_y=groups_y, groups_z=1)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.output_graphics.render({"u_texture": self.texture_unit})
