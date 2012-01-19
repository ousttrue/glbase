#!/usr/bin/env python
"""
File Explorer
"""
import sys
import os
import  wx
#from wx.lib.buttons import GenButton
from win32com.shell import shell, shellcon
from win32con import FILE_ATTRIBUTE_NORMAL

import glglue.wxglcanvas
import glbase
import glbase.view


EVTTYPE_CHDIR = wx.NewEventType()
EVT_CHDIR = wx.PyEventBinder(EVTTYPE_CHDIR)
class ChdirEvent(wx.PyCommandEvent):
    def __init__(self, path):
        wx.PyCommandEvent.__init__(self, EVTTYPE_CHDIR)
        self.path = path


EVTTYPE_HISTORY = wx.NewEventType()
EVT_HISTORY = wx.PyEventBinder(EVTTYPE_HISTORY)
class HistoryEvent(wx.PyCommandEvent):
    def __init__(self, d):
        wx.PyCommandEvent.__init__(self, EVTTYPE_HISTORY)
        self.d = d


EVTTYPE_VIEW = wx.NewEventType()
EVT_VIEW = wx.PyEventBinder(EVTTYPE_VIEW)
class ViewEvent(wx.PyCommandEvent):
    def __init__(self, path):
        wx.PyCommandEvent.__init__(self, EVTTYPE_VIEW)
        self.path = path


class ToolBar(wx.ToolBar):
    def __init__(self, parent):
        TBFLAGS = ( wx.TB_HORIZONTAL
                | wx.NO_BORDER
                | wx.TB_FLAT
                #| wx.TB_TEXT
                #| wx.TB_HORZ_LAYOUT
                )
        super(ToolBar, self).__init__(parent, style=TBFLAGS)

        tsize = (24,24)
        self.SetToolBitmapSize(tsize)
        # back
        bmp_back =  wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, tsize)
        back=self.AddLabelTool(-1, "back", bmp_back, shortHelp="Back", 
                longHelp="back to previous folder")
        self.Bind(wx.EVT_TOOL, self.OnGoBack, id=back.GetId())
        # forward
        bmp_forward = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, tsize)
        forward=self.AddLabelTool(-1, "forward", bmp_forward, shortHelp="Forward", 
                longHelp="forward folder history")
        self.Bind(wx.EVT_TOOL, self.OnGoForward, id=forward.GetId())

        self.Realize()

    def OnGoBack(self, event):
        self.GetEventHandler().ProcessEvent(HistoryEvent(-1))

    def OnGoForward(self, event):
        self.GetEventHandler().ProcessEvent(HistoryEvent(1))


class PathArea(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(PathArea, self).__init__(parent, **kwargs)
        #self.SetSizer(wx.WrapSizer())
        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        self.buttons=[]
        drives=glbase.asset.get_drives()
        self.current_path_map=dict([(l, glbase.asset.Path(l+u':')) for l in drives])
        self.current_drive=drives[0]

    def removeChildren(self, destroy=True):
        """
        Remove all my children components and optionally
        destroy them.
        """
        for i in range(len(self.GetChildren())):
            self.GetSizer().Remove(0)
        if destroy:
            self.DestroyChildren()

    def chdir(self, path):
        assert isinstance(path, glbase.asset.IAsset)
        self.current_drive=path.get_drive()
        self.current_path_map[self.current_drive]=path
        self.removeChildren()
        # drive selector
        drives=glbase.asset.get_drives()
        self.drives=wx.Choice(self, -1, size=(32, 32), choices=drives)
        current_drive_index=None
        for i, l in enumerate(drives):
            if self.current_drive==l:
                current_drive_index=i
                break
        assert current_drive_index is not None
        self.drives.SetSelection(current_drive_index)
        self.GetSizer().Add(self.drives, 0, wx.ALL)
        self.drives.Bind(wx.EVT_CHOICE, self.OnSelectDrive)
        # path button
        self.buttons=[self.create_button(e) 
            for e in self.current_path_map[self.current_drive].from_root()]

    def OnSelectDrive(self, event):
        print 'OnSelectDrive', event.GetString()
        self.GetEventHandler().ProcessEvent(
                ChdirEvent(self.current_path_map[event.GetString()]))
               
    def create_button(self, asset):
        name=asset.path.get_name()
        if name==u'':
            # for root path
            name=u' '
        b=wx.Button(self, -1, name, style=wx.BU_EXACTFIT)
        if isinstance(asset, glbase.asset.ZipAsset):
            b.SetBackgroundColour(wx.Colour(255, 128, 0))
        elif isinstance(asset, glbase.asset.DirectoryAsset):
            b.SetBackgroundColour(wx.Colour(255, 255, 0))
        self.GetSizer().Add(b, 0, wx.ALL)
        e=ChdirEvent(asset)
        def OnClick(event):
            print 'OnClick', e.path.__str__().encode('utf-8')
            self.GetEventHandler().ProcessEvent(e)
        b.Bind(wx.EVT_BUTTON, OnClick)
        return b
 

class FileList(wx.ListCtrl):
    def __init__(self, parent):
        super(FileList, self).__init__(
                parent, -1, 
                style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES
                )

        # setup image list
        self.il = wx.ImageList(16, 16)

        self.id_empty=self.il.Add(self.makeBlank())
        self.id_file=self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER))
        self.id_dir=self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER))

        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        self.extension_map={}

        # setup columns
        self.InsertColumn(0, "name")
        self.SetColumnWidth(0, 300)

        # attributes
        self.attr_dir = wx.ListItemAttr()
        self.attr_dir.SetBackgroundColour("yellow")

        self.attr_archive = wx.ListItemAttr()
        self.attr_archive.SetBackgroundColour("orange")

        # event binding
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

    def chdir(self, path):
        assert isinstance(path, glbase.asset.IAsset)
        self.asset=path
        self.files=sorted(self.asset.get_entries())
        self.SetItemCount(len(self.files))
        self.Refresh()

    def extension_to_bitmap(self, extension):
        """
        http://ginstrom.com/scribbles/2007/08/31/file-list-with-icons-on-wxpython-windows/
        dot is mandatory in extension
        """
        flags = shellcon.SHGFI_SMALLICON | \
                shellcon.SHGFI_ICON | \
                shellcon.SHGFI_USEFILEATTRIBUTES

        retval, info = shell.SHGetFileInfo(extension,
                                 FILE_ATTRIBUTE_NORMAL,
                                 flags)
        # non-zero on success
        assert retval

        hicon, iicon, attr, display_name, type_name = info

        # Get the bitmap
        icon = wx.EmptyIcon()
        icon.SetHandle(hicon)
        bitmap=wx.BitmapFromIcon(icon)
        return self.il.Add(bitmap)

    def makeBlank(self):
        empty = wx.EmptyBitmap(16,16,32)
        dc = wx.MemoryDC(empty)
        dc.SetBackground(wx.Brush((0,0,0,0)))
        dc.Clear()
        del dc
        empty.SetMaskColour((0,0,0))
        return empty

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        asset=self.files[event.m_itemIndex]
        if isinstance(asset, glbase.asset.DirectoryAsset):
            self.GetEventHandler().ProcessEvent(ChdirEvent(asset))
        elif isinstance(asset, glbase.asset.ZipAsset):
            self.GetEventHandler().ProcessEvent(ChdirEvent(asset))
        else:
            self.GetEventHandler().ProcessEvent(ViewEvent(asset))

    def getColumnText(self, index, col):
        print 'getColumnText'
        item = self.GetItem(index, col)
        return item.GetText()

    def OnItemDeselected(self, evt):
        pass

    def OnGetItemText(self, item, col):
        return self.files[item].get_name()

    def OnGetItemImage(self, item):
        target=self.files[item]
        extension=target.get_extension()
        if extension:
            if not extension in self.extension_map:
                icon=self.extension_to_bitmap(extension.encode('ascii'))
                self.extension_map[extension]=icon
            return self.extension_map[extension]
        elif target.is_dir():
            return self.id_dir
        else:
            return self.id_file

    def OnGetItemAttr(self, item):
        return None


