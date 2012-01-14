# coding: utf-8
import os
import io
import time
import glbase.scene
import glbase.material
import glbase.texture
import pymeshio.pmd.reader

def build(asset, entry_string):
    t=time.time()

    data=asset.get(entry_string)
    if not data:
        print 'fail to get %s from %s' % (entry_string, asset)
        return

    model=pymeshio.pmd.reader.read(io.BytesIO(data))
    if not model:
        return
    d=time.time()-t

    # build
    indexedVertexArray=glbase.scene.IndexedVertexArray()
    for v in model.vertices:
        # left-handed y-up to right-handed y-up                
        indexedVertexArray.addVertex(
                (v.pos[0], v.pos[1], -v.pos[2], 1), 
                (v.normal[0], v.normal[1], -v.normal[2]), 
                (v.uv[0], v.uv[1]), 
                (1, 1, 1, 1),
                v.bone0, v.bone1, v.weight0)
    
    # material
    textureMap={}
    faceIndex=0
    def indices():
        for i in model.indices:
            yield i
    indexGen=indices()
    dirname=os.path.dirname(entry_string)
    if len(dirname)>0:
        dirname+=u"/"
    for i, m in enumerate(model.materials):
        material=glbase.material.MQOMaterial()
        material.vcol=True
        material.rgba=(
                m.diffuse_color[0], 
                m.diffuse_color[1], 
                m.diffuse_color[2], 
                m.alpha)
        texturefile=m.texture_file.decode('cp932')
        if len(texturefile)>0:
            texturefile=u"%s%s" % (dirname, texturefile)
            if asset.is_exist(texturefile):
                if not texturefile in textureMap:
                    texture=glbase.texture.Texture(asset, texturefile)
                    textureMap[texturefile]=texture
                material.texture=textureMap[texturefile]
            else:
                print 'no such entry', texturefile
        indices=indexedVertexArray.addMaterial(material)
        indices+=[next(indexGen) for n in range(m.vertex_count)]
    indexedVertexArray.optimize()
    return indexedVertexArray

