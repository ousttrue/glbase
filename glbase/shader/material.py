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
        texture_map={}
        for i, (texture, unit) in enumerate(zip(self.textures, [
            GL_TEXTURE0,
            GL_TEXTURE1,
            GL_TEXTURE2,
            GL_TEXTURE3,
            GL_TEXTURE4,
            GL_TEXTURE5,
            GL_TEXTURE6,
            GL_TEXTURE7
            ])):
            glActiveTexture(unit)
            texture.begin()
            texture_map['s_texture%d' % i]=[i]
        shader.set_uniform(**texture_map)
        # uniform variable
        shader.set_uniform(**self.uniform_map)

    def end(self, shader):
        for texture in self.textures:
            texture.end()

