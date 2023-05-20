import bpy
import json
import numpy as np
import math
import os
import mathutils

def add_json(self,context):
    layout = self.layout
    layout.separator()
    layout.operator("object.o2mcd_add_object")
    layout.menu("OBJECTTOMCDISPLAY_MT_Models",text="json")
def add_object(self,context):
    file=self.enum.lower()
    path=bpy.context.preferences.addons[__package__ ].preferences.path
    path=path+"models\\"
    if self.action =='BLOCK':
        path=path+"block\\"
    elif self.action =='ITEM':
        path=path+"item\\"
    with open(f"{path}{file}.json", "r") as f:
        data = json.load(f)
        elements= data["elements"]
    vertices = []
    edges = []
    faces=[]
    uvs=[]
    direction = np.array([
    "east",
    "south",
    "west",
    "north",
    "down",
    "up",
])
    for i, e in enumerate(elements):
        f=len(vertices)
        # get cube min/max
        frm = np.array([e["from"][0]/16-0.5, e["from"][2]/16-0.5, e["from"][1]/16-0.5])
        to = np.array([e["to"][0]/16-0.5, e["to"][2]/16-0.5, e["to"][1]/16-0.5])
        
        vertices.append((frm[0], frm[1], frm[2]))
        vertices.append((frm[0], frm[1], to[2]))
        vertices.append((frm[0], to[1], frm[2]))
        vertices.append((frm[0], to[1], to[2]))
        vertices.append((to[0], frm[1], frm[2]))
        vertices.append((to[0], frm[1], to[2]))
        vertices.append((to[0], to[1], frm[2]))
        vertices.append((to[0], to[1], to[2]))
        faces.append((f+0, f+1, f+3, f+2))
        faces.append((f+2, f+3, f+7, f+6))
        faces.append((f+6, f+7, f+5, f+4))
        faces.append((f+4, f+5, f+1, f+0))
        faces.append((f+2, f+6, f+4, f+0))
        faces.append((f+7, f+3, f+1, f+5))
        
        for d in direction:
            if d in e["faces"]:
                if "uv" in e["faces"][d]:
                    uv=e["faces"][d]["uv"]
                    xfrm = uv[0] / 16.0
                    xto = uv[2] / 16.0
                    yfrom = 1.0 - uv[3] / 16.0
                    yto = 1.0 - uv[1] / 16.0
                    uvs.append(mathutils.Vector((xto, yto)))
                    uvs.append(mathutils.Vector((xfrm, yto)))
                    uvs.append(mathutils.Vector((xfrm, yfrom)))
                    uvs.append(mathutils.Vector((xto, yfrom)))
                else:
                    uvs.append("SET")
                    uvs.append("SET")
                    uvs.append("SET")
                    uvs.append("SET")
            else:
                uvs.append("NONE")
                uvs.append("NONE")
                uvs.append("NONE")
                uvs.append("NONE")
    new_mesh = bpy.data.meshes.new('new_mesh')
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    # make object from mesh
    new_object = bpy.data.objects.new(file, new_mesh)
    # make collection
    # add object to scene collection
    bpy.context.collection.objects.link(new_object)
    new_uv = new_mesh.uv_layers.new(name='UVMap')
            
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
            elif uvs[pi*4+vi] == "NONE":
                new_object.data.polygons.remove(new_object.data.polygons[pi], True)
            else:
                new_uv.data[pi*4+vi].uv= uvs[pi*4+vi]
            
    material= bpy.data.materials.new("test")
    material.use_nodes = True
    material.blend_method="BLEND"
    material.show_transparent_back=False
    node_tree= material.node_tree
    bsdf= node_tree.nodes[0]
    bsdf.inputs[7].default_value=0
    
    tex_node=node_tree.nodes.new(type="ShaderNodeTexImage")
    tex_node.interpolation="Closest"
    tex_node.location = (-420, 220)
    
    math_node=node_tree.nodes.new(type="ShaderNodeMath")
    math_node.operation="MULTIPLY"
    math_node.location = (-160, 0)
    
    map_node=node_tree.nodes.new(type="ShaderNodeMapRange")
    map_node.inputs[1].default_value=0
    map_node.inputs[2].default_value=0.01
    map_node.location = (-320, -100)
    
    uv_node=node_tree.nodes.new(type="ShaderNodeUVMap")
    uv_node.from_instancer=True
    uv_node.location = (-500, -200)
    
    node_tree.links.new(tex_node.outputs[0], bsdf.inputs[0])
    node_tree.links.new(tex_node.outputs[1], math_node.inputs[0])
    node_tree.links.new(uv_node.outputs[0], map_node.inputs[0])
    node_tree.links.new(map_node.outputs[0], math_node.inputs[1])
    node_tree.links.new(math_node.outputs[0], bsdf.inputs[21])
    
    image = bpy.data.images.load("C:\\Users\\yasei\\Desktop\\minecraft\\textures\\block\\yellow_stained_glass.png")
    tex_node.image= image
    new_object.data.materials.append(material)
    
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
