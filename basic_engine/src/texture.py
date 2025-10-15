#encapsula toda la info relacionada con una textura q se aplicara a un modelo 3D o Quad
# datos crudos de la imagen y flags de configuración

import numpy as np

# contenedor de los pixeles de la imafen
# matriz con tres dimensiones: alto x ancho x canales
# nos permitira manipular la imagen de forma intuitiva]
# podremos pintar píxel por píxel mediante un método set_pixel, y 
# al final podremos transformarla en bytes con un método tobytes
class ImageData:
    def __init__(self, height, width, channels, color = (0,0,0)):
        self.data = np.full((height,width,channels), color, dtype=np.uint8)
    
     #el primer índice corresponde al eje y (filas) y el segundo índice al eje x (columnas).
    def set_pixel(self, x, y, color):
        self.data[y,x] = color 

    def tobytes(self):
        return self.data.tobytes()
    
class Texture:
    def __init__(self, name = "u_texture", width =1, height =1, channels_amount =3, image_data:ImageData = None, 
                color = (0,0,0), repeat_x = False, repeat_y = False, build_mipmaps = False):
       # nombre de la textura que usaremos como uniform en los shaders
        self.name = name
       # tamaño de la textura antes de ser mapeada
        self.size = (width, height)
       # cantidad de componentes o canales de color que admite la textura
        self.channels_amount = channels_amount
       # repeticion horizontal de la textura.
       # si es true --> la imagen de fondo se repite en ambos ejes
        self.repeat_x = repeat_x
        self.repeat_y = repeat_y
      # si es true, se generarán secuencias de versiones de baja resolución de una textura
      # precalculadas para mejorar la calidad visual y 
      # velocidad de renderiza
        self.build_mipmaps = build_mipmaps

        self.width = width
        self.height = height

        if image_data is not None:
            self._image_data = image_data
        else:
            self._image_data = ImageData(height, width, channels_amount, color) 

    @property
    def image_data(self):
        return self._image_data
    
    def update_data(self, new_data: ImageData):
        self._image_data = new_data
    
    def set_pixel(self, x, y, color):
        self._image_data.set_pixel(x,y,color)
      
    def get_bytes(self):
        return self._image_data.tobytes()