

class Graphics:
    def __init__(self, ctx, model, material):
        self.__ctx = ctx
        self.__model = model
        self.__material = material
        
        self.__vbo = self.create_buffers()
        self.__ibo = ctx.buffer(model.indices.tobytes())
        self.__vao = ctx.vertex_array(material.shader_program.prog, [*self.__vbo], self.__ibo)
        
        self.__textures = self.load_textures(material.texture_data)
        
    def create_buffers(self):
        buffers = []
        shader_attributes = self.__material.shader_program.attributes
        
        for attribute in self.__model.vertex_layout.get_attributes():
            if attribute.name in shader_attributes:
                vbo = self.__ctx.buffer(attribute.array.tobytes())
                buffers.append((vbo, attribute.format, attribute.name))
        return buffers
        
    def load_textures(self, texture_data):
        textures = {}
        for texture in texture_data:
            if texture.image_data:
                texture_ctx = self.__ctx.texture(texture.size, texture.channels_amount, texture.get_bytes())
                if texture.build_mipmaps:
                    texture_ctx.build_mipmaps()
                texture_ctx.repeat_x = texture.repeat_x
                texture_ctx.repeat_y = texture.repeat_y
                textures[texture.name] = (texture, texture_ctx)
        return textures
    
    def render(self, uniforms):
        for name, value in uniforms.items():
            if name in self.__material.shader_program.prog:
                self.__material.set_uniform(name, value)
                
        for i, (name, (_, tex_ctx)) in enumerate(self.__textures.items()):
            tex_ctx.use(i)
            self.__material.shader_program.set_uniform(name, i)
            
        self.__vao.render()
        
    def update_texture(self, texture_name, new_data):
        if texture_name not in self.__textures:
            raise ValueError(f"No existe la textura {texture_name}")
        
        texture_obj, texture_ctx = self.__textures[texture_name]
        texture_obj.update_data(new_data)
        texture_ctx.write(texture_obj.get_bytes())