class Viewer(wx.Panel):
    def __init__(self, parent, **kwargs):
        super(Viewer, self).__init__(parent, **kwargs)
        # setup opengl widget
        self.controller=glbase.Controller()
        self.glwidget=glglue.wxglcanvas.Widget(self, self.controller)
        # packing
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        sizer.Add(self.glwidget, 1, wx.EXPAND)

    def OnView(self, event):
        path=event.path
        print 'OnView', path.__str__().encode('utf-8')
        self.Refresh()


class Frame(wx.Frame):
    def __init__(self, parent):
        super(Frame, self).__init__(parent)

        sizer=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        # toolbar
        tb=ToolBar(self)
        sizer.Add(tb, 0, wx.EXPAND)
        # path area
        self.asset=PathArea(self)
        sizer.Add(self.asset, 0, wx.EXPAND)
        #
        splitter=wx.SplitterWindow(self)
        self.filer=FileList(splitter)
        self.viewer=Viewer(splitter, style=wx.BORDER_SUNKEN)
        splitter.SplitVertically(self.filer, self.viewer, -100)
        sizer.Add(splitter, 1, wx.EXPAND)

        # history
        self.history=[]
        self.history_end=0

        self.Bind(EVT_CHDIR, self.OnChdir)
        self.Bind(EVT_HISTORY, self.OnHistory)
        self.Bind(EVT_VIEW, self.viewer.OnView)

    def OnChdir(self, e):
        #print 'OnChdir', e.path
        self.chdir(e.path)

    def chdir(self, path):
        assert isinstance(path, glbase.asset.IAsset)
        self.history=self.history[:self.history_end]
        self.history.append(path)
        self.history_end+=1
        self._chdir(path)
        self.Layout()
        self.Refresh()

    def _chdir(self, path):
        self.asset.chdir(path)
        self.filer.chdir(path)

    def OnHistory(self, e):
        #print 'OnHistory', e.d
        self.history_end+=e.d
        if self.history_end<0:
            self.history_end=0
        elif self.history_end>len(self.history):
            self.history_end=len(self.history)
        self._chdir(self.history[self.history_end-1])


if __name__ == '__main__':
    app = wx.App(False)
    frame=Frame(None)
    frame.chdir(len(sys.argv)>1 
            and glbase.asset.get_asset(sys.argv[1].decode('utf-8')) 
            or glbase.asset.pwd())

    frame.viewer.controller.set_projection(glbase.view.PerspectiveProjection())
    frame.viewer.controller.set_view(glbase.view.RokuroView())
    #frame.viewer.controller.load_model(*sys.argv[1:])
    def callback(keycode):
        if keycode==81: # q
            frame.Destroy()
        else:
            print 'callback 0x%02x(%02d)' %  (keycode, keycode) 
    class KeyDownCallback(object):
        def __init__(self, callback):
            self.onKeyDown=callback
    frame.viewer.controller.delegate(KeyDownCallback(callback))

    frame.Show()
    app.MainLoop()

