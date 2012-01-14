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


def load_model(argv):
    asset=glbase.get_asset(argv[1].decode('cp932'))
    if not asset:
        print 'fail to get asset'
        return

    if len(argv)<3:
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
        entry_string=asset, argv[2].decode('cp932')

    model=glbase.load_model(asset, entry_string)
    if not model:
        print 'fail to load model'
        return

    return model


if __name__=="__main__":
    import sys
    import os
    import codecs
    sys.stdout = codecs.lookup('utf_8')[-1](sys.stdout)
    if len(sys.argv)<2:
        print '''
usage:
    %s {asset}
or
    %s {asset} {model relative path from asset} 

{asset} should be directory or zip archive.  
''' % os.path.dirname(sys.argv[0])
        sys.exit(0)

    model=load_model(sys.argv)
    if not model:
        sys.exit(1)

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

