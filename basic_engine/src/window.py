
import moderngl
import pyglet

class Window(pyglet.window.Window):
    def __init__(self, width, height, title):
        config = pyglet.gl.Config(double_buffer=True, depth_size=24)
        super().__init__(width, height, title, resizable=True, config=config)        
       
        self.ctx = moderngl.create_context()
        self.ctx.viewport = (0, 0, width, height)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.scene = None
        
    def set_scene(self, scene):
        self.scene = scene
        scene.start()


    def on_draw(self): #se ejecuta por frame, limpia y renderiza
        #self.clear()

        self.ctx.clear()
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        if self.scene:
            self.scene.render()

    def on_mouse_press(self,x,y, button, modifiers):
        if self.scene is None:
            return
        
        # convertir posición del mouse a u,v [0,1]
        u = x / self.width
        v = y / self.height

        self.scene.on_mouse_click(u,v)

    def on_resize(self, width, height): #escalar el contexto al escalar la ventana
        if self.scene:
            self.scene.on_resize(width, height)

    def run(self): #activar el loop de la ventana
        pyglet.app.run()