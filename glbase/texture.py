import io
from PIL import Image
from OpenGL.GL import *


class Texture(object):
    def __init__(self, asset, entry_string):
        self.asset=asset
        self.entry_string=entry_string
        self.image=None
        self.id=0
        self.isInitialized=False

    def onInitialize(self):
        self.isInitialized=False

    def _createTexture(self):
        self.id=glGenTextures(1)
        if self.id==0:
            print("fail to glGenTextures")
            return False
        print("_createTexture: %d" % self.id)

        channels=len(self.image.getbands())
        w, h=self.image.size
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        if channels==4:
            print("RGBA")
            glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, self.image.tostring())
        elif channels==3:
            print("RGB")
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 
                    0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tostring())

    def begin(self):
        if not self.isInitialized:
            try:
                # load image
                if not self.image:
                    self.image=Image.open(io.BytesIO(self.asset.get(self.entry_string)))
                    if self.image:
                        print("load image:", self.entry_string)
                    else:
                        print("failt to load image:", self.entry_string)
                        return
                # createTexture
                if self.image:
                    self._createTexture()
            except Exception as e:
                print(e)
                return
            finally:
                self.isInitialized=True

        if self.id!=0:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.id)

    def end(self):
        glBindTexture(GL_TEXTURE_2D, 0);
        glDisable(GL_TEXTURE_2D)

