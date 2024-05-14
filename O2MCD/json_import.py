# Copyright (c) 2023 200Q

import bpy
import math
import os
import mathutils
from bpy_extras.io_utils import ImportHelper
import json
import tempfile
import zipfile
from math import *

def menu_fn(self, context):
    self.layout.separator()
    self.layout.menu("OBJECTTOMCDISPLAY_MT_ObjectSub", text='O2MCD')

def enum_item(self, context):  # アイテムリスト
    enum_items = []
    for i in context.preferences.addons[__package__].preferences.item_id.split(","):
        enum_items.append((i, i, ""))
    return enum_items
def enum_block(self, context):  # ブロックリスト
    enum_items = []
    for i in context.preferences.addons[__package__].preferences.block_id.split(","):
        enum_items.append((i, i, ""))
    return enum_items

def check_path(self,context):   #ファイルかフォルダ化を判定
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
            data.name="/".join(file[file.index("textures")+1:])
            is_anim= os.path.isfile(directory+file+".mcmeta")
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    file=os.sep.join(file)
                    if os.path.isfile(p.path+file):
                        data= bpy.data.images.load(p.path+file)
                        data.name="/".join(file[file.index("textures")+1:])
                        is_anim= os.path.isfile(p.path+file+".mcmeta")
                        break
                else:
                    with zipfile.ZipFile(p.path) as zip:
                        try:
                            with tempfile.TemporaryDirectory() as temp:
                                zip.extract("/".join(file),temp)
                                data= bpy.data.images.load(os.path.join(temp,*file))
                                data.pack()
                                data.name="/".join(file[file.index("textures")+1:])
                                is_anim= "/".join(file)+".mcmeta" in zip.namelist()
                                break
                        except:
                            data=None
                            is_anim= False
        return data,is_anim
    
def variants(self):
    node_tree=bpy.data.node_groups.new(name="variants", type='GeometryNodeTree')
    node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Attribute", in_out="INPUT", socket_type="NodeSocketString")
    node_tree.interface.new_socket("Rotation", in_out="INPUT", socket_type="NodeSocketRotation")
    node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Name", in_out="INPUT", socket_type="NodeSocketString")
    node_tree.interface.new_socket("Menu", in_out="INPUT", socket_type="NodeSocketString")
    group_in = node_tree.nodes.new(type="NodeGroupInput")
    group_out = node_tree.nodes.new(type="NodeGroupOutput")
    atr=node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
    atr.data_type="BOOLEAN"
    sptoins=node_tree.nodes.new(type="GeometryNodeSplitToInstances")
    rotins=node_tree.nodes.new(type="GeometryNodeRotateInstances")
    switch=node_tree.nodes.new(type="GeometryNodeSwitch")
    comp=node_tree.nodes.new(type="FunctionNodeCompare")
    comp.data_type="STRING"
    node_tree.links.new(group_in.outputs['Attribute'], atr.inputs['Name'])
    node_tree.links.new(group_in.outputs['Geometry'], sptoins.inputs['Geometry'])
    node_tree.links.new(atr.outputs['Attribute'], sptoins.inputs['Selection'])
    node_tree.links.new(sptoins.outputs['Instances'], rotins.inputs['Instances'])
    node_tree.links.new(rotins.outputs['Instances'], switch.inputs['True'])
    node_tree.links.new(switch.outputs['Output'], group_out.inputs['Geometry'])
    node_tree.links.new(group_in.outputs['Rotation'], rotins.inputs['Rotation'])
    node_tree.links.new(group_in.outputs['Name'], comp.inputs["A"])
    node_tree.links.new(group_in.outputs['Menu'], comp.inputs["B"])
    node_tree.links.new(comp.outputs['Result'], switch.inputs['Switch'])
    return node_tree

