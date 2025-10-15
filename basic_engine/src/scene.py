# Posiciona una cámara, administra los objetos y sus Graphics (VBO, VAO,
#ShaderProgram). Realiza transformaciones a los objetos que están en la escena y
#actualiza sus shaders. También actualiza viewport en on resize.
from graphics import Graphics, ComputeGraphics
from raytracer import RayTracer, RayTracerGPU
import glm
import math
import numpy as np
class Scene:
    def __init__(self, ctx, camera):
        self.ctx = ctx
        self.objects = []
        self.graphics = {} #objeto con shader
        self.camera = camera
        self.model = glm.mat4(1)
        self.view = camera.get_view_matrix()
        self.projection = camera.get_perspective_matrix()
        self.time = 0
        

    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = Graphics(self.ctx, model, material)
    

    def render(self):
        self.time += 0.01
        #Rotar los objetos fuera del shader y actualizar sus matrices 
    
        for obj in self.objects:
            if(obj.animated):
                obj.rotation.x += 0.8 
                obj.rotation.y += 0.6 
                obj.rotation.z += 0.4 

                obj.position.x += math.sin(self.time) * 0.025
                obj.position.y += math.sin(self.time) * 0.001
                obj.position.z += math.sin(self.time) * 0.025

            model = obj.get_model_matrix()
            mvp = self.projection * self.view * model
            self.graphics[obj.name].render({'Mvp': mvp})
            self.graphics[obj.name].render({'pos_x': obj.position.x})


    def on_mouse_click(self, u, v):
        ray = self.camera.raycast(u,v)

        for obj in self.objects:
            if obj.check_hit(ray.origin, ray.direction):
                print(f"Golpeaste al objeto {obj.name}!")
                
    def on_resize(self, width, height):
        self.ctx.viewport = (0,0,width,height)
        self.camera.projection = glm.perspective(glm.radians(45),width/height, 0.1 , 100.0 )

    #depuracion
    def start(self):
        print("Start")

#es extender la funcionalidad de la escena base para que soporte raytracing utilizando un framebuffer.
class RayScene(Scene):
    def __init__(self, ctx, camera, width, height):
        super().__init__(ctx, camera)
        self.raytracer = RayTracer(camera,width,height)

    def start(self):
        self.raytracer.render_frame(self.objects)
        #busca el objeto con nombre "Sprite" y 
        # pide que actualice su textura con el contenido generado en el framebuffer.
        if "Sprite" in self.graphics:
            self.graphics["Sprite"].update_texture("u_texture", self.raytracer.get_texture())
        
    def render(self):
        super().render()

    #limpia el framebuffer, lo ajusta al nuevo tamaño de pantalla y 
    # ejecuta nuevamente start para redibujar el buffer con las dimensiones correctas.
    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.raytracer = RayTracer(self.camera, width, height)
        self.start()

# sigue usando el pipeline tradicional de OpenGL para dibujar Quad
# utiliza compute shader para calcular raytracing en todos los objetos de la escena

class RaySceneGPU(Scene):
    def __init__(self, ctx, camera, width, height, output_model, output_material):
        self.ctx = ctx
        self.camera = camera
        self.width = width
        self.height = height
        self.raytracer = None
       
       # creamos quad
        self.output_graphics = Graphics(ctx, output_model, output_material)
       # crea la instancia raytracergpu  --> ejecuta el compute shader 
        self.raytracer = RayTracerGPU(self.ctx, self.camera, self.width, self.height, self.output_graphics)
       
        super().__init__(self.ctx, self.camera)
    
    # cada vez que incorporamos un nuevo objeto, lo guardamos en computegraphics
    #  necesita datos adicionales como buffers, materiales y jerarquía
    def add_object(self, model, material):
        self.objects.append(model)
        self.graphics[model.name] = ComputeGraphics(self.ctx, model, material)
        
    def start(self):
        print("Start Raytracing")
        self.primitives = []
        n = len(self.objects)

        #matrices de tamaño (n,16) porque cada matriz de transformacion 4x4 tiene 16 valores
        # guarda las matrices de transformación de los objetos (posición, rotación y escala)
        self.models_f = np.zeros((n,16), dtype='f4')
        # guarda las matrices inversas de transformación (se usa para el calculo inverso de colisiones)
        self.inv_f = np.zeros((n,16), dtype='f4')
        # guarda la info de materiales de cada obj (color y reflectividad )
        self.mats_f = np.zeros((n,4), dtype='f4')

        # recorre cada objeto, obtiene su info geométrica y la transforma en el formato para compu shader
        self._update_matrix()

        # escribe esos arreglos en SSBOs
        self._matrix_to_ssbo()

    def render(self):
        self.time += 0.01
        for obj in self.objects:
            if obj.animated:
                obj.rotation.x += 0.8 
                obj.rotation.y += 0.6 
                obj.rotation.z += 0.4 

                obj.position.x += math.sin(self.time) * 0.025
                obj.position.y += math.sin(self.time) * 0.001
                obj.position.z += math.sin(self.time) * 0.025

        if(self.raytracer is not None):
           self._update_matrix()  
           self._matrix_to_ssbo()
           self.raytracer.run()


    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.width, self.height  = width, height
        self.camera.aspect = width/height

    def _update_matrix(self):
        self.primitives = []

        for i, (name, graphics) in enumerate(self.graphics.items()):
            graphics.create_primitive(self.primitives)
            graphics.create_transformation_matrix(self.models_f, i)
            graphics.create_inverse_transformation_matrix(self.inv_f,i)
            graphics.create_material_matrix(self.mats_f, i)

    def _matrix_to_ssbo(self):
        self.raytracer.matrix_to_ssbo(self.models_f, 0)
        self.raytracer.matrix_to_ssbo(self.inv_f, 1)
        self.raytracer.matrix_to_ssbo(self.mats_f, 2)
        self.raytracer.primitives_to_ssbo(self.primitives, 3)