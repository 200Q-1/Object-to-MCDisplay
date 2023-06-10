import bpy
import json
import math
import numpy as np
import os
import mathutils
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
    
def get_pack(file,form):
    pack=[]
    for p in bpy.context.scene.O2MCD_rc_packs[1:]:
        if p.type =='FOLDER':
            if form == 'json':
                with open(os.path.join(p.path,*file),'r') as js:
                    pack=json.load(js)
            elif form == 'png':
                pack= bpy.data.images.load(os.path.join(p.path,*file))
            break
        else:
            with zipfile.ZipFile(p.path) as zip:
                if form == 'json':
                    try:
                        pack=json.load(zip.open("/".join(file),'r'))
                        break
                    except:pass
                elif form == 'png':
                    try:
                        with tempfile.TemporaryDirectory() as temp:
                            zip.extract("/".join(file),temp)
                            pack= bpy.data.images.load(os.path.join(temp,*file))
                            pack.pack()
                    except:pass
    return pack

def add_json(self,context):
    layout = self.layout
    layout.separator()
    layout.menu("OBJECTTOMCDISPLAY_MT_Models",text="json")
    
def parents(path):
    data= get_pack(path,'json')
    if "parent" in data:
        parent_path=data["parent"].split(":")[-1]+".json"
        parent=parents(["assets","minecraft","models"]+parent_path.split("/"))
        del data["parent"]
        for k,v in parent.items():
            if k == "elements":
                if not "elements" in data:
                    data[k]=v
            elif type(parent[k]) is dict:
                for k2,v2 in parent[k].items():
                    if not k in data:
                        data[k]={}
                    data[k][k2]=v2
            else:
                data[k]=v
    return data

