# para saber si un rayo intercept un objeto necesitamos de hitbox
# representación geométrica simplificada que enmarca a un objeto poligonal
# se utiliza para detectar colisiones o intersecciones
# es una estructura lógica/matemática

#tendra un posición y una escala

import glm

class Hit:
       # recibe una función que paunta al me2todo del objeto que devuelve su matriz actualizada
    def __init__(self, get_model_matrix, hittable = True):
        self.__model_matrix = get_model_matrix
        self.hittable = hittable

    @property
    def model_matrix(self) -> glm.mat4:
        return self.__model_matrix()

    #obtenemos la ultima columna de la matriz que representa la traslación
    @property
    def position(self) -> glm.vec4:
        m = self.model_matrix
        return glm.vec3(m[3].x, m[3].y, m[3].z)
    
    #obtenemos la longitud de cada vector base de la mtriz (columnas 0,1,2)
    @property
    def scale(self) -> glm.vec3:
        m = self.model_matrix
        return glm.vec3(glm.length(glm.vec3(m[0])),
                        glm.length(glm.vec3(m[1])),
                        glm.length(glm.vec3(m[2])))
    
    # comprueba si un rayo colisiona con el objeto
    # cada subclase lo definira segu su propia gemotría
    def check_hit(self, origin, direction) :
        if (not self.hittable):
            return False
        
        raise NotImplementedError("Subclasses should implement this method")
        
# representa una caja de colisión alineada a los ejes mundiales 
class HitBox(Hit):
    def __init__(self, get_model_matrix, hittable = True):
        super().__init__(get_model_matrix, hittable)

    # recibe el origen y la dirección de un rayo
    # se utilizan tuplas de 3 coordenadas --> vec3 --> normalizamos
    def check_hit(self, origin, direction):
       
        if (not self.hittable):
            return False
        
        origin = glm.vec3(origin)
        direction = glm.normalize(glm.vec3(direction))

        # calculamos los limites de la caja a partir de su posición y escala
        # determinar así la esquina inferior y la esquina superior del volumen
        mix_bounds = self.position - self.scale
        max_bounds = self.position + self.scale 

        # un rayo puede tener dos puntos de intersección o uno solo en caso de tangencial
        # se representa medianto el parametro t en la ecuación de rayo 
        # P(t) = origen + t * direccion

        # para cada eje, se despeja el valor de t de la ecuación usando como origen los planos de min y max
        # entrada del rayo en ese eje
        tmin = (mix_bounds - origin) / direction
        #salida del rayo en ese eje
        tmax = (max_bounds - origin) / direction

        # como no sabemos los valores, reorganizamos los valores para que t1 siempre sea la entrada
        t1 = glm.min(tmin,tmax)
        t2 = glm.max(tmin,tmax)

        # calculamos el t_near y t_far

        # t_near --> valor de entrada global, el mayor de las entradas en x,y,z
        # representa el punto más cercano en el que el rayo entra en la caja
        t_near = max(t1.x, t1.y, t1.z)
        # t_far --> valor de salida global, el menor de las salidas x,y,z
        # representa el punto más lejano en el que el rayo sale de la caja
        t_far = min(t2.x, t2.y, t2.z)

        # devolver un valor booleano 
        # el rayo entra por algún punto de la caja y sale mas adelante ?
        # true --> si existe intersección  (t_near <= t_far y t_far >= 0).
        # false --> si el rayo no atraviesa la caja
        return t_near <= t_far and t_far >= 0
    
class HitBoxOBB(Hit):
    def __init__(self, get_model_matrix, hittable = True):
        super().__init__(get_model_matrix, hittable)

    def check_hit(self,origin,direction):
        if (not self.hittable):
            return False
        
        origin = glm.vec3(origin)
        direction = glm.normalize(glm.vec3(direction))

        #con la inversa, transformamos el rayo en sus componentes locales
        inv_model = glm.inverse(self.model_matrix)
        #multiplicamos el origen del rayo por la inversa usando coordenadas homogéneas w = 1.0 (porque es un punto)
        local_origin = inv_model * glm.vec4(origin, 1.0)
        #multiplicamos la dirección por la misma inversa con w = 0.0,  no debe verse afectada por la traslación
        local_dir = inv_model * glm.vec4(direction, 0.0)

        # convertimos el resultado a vec3 (local_origin, local_dir)
        local_origin = glm.vec3(local_origin)

        #normalizamos local_dir para obtener una dirección unitaria en el espacio local.
        local_dir = glm.normalize(glm.vec3(local_dir))

        # calculamos los limites de la cajausando las variables transformadas al espacio total
        mix_bounds = glm.vec3(-1,-1,-1)
        max_bounds = glm.vec3(1,1,1)

        # para cada eje, se despeja el valor de t de la ecuación usando como origen los planos de min y max
        # entrada del rayo en ese eje
        tmin = (mix_bounds - local_origin) / local_dir
        #salida del rayo en ese eje
        tmax = (max_bounds - local_origin) / local_dir

        # como no sabemos los valores, reorganizamos los valores para que t1 siempre sea la entrada
        t1 = glm.min(tmin,tmax)
        t2 = glm.max(tmin,tmax)

        t_near = max(t1.x, t1.y, t1.z)
        t_far = min(t2.x, t2.y, t2.z)

        return t_near <= t_far and t_far >= 0