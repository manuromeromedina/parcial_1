
#clase Vertex representa un atributo de vértice de forma abstracta

class Vertex:
    def __init__(self, name, format, array):
        self.__name = name
        self.__format = format
        self.__array = array

    @property
    def name(self):
        return self.__name
     
    @property
    def format(self):
        return self.__format
    
    @property
    def array(self):
        return self.__array


# agrupa un conjunto de atributos de vertices. describir qué datos forman parte   
class VertexLayout:
    def __init__(self):
        self.__attributes = []

    def add_attribute(self, name: str, format: str, array):
        self.__attributes.append(Vertex(name, format, array))

    def get_attribute(self):
        return self.__attributes
    

# clase base de todos los modelos 3D. 
#guarda indices
#construye el vertexlayout
# organiza posiciones, colores, normales y coordenadas

class Model:
    def __init__(self, vertices =None, indices =None, colors =None, normals =None, texcords =None):
        self.indices = indices
        self.vertex_layout = VertexLayout()

        if vertices is not None:
            self.vertex_layout.add_attribute("in_pos", "3f", vertices)
        
        if colors is not None:
            self.vertex_layout.add_attribute("in_color", "3f", colors)
       
        if normals is not None:
            self.vertex_layout.add_attribute("in_normal", "3f", normals)
       
        if texcords is not None:
            self.vertex_layout.add_attribute("in_uv", "2f", texcords)