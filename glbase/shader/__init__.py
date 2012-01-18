# coding: utf-8
import sys
import re
from OpenGL.GL import *
import numpy

from .variable import *
from .drawable import *
from .material import *


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
        #if len(splited)!=3:
        #    break
        splited=[e.strip() for e in splited]
        kind=splited[0]
        if kind=='void':
            break
        elif kind=='attribute':
            vars.append(Attribute(*splited[1:]))
        elif kind=='uniform':
            vars.append(Uniform(*splited[1:]))
        elif kind=='varying' or kind=='const':
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
            try:
                self.attach_map[k](*v)
            except KeyError as e:
                print e

    def set_attribute(self, **kwargs):
        for k, v in kwargs.items():
            self.attach_map[k](*v)

    def begin(self):
        glUseProgram(self.program)

    def end(self):
        glUseProgram(0)

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, type, value, traceback):
        self.end()

