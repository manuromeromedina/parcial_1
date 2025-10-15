import glm
from ray import Ray

#datos de una camara simple
# Útil para obtener las coordenadas de la cámara y su proyección
class Camera:
    def __init__(self, position, target, up, fov, aspect, near, far):
        self.position = glm.vec3(*position)
        self.target = glm.vec3(*target)
        self.up = glm.vec3(*up)
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far
        # cuando un rayo no golpea ningún objeto la imagen muestre un cielo suave en lugar de un color plano
        self.__sky_color_top = None
        self.__sky_color_bottom = None

    # Estos colores se inicializan como None y se asignan con el método set_sky_colors(top, bottom)
    def set_sky_colors(self, top, bottom):
        self.__sky_color_top = glm.vec3(*top)
        self.__sky_color_bottom = glm.vec3(*bottom)

    # Para suavizar la transición entre ambos extremos se utiliza la función de potencia 
    # cuando el rayo no colisiona con ningún objeto, 
    # el fondo que se pinta corresponde a este gradiente de cielo calculado a partir de la altura.
    def get_sky_gradient(self, height):
        point = pow(0.5 * (height + 1.0), 1.5)
        return (1.0 - point) * self.__sky_color_bottom + point * self.__sky_color_top

    def get_perspective_matrix(self):
        return glm.perspective(glm.radians(self.fov), self.aspect, self.near, self.far)

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, self.up)

    # recibe la coordenadas normalizadas de la pantalla (la posición del mouse de [0,1])
    # hay que transformarlas a NDC, de [-1,1]

    def raycast(self, u, v):
        # fov --> angulo de vision vertical u horizontal de la camara
        # se divide entre 2 porque la apertura se reparte de hacia arriba y hacia abajo
        # la tangente convierte ese angulo en una relación trigonométrica 
            #dice cuando se abre la camara por unidad de distancia
        fov_adjustment = glm.tan(glm.radians(self.fov)/2)

        #  para u --> esta entre [0,1]
            # se escala 2 * u --> [0,2]
            # se resta 1 --> queda centralizado  [-1,1]
            # si u = 0 --> ndc_x = - 1 (izquierda)
            # si u = 1 --> ndc_x =  1 (derecha)
            # al multiplicar por el fov, corregimos según el ángulo de vision y la relación de aspecto
        ndc_x = ((2 * u ) - 1) * self.aspect * fov_adjustment

        #  para v --> esta entre [0,1]
            # se escala 2 * u --> [0,2]
            # se invierte con 1 - (2*v) para corregir el eje vertical
            # ya que en la ventana v = 0 esta en la esquina superior izquierda --> y+1            
            # si v = 0 --> ndc_y = 1 (superior)
            # si v = 1 --> ndc_y = -1 (inferior)
            # al multiplicar por el fov, corregimos según el ángulo de vision y la relación de aspecto

        ndc_y = ((2 * v ) - 1) * fov_adjustment

        # debemos calcular la dirección asumiendo que la cámara  mira en una dirección -Z
        # el rayo es un vector desde el origen (0,0,0 en cámara) hacia ray_dir_camera
        # se normaliza el vector para obtener una dirección unitaria
        ray_dir_camera = glm.vec3(ndc_x, ndc_y, -1.0)
        ray_dir_camera = glm.normalize(ray_dir_camera)

        # tenemos que llevarlo al espacio mundial --> multiplicación de matrices
        # se convierte a vecotr con coordenadas homogeneas (vec4) con w=0, porque es un vector dirección
        view = self.get_view_matrix()
        # se multiplica por la matriz 4x4 de vista inversa
        # la matriz view convierte un vector de espacio de mundo a espacio de cámara 
        # la inversa hace lo opuesto
        inv_view = glm.inverse(view)
        # se toma el resultado como vec3, que sera la dirección final del rayo en el mundo
        # el origen del rayo es simplemente la posición de la camara  en el espacio del mundo
        ray_dir_world = glm.vec3(inv_view * glm.vec4(ray_dir_camera, 0.0))

        return Ray(self.position, ray_dir_world)
    
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, self.up)
    
     
    def get_inverse_view_matrix(self):
        return glm.inverse(self.get_view_matrix())