def add_object(self,context):
    name=self.enum.lower()
    model_path=["assets","minecraft","models"]
    if self.action =='BLOCK':
        model_path.append("block")
    elif self.action =='ITEM':
        model_path.append("item")
    model_path.append(name+".json")
    data=parents(model_path)
    elements= data["elements"]
    vertices = []
    edges = []
    faces=[]
    uvs=[]
    uv_rot=[]
    dire = (
    "east",
    "south",
    "west",
    "north",
    "down",
    "up",
    )
    
    new_mesh = bpy.data.meshes.new(name)  # オブジェクト作成
    new_object = bpy.data.objects.new(name, new_mesh)
    bpy.context.collection.objects.link(new_object)

    textures=data["textures"]  # マテリアル作成
    if "particle" in textures: del textures["particle"]
    for key,value in textures.items():
        value=value.split(":")[-1]
        if not value[0] == "#":
            if  not os.path.basename(value) in bpy.data.materials:
                material= bpy.data.materials.new(os.path.basename(value))
                material.use_nodes = True
                material.blend_method='CLIP'
                material.show_transparent_back=False
                node_tree= material.node_tree
                bsdf= node_tree.nodes[0]
                bsdf.inputs[7].default_value=0
                
                tex_node=node_tree.nodes.new(type="ShaderNodeTexImage")
                tex_node.interpolation="Closest"
                tex_node.location = (-420, 220)
                
                node_tree.links.new(tex_node.outputs[0], bsdf.inputs[0])
                node_tree.links.new(tex_node.outputs[1], bsdf.inputs[21])
                tex=(value+".png").split("/")
                if not tex[-1] in bpy.data.images:
                    image= get_pack(["assets","minecraft","textures"]+tex,"png")
                else:
                    image= bpy.data.images[tex[-1]]
                tex_node.image= image
            else:
                material=bpy.data.materials[os.path.basename(value)]
            if not material.name in new_object.data.materials:
                new_object.data.materials.append(material)
                
    texture= []
    for e in elements:  # 頂点作成
        ve=[0,1,2,3,4,5,6,7]
        f=len(vertices)
        frm = np.array([(e["to"][0]/16-0.5)*-1, e["from"][2]/16-0.5, e["from"][1]/16-0.5])
        to = np.array([(e["from"][0]/16-0.5)*-1, e["to"][2]/16-0.5, e["to"][1]/16-0.5])
        
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
        (ve[5], ve[7], ve[3], ve[1]),
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
                    
                    uvs.append(
                        (mathutils.Vector((xto, yfrom)),
                            mathutils.Vector((xto, yto)),
                            mathutils.Vector((xfrm, yto)),
                            mathutils.Vector((xfrm, yfrom)))
                        )
                else:
                    uvs.append("SET")
                if "rotation" in e["faces"][key]:
                    uv_rot.append(e["faces"][key]["rotation"])
                else:
                    uv_rot.append(0)
                    
        if "rotation" in e:
            axis={"x":(-1,0,0),"y":(0,1,0),"z":(0,0,1)}
            for i,v in enumerate(vertices[f:]):
                v=mathutils.Vector(v)
                origin=e["rotation"]["origin"]
                origin= mathutils.Matrix.Translation(((origin[0]/16-0.5)*-1,origin[2]/16-0.5,origin[1]/16-0.5))
                r=mathutils.Matrix.Rotation(math.radians(e["rotation"]["angle"]), 4,axis[e["rotation"]["axis"]])
                vertices[f+i]= origin @ r @ v
                
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    for p,t in zip(new_object.data.polygons,texture):
        p.material_index=new_object.data.materials.find(t)
    new_uv = new_mesh.uv_layers.new(name='UVMap')  #  UV作成
    for pi,p in enumerate(new_object.data.polygons):
        vecuv=[]
        if uvs[pi] == "SET":
            vecuv=[new_object.data.vertices[i].co for i in p.vertices]
            if p.normal == mathutils.Vector((-1.0,0.0,0.0)):
                vecuv=[mathutils.Vector((v[1]+0.5,v[2]+0.5)) for v in vecuv]
            elif p.normal == mathutils.Vector((1.0,0.0,0.0)):
                vecuv=[mathutils.Vector((v[1]+0.5,v[2]+0.5)) for v in vecuv]
            elif p.normal == mathutils.Vector((0.0,0.0,-1.0)):
                vecuv=[mathutils.Vector((v[0]+0.5,v[1]+0.5)) for v in vecuv]
            elif p.normal == mathutils.Vector((0.0,0.0,1.0)):
                vecuv=[mathutils.Vector((v[0]+0.5,v[1]+0.5)) for v in vecuv]
            elif p.normal == mathutils.Vector((0.0,-1.0,0.0)):
                vecuv=[mathutils.Vector((v[0]+0.5,v[2]+0.5)) for v in vecuv]
            elif p.normal == mathutils.Vector((0.0,1.0,0.0)):
                vecuv=[mathutils.Vector((v[0]+0.5,v[2]+0.5)) for v in vecuv]
        else:
            vecuv.append(uvs[pi][0])
            vecuv.append(uvs[pi][1])
            vecuv.append(uvs[pi][2])
            vecuv.append(uvs[pi][3])
            
        if p.normal == mathutils.Vector((0.0,0.0,1.0)):
            vecuv=[vecuv[2],vecuv[3],vecuv[0],vecuv[1]]
        elif p.normal == mathutils.Vector((0.0,0.0,-1.0)):
            vecuv=[vecuv[1],vecuv[2],vecuv[3],vecuv[0]]
        
        if uv_rot[pi] == 90:
            vecuv=[vecuv[1],vecuv[2],vecuv[3],vecuv[0]]
        elif uv_rot[pi] == 180:
            vecuv=[vecuv[2],vecuv[3],vecuv[0],vecuv[1]]
        elif uv_rot[pi] == 270:
            vecuv=[vecuv[3],vecuv[0],vecuv[1],vecuv[2]]
        
        for i,u in enumerate(new_uv.uv[pi*4:pi*4+4]):
            u.vector=vecuv[i]
            
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
        pack= context.scene.O2MCD_rc_packs[len(context.scene.O2MCD_rc_packs)-1].path
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
