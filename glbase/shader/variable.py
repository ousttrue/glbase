import ctypes
from OpenGL.GL import *


class Variable(object):
    def __init__(self, type, name):
        self.name=name
        self.type=type


class Attribute(Variable):
    def create_attacher(self, index):
        if self.type=='vec2':
            size=2
        elif self.type=='vec3':
            size=3
        elif self.type=='vec4':
            size=4
        else:
            print 'unknown type', self.type
            assert False
        def attach(vbo, stride, offset):
            glBindBuffer(GL_ARRAY_BUFFER, vbo);
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, 
                    stride, ctypes.c_void_p(offset))
            glEnableVertexAttribArray(index)
        return self.name, attach

    def get_index(self, program):
        return glGetAttribLocation(program, self.name)


class Uniform(Variable):
    def create_attacher(self, index):
        if self.type=='vec2':
            size=2
            def attach(x, y):
                glUniform2f(index, x, y)
            return self.name, attach
        elif self.type=='vec3':
            size=3
            def attach(x, y, z):
                glUniform3f(index, x, y, z)
            return self.name, attach
        elif self.type=='vec4':
            size=4
            def attach(x, y, z, w):
                glUniform4f(index, x, y, z, w)
            return self.name, attach
        elif self.type=='mat4':
            def attach(data):
                data = (ctypes.c_float*16)(*[n 
                    for row in data
                    for n in row])
                glUniformMatrix4fv(index, 1, GL_TRUE, data)
            return self.name, attach
        elif self.type=='sampler2D':
            def attach(data):
                glUniform1i(index, data)
            return self.name, attach
        else:
            print 'unknown type', self.type
            assert False

    def get_index(self, program):
        return glGetUniformLocation(program, self.name)

