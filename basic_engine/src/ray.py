import glm

# representa el rayo.
#recibe dos tuplas de tres coordenadas, origen y dirección
class Ray:
    def __init__(self, origin = (0,0,0), direction = (0,0,1)):
        # __atributo para evitar accesos accidentales desde fuera de la clase 
        # y resfuerza la encapsulación
        self.__origin = glm.vec3(*origin)
        self.__direction = glm.normalize(glm.vec3(*direction))

        # encapsulación
        # permite leer los valores y no modificar de forma directa

    @property
    def origin(self) -> glm.vec3:
        return self.__origin
    
    @property 
    def direction(self) -> glm.vec3:
        return self.__direction
    