def multipart(self):
    node_tree=bpy.data.node_groups.new(name="multipart", type='GeometryNodeTree')
    node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Attribute", in_out="INPUT", socket_type="NodeSocketString")
    node_tree.interface.new_socket("Rotation", in_out="INPUT", socket_type="NodeSocketRotation")
    node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("active", in_out="INPUT", socket_type="NodeSocketBool")
    group_in = node_tree.nodes.new(type="NodeGroupInput")
    group_out = node_tree.nodes.new(type="NodeGroupOutput")
    atr=node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
    atr.data_type="BOOLEAN"
    sptoins=node_tree.nodes.new(type="GeometryNodeSplitToInstances")
    rotins=node_tree.nodes.new(type="GeometryNodeRotateInstances")
    switch=node_tree.nodes.new(type="GeometryNodeSwitch")
    
    node_tree.links.new(group_in.outputs['Attribute'], atr.inputs['Name'])
    node_tree.links.new(group_in.outputs['Geometry'], sptoins.inputs['Geometry'])
    node_tree.links.new(atr.outputs['Attribute'], sptoins.inputs['Selection'])
    node_tree.links.new(sptoins.outputs['Instances'], rotins.inputs['Instances'])
    node_tree.links.new(rotins.outputs['Instances'], switch.inputs['True'])
    node_tree.links.new(group_in.outputs['active'], switch.inputs['Switch'])
    node_tree.links.new(switch.outputs['Output'], group_out.inputs['Geometry'])
    node_tree.links.new(group_in.outputs['Rotation'], rotins.inputs['Rotation'])
    return node_tree

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
            if len(data["parent"].split(":"))==2 :
                parent_file[1]=data["parent"].split(":")[0]
            else:
                parent_file[1]="minecraft"
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
    if "models" in  file:
        data["name"]="/".join(file[file.index("models"):-1]+[file[-1][:-5]])
    else:
        data["name"]=file[-1][:-5]
    return data

