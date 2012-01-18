# coding: utf-8
import os
import io
import time
import glbase.texture
import glbase.shader
import pymeshio.mqo.reader


class Material(object):
    def __init__(self):
        pass


class VertexArray(object):
    def __init__(self):
        self.materials=[]

    def addTriangle(self, material_index,
            v0, v1, v2,
            uv0, uv1, uv2
            ):
        pass


def build(asset, entry_string):
    # load
    model=pymeshio.mqo.reader.read_from_file(path)
    if not model:
        return

    # build
    vertexArray=VertexArray()
    vertexArray.materials=[
            Material(m.color.r, m.color.g, m.color.b, m.color.a, 
                m.tex and m.tex.decode('cp932') or None)
            for m in model.materials]

    for o in model.objects:
        # skip mikoto objects
        if o.name.startswith(b"anchor"):
            continue
        if o.name.startswith(b"bone:"):
            continue
        if o.name.startswith(b"MCS:"):
            continue

        for f in o.faces:
            if f.index_count==3:
                vertexArray.addTriangle(
                        f.material_index,
                        o.vertices[f.indices[0]],
                        o.vertices[f.indices[1]],
                        o.vertices[f.indices[2]],
                        f.uv[0], f.uv[1], f.uv[2]
                        )
            elif f.index_count==4:
                # triangle 1
                vertexArray.addTriangle(
                        f.material_index,
                        o.vertices[f.indices[0]],
                        o.vertices[f.indices[1]],
                        o.vertices[f.indices[2]],
                        f.uv[0], f.uv[1], f.uv[2]
                        )
                # triangle 2
                vertexArray.addTriangle(
                        f.material_index,
                        o.vertices[f.indices[2]],
                        o.vertices[f.indices[3]],
                        o.vertices[f.indices[0]],
                        f.uv[2], f.uv[3], f.uv[0]
                        )

    """ ToDo
    # attributes
    position=glbase.shader.AttributeArray('a_position')
    normal=glbase.shader.AttributeArray('a_normal')
    uv=glbase.shader.AttributeArray('a_texCoord')
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
     basedir=os.path.dirname(path)
     """

