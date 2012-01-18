# coding: utf-8
"""
"""
import re
import os
from OpenGL.GL import *
import glbase


VS='''
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_texCoord;
//attribute vec3 a_skinning;
uniform vec3 light_direction;
uniform mat4 u_pv_matrix;
//varying vec3 v_normal;
varying vec2 v_texCoord;
varying float v_light_power;

void main()
{
    gl_Position = u_pv_matrix * vec4(a_position.x, a_position.y, a_position.z, 1.0);
    //v_normal=a_normal;
    v_texCoord=a_texCoord;
    v_light_power=0.5+0.5*max(0.0, -dot(light_direction, a_normal));
}                

'''


FS='''
varying vec2 v_texCoord;
varying float v_light_power;
uniform sampler2D s_texture0;
uniform vec4 u_color;

void main()
{
    vec4 tex=texture2D(s_texture0, v_texCoord);
    float inv=1.0-tex.a;
    gl_FragColor=vec4(
        vec3(
        tex.r*tex.a+u_color.r*inv,
        tex.g*tex.a+u_color.g*inv,
        tex.b*tex.a+u_color.b*inv
        )*v_light_power,
        tex.a+u_color.a);
}
'''


class Empty(object):
    def draw(self):
        pass


DELEGATE_PATTERN=re.compile('^on[A-Z]')


class Controller(object):
    def __init__(self):
        self.bg=(0.9, 0.5, 0.0, 0.0)
        self.set_view(Empty())
        self.set_root(Empty())
        self.is_initialized=False

    def onResize(self, w, h):
        self.view.set_size(w, h)
        glViewport(0, 0, w, h)

    def onLeftDown(self, x, y):
        print 'onLeftDown', x, y

    def onLeftUp(self, x, y):
        print 'onLeftUp', x, y

    def onMiddleDown(self, x, y):
        print 'onMiddleDown', x, y

    def onMiddleUp(self, x, y):
        print 'onMiddleUp', x, y

    def onRightDown(self, x, y):
        print 'onRightDown', x, y

    def onRightUp(self, x, y):
        print 'onRightUp', x, y

    def onMotion(self, x, y):
        print 'onMotion', x, y

    def onWheel(self, d):
        print 'onWheel', d

    def onKeyDown(self, keycode):
        print 'onKeyDown', keycode

    def onUpdate(self, d):
        print 'onUpdate', d

    def set_view(self, view):
        self.view=view
        self.delegate(self.view)

    def set_root(self, root):
        self.root=root
        self.delegate(self.root)

    def delegate(self, to):
        for name in dir(to):  
            if DELEGATE_PATTERN.match(name):
                method = getattr(to, name)  
                setattr(self, name, method)

    def load_model(self, asset_path, entry=None):
        if entry:
            asset=glbase.get_asset(asset_path.decode('cp932'))
            entry_string=entry.decode('cp932')
        else:
            asset=glbase.get_asset(os.path.dirname(asset_path).decode('cp932'))
            entry_string=os.path.basename(asset_path).decode('cp932')
        self.root=glbase.load_model(asset, entry_string)

    def initilaize(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(*self.bg)
        self.shader=glbase.shader.Program(VS, FS)
        self.view.onInitialize()
        self.root.onInitialize()
        self.is_initialized=True

    def draw(self):
        if not self.is_initialized:
            self.initilaize()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        with self.shader as s:
            s.set_uniform(
                    light_direction=[0.0, -1.0, 0.0]
                    )
            self.view.onShader(s)
            self.root.onShader(s)
        glFlush()

