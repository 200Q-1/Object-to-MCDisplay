import bpy
import json
import numpy as np
import os
import mathutils

def add_json(self,context):
    layout = self.layout
    layout.separator()
    layout.operator("object.o2mcd_add_object")
    layout.menu("OBJECTTOMCDISPLAY_MT_Models",text="json")
    
def parents(pack,path):
    model_path=os.path.join(pack,"models",*path.split("/"))
    with open(model_path+".json", "r") as f:
        data = json.load(f)
    if "parent" in data:
        parent_path=data["parent"].split(":")[-1]
        parent=parents(pack,parent_path)
        del data["parent"]
        for k,v in parent.items():
            if type(parent[k]) is dict and not k == "elements":
                for k2,v2 in parent[k].items():
                    if not k in data:
                        data[k]={}
                    data[k][k2]=v2
            else:
                data[k]=v
    return data

def add_object(self,context):
    name=self.enum.lower()
    pack=bpy.context.preferences.addons[__package__ ].preferences.path
    if self.action =='BLOCK':
        model_path="block"
    elif self.action =='ITEM':
        model_path="item"
    model_path=model_path+"/"+name
    data=parents(pack,model_path)
    elements= data["elements"]
    vertices = []
    edges = []
    faces=[]
    uvs=[]
    dire = (
    "east",
    "south",
    "west",
    "north",
    "down",
    "up",
    )
    
    new_mesh = bpy.data.meshes.new(name)
    new_object = bpy.data.objects.new(name, new_mesh)  # オブジェクト作成
    bpy.context.collection.objects.link(new_object)

    textures=data["textures"]
    del textures["particle"]
    for key,value in textures.items():
        value=value.split(":")[-1]
        if not os.path.basename(value) in bpy.data.materials:
            material= bpy.data.materials.new(os.path.basename(value))  # マテリアル作成
            material.use_nodes = True
            material.blend_method="BLEND"
            material.show_transparent_back=False
            node_tree= material.node_tree
            bsdf= node_tree.nodes[0]
            bsdf.inputs[7].default_value=0
            
            tex_node=node_tree.nodes.new(type="ShaderNodeTexImage")
            tex_node.interpolation="Closest"
            tex_node.location = (-420, 220)
            
            node_tree.links.new(tex_node.outputs[0], bsdf.inputs[0])
            node_tree.links.new(tex_node.outputs[1], bsdf.inputs[21])
            tex=value.split("/")
            tex_path=os.path.join(pack,"textures",*tex)
            if not tex[-1]+".png" in bpy.data.images:
                image= bpy.data.images.load(tex_path+".png")
            else:
                image= bpy.data.images[tex[-1]+".png"]
            tex_node.image= image
        else:
            material=bpy.data.materials[os.path.basename(value)]
        if not material.name in new_object.data.materials:
            new_object.data.materials.append(material)
    texture= []
    for e in elements:  # 頂点作成
        ve=[0,1,2,3,4,5,6,7]
        f=len(vertices)
        frm = np.array([e["from"][0]/16-0.5, e["from"][2]/16-0.5, e["from"][1]/16-0.5])
        to = np.array([e["to"][0]/16-0.5, e["to"][2]/16-0.5, e["to"][1]/16-0.5])
        if dire[0] in e["faces"] or dire[3] in e["faces"] or dire[4] in e["faces"]:
            vertices.append((frm[0], frm[1], frm[2]))
        else:ve=[v-1 if i>=0 else v for i,v in enumerate(ve)]
        if dire[0] in e["faces"] or dire[3] in e["faces"] or dire[5] in e["faces"]:
            vertices.append((frm[0], frm[1], to[2]))
        else:ve=[v-1 if i>=1 else v for i,v in enumerate(ve)]
        if dire[0] in e["faces"] or dire[1] in e["faces"] or dire[4] in e["faces"]:
            vertices.append((frm[0], to[1], frm[2]))
        else:ve=[v-1 if i>=2 else v for i,v in enumerate(ve)]
        if dire[0] in e["faces"] or dire[1] in e["faces"] or dire[5] in e["faces"]:
            vertices.append((frm[0], to[1], to[2]))
        else:ve=[v-1 if i>=3 else v for i,v in enumerate(ve)]
        if dire[2] in e["faces"] or dire[3] in e["faces"] or dire[4] in e["faces"]:
            vertices.append((to[0], frm[1], frm[2]))
        else:ve=[v-1 if i>=4 else v for i,v in enumerate(ve)]
        if dire[2] in e["faces"] or dire[3] in e["faces"] or dire[5] in e["faces"]:
            vertices.append((to[0], frm[1], to[2]))
        else:ve=[v-1 if i>=5 else v for i,v in enumerate(ve)]
        if dire[2] in e["faces"] or dire[1] in e["faces"] or dire[4] in e["faces"]:
            vertices.append((to[0], to[1], frm[2]))
        else:ve=[v-1 if i>=6 else v for i,v in enumerate(ve)]
        if dire[2] in e["faces"] or dire[1] in e["faces"] or dire[5] in e["faces"]:
            vertices.append((to[0], to[1], to[2]))
        else:ve=[v-1 if i>=7 else v for i,v in enumerate(ve)]
        dire_val=[
        (ve[0], ve[1], ve[3], ve[2]),
        (ve[2], ve[3], ve[7], ve[6]),
        (ve[6], ve[7], ve[5], ve[4]),
        (ve[4], ve[5], ve[1], ve[0]),
        (ve[2], ve[6], ve[4], ve[0]),
        (ve[7], ve[3], ve[1], ve[5]),
    ]
        for key, value in zip(dire,dire_val):  # 面作成
            if key in e["faces"]:
                faces.append((f+value[0],f+value[1],f+value[2],f+value[3]))
                m=e["faces"][key]["texture"][1:]
                if textures[m][0] == "#":
                    m=textures[m][1:]
                texture.append(textures[m].split("/")[-1])
                if "uv" in e["faces"][key]:
                    uv=e["faces"][key]["uv"]
                    xfrm = uv[0] / 16.0
                    xto = uv[2] / 16.0
                    yfrom = 1.0 - uv[3] / 16.0
                    yto = 1.0 - uv[1] / 16.0
                    uvs.append(mathutils.Vector((xto, yfrom)))
                    uvs.append(mathutils.Vector((xto, yto)))
                    uvs.append(mathutils.Vector((xfrm, yto)))
                    uvs.append(mathutils.Vector((xfrm, yfrom)))
                else:
                    uvs.append("SET")
                    uvs.append("SET")
                    uvs.append("SET")
                    uvs.append("SET")
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    for p,t in zip(new_object.data.polygons,texture):
        p.material_index=new_object.data.materials.find(t)
    new_mesh.update()
    new_uv = new_mesh.uv_layers.new(name='UVMap')  #  UV作成
    for pi,p in enumerate(new_object.data.polygons):
        for vi,ver in enumerate(p.vertices):
            v=new_object.data.vertices[ver].co
            if p.normal == mathutils.Vector((-1.0,0.0,0.0)):
                vecuv=mathutils.Vector((v[1],v[2]))
            elif p.normal == mathutils.Vector((1.0,0.0,0.0)):
                vecuv=mathutils.Vector((v[1],v[2]))
            elif p.normal == mathutils.Vector((0.0,0.0,-1.0)):
                vecuv=mathutils.Vector((v[0],v[1]))
            elif p.normal == mathutils.Vector((0.0,0.0,1.0)):
                vecuv=mathutils.Vector((v[0],v[1]))
            elif p.normal == mathutils.Vector((0.0,-1.0,0.0)):
                vecuv=mathutils.Vector((v[0],v[2]))
            elif p.normal == mathutils.Vector((0.0,1.0,0.0)):
                vecuv=mathutils.Vector((v[0],v[2]))
            if uvs[pi*4+vi] == "SET":
                new_uv.data[pi*4+vi].uv= vecuv + mathutils.Vector((0.5,0.5))
            else:
                new_uv.data[pi*4+vi].uv= uvs[pi*4+vi]
            

