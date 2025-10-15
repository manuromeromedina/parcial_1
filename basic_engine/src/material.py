from texture import Texture

# apariencia de un objeto
# combina shaderprogram con un conjunto de texture
# interfaz para actualizar uniforms del shader
class Material:
    def __init__(self, shader_program, textures_data = []):
        self.__shader_program = shader_program
        self.__textures_data = textures_data

    @property
    def shader_program(self):
        return self.__shader_program
    
    @property
    def textures_data(self):
        return self.__textures_data
    
    def set_uniform(self, name, value):
        self.__shader_program.set_uniform(name, value)

# agrega propiedades fisicas simples como color base y reflectividad
# se envian al compute shader para calcular la interacción de los rayos
# solo tomamos un color solido
class StandardMaterial(Material):
    def __init__(self, shader_program, albedo: Texture, reflectivity=0.0):
        self.reflectivity = reflectivity
        self.colorRGB = albedo.image_data.data[0,0] # primer pixel de la textura albedo
     
        super().__init__(shader_program, textures_data=[albedo])