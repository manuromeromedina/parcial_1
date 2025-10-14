import moderngl
import pyglet

class Window(pyglet.window.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.ctx = moderngl.create_context()
        self.scene = None

    def set_scene(self, scene):
        self.scene = scene
        scene.start()

    def on_draw(self):
        self.clear()
        # limpiar también el z-buffer
        self.ctx.clear(0.1, 0.1, 0.1, 1.0, depth=1.0)

        # activar depth test
        self.ctx.enable(moderngl.DEPTH_TEST)

        if self.scene:
         self.scene.render()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.scene is None: 
            return
        
        #Convertir posición del mouse a u,v [0,1]
        u = x / self.width
        v = y / self.height
        
        self.scene.on_mouse_click(u,v)

    def on_resize(self, width, height):
        if self.scene:
            self.scene.on_resize(width, height)

    def run(self):  # activar el loop de la ventana
        pyglet.app.run()
