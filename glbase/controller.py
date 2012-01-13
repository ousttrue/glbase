# coding: utf-8
"""
"""
import re
from OpenGL.GL import *


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

    def initilaize(self):
        self.view.onResize()
        glEnable(GL_DEPTH_TEST)
        glClearColor(*self.bg)

    def draw(self):
        if not self.is_initialized:
            self.initilaize()
            self.is_initialized=True

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.view.draw()
        self.root.draw()

        glFlush()