items = []
def enum_item(self, context):  # プロパティリスト
    global items
    items = []
    if self.action =='BLOCK':
        for i in context.scene.O2MCD_block_list:
            items.append((i.name.upper(), i.name+" ", ""))
    elif self.action =='ITEM':
        for i in context.scene.O2MCD_item_list:
            items.append((i.name.upper(), i.name+" ", ""))
    return items

class BKTEMP_MT_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    path: bpy.props.StringProperty(name="ResourcePack", subtype='DIR_PATH', default="C:\\Users\\yasei\\Desktop\\minecraft\\")
    def draw(self, context):
        layout = self.layout
        layout.prop(self,"path")
class OBJECTTOMCDISPLAY_MT_Models(bpy.types.Menu):
    bl_label = "json"
    def draw(self, context):
        layout = self.layout
        layout.operator("object.search_json",text="Block").action = 'BLOCK'
        layout.operator("object.search_json",text="Item").action = 'ITEM'
class OBJECTTOMCDISPLAY_OT_SearchJson(bpy.types.Operator):  # 検索
    bl_idname = "object.search_json"
    bl_label = ""
    bl_property = "enum"
    action: bpy.props.EnumProperty(items=(('BLOCK', "Block", ""),('ITEM', "Item", "")))
    enum: bpy.props.EnumProperty(items=enum_item)

    def execute(self, context):
        add_object(self, context)
        self.report({'INFO'}, self.enum)
        return {'FINISHED'}

    def invoke(self, context, event):
        if self.action =='BLOCK':
            context.window_manager.invoke_search_popup(self)
        elif self.action =='ITEM':
            context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
classes = (
    BKTEMP_MT_Preferences,
    OBJECTTOMCDISPLAY_MT_Models,
    OBJECTTOMCDISPLAY_OT_SearchJson
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
