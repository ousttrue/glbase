# coding: utf-8
import os
import io
import time
import glbase.texture
import glbase.shader
import pymeshio.pmd.reader


def build(asset, entry_string):
    # load
    data=asset.get(entry_string)
    if not data:
        print 'fail to get %s from %s' % (entry_string, asset)
        return
    model=pymeshio.pmd.reader.read(io.BytesIO(data))
    if not model:
        return

    # attributes
    position=glbase.shader.AttributeArray('a_position')
    normal=glbase.shader.AttributeArray('a_normal')
    uv=glbase.shader.AttributeArray('a_texCoord')
    skinning=glbase.shader.AttributeArray('a_skinning')
    for v in model.vertices:
        # left-handed y-up to right-handed y-up                
        position.push(v.pos[0], v.pos[1], -v.pos[2])
        normal.push(v.normal[0], v.normal[1], -v.normal[2])
        uv.push(v.uv[0], v.uv[1])
        skinning.push(v.bone0, v.bone1, v.weight0)
    indexedVertexArray=glbase.shader.IndexedVertexArray(model.indices, len(model.vertices),
            position, 
            normal, 
            uv, 
            #skinning
            )
   
    # material
    textureMap={}
    dirname=os.path.dirname(entry_string)
    if len(dirname)>0:
        dirname+=u"/"
    def indexGen():
        for i in model.indices:
            yield i
    indexGen=indexGen()
    for i, m in enumerate(model.materials):
        material=glbase.shader.Material()
        material.set(u_color=(
            m.diffuse_color[0], 
            m.diffuse_color[1], 
            m.diffuse_color[2], 
            m.alpha))
        texturefile=m.texture_file.decode('cp932')
        if len(texturefile)>0:
            texturefile=u"%s%s" % (dirname, texturefile)
            if asset.is_exist(texturefile):
                if not texturefile in textureMap:
                    texture=glbase.texture.Texture(asset, texturefile)
                    textureMap[texturefile]=texture
                material.textures.append(textureMap[texturefile])
            else:
                print 'no such entry', texturefile
        material.indices=[indexGen.next() for _ in range(m.vertex_count)]
        indexedVertexArray.materials.append(material)
    return indexedVertexArray

