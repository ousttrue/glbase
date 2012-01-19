#!/usr/bin/env python
# coding: utf-8
import numpy


class BaseView(object):
    def __init__(self):
        self.x=0
        self.y=0
        self.isLeftDown=False
        self.isMiddelDown=False
        self.isRightDown=False
        self.matrix=numpy.identity(4, 'f')

    def set_size(self, w, h):
        self.w=w
        self.h=h

    def onLeftDown(self, x, y):
        self.isLeftDown=True
        self.x=x
        self.y=y

    def onLeftUp(self, x, y):
        self.isLeftDown=False

    def onMiddleDown(self, x, y):
        self.isMiddelDown=True
        self.x=x
        self.y=y

    def onMiddleUp(self, x, y):
        self.isMiddelDown=False

    def onRightDown(self, x, y):
        self.isRightDown=True
        self.x=x
        self.y=y

    def onRightUp(self, x, y):
        self.isRightDown=False

    def onMotion(self, x, y):
        print("onMotion", x, y)

    def onInitialize(self):
        pass

    def get_matrix(self):
        return self.matrix

