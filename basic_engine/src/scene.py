from graphics import Graphics
import glm
import numpy as np
from raytracer import RayTracer
import math

class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.objects = []
        self.graphics = {}
        self.camera = camera
        self.view = camera.get_view_matrix()
        self.projection = camera.get_perspective_matrix()
        self.time = 0

    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = Graphics(self.ctx, model, material)

    def render(self):
        self.time += 0.01
        for obj in self.objects:
            if(obj.name != "Sprite"):
                obj.rotation += glm.vec3(0.8, 0.6, 0.4)
                obj.position.x += math.sin(self.time) * 0.01
            
            model = obj.get_model_matrix()
            mvp = self.projection * self.view * model
            self.graphics[obj.name].render({'Mvp': mvp})
            
    def start(self):
        print("Start!")

    def on_mouse_click(self, u, v):
        ray = self.camera.raycast(u, v)
        
        hit_any = False
        for obj in self.objects:
            if obj.check_hit(ray.origin, ray.direction):
                print(f"¡Golpreaste al objeto {obj.name}!")
                hit_any = True

        if not hit_any:
            print("😶 No le pegaste a ningún objeto.")

    def on_resize(self, width, height):
        # Ajustar el viewport y recalcular la proyección con el nuevo aspect
        self.ctx.viewport = (0, 0, width, height)
        self.camera.aspect = width / height


class RayScene(Scene):
    def __init__(self, ctx, camera, width, height):
        super().__init__(ctx, camera)
        self.raytracer = RayTracer(camera, width, height)
        
    def start(self):
        self.raytracer,render_frame(self.objects)
        if "Sprite" in self.graphics:
            self.graphics["Sprite"].update_texture("u_texture", self.raytracer.get_texture())
            
    def render(self):
        super().render()
        
    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.raytracer = RayTracer(self.camera, width, height)
        self.start()
        
        