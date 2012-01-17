# coding: utf-8
"""
"""
import re
import os
import zipfile
from OpenGL.GL import *
import glbase


def load_model(argv):
    if not os.path.isdir(argv[0]) and not zipfile.is_zipfile(argv[0]):
        assert(len(argv)==1)
        argv=[
                os.path.dirname(argv[0]), 
                os.path.basename(argv[0]), 
                ]
    print 'load_model', argv
    asset=glbase.get_asset(argv[0].decode('cp932'))
    if not asset:
        print 'fail to get asset'
        return

    if len(argv)<2:
        # specify asset entry
        entries=asset.get_entries(lambda asset, entry: glbase.asset.loadable(asset, entry))
        if len(entries)==0:
            print 'no loadable entry'
            return
        elif len(entries)==1:
            index=0
        else:
            index=selector(entries)
        entry_string=entries[index]
    else:
        entry_string=argv[1].decode('cp932')

    print entry_string
    return glbase.load_model(asset, entry_string)


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
        model=load_model(self.initial_model)
        assert model
        self.root=model
        self.is_initialized=True

    def draw(self):
        if not self.is_initialized:
            self.initilaize()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glMatrixMode(GL_PROJECTION)
        #glLoadIdentity()
        #glMatrixMode(GL_MODELVIEW)
        #glLoadIdentity()

        self.root.shader.set_uniform(
                u_model_matrix=self.view.get_matrix()
                )
        self.root.draw()

        glFlush()