def create_model(self,directory,name):
    
    # オブジェクト作成
    new_mesh = bpy.data.meshes.new(name)
    new_object = bpy.data.objects.new(name, new_mesh)
    bpy.context.collection.objects.link(new_object)
    
    datas=[]
    types=directory.split(os.sep)[-2]
    file=name+".json"
    directory=directory.split(os.sep)
    folder=directory[:-1][directory.index("assets"):directory.index("assets")+2]
    file=folder+directory[directory.index("assets")+2:-1]+[file]
    directory=os.sep.join(directory[:directory.index("assets")])+os.sep
    datas=parents(self,directory,file)
    datalist=[]
    values=None
    
    if types== "item" : 
        datas["CMD"]="0"
        datalist.append(datas)
        if "overrides" in datas: 
            for ov in datas["overrides"]:
                if len(ov["predicate"]) == 1 and "custom_model_data" in ov["predicate"]:
                    model=ov["model"].split(":")
                    of=file[:file.index("models")+1]+(model[-1]+".json").split("/")
                    if len(model)==2:
                        of[1]=model[0]
                    p=parents(self,directory,of)
                    p["CMD"]=str(ov["predicate"]["custom_model_data"])
                    datalist.append(p)
            
    elif types=="variants" or types=="multipart" :
        if "variants" in datas:
            types="variants"
            values=list(datas[types].values())
        else:
            types="multipart"
            values=[i for i in datas[types]]
            values=[dict(**i["apply"][0] if type(i["apply"]) is list else i["apply"], **dict(when=i["when"])) if len(i) > 1 else i["apply"] for i in values]
        for v in values:
            for ii,vv in v.items():
                if ii=="model":
                    model=vv.split(":")
                    va=file[:file.index("blockstates")+1]+(model[-1]+".json").split("/")
                    va[va.index("blockstates")]="models"
                    if len(model)==2:
                        va[1]=model[0]
                if not va[-1][:-5] in [n["name"] for n in datalist] :datalist.append(parents(self,directory,va))
        
    vertices = []
    edges = []
    faces=[]
    normal=[]
    uvs=[]
    ratio=[]
    texture= []
    uv_rot=[]
    megu={}
    for data in datalist:
        try:elements= data["elements"]
        except:
            self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("There are no elements. It could be a block entity.\nFILE: %s") % ({file[-1]}))
            # return
        axis={"x":(-1,0,0),"y":"Z","z":"Y"}
        dire = (
        "east",
        "south",
        "west",
        "north",
        "down",
        "up",
        )
        
        
        # マテリアル作成
        if "textures" in data :
            textures=data["textures"]
            if "particle" in textures: del textures["particle"]
        else: textures={}
        for key,value in textures.items():
            texfile=folder+["textures"]
            if len(value.split(":"))==2 :
                texfile[1]=value.split(":")[0]
                value=value.split(":")[-1]
            else:
                texfile[1]="minecraft"
            texfile=texfile+(value+".png").split("/")
            if not value[0] == "#":
                if  not value in bpy.data.materials:
                    material= bpy.data.materials.new(value)
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
                    node_tree.links.new(tex_node.outputs[1], bsdf.inputs[4])
                    
                    if not texfile[-1] in bpy.data.images:
                        image,anim=get_pack(directory,texfile)
                        anim=False
                        material.O2MCD_is_anim= anim
                        if not image : 
                            self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture not found.\nFILE:%s\nTEXTUR:%s") % (file[-1],texfile[-1]))
                            image=None
                    else:
                        image= bpy.data.images[texfile[-1]]
                    tex_node.image= image
                else:
                    material=bpy.data.materials[value]
                if not material.name in new_object.data.materials:
                    new_object.data.materials.append(material)
    
        # 頂点作成
        for e in elements:  
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
                        texture.append(textures[m])
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
            if data["name"] in megu :megu[data["name"]]+=len(vertices[f:])
            else: megu[data["name"]]=len(vertices[f:])
            megut=tuple(megu.items())
    new_mesh.from_pydata(vertices, edges, faces)
    new_mesh.update()
    
    pv=0
    for i,v in enumerate(megu):
        pv+=megut[i][1]
        vertex_group = new_object.vertex_groups.new(name=megut[i][0])
        if i==0 :vertex_group.add([ind for ind in range(pv)], 1.0, 'REPLACE')
        else:vertex_group.add([ind for ind in range(pv-megut[i][1],pv)], 1.0, 'REPLACE')
        
    for p,t in zip(new_object.data.polygons,texture):
        if t and bpy.data.materials[t].node_tree.nodes[2].image:
            p.material_index=new_object.data.materials.find(t)
            width,height=bpy.data.materials[t].node_tree.nodes[2].image.size
            ratio.append(height/width)
        else:ratio.append(1)
        
    #  UV作成
    new_uv = new_mesh.uv_layers.new(name='UVMap')
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
            
    #  ノード生成
    modi=new_object.modifiers.new("O2MCD", "NODES")
    node_tree=bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
    modi.node_group=node_tree
    node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    geo_in =      node_tree.nodes.new(type="NodeGroupInput")
    geo_out =     node_tree.nodes.new(type="NodeGroupOutput")
    geo_to_ins =  node_tree.nodes.new(type="GeometryNodeGeometryToInstance")
    
    node_tree.links.new(geo_to_ins.outputs['Instances'], geo_out.inputs['Geometry'])
    
    geo_in.location = (-600, 0)
    geo_out.location = (1000, 0)
    geo_to_ins.location =(800, 0)
    
    
    if types== "variants" or types== "multipart":
        vari={}
        stjo_inv=[]
        value_list=[]
        sep_inv=[]
        
        if types=="variants":
            value_list=[item for sublist in list(map(lambda l: [i.split("=") for i in l.split(",")],datas["variants"].keys())) for item in sublist]
        else:
            value_list=[]
            for val in [i["when"] for i in values if "when" in i]:
                for k,v in val.items():
                    if k == "OR" or k == "AND":
                        for orv in v:
                            for ok,ov in orv.items():
                                if "|" in ov:
                                    for s in ov.split("|"):
                                        if not [ok,str(s)] in value_list: value_list.append([ok,str(s)])
                                else:
                                    if not [ok,str(ov)] in value_list:value_list.append([ok,str(ov)])
                    else:
                        if "|" in v:
                            for s in v.split("|"):
                                if not [k,str(s)] in value_list: value_list.append([k,str(s)])
                        else:
                            if not [k,str(v)] in value_list: value_list.append([k,str(v)])
        for v in value_list:
            if v[0] in vari:
                if not v[1] in vari[v[0]]:  vari[v[0]].append(v[1])
            elif v[0] == "":
                pass
            else:
                vari[v[0]]=[v[1]]
        vari_sort = sorted(vari.items(), key=lambda x:x[0])
        for i,(k,v) in enumerate(vari_sort):
            node_tree.interface.new_socket(k, in_out="INPUT", socket_type="NodeSocketMenu")
            menu= node_tree.nodes.new(type="GeometryNodeMenuSwitch")
            menu.data_type="STRING"
            if len(v) < 2:
                menu.enum_definition.enum_items.remove(menu.enum_definition.enum_items.get("B"))
                
            for e,l in enumerate(v):
                if e <= 1:
                    menu.enum_definition.enum_items[e].name=l
                else:
                    menu.enum_definition.enum_items.new(l)
                menu.inputs[e+1].default_value=l
            node_tree.links.new(geo_in.outputs[k], menu.inputs[0])
            menu.location = (-400, len(vari)*80-i*160)
            menu.name=k
            menu.label=k
            stjo_inv.insert(0,menu.outputs[0])
            modi["Socket_"+str(i+2)]=0
                
            
        if types=="variants":
            if not "variants" in bpy.data.node_groups:
                sep=variants(self)
            else:
                sep=bpy.data.node_groups["variants"]
                
            stjo =  node_tree.nodes.new(type="GeometryNodeStringJoin")
            stjo.inputs[0].default_value=","
            stjo.location =(-200, 0)
            for s in stjo_inv: node_tree.links.new(s, stjo.inputs[1])
            
            model_data=tuple(datas[types].items())
            for i,(k,v) in enumerate(model_data[::-1]):
                x=radians(v.get("x")) if v.get("x") else 0
                z=radians(v.get("y")) if v.get("y") else 0
                sep_node = node_tree.nodes.new("GeometryNodeGroup")
                sep_node.node_tree = sep
                sep_node.inputs['Attribute'].default_value=v["model"].split("/")[-1]
                sep_node.inputs['Rotation'].default_value=(x,0,-z)
                sep_node.inputs['Name'].default_value=",".join(list(map(lambda l: l[l.index("=")+1:] if "=" in l else l, k.split(","))))
                sep_node.name=k
                sep_node.label=k
                sep_node.location = (0, i*200-len(datas[types])*100)
                node_tree.links.new(geo_in.outputs['Geometry'], sep_node.inputs['Geometry'])
                node_tree.links.new(stjo.outputs['String'], sep_node.inputs['Menu'])
                node_tree.links.new(sep_node.outputs['Geometry'], geo_to_ins.inputs['Geometry'])
        else:
            if not "multipart" in bpy.data.node_groups:
                sep=multipart(self)
            else:
                sep=bpy.data.node_groups["multipart"]
            
            for i,(k,v) in enumerate(vari_sort):
                for e,l in enumerate(v):
                    comp=node_tree.nodes.new(type="FunctionNodeCompare")
                    comp.data_type="STRING"
                    comp.name=k+"="+l
                    comp.label=k+"="+l
                    comp.inputs["B"].default_value=l
                    comp.location = (-200, (len(vari_sort)*len(v))*80-(e+(len(v))*i)*160)
                    node_tree.links.new(node_tree.nodes[k].outputs[0],comp.inputs["A"])
            for s in sep_inv: node_tree.links.new(s, geo_to_ins.inputs['Geometry'])
            
            
            model_data=[]
            for da in datas[types]:
                if type(da["apply"]) is list:
                    da["apply"]=da["apply"][0]
                if "when" in da:
                    d=[]
                    for k,v in da["when"].items():
                        if k== "OR":
                            for o in v:
                                d=[]
                                for kk,vv in o.items():
                                    d.append(kk+"="+vv)
                                model_data.append((d,da["apply"]))
                            continue
                        elif k== "AND":
                            for o in v:
                                for kk,vv in o.items():
                                    d.append(kk+"="+vv)
                        else:
                            d.append(k+"="+v)
                else:
                    d=name
                model_data.append((d,da["apply"]))
                
            for i,(k,v) in enumerate(model_data):
                x=radians(v.get("x")) if v.get("x") else 0
                z=radians(v.get("y")) if v.get("y") else 0
                sep_node = node_tree.nodes.new("GeometryNodeGroup")
                sep_node.node_tree = sep
                sep_node.inputs["active"].default_value=True
                sep_node.location = (600, len(datas[types])*100-i*200)
                node_tree.links.new(geo_in.outputs['Geometry'], sep_node.inputs['Geometry'])
                sep_node.inputs['Attribute'].default_value=v["model"].split("/")[-1]
                sep_node.inputs['Rotation'].default_value=(x,0,-z)
                node_tree.links.new(sep_node.outputs['Geometry'], geo_to_ins.inputs['Geometry'])
                if type(k) is list: sep_node.label=str(k).replace("'","")[1:-1]
                sep_inv.insert(0,sep_node.outputs['Geometry'])
                comp_pre=None
                for kin,w in enumerate(k) :
                    if not type(k) is str:
                        if kin+1 == len(k):
                            if len(k) == 1:
                                if "|" in w :
                                    cor_pre=None
                                    for win,l in enumerate(w.split("=")[-1].split("|")):
                                        if win+1 == len(w.split("|")):
                                            node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor_pre.inputs[1])
                                        else:
                                            cor=node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                            cor.operation='OR'
                                            node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor.inputs[0])
                                            if cor_pre:
                                                node_tree.links.new(cor.outputs[0],cor_pre.inputs[1])
                                            else:
                                                node_tree.links.new(cor.outputs[0],sep_node.inputs["active"])
                                            cor_pre=cor
                                    comp=cor_pre
                                else:
                                    node_tree.links.new(node_tree.nodes[w].outputs[0],sep_node.inputs["active"])
                            else:
                                if "|" in w :
                                    cor_pre=None
                                    for win,l in enumerate(w.split("=")[-1].split("|")):
                                        if win+1 == len(w.split("|")):
                                            node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor_pre.inputs[1])
                                        else:
                                            cor=node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                            cor.operation='OR'
                                            node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor.inputs[0])
                                            if cor_pre:
                                                node_tree.links.new(cor.outputs[0],cor_pre.inputs[1])
                                            else:
                                                node_tree.links.new(cor.outputs[0],comp_pre.inputs[1])
                                            cor_pre=cor
                                    comp=cor_pre
                                else:
                                    node_tree.links.new(node_tree.nodes[w].outputs[0],comp_pre.inputs[1])
                        else:
                            comp=node_tree.nodes.new(type="FunctionNodeBooleanMath")
                            if "|" in w :
                                    cor_pre=None
                                    for win,l in enumerate(w.split("=")[-1].split("|")):
                                        if win+1 == len(w.split("|")):
                                            node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor_pre.inputs[1])
                                        else:
                                            cor=node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                            cor.operation='OR'
                                            node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor.inputs[0])
                                            if cor_pre:
                                                node_tree.links.new(cor.outputs[0],cor_pre.inputs[1])
                                            else:
                                                node_tree.links.new(cor.outputs[0],sep_node.inputs["active"])
                                            cor_pre=cor
                                    comp=cor_pre
                            else:
                                node_tree.links.new(node_tree.nodes[w].outputs[0],comp.inputs[0])
                            if comp_pre:
                                node_tree.links.new(comp.outputs[0],comp_pre.inputs[1])
                            else:
                                node_tree.links.new(comp.outputs[0],sep_node.inputs["active"])
                    comp_pre=comp
            
                
                
    elif types== "item":
        node_tree.interface.new_socket("CustomModelData", in_out="INPUT", socket_type="NodeSocketMenu")
        menu= node_tree.nodes.new(type="GeometryNodeMenuSwitch")
        menu.data_type="STRING"
        menu.location = (-400, 0)
        menu.name="CustomModelData"
        menu.label="CustomModelData"
                
        namelist=[(i["name"],i["CMD"]) for i in datalist]
        for i,(n,c) in enumerate(namelist):
            if not "variants" in bpy.data.node_groups:
                sep=variants(self)
            else:
                sep=bpy.data.node_groups["variants"]
                
            if len(namelist) < 2:
                menu.enum_definition.enum_items.remove(menu.enum_definition.enum_items.get("B"))
                
            if i <= 1:
                menu.enum_definition.enum_items[i].name=c
            else:
                menu.enum_definition.enum_items.new(c)
            menu.inputs[i+1].default_value=c
            node_tree.links.new(geo_in.outputs["CustomModelData"], menu.inputs[0])
            
            sep_node = node_tree.nodes.new("GeometryNodeGroup")
            sep_node.node_tree = sep
            sep_node.inputs['Attribute'].default_value=n
            sep_node.inputs['Name'].default_value=c
            modi["Socket_2"]=0
            sep_node.location = (0, len(namelist)*80-i*160)
            node_tree.links.new(geo_in.outputs['Geometry'], sep_node.inputs['Geometry'])
            node_tree.links.new(sep_node.outputs['Geometry'], geo_to_ins.inputs['Geometry'])
            node_tree.links.new(menu.outputs[0], sep_node.inputs['Menu'])
        



