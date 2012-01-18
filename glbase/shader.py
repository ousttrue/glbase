# coding: utf-8
import ctypes
import sys
import re
from OpenGL.GL import *
#from OpenGL.GL.VERSION.GL_3_2 import *
import numpy


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


class Shader(object):
    def __init__(self, type, src):
        self.src=src
        self.shader=glCreateShader(type)
        glShaderSource(self.shader, self.src)
        glCompileShader(self.shader)
        self.log()

    def log(self):
        length=glGetShaderiv(self.shader, GL_INFO_LOG_LENGTH)
        if length > 1:
            print 'SHADER ERROR: ', length, glGetShaderInfoLog(self.shader)
            sys.exit()


class VertexShader(Shader):
    def __init__(self, src):
        Shader.__init__(self, GL_VERTEX_SHADER, src)


class FragmentShader(Shader):
    def __init__(self, src):
        Shader.__init__(self, GL_FRAGMENT_SHADER, src)


COMMENT_PATTERN=re.compile(r"(?://|/\*)")
LINE_PATTERN=re.compile(r"//.*?\n", re.S)
C_PATTERN=re.compile(r"/\*.*?\*/", re.S)
def drop_comment(src):
    while True:
        m=COMMENT_PATTERN.search(src)
        if not m:
            break
        if m.group(0)=='//':
            src=re.sub(LINE_PATTERN, '', src)
        elif m.group(0)=='/*':
            src=re.sub(C_PATTERN, '', src)
        else:
            assert False
    return src


def parse(src):
    no_comment=drop_comment(src)
    #print no_comment
    vars=[]
    for s in no_comment.split(';'):
        splited=s.split()
        if len(splited)!=3:
            break
        kind, type, name=[e.strip() for e in splited]
        if kind=='attribute':
            vars.append(Attribute(type, name))
        elif kind=='uniform':
            vars.append(Uniform(type, name))
        elif kind=='varying':
            pass
        else:
            print 'unknown kind', kind
            assert False
    return vars


class Program(object):
    def __init__(self, vs_src, fs_src):
        vs=VertexShader(vs_src)
        fs=FragmentShader(fs_src)
        self.program=glCreateProgram()
        glAttachShader(self.program, vs.shader)
        glAttachShader(self.program, fs.shader)
        self.log()
        glLinkProgram(self.program)
        self.log()
        self.index_map={}
        self.attach_map=dict([arg.create_attacher(self.get_index(arg)) 
            for arg in parse(vs_src)])
        self.attach_map.update(dict([arg.create_attacher(self.get_index(arg)) 
            for arg in parse(fs_src)]))

    def log(self):
        length=glGetProgramiv(self.program, GL_INFO_LOG_LENGTH)
        if length > 1:
            print ' ERROR: ', length, glGetProgramInfoLog(self.program)
            sys.exit()

    def get_index(self, arg):
        if arg.name not in self.index_map:
            index=arg.get_index(self.program)
            if index==-1:
                print 'fail to get index for %s' % arg.name
                assert(False)
            self.index_map[arg.name]=index
        return self.index_map[arg.name]

    def set_texture(self, **kwargs):
        for k, v in kwargs.items():
            if v==GL_TEXTURE0:
                glActiveTexture(GL_TEXTURE0)
                self.attach_map[k](0)
            else:
                print 'unknown texture unit', v
                assert False

    def set_uniform(self, **kwargs):
        for k, v in kwargs.items():
            self.attach_map[k](*v)

    def set_attribute(self, **kwargs):
        for k, v in kwargs.items():
            self.attach_map[k](*v)

    def begin(self):
        #print 'begin', self.program
        glUseProgram(self.program)

    def end(self):
        #print 'end', self.program
        glUseProgram(0)

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, type, value, traceback):
        self.end()


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
        for material in self.materials:
            material.onInitialize()

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
        #glDrawElements(GL_TRIANGLES, self.indices_count, GL_UNSIGNED_INT, None)
        for material in self.materials:
            with material as m:
                m.onShader(shader)


class UniformSupplier(object):
    def __init__(self):
        self.uniform_map={}
        self.textures=[]
        self.offset=0

    def set(self, **kwargs):
        for k, v in kwargs.items():
            self.uniform_map[k]=v

    def onInitialize(self):
        for texture in self.textures:
            texture.onInitialize()

        self.indices_vbo=create_vbo(GL_ELEMENT_ARRAY_BUFFER, 
                numpy.array(self.indices, numpy.uint))
        self.indices_count=len(self.indices)

    def begin(self):
        for texture in self.textures:
            texture.begin()

    def end(self):
        for texture in self.textures:
            texture.end()

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, type, value, traceback):
        self.end()

    def onShader(self, shader):
        # backface culling
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CW)
        glCullFace(GL_BACK)
        # alpha test
        glEnable(GL_ALPHA_TEST);
        glAlphaFunc(GL_GREATER, 0.5);
        # uniform variable
        shader.set_uniform(**self.uniform_map)
        # draw element
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indices_vbo)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None);
