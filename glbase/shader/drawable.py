import numpy
from OpenGL.GL import *


def create_vbo(type, array):
    vbo=glGenBuffers(1)
    glBindBuffer(type, vbo)
    glBufferData(type, array, GL_STATIC_DRAW)
    return vbo


class AttributeArray(object):
    def __init__(self, name, data=None):
        self.name=name
        self.data=data or []
        self.element_count=None

    def push(self, *args):
        for arg in args:
            self.data.append(arg)


class IndexedVertexArray(object):
    def __init__(self, indices, vertex_count, *attributes):
        self.indices=indices
        self.vertex_count=vertex_count
        self.attributes=attributes
        for array in self.attributes:
            array.element_count=len(array.data)/self.vertex_count
        self.materials=[]

    def onInitialize(self):
        # as float
        interleave_count=sum([len(array.data)/self.vertex_count 
            for array in self.attributes])
        stride=interleave_count*4

        # vbo
        self.interleave=numpy.zeros(self.vertex_count * interleave_count, numpy.float32)
        arrayiters=[(array, iter(array.data)) for array in self.attributes]
        pos=0
        for i in range(self.vertex_count):
            for array, it in arrayiters:
                for j in range(array.element_count):
                    self.interleave[pos]=it.next()
                    pos+=1
        assert pos==len(self.interleave)
        self.vbo=create_vbo(GL_ARRAY_BUFFER, self.interleave)

        # index vbo
        self.indices=[(
            create_vbo(GL_ELEMENT_ARRAY_BUFFER, 
                numpy.array(material.indices, numpy.uint)),
            len(material.indices)
            ) for material in self.materials ]

        # shader params
        shader_params=[]
        offset=0
        for array in self.attributes:
            shader_params.append((array.name, (self.vbo, stride, offset)))
            offset+=array.element_count*4
        self.shader_params=dict(shader_params)

    def onShader(self, shader):
        # set attribute variable
        shader.set_attribute(**self.shader_params)
        # draw elements
        for material, (vbo, index_count) in zip(self.materials, self.indices):
            # material begin
            material.begin(shader)
            # draw element
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vbo)
            glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None);
            # material end
            material.end(shader)

