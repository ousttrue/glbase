#!/usr/bin/env python
# coding: utf-8
"""
wxPython asset viewer 
"""
import zipfile
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


def selector(entries):
    print '[select entry]'
    for i, e in enumerate(entries):
        print i, e
    print '?'
    sys.stdout.flush()
    try:
        index=int(raw_input(''))
    except ValueError as e:
        index=0
    return index


if __name__=="__main__":
    import sys
    import os
    import codecs
    sys.stdout = codecs.lookup('utf_8')[-1](sys.stdout)
    name=os.path.basename(sys.argv[0])
    if len(sys.argv)<2:
        print '''
usage:
    %s {model}
or
    %s {asset}
or
    %s {asset} {model relative path from asset} 

{asset} should be directory or zip archive.  
''' % (name, name, name)
        sys.exit(0)

    app = wx.App(False)
    frame=Frame(None)

    frame.controller.set_projection(glbase.view.PerspectiveProjection())
    frame.controller.set_view(glbase.view.RokuroView())
    frame.controller.load_model(*sys.argv[1:])
    def callback(keycode):
        if keycode==81: # q
            frame.Destroy()
        else:
            print 'callback 0x%02x(%02d)' %  (keycode, keycode) 
    frame.controller.delegate(KeyDownCallback(callback))

    frame.SetSize((640, 480))
    frame.Show()
    app.MainLoop()

