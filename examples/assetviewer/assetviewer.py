#!/usr/bin/env python
# coding: utf-8
"""
wxPython asset viewer 
"""
import wx
import glbase
import glbase.view
import glglue.wxglcanvas


class KeyDownCallback(object):
    def __init__(self, callback):
        self.onKeyDown=callback


class Frame(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(Frame, self).__init__(parent, **kwargs)
        # setup opengl widget
        self.controller=glbase.Controller()
        self.glwidget=glglue.wxglcanvas.Widget(self, self.controller)
        # packing
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        sizer.Add(self.glwidget, 1, wx.EXPAND)


if __name__=="__main__":
    import sys
    import os
    if len(sys.argv)!=3:
        print '''
usage:
    %s {asset} {model relative path from asset} 

{asset} should be directory or zip archive.  
''' % os.path.dirname(sys.argv[0])
        sys.exit(0)

    asset=glbase.get_asset(sys.argv[1].decode('cp932'))
    if not asset:
        print 'fail to get asset'
        sys.exit(1)

    model=glbase.load_model(asset, sys.argv[2].decode('cp932'))
    if not model:
        print 'fail to load model'
        sys.exit(2)

    app = wx.App(False)
    frame=Frame(None)

    frame.controller.set_view(glbase.view.RokuroView())
    frame.controller.set_root(model)
    def callback(keycode):
        if keycode==81: # q
            frame.Destroy()
        else:
            print 'callback 0x%02x(%02d)' %  (keycode, keycode) 
    frame.controller.delegate(KeyDownCallback(callback))

    frame.SetSize((640, 480))
    frame.Show()
    app.MainLoop()

