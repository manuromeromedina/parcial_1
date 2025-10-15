from graphics import Graphics, ComputeGraphics
import glm
import numpy as np
from raytracer import RayTracer, RayTracerGPU
import math

class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.objects = []
        self.graphics = {}
        self.camera = camera
        self.view = camera.get_view_matrix()
        self.projection = camera.get_perspective_matrix()
        self.time = 0.0

    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = Graphics(self.ctx, model, material)

    def render(self):
        self.time += 0.01
        self.view = self.camera.get_view_matrix()
        self.projection = self.camera.get_perspective_matrix()

        for obj in self.objects:
            if getattr(obj, "animated", False):
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01

            mvp = self.projection * self.view * obj.get_model_matrix()
            self.graphics[obj.name].render({'Mvp': mvp})

    def start(self):
        print("Start!")

    def on_mouse_click(self, u, v):
        ray = self.camera.raycast(u, v)
        hit_any = False
        for obj in self.objects:
            if obj.check_hit(ray.origin, ray.direction):
                print(f"¡Golpeaste al objeto {obj.name}!")
                hit_any = True
        if not hit_any:
            print("😶 No le pegaste a ningún objeto.")

    def on_resize(self, width, height):
        self.ctx.viewport = (0, 0, width, height)
        self.camera.aspect = width / height


class RayScene(Scene):
    def __init__(self, ctx, camera, width, height):
        super().__init__(ctx, camera)
        self.raytracer = RayTracer(camera, width, height)

    def start(self):
        self.raytracer.render_frame(self.objects)
        if "Sprite" in self.graphics:
            self.graphics["Sprite"].update_texture("u_texture", self.raytracer.get_texture())

    def render(self):
        super().render()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.raytracer = RayTracer(self.camera, width, height)
        self.start()


class RaySceneGPU(Scene):
    def __init__(self, ctx, camera, width, height, output_model, output_material):
        # 1) Inicializar base primero
        super().__init__(ctx, camera)

        # 2) Guardar tamaño
        self.width = width
        self.height = height

        # 3) Sprite/Quad donde escribirá el compute shader (u_texture)
        self.output_graphics = Graphics(ctx, output_model, output_material)

        # 4) Raytracer GPU
        self.raytracer = RayTracerGPU(self.ctx, self.camera, self.width, self.height, self.output_graphics)

        # Buffers de matrices / materiales (se rellenan en start())
        self.primitives = []
        self.models_f = None
        self.inv_f = None
        self.mats_f = None

    def add_object(self, model, material):
        self.objects.append(model)
        # Usa ComputeGraphics si tu graphics.py lo implementa; si no, dejá Graphics
        try:
            self.graphics[model.name] = ComputeGraphics(self.ctx, model, material)
        except NameError:
            self.graphics[model.name] = Graphics(self.ctx, model, material)

    def start(self):
        print("Start Raytracing!")
        n = len(self.objects)
        self.primitives = []
        self.models_f = np.zeros((n, 16), dtype='f4')
        self.inv_f    = np.zeros((n, 16), dtype='f4')
        self.mats_f   = np.zeros((n, 16), dtype='f4')

        self._update_matrix()
        self._matrix_to_ssbo()

    def render(self):
        self.time += 0.01
        for obj in self.objects:
            if getattr(obj, "animated", False):
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01

        if self.raytracer is not None:
            self._update_matrix()
            self._matrix_to_ssbo()
            self.raytracer.run()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.width, self.height = width, height
        # Re-crear el raytracer con el nuevo tamaño (y re-bind de image)
        self.raytracer = RayTracerGPU(self.ctx, self.camera, self.width, self.height, self.output_graphics)
        # Re-subir matrices
        self._matrix_to_ssbo()

    def _update_matrix(self):
        self.primitives = []
        for i, (name, graphics) in enumerate(self.graphics.items()):
            # Estos nombres deben existir en tu Graphics/ComputeGraphics:
            # - create_primitive(self.primitives)
            # - create_transformation_matrix(self.models_f, i)
            # - create_inverse_transformation_matrix(self.inv_f, i)
            # - create_material_matrix(self.mats_f, i)
            graphics.create_primitive(self.primitives)
            graphics.create_transformation_matrix(self.models_f, i)
            graphics.create_inverse_transformation_matrix(self.inv_f, i)
            graphics.create_material_matrix(self.mats_f, i)

    def _matrix_to_ssbo(self):
        # Bindings 0,1,2,3 deben coincidir con tu compute shader:
        # layout(std430, binding = 0) buffer Models { mat4 modelMatrices[]; };
        # layout(std430, binding = 1) buffer InvModels { mat4 inverseModelMatrices[]; };
        # layout(std430, binding = 2) buffer Materials { mat4 materialData[]; };
        # layout(std430, binding = 3) buffer BVH { mat4 bvhNodes[]; };
        if self.raytracer is None:
            return
        self.raytracer.matrix_to_ssbo(self.models_f, 0)
        self.raytracer.matrix_to_ssbo(self.inv_f, 1)
        self.raytracer.matrix_to_ssbo(self.mats_f, 2)
        self.raytracer.primitives_to_ssbo(self.primitives, 3)