# 新しいサブメニューを定義
class OBJECTTOMCDISPLAY_MT_ObjectSub(bpy.types.Menu):
    bl_label = ""
    bl_description = ""
    def draw(self, context):
        layout = self.layout
        layout.operator("o2mcd.search_item", text="Item")
        layout.operator("o2mcd.search_block", text="Block")

class OBJECTTOMCDISPLAY_OT_SearchItem(bpy.types.Operator):  # アイテム検索
    bl_idname = "o2mcd.search_item"
    bl_label = ""
    bl_description= ""
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=enum_item)

    def execute(self, context):
        directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","models","item"])+os.sep
        create_model(self,directory,self.enum)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_SearchBlock(bpy.types.Operator):  # ブロック検索
    bl_idname = "o2mcd.search_block"
    bl_label = ""
    bl_description= ""
    bl_property = "enum"
    enum: bpy.props.EnumProperty(name="Objects", description="", items=enum_block)

    def execute(self, context):
        directory=context.preferences.addons[__package__].preferences.mc_jar+os.sep+os.sep.join(["assets","minecraft","blockstates"])+os.sep
        create_model(self,directory,self.enum)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}


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


classes = (
    O2MCD_ResourcePacks,
    OBJECTTOMCDISPLAY_UL_ResourcePacks,
    OBJECTTOMCDISPLAY_OT_ResourcePackAdd,
    OBJECTTOMCDISPLAY_OT_ResourcePackRemove,
    OBJECTTOMCDISPLAY_OT_ResourcePackMove,
    OBJECTTOMCDISPLAY_MT_ObjectSub,
    OBJECTTOMCDISPLAY_OT_SearchItem,
    OBJECTTOMCDISPLAY_OT_SearchBlock,
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_rc_packs = bpy.props.CollectionProperty(type=O2MCD_ResourcePacks)
    bpy.types.Scene.O2MCD_rc_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.Material.O2MCD_is_anim = bpy.props.BoolProperty(default=False)
    bpy.types.VIEW3D_MT_add.append(menu_fn)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_add.remove(menu_fn)