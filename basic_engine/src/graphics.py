import numpy as np
import glm
# crea el VBO, IBO y VAO con el shaderprogram  y el format
# implementa el metodo render para renderizar el vao

class Graphics:
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material

        #VBO IBO Y VAO
        #VBO --> vertex buffer object: almacena los datos de los vertices
        self.__vbo = self.create_buffers()
        # IBO --> index buffer object: almacena los indices para dibujar los vertices
        self.__ibo = ctx.buffer(model.indices.tobytes())
        # VAO --> vertex array object: combina el vbo e ibo y define el formato de los datos
        self.__vao = ctx.vertex_array(material.shader_program.prog, [*self.__vbo], self.__ibo)

        self.__textures = self.load_textures(material.textures_data)
    # se recorre cada atributo expuesto del shader y se compara con los atributos que tare
    # el modelo, si coinciden, se crea el buffer y se agrega el VBO al array de buffers




    def create_buffers(self):
        buffers = []
        shader_attributes = self.__material.shader_program.attributes

        #lee los atributos
        for attribute in self.__model.vertex_layout.get_attribute():
            # por cada atributo del vertex, si attribute.name esta en los atributos del shader
            # se crea el buffer 
            if attribute.name in shader_attributes:
                vbo = self.__ctx.buffer(attribute.array.tobytes())
                buffers.append((vbo,attribute.format, attribute.name))

        return buffers

    #En el método load_textures por cada Texture en texture_data:
    def load_textures(self, textures_data):
        textures = {}
        for texture in textures_data:
            #Si existe información de la imagen,
            #Cargar la textura en el GPU con sus datos (ctx.texture).
            if texture.image_data:
                texture_ctx = self.__ctx.texture(texture.size, texture.channels_amount, texture.get_bytes())
             
                 #Aplicar texture_ctx.build_mipmaps() si corresponde.
                if texture.build_mipmaps:
                    texture_ctx.build_mipmaps()
               
                #Ajustar texture_ctx.repeat_x / repeat_y según flags.
                texture_ctx.repeat_x = texture.repeat_x
                texture_ctx.repeat_y = texture.repeat_y
                
                textures[texture.name] = (texture, texture_ctx)
     
        #Devolver lista con pares (nombre de textura, textura en memoria de GPU).
        return textures

    def bind_to_image(self, name = "u_texture", unit = 0, read = False, write=True):
        self.__textures[name][1].bind_to_image(unit, read, write)
        
    def render(self,uniforms):
        #Actualizar uniforms: los valores dinámicos (MVP, luz, tiempo) se actualizan por draw call. 
        # Iterar uniforms.items() y, si el nombre existe en el shader,
        # llamar actualizar el uniform en el shader.
        for name, value in uniforms.items():
            if name in self.__material.shader_program.prog:
                self.__material.set_uniform(name,value)

        #Bind de texturas: vincular la textura con el sampler del shader. 
        # Para cada textura (name, texture_ctx) en self.textures, 
        # notificar al shader con el uniform en el slot de memoria con localización n° i 
        # (el shader espera un entero que es el número de unidad de textura).
        for i, (name, (tex, texture_ctx)) in enumerate(self.__textures.items()):
            texture_ctx.use(i)
            self.__material.shader_program.set_uniform(name, i)
    
        # Dibujar VAO: self.vao.render().
        self.__vao.render()
        
    def update_texture(self, texture_name, new_data):
        if texture_name not in self.__textures:
            raise ValueError(f"No existe la textura {texture_name}")
        
        texture_obj, texture_ctx = self.__textures[texture_name]
        texture_obj.update_data(new_data)
        texture_ctx.write(texture_obj.get_bytes())

# encargada de generar SSBOs (shader storage buffer objects)
# interfaz entre un modelo y el sistema de raytracing en GPU
class ComputeGraphics(Graphics):
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material
        self.textures = material.textures_data        
        super().__init__(ctx, model, material)

    # calcula la AABB de un obj y la agrega a la lista de primitivas
    def create_primitive(self, primitives):
        amin, amax = self.__model.aabb
        primitives.append({"aabb_min": amin, "aabb_max": amax})

    # genera la matriz 4x4 del objeto y la guarda en el array
    def create_transformation_matrix(self, transformations_matrix, index):
        m = self.__model.get_model_matrix()
        transformations_matrix[index, :] = np.array(m.to_list(), dtype="f4").reshape(16)

    # guarda la matriz inversa, necesaria para pasar de coordenadas globales a locales.
    def create_inverse_transformation_matrix(self, inverse_transformations_matrix, index):
        m = self.__model.get_model_matrix()
        inverse = glm.inverse(m)
        inverse_transformations_matrix[index, :] = np.array(inverse.to_list(), dtype="f4").reshape(16)

    # empaqueta el color y reflectividad en un arreglo de 4 valores.
    def create_material_matrix(self, materials_matrix, index):
        reflectivity = self.__material.reflectivity
        r,g,b = self.__material.colorRGB

        r = r / 255.00 if r > 1.0 else r
        g = g / 255.00 if g > 1.0 else g
        b = b / 255.00 if b > 1.0 else b

        materials_matrix[index, :] = np.array([r,g,b,reflectivity], dtype="f4")

    