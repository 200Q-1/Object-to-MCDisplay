import bpy
import math
import os
import mathutils
from bpy_extras.io_utils import ImportHelper
import json
class OBJECTTOMCDISPLAY_OT_ImpJson(bpy.types.Operator, ImportHelper):
    bl_idname = "import.json_model"
    bl_label = "jsonをインポート"
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
    if file == 'generated':
        file = os.path.join(bpy.path.abspath(os.path.dirname(__file__)),"generated.json")
    try:
        with open(directory+file,'r') as js:
            data=json.load(js)
    except:
        self.report({'ERROR'}, f"{file}が見つかりませんでした。")
        data={}
    if "parent" in data:
        if data["parent"].split(":")[-1] == "item/generated":
            parent_file="generated"
            parent_path=""
        else:
            parent_file=data["parent"].split(":")[-1]+".json"
            parent_type=parent_file.split("/")[:-1]
            parent_file=parent_file.split("/")[-1]
            parent_path=directory.split(os.sep)
            parent_path=os.sep.join(parent_path[:parent_path.index("models")+1]+parent_type)+os.sep
        parent=parents(self,parent_path,parent_file)
        del data["parent"]
        for k,v in parent.items():
            if k == "elements" and not "elements" in data:
                data[k]=v
            elif type(v) is dict:
                if not k in data:data[k]={}
                for k2,v2 in v.items():
                    if not k2 in data[k]: data[k][k2]=v2
            else:
                data[k]=v

    return data

def create_model(self,file):
    directory=self.directory
    name=file[:-5]
    data=parents(self,directory,file)
    try:elements= data["elements"]
    except:
        self.report({'ERROR_INVALID_INPUT'}, f"elementsがありません。ブロックエンティティの可能性があります。\nFILE:{file}")
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
                    image= directory.split(os.sep)[:directory.split(os.sep).index("models")]
                    image= os.sep.join(image+["textures"]+tex)
                    try:
                        image= bpy.data.images.load(image)
                    except:
                        self.report({'ERROR_INVALID_INPUT'}, f"テクスチャが見つかりません。\nFILE:{file}\nTEXTUR:{image}")
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
                    self.report({'ERROR_INVALID_INPUT'}, f"テクスチャのパスが設定されていません。\nFILE:{file}")
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
        if t:
            p.material_index=new_object.data.materials.find(t)
            width,height=bpy.data.materials[t].node_tree.nodes[2].image.size
            ratio.append(height/width)
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
            if key == "down":
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
    
def json_import(self, context):
    self.layout.operator(OBJECTTOMCDISPLAY_OT_ImpJson.bl_idname, text="json")

def register():
    bpy.utils.register_class(OBJECTTOMCDISPLAY_OT_ImpJson)

def unregister():
    bpy.utils.unregister_class(OBJECTTOMCDISPLAY_OT_ImpJson)