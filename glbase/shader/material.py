from OpenGL.GL import *


class Material(object):
    def __init__(self):
        self.uniform_map={}
        self.textures=[]

    def set(self, **kwargs):
        for k, v in kwargs.items():
            self.uniform_map[k]=v

    def onInitialize(self):
        for texture in self.textures:
            texture.onInitialize()

    def begin(self, shader):
        # backface culling
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CW)
        glCullFace(GL_BACK)
        # alpha test
        glEnable(GL_ALPHA_TEST);
        glAlphaFunc(GL_GREATER, 0.5);

        # texture begin
        if len(self.textures)>0:
            glActiveTexture(GL_TEXTURE0)
            shader.set_uniform(s_texture=[0])
            self.textures[0].begin()
        # uniform variable
        shader.set_uniform(**self.uniform_map)

    def end(self, shader):
        if len(self.textures)>0:
            self.textures[0].end()

