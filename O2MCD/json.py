import bpy
import json
import numpy as np
import os
import mathutils
import glob
import zipfile
import tempfile

def check_path(self,context):
    if os.path.isfile(self.path):
        if os.path.splitext(self.path)[1] == ".zip" or os.path.splitext(self.path)[1] == ".jar":
            name= self.path.split(os.sep)[-1]
        else:
            self.path=os.path.dirname(self.path)
            name= self.path.split(os.sep)[-1]
    else:
        if os.path.splitext(self.path)[1]:
            self.path= os.sep.join(self.path.split(os.sep)[:-1])+os.sep
        name= self.path.split(os.sep)[-2]
    self.name= name
    self.icon=bpy.data.images[0]
def get_pack():
    pack=[]
    for p in bpy.context.scene.O2MCD_rc_packs:
        if os.path.splitext(p.path)[1] == ".zip" or os.path.splitext(p.path)[1] == ".jar":
            pack.append(zipfile.ZipFile(p.path, 'r'))
        else:
            pack.append(p.path)
    return pack

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
    return tuple(items)

class O2MCD_ResourcePacks(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="ResourcePack",default="",subtype="FILE_PATH",update=check_path)
    name: bpy.props.StringProperty(name="name",default="")
    image: bpy.props.PointerProperty(name="image",type=bpy.types.Image)
    type: bpy.props.EnumProperty(items=(('ZIP', "zip", ""),('JAR', "jar", ""),('FOLDER', "folder", "")))
class O2MCD_ResourcePack(bpy.types.PropertyGroup):
    index:bpy.props.IntProperty(name="index", default=0)

class OBJECTTOMCDISPLAY_UL_ResourcePacks(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row()
        if index == len(context.scene.O2MCD_rc_packs)-1:
            if context.scene.O2MCD_rc_packs[len(context.scene.O2MCD_rc_packs)-1].path == "":
                row.operator(OBJECTTOMCDISPLAY_OT_JarAdd.bl_idname)
            else:
                row.alignment="LEFT"
                row.label(text=item.name)
                row = layout.row()
                row.alignment="RIGHT"
                row.operator(OBJECTTOMCDISPLAY_OT_JarAdd.bl_idname)
        else:
            if index == 0:
                row.operator(OBJECTTOMCDISPLAY_OT_ResourcePackAdd.bl_idname)
            else:
                row.alignment="LEFT"
                if item.image:
                    row.label(text="",icon_value=layout.icon(item.image))
                row.label(text=item.name)
                row = layout.row()
                row.alignment="RIGHT"
                # row.label(text=item.path)
                row.operator(OBJECTTOMCDISPLAY_OT_ResourcePackRemove.bl_idname,icon='X').index=index

class OBJECTTOMCDISPLAY_OT_ResourcePackAdd(bpy.types.Operator): #追加
    bl_idname = "render.o2mcd_resource_pack_add"
    bl_label = "リソースパックを開く"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename : bpy.props.StringProperty()
    directory : bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip;*.jar",options={"HIDDEN"})
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        rc_pack=context.scene.O2MCD_rc_packs.add()
        rc_pack.path = self.filepath
        if os.path.isdir(self.filepath):
            rc_pack.type='FOLDER'
            image= bpy.data.images.load(os.path.join(self.filepath,"pack.png"))
            rc_pack.image= image
        elif os.path.splitext(self.filepath)[1] == ".zip":
            rc_pack.type='ZIP'
            with tempfile.TemporaryDirectory() as temp:
                with zipfile.ZipFile(self.filepath) as zip:
                    zip.extract('pack.png',temp)
                    image= bpy.data.images.load(os.path.join(temp,"pack.png"))
                    image.pack()
                    rc_pack.image= image
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1,1)
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_JarAdd(bpy.types.Operator): #追加
    bl_idname = "render.o2mcd_jar_add"
    bl_label = "jarを開く"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename : bpy.props.StringProperty()
    directory : bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.jar",options={"HIDDEN"})
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        if self.filename[-4:]== ".jar":
            context.scene.O2MCD_rc_packs[len(context.scene.O2MCD_rc_packs)-1].path=self.filepath
        return {'FINISHED'}
    
def JarSet(self, context):
    if len(context.scene.O2MCD_rc_packs) == 0:
        context.scene.O2MCD_rc_packs.add()
        context.scene.O2MCD_rc_packs.add()
    return {'FINISHED'}
class OBJECTTOMCDISPLAY_OT_ResourcePackRemove(bpy.types.Operator): #削除
    bl_idname = "render.o2mcd_resource_pack_remove"
    bl_label = ""
    bl_description = ""
    index : bpy.props.IntProperty(default=0)
    def execute(self, context):
        context.scene.O2MCD_rc_packs.remove(self.index)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_ResourcePackMove(bpy.types.Operator): #移動
    bl_idname = "render.o2mcd_resource_pack_move"
    bl_label = ""
    bl_description = "リソースパックを移動"
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", "")))

    def invoke(self, context, event):
        list=context.scene.O2MCD_rc_packs
        index=context.scene.O2MCD_rc_pack.index
        if self.action == 'DOWN' and index < len(list) - 1:
            list.move(index, index+1)
            context.scene.O2MCD_rc_pack.index += 1
        elif self.action == 'UP' and index >= 1:
            list.move(index, index-1)
            context.scene.O2MCD_rc_pack.index -= 1
        return {"FINISHED"}
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
        return {'FINISHED'}

    def invoke(self, context, event):
        pack= get_pack()
        if os.path.splitext(pack)[1] == ".zip" or os.path.splitext(pack)[1] == ".jar":
            if self.action =='BLOCK':
                with zipfile.ZipFile(pack, 'r') as zip:
                    blocks= zip.namelist()
                blocks=[i.split("/")[-1][:-5] for i in blocks if i.startswith('assets/minecraft/blockstates/')]
                blocks.sort()
                for i in blocks:
                    items.append((i.upper(), i+" ", ""))
            elif self.action =='ITEM':
                for i in context.scene.O2MCD_item_list:
                    items.append((i.name.upper(), i.name+" ", ""))
        else:
            if self.action =='BLOCK':
                for i in glob.glob(os.path.join(pack,"assets","minecraft","blockstates","*")):
                    i=i.split("\\")[-1][:-5]
                    items.append((i.upper(), i+" ", ""))
            elif self.action =='ITEM':
                for i in context.scene.O2MCD_item_list:
                    items.append((i.name.upper(), i.name+" ", ""))
        
        if self.action =='BLOCK':
            context.window_manager.invoke_search_popup(self)
        elif self.action =='ITEM':
            context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
classes = (
    O2MCD_ResourcePacks,
    OBJECTTOMCDISPLAY_UL_ResourcePacks,
    O2MCD_ResourcePack,
    OBJECTTOMCDISPLAY_MT_Models,
    OBJECTTOMCDISPLAY_OT_SearchJson,
    OBJECTTOMCDISPLAY_OT_ResourcePackAdd,
    OBJECTTOMCDISPLAY_OT_JarAdd,
    OBJECTTOMCDISPLAY_OT_ResourcePackRemove,
    OBJECTTOMCDISPLAY_OT_ResourcePackMove
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_rc_packs = bpy.props.CollectionProperty(type=O2MCD_ResourcePacks)
    bpy.types.Scene.O2MCD_rc_pack = bpy.props.PointerProperty(type=O2MCD_ResourcePack)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
