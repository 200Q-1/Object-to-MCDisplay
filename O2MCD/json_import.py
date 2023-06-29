# Copyright (c) 2023 200Q

import bpy
import math
import os
import mathutils
from bpy_extras.io_utils import ImportHelper
import json
import tempfile
import zipfile

def check_path(self,context):
    if self.path:
        if os.path.isfile(self.path):
            if os.path.splitext(self.path)[1] == ".zip" or os.path.splitext(self.path)[1] == ".jar":
                self.name= self.path.split(os.sep)[-1]
                self.type= "ZIP"
            else:
                self.path=os.path.dirname(self.path)
                self.name= self.path.split(os.sep)[-1]
                self.type= "FOLDER"
        else:
            if os.path.splitext(self.path)[1]:
                self.path= os.sep.join(self.path.split(os.sep)[:-1])+os.sep
            self.name= self.path.split(os.sep)[-2]
            self.type= "FOLDER"
    
def get_pack(directory,file):
    data={}
    is_anim=False
    if os.path.splitext(file[-1])[1] == '.json':
        if os.path.isfile(directory+os.sep.join(file)):
            file=os.sep.join(file)
            with open(directory+file,'r') as js:
                data=json.load(js)
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    file=os.sep.join(file)
                    if os.path.isfile(p.path+file):
                        with open(p.path+file,'r') as js:
                            data=json.load(js)
                            break
                else:
                    try:
                        with zipfile.ZipFile(p.path) as zip:
                            data=json.load(zip.open("/".join(file),'r'))
                            break
                    except:pass
        return data
    elif os.path.splitext(file[-1])[1] == '.png':
        if os.path.isfile(directory+os.sep.join(file)):
            file=os.sep.join(file)
            data= bpy.data.images.load(directory+file)
            is_anim= os.path.isfile(directory+file+".mcmeta")
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    file=os.sep.join(file)
                    if os.path.isfile(p.path+file):
                        data= bpy.data.images.load(p.path+file)
                        is_anim= os.path.isfile(p.path+file+".mcmeta")
                        break
                else:
                    with zipfile.ZipFile(p.path) as zip:
                        try:
                            with tempfile.TemporaryDirectory() as temp:
                                zip.extract("/".join(file),temp)
                                data= bpy.data.images.load(os.path.join(temp,*file))
                                data.pack()
                                is_anim= "/".join(file)+".mcmeta" in zip.namelist()
                                break
                        except:
                            data=None
                            is_anim= False
        return data,is_anim
    

class OBJECTTOMCDISPLAY_OT_ImpJson(bpy.types.Operator, ImportHelper):
    bl_idname = "o2mcd.json_model"
    bl_description = bpy.app.translations.pgettext("Import json file as object.")
    bl_label = bpy.app.translations.pgettext("import json")
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(default="*.json",options={"HIDDEN"})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement,options={"HIDDEN", "SKIP_SAVE"})
    directory : bpy.props.StringProperty()

    def execute(self, context):
        for file in self.files:
            create_model(self,file.name)
        return {'FINISHED'}

def parents(self,directory,file):
    if file[0] == 'generated.json':
        directory=bpy.path.abspath(os.path.dirname(__file__))+os.sep
    data=get_pack(directory,file)
    if not data:self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("%s was not found.") % (file[-1]))
    if "parent" in data:
        if data["parent"].split(":")[-1] == "item/generated":
            parent_file=["generated.json"]
        else:
            parent_file=data["parent"].split(":")[-1]+".json"
            parent_file=file[:file.index("models")+1]+parent_file.split("/")
        parent=parents(self,directory,parent_file)
        del data["parent"]
        for k,v in parent.items():
            if k == "elements" and not "elements" in data:
                data[k]=v
            elif type(parent[k]) is dict:
                if not k in data: data[k]= {}
                for k2,v2 in v.items():
                    if not k2 in data[k]: data[k][k2]=v2
            else:
                data[k]=v

    return data

