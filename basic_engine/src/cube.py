from model import Model
from hit import  HitBoxOBB
import numpy as np
import glm

class Cube(Model):
    def __init__(self, position=(0,0,0), rotation=(0,0,0), scale=(1,1,1), name="cube" ,animated = True, hittable = True):
        self.name = name
        self.animated = animated
        self.position = glm.vec3(*position)
        self.rotation = glm.vec3(*rotation)
        self.scale = glm.vec3(*scale)
        # variable collision e instanciamos un HitBox
        self.__colision = HitBoxOBB(get_model_matrix= lambda: self.get_model_matrix(), hittable = hittable)

        vertices = np.array([
            -1,-1,-1,  1,-1,-1,  1,1,-1, -1,1,-1,
            -1,-1,1,   1,-1,1,   1,1,1,  -1,1,1
        ], dtype='f4')


        colors = np.array([
            1,0,0, 0,1,0, 0,0,1, 1,1,0,
            1,0,1, 0,1,1, 1,1,1, 0,0,0
        ], dtype='f4')


        normals = np.array([
            -1,-1,-1,  1,-1,-1,  1,1,-1, -1,1,-1,
            -1,-1,1,   1,-1,1,   1,1,1,  -1,1,1
        ], dtype='f4')


        texcoords = np.array([
            0,0, 1,0, 1,1, 0,1,
            0,0, 1,0, 1,1, 0,1
        ], dtype='f4')


        indices = np.array([
            0,1,2, 2,3,0, 4,5,6, 6,7,4,
            0,4,7, 7,3,0, 1,5,6, 6,2,1,
            3,2,6, 6,7,3, 0,1,5, 5,4,0
        ], dtype='i4')

        self.__vertices = vertices

        super().__init__(vertices, indices, colors, normals, texcoords)

    @property
    def aabb(self):
        #reorganizamos el array de vertices para obtener cada punto
        verts3 = self.__vertices.reshape(-1,3)
        
        # multiplicamos cada vertice por la model_matriz del objeto para transformarlo
        # de espacio local a espacio global
        # usamo glm.vec4 con w=1 porque estamos transformando posiciones
        pts = [self.get_model_matrix() * glm.vec4(v[0], v[1], v[2], 1.0) for v in verts3]

        # extraemos las coordenadas
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        zs = [p.z for p in pts] 

        # primero devolvemos el punto mínimo de AABB (esquina mas baja)
        # despues el punto maximo de AABB (esquina mas alta)
        return (glm.vec3(min(xs), min(ys), min(zs)),
                    glm.vec3(max(xs), max(ys), max(zs)))

    # delega la comprobación de colision al HitBox asociado y devuelve un valor booleano
    # indica si ocurrió o no 
    def check_hit(self,origin,direction):
        return self.__colision.check_hit(origin,direction)

    def get_model_matrix(self):
        model = glm.mat4(1)
        model = glm.translate(model, self.position)
        model = glm.rotate(model, glm.radians(self.rotation.x % 360), glm.vec3(1,0,0))
        model = glm.rotate(model, glm.radians(self.rotation.y % 360), glm.vec3(0,1,0))
        model = glm.rotate(model, glm.radians(self.rotation.z % 360), glm.vec3(0,0,1))
        model = glm.scale(model, self.scale)
        return model