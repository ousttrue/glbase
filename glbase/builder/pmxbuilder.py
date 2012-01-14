#!/usr/bin/env python
# coding: utf-8

import time
import os
import io
import pymeshio.pmx.reader
import glbase.asset
import glbase.material
import glbase.texture
import glbase.scene.vertexarray


def build(asset, entry_string):
    t=time.time()
    model=pymeshio.pmx.reader.read(io.BytesIO(asset.get(entry_string)))
    if not model:
        return
    print(time.time()-t, "sec")
    # build
    indexedVertexArray=glbase.scene.vertexarray.IndexedVertexArray()
    for v in model.vertices:
        # left-handed y-up to right-handed y-up                
        if v.deform.__class__ is pymeshio.pmx.Bdef1:
            indexedVertexArray.addVertex(
                    (v.position[0], v.position[1], -v.position[2], 1), 
                    (v.normal[0], v.normal[1], -v.normal[2]), 
                    (v.uv[0], v.uv[1]), 
                    (1, 1, 1, 1),
                    v.deform.index0, 0, 1.0)
        elif v.deform.__class__ is pymeshio.pmx.Bdef2:
            indexedVertexArray.addVertex(
                    (v.position[0], v.position[1], -v.position[2], 1), 
                    (v.normal[0], v.normal[1], -v.normal[2]), 
                    (v.uv[0], v.uv[1]), 
                    (1, 1, 1, 1),
                    v.deform.index0, v.deform.index1, v.deform.weight0)
        elif v.deform.__class__ is pymeshio.pmx.Sdef:
            indexedVertexArray.addVertex(
                    (v.position[0], v.position[1], -v.position[2], 1), 
                    (v.normal[0], v.normal[1], -v.normal[2]), 
                    (v.uv[0], v.uv[1]), 
                    (1, 1, 1, 1),
                    v.deform.index0, v.deform.index1, v.deform.weight0)
        else:
            print("unknown deform: {0}".format(v.deform))
    
    # material
    textureMap={}
    faceIndex=0
    def indices():
        for i in model.indices:
            yield i
    indexGen=indices()
    #dirname=glbase.asset.dirname(entry_string)
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
        if m.texture_index!=255:
            texturepath=u'%s%s' % (dirname, model.textures[m.texture_index].decode('cp932'))
            texturepath=texturepath.replace(u'\\', '/')
            if asset.is_exist(texturepath):
                if not texturepath in textureMap:
                    texture=glbase.texture.Texture(asset, texturepath)
                    textureMap[texturepath]=texture
                material.texture=textureMap[texturepath]
            else:
                print 'no suche entry', texturepath
        indices=indexedVertexArray.addMaterial(material)
        indices+=[next(indexGen) for n in range(m.vertex_count)]
    indexedVertexArray.optimize()
    return indexedVertexArray