def create_model(self,file):
    directory=self.directory
    name=file[:-5]
    directory=directory.split(os.sep)
    folder=directory[:-1][directory.index("assets"):directory.index("assets")+2]
    file=folder+directory[directory.index("assets")+2:-1]+[file]
    directory=os.sep.join(directory[:directory.index("assets")])+os.sep
    data=parents(self,directory,file)
    try:elements= data["elements"]
    except:
        self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("There are no elements. It could be a block entity.\nFILE: %s") % ({file[-1]}))
        return
    vertices = []
    edges = []
    faces=[]
    normal=[]
    texture= []
    ratio=[]
    uvs=[]
    uv_rot=[]
    axis={"x":(-1,0,0),"y":"Z","z":"Y"}
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

    if "textures" in data :  # マテリアル作成
        textures=data["textures"]
    else: textures={}
    if "particle" in textures: del textures["particle"]
    for key,value in textures.items():
        value=value.split(":")[-1]
        if not value[0] == "#":
            if  not os.path.basename(value) in bpy.data.materials:
                material= bpy.data.materials.new(os.path.basename(value))
                material.use_nodes = True
                material.blend_method='CLIP'
                material.show_transparent_back=False
                material.use_backface_culling= True
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
                    tex=folder+["textures"]+tex
                    image,anim=get_pack(directory,tex)
                    material.O2MCD_is_anim= anim
                    if not image : 
                        self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture not found.\nFILE:%s\nTEXTUR:%s") % (file[-1],tex[-1]))
                        image=None
                else:
                    image= bpy.data.images[tex[-1]]
                tex_node.image= image
            else:
                material=bpy.data.materials[os.path.basename(value)]
            if not material.name in new_object.data.materials:
                new_object.data.materials.append(material)
    for e in elements:  # 頂点作成
        ve=[0,1,2,3,4,5,6,7]
        f=len(vertices)
        frm = ([(e["to"][0]/16-0.5)*-1, e["from"][2]/16-0.5, e["from"][1]/16-0.5])
        to = ([(e["from"][0]/16-0.5)*-1, e["to"][2]/16-0.5, e["to"][1]/16-0.5])
        
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
        if "rotation" in e:
            for i,v in enumerate(vertices[f:]):
                v=mathutils.Vector(v)
                origin=e["rotation"]["origin"]
                origin= mathutils.Matrix.Translation((-(origin[0]/16-0.5),origin[2]/16-0.5,origin[1]/16-0.5))
                r=mathutils.Matrix.Rotation(math.radians(e["rotation"]["angle"]), 4,axis[e["rotation"]["axis"]])
                vertices[f+i]= origin @ r @ mathutils.Matrix.inverted(origin) @ v
                
        for key, value in zip(dire,dire_val):  # 面作成
            if key in e["faces"]:
                normal.append(key)
                faces.append((f+value[0],f+value[1],f+value[2],f+value[3]))
                
                m=e["faces"][key]["texture"][1:]
                try:
                    pretex=""
                    for i in range(5):
                        if textures[m][0] == "#":
                            if pretex == textures[m][1:]:
                                raise
                            m=textures[m][1:]
                            pretex=m
                    texture.append(textures[m].split("/")[-1])
                except:
                    self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture path is not set.\nFILE:%s") % (file[-1]))
                    texture.append(None)
                if "uv" in e["faces"][key]:
                    uv=e["faces"][key]["uv"]
                    xfrm = uv[0] / 16.0
                    xto = uv[2] / 16.0
                    yfrom = uv[3] / 16.0
                    yto = uv[1] / 16.0
                    uvs.append(
                    (   mathutils.Vector((xto, yfrom)),
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
                
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    for p,t in zip(new_object.data.polygons,texture):
        if t and bpy.data.materials[t].node_tree.nodes[2].image:
            p.material_index=new_object.data.materials.find(t)
            width,height=bpy.data.materials[t].node_tree.nodes[2].image.size
            if bpy.data.materials[t].O2MCD_is_anim: ratio.append(height/width)
            else: ratio.append(1)
        else:ratio.append(1)
    new_uv = new_mesh.uv_layers.new(name='UVMap')  #  UV作成
    for ind,p in enumerate(new_object.data.polygons):
        vecuv=[]
        if uvs[ind] == "SET":
            vecuv=[new_object.data.vertices[i].co for i in p.vertices]
            if normal[ind] == "east":
                vecuv=[mathutils.Vector((v[1]+0.5,((v[2]+0.5)+ratio[ind]-1)/ratio[ind])) for v in vecuv]
            elif normal[ind] == "south":
                vecuv=[mathutils.Vector((v[0]+0.5,((v[2]+0.5)+ratio[ind]-1)/ratio[ind])) for v in vecuv]
            elif normal[ind] == "west":
                vecuv=[mathutils.Vector((v[1]+0.5,((v[2]+0.5)+ratio[ind]-1)/ratio[ind])) for v in vecuv]
            elif normal[ind] == "north":
                vecuv=[mathutils.Vector((v[0]+0.5,((v[2]+0.5)+ratio[ind]-1)/ratio[ind])) for v in vecuv]
            elif normal[ind] == "down":
                vecuv=[mathutils.Vector((v[0]+0.5,((v[1]+0.5)+ratio[ind]-1)/ratio[ind])) for v in vecuv]
            elif normal[ind] == "up":
                vecuv=[mathutils.Vector((v[0]+0.5,((v[1]+0.5)+ratio[ind]-1)/ratio[ind])) for v in vecuv]
        else:
            uvs[ind][0][1]=1-(uvs[ind][0][1]/ratio[ind])
            uvs[ind][3][1]=1-(uvs[ind][3][1]/ratio[ind])
            uvs[ind][1][1]=1-(uvs[ind][1][1]/ratio[ind])
            uvs[ind][2][1]=1-(uvs[ind][2][1]/ratio[ind])
            if normal[ind] == "down":
                vecuv.append(uvs[ind][1])
                vecuv.append(uvs[ind][2])
                vecuv.append(uvs[ind][3])
                vecuv.append(uvs[ind][0])
            else:
                vecuv.append(uvs[ind][0])
                vecuv.append(uvs[ind][1])
                vecuv.append(uvs[ind][2])
                vecuv.append(uvs[ind][3])
        if normal[ind] == "up":
            vecuv=[vecuv[2],vecuv[3],vecuv[0],vecuv[1]]

        if uv_rot[ind] == 90:
            vecuv=[vecuv[1],vecuv[2],vecuv[3],vecuv[0]]
        elif uv_rot[ind] == 180:
            vecuv=[vecuv[2],vecuv[3],vecuv[0],vecuv[1]]
        elif uv_rot[ind] == 270:
            vecuv=[vecuv[3],vecuv[0],vecuv[1],vecuv[2]]
        
        for i,u in enumerate(new_uv.uv[ind*4:ind*4+4]):
            u.vector=vecuv[i]

class OBJECTTOMCDISPLAY_UL_ResourcePacks(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row()
        if index == 0:
                row.operator(OBJECTTOMCDISPLAY_OT_ResourcePackAdd.bl_idname)
        else:
            row = row.row()
            row.alignment="LEFT"
            row.label(text=item.name)
            row = layout.row()
            row.alignment="RIGHT"
            row.label(text=item.path)
            row.operator(OBJECTTOMCDISPLAY_OT_ResourcePackRemove.bl_idname,text="",icon='X').index=index
            
class OBJECTTOMCDISPLAY_OT_ResourcePackAdd(bpy.types.Operator): #追加
    bl_idname = "o2mcd.resource_pack_add"
    bl_label = bpy.app.translations.pgettext("open resource pack")
    bl_description =  bpy.app.translations.pgettext("Open a resource pack.\nFolders, zips and jars are supported.")
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
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1,1)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_ResourcePackRemove(bpy.types.Operator): #削除
    bl_idname = "o2mcd.resource_pack_remove"
    bl_label = "Remove"
    bl_description = bpy.app.translations.pgettext("Remove resource packs")
    index : bpy.props.IntProperty(default=0)
    def execute(self, context):
        context.scene.O2MCD_rc_packs.remove(self.index)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_ResourcePackMove(bpy.types.Operator): #移動
    bl_idname = "o2mcd.resource_pack_move"
    bl_label = "Move"
    bl_description = bpy.app.translations.pgettext("move resource pack")
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", "")))

    def invoke(self, context, event):
        list=context.scene.O2MCD_rc_packs
        index=bpy.context.scene.O2MCD_rc_index
        if self.action == 'DOWN' and index < len(list):
            list.move(index, index+1)
            bpy.context.scene.O2MCD_rc_index += 1
        elif self.action == 'UP' and index >= 1:
            list.move(index, index-1)
            bpy.context.scene.O2MCD_rc_index -= 1
        return {"FINISHED"}

class O2MCD_ResourcePacks(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name="ResourcePack",default="",subtype="FILE_PATH",update=check_path)
    name: bpy.props.StringProperty(name="name",default="")
    type: bpy.props.EnumProperty(items=(('ZIP', "zip", ""),('JAR', "jar", ""),('FOLDER', "folder", "")))

def json_import(self, context):
    self.layout.operator(OBJECTTOMCDISPLAY_OT_ImpJson.bl_idname, text="O2MCD (.json)")
classes = (
    OBJECTTOMCDISPLAY_OT_ImpJson,
    O2MCD_ResourcePacks,
    OBJECTTOMCDISPLAY_UL_ResourcePacks,
    OBJECTTOMCDISPLAY_OT_ResourcePackAdd,
    OBJECTTOMCDISPLAY_OT_ResourcePackRemove,
    OBJECTTOMCDISPLAY_OT_ResourcePackMove
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_rc_packs = bpy.props.CollectionProperty(type=O2MCD_ResourcePacks)
    bpy.types.Scene.O2MCD_rc_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.Material.O2MCD_is_anim = bpy.props.BoolProperty(default=False)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)