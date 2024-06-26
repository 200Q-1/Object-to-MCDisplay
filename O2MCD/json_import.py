# Copyright (c) 2023 200Q

import bpy
import math
import os
import re
import mathutils
import json
import tempfile
import zipfile
from . import object
from math import *

def menu_fn(self, context):
    if context.preferences.addons[__package__].preferences.jar_path:
        self.layout.separator()
        self.layout.menu("OBJECTTOMCDISPLAY_MT_ObjectSub", text='O2MCD')


def enum_item(self, context):  # アイテムリスト
    enum_items = []
    if self.action == 'ITEM':
        list = context.preferences.addons[__package__].preferences.item_list
    else:
        list = context.preferences.addons[__package__].preferences.block_list
    for i in list:
        enum_items.append((i.name, i.name, ""))
    return enum_items


def check_path(self, context):   # ファイルかフォルダ化を判定
    if self.path:
        if os.path.isfile(self.path):
            if os.path.splitext(self.path)[1] == ".zip" or os.path.splitext(self.path)[1] == ".jar":
                self.name = self.path.split(os.sep)[-1]
                self.type = "ZIP"
            else:
                self.path = os.path.dirname(self.path)
                self.name = self.path.split(os.sep)[-1]
                self.type = "FOLDER"
        else:
            if os.path.splitext(self.path)[1]:
                self.path = os.sep.join(self.path.split(os.sep)[:-1])+os.sep
            self.name = self.path.split(os.sep)[-2]
            self.type = "FOLDER"


def get_pack(directory, file):
    data = {}
    is_anim = False
    if os.path.splitext(file[-1])[1] == '.json':
        if os.path.isfile(directory+os.sep.join(file)):
            file = os.sep.join(file)
            with open(directory+file, 'r') as js:
                data = json.load(js)
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    file = os.sep.join(file)
                    if os.path.isfile(p.path+file):
                        with open(p.path+file, 'r') as js:
                            data = json.load(js)
                            break
                else:
                    try:
                        with zipfile.ZipFile(p.path) as zip:
                            data = json.load(zip.open("/".join(file), 'r'))
                            break
                    except:
                        pass
        return data
    elif os.path.splitext(file[-1])[1] == '.png':
        if os.path.isfile(directory+os.sep.join(file)):
            fi = os.sep.join(file)
            data = bpy.data.images.load(directory+fi)
            data.name = "/".join(file[file.index("textures")+1:])
            is_anim = os.path.isfile(directory+fi+".mcmeta")
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    fi = os.sep.join(file)
                    if os.path.isfile(p.path+fi):
                        data = bpy.data.images.load(p.path+fi)
                        data.name = "/".join(file[file.index("textures")+1:])
                        is_anim = os.path.isfile(p.path+fi+".mcmeta")
                        break
                else:
                    try:
                        with zipfile.ZipFile(p.path) as zip:
                            with tempfile.TemporaryDirectory() as temp:
                                zip.extract("/".join(file),temp)
                                data = bpy.data.images.load(os.path.join(temp, *file))
                                data.pack()
                                data.name = "/".join(file[file.index("textures") + 1:])
                                is_anim = "/".join(file)+".mcmeta" in zip.namelist()
                                break
                    except:
                        data = None
                        is_anim = False
        return data, is_anim


def variants(self):
    node_tree = bpy.data.node_groups.new(name="variants", type='GeometryNodeTree')
    node_tree.is_modifier = True
    node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Attribute", in_out="INPUT", socket_type="NodeSocketString")
    node_tree.interface.new_socket("Rotation", in_out="INPUT", socket_type="NodeSocketRotation")
    node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Name", in_out="INPUT", socket_type="NodeSocketString")
    node_tree.interface.new_socket("Menu", in_out="INPUT", socket_type="NodeSocketString")
    group_in = node_tree.nodes.new(type="NodeGroupInput")
    group_out = node_tree.nodes.new(type="NodeGroupOutput")
    atr = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
    atr.data_type = "BOOLEAN"
    sptoins = node_tree.nodes.new(type="GeometryNodeSplitToInstances")
    rotins = node_tree.nodes.new(type="GeometryNodeRotateInstances")
    switch = node_tree.nodes.new(type="GeometryNodeSwitch")
    comp = node_tree.nodes.new(type="FunctionNodeCompare")
    comp.data_type = "STRING"
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
    node_tree = bpy.data.node_groups.new(name="multipart", type='GeometryNodeTree')
    node_tree.is_modifier = True
    node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Attribute", in_out="INPUT", socket_type="NodeSocketString")
    node_tree.interface.new_socket("Rotation", in_out="INPUT", socket_type="NodeSocketRotation")
    node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("active", in_out="INPUT", socket_type="NodeSocketBool")
    group_in = node_tree.nodes.new(type="NodeGroupInput")
    group_out = node_tree.nodes.new(type="NodeGroupOutput")
    atr = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
    atr.data_type = "BOOLEAN"
    sptoins = node_tree.nodes.new(type="GeometryNodeSplitToInstances")
    rotins = node_tree.nodes.new(type="GeometryNodeRotateInstances")
    switch = node_tree.nodes.new(type="GeometryNodeSwitch")
    node_tree.links.new(group_in.outputs['Attribute'], atr.inputs['Name'])
    node_tree.links.new(group_in.outputs['Geometry'], sptoins.inputs['Geometry'])
    node_tree.links.new(atr.outputs['Attribute'], sptoins.inputs['Selection'])
    node_tree.links.new(sptoins.outputs['Instances'], rotins.inputs['Instances'])
    node_tree.links.new(rotins.outputs['Instances'], switch.inputs['True'])
    node_tree.links.new(group_in.outputs['active'], switch.inputs['Switch'])
    node_tree.links.new(switch.outputs['Output'], group_out.inputs['Geometry'])
    node_tree.links.new(group_in.outputs['Rotation'], rotins.inputs['Rotation'])
    return node_tree


def parents(self, directory, file):
    blc = ["banner", "chest", "ender_chest", "conduit", "decorated_pot", "shulker_box"]
    colors = "(black|blue|brown|cyan|gray|green|light_blue|light_gray|lime|magenta|orange|pink|purple|red|white|yellow)"
    if file[-1][:-5] in blc and len(file) > 4 and file[3] == "block":
        directory = bpy.path.abspath(os.path.dirname(__file__))+os.sep
        file = ["model", file[-1]]

    data = get_pack(directory, file)
    if "blockstates" not in file:
        if re.fullmatch(f"{colors}_bed", file[-1][:-5]):
            data["parent"] = "block/bed"
            n = file[-1][:-5].split("_")[0]
            data["textures"] = {}
            data["textures"]["0"] = f"entity/bed/{n}"
        elif re.fullmatch(f"{colors}_shulker_box", file[-1][:-5]):
            col = re.sub(f"{colors}.*", "\\1", file[-1][:-5])
            data["textures"]["0"] = f"entity/shulker/shulker_{col}"
            data["parent"] = "block/shulker_box"
        elif file[-1][:-5] == "ender_chest":
            data["textures"]["0"] = "entity/chest/ender"
        if not data and not file[-1][:-5] == "air":
            self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("%s was not found.") % (file[-1]))
        if re.fullmatch("bed", file[-1][:-5]) and "elements" not in data:
            data["parent"] = "builtin/entity"

        if "parent" in data:
            if data["parent"].split(":")[-1] == "builtin/entity":
                parent = {"builtin/entity": "True"}
            else:
                if data["parent"].split(":")[-1] == "item/generated":
                    directory = bpy.path.abspath(os.path.dirname(__file__))+os.sep
                    parent_file = ["model", "generated.json"]
                elif data["parent"].split(":")[-1] == "model/chest":
                    parent_file = ["chest.json"]
                else:
                    parent_file = data["parent"].split(":")[-1]+".json"
                    parent_file = file[:file.index("models")+1]+parent_file.split("/")
                    if len(data["parent"].split(":")) == 2:
                        parent_file[1] = data["parent"].split(":")[0]
                    else:
                        parent_file[1] = "minecraft"
                parent = parents(self, directory, parent_file)
            del data["parent"]

            if "builtin/entity" in parent:
                directory = bpy.path.abspath(os.path.dirname(__file__))+os.sep
                if file[-1][:-5] == "template_banner":
                    parent_file = ["model", "banner.json"]
                elif file[-1][:-5] == "template_skull":
                    parent_file = ["model", "template_skull.json"]
                elif re.fullmatch("skeleton_skull|wither_skeleton_skull|creeper_head|player_head|zombie_head",file[-1][:-5]):
                    parent_file = ["model", "player_head.json"]
                else:
                    parent_file = ["model", file[-1]]
                parent = parents(self, directory, parent_file)
            if re.fullmatch("skeleton_skull|wither_skeleton_skull|creeper_head|zombie_head", file[-1][:-5]):
                t = file[-1][:-5].split("_")[0]
                parent["textures"]["0"] = f"entity/{t}/{t}"
            for k, v in parent.items():
                if k == "elements" and "elements" not in data:
                    data[k] = v
                elif type(parent[k]) is dict:
                    if k not in data:
                        data[k] = {}
                    for k2, v2 in v.items():
                        if k2 not in data[k]:
                            data[k][k2] = v2
                else:
                    data[k] = v
    elif re.fullmatch(f"{colors}_bed", file[-1][:-5]):
        f = file[-1][:-5]
        data["variants"][""]["model"] = f"block/{f}"
    if "models" in file:
        data["name"] = "/".join(file[file.index("models")+1:-1]+[file[-1][:-5]])
    else:
        data["name"] = file[-1][:-5]
    return data


def create_model(self, context, directory, name, types, new):
    # オブジェクト作成
    if "/".join([types, name]) in bpy.data.meshes:
        new_mesh = bpy.data.meshes["/".join([types, name])]
        make_mesh = False
    else:
        new_mesh = bpy.data.meshes.new("/".join([types, name]))
        make_mesh = True
    if new:
        new_object = bpy.data.objects.new(name, new_mesh)
        bpy.context.collection.objects.link(new_object)
    else:
        new_object = context.view_layer.objects.active
        new_object.data = new_mesh
    if make_mesh:
        mat_list = []
        datas = []
        file = name+".json"
        directory = directory.split(os.sep)
        folder = directory[:-1][directory.index("assets"):directory.index("assets")+2]
        file = folder+directory[directory.index("assets")+2:-1]+[file]
        directory = os.sep.join(directory[:directory.index("assets")])+os.sep
        datas = parents(self, directory, file)
        datalist = []
        values = None
        if types == "item":
            datas["CMD"] = "0"
            datalist.append(datas)
            if "overrides" in datas: 
                for ov in datas["overrides"]:
                    if len(ov["predicate"]) == 1 and "custom_model_data" in ov["predicate"]:
                        model = ov["model"].split(":")
                        of = file[:file.index("models")+1]+(model[-1]+".json").split("/")
                        if len(model) == 2:
                            of[1] = model[0]
                        p = parents(self, directory, of)
                        p["CMD"] = str(ov["predicate"]["custom_model_data"])
                        datalist.append(p)
        elif types == "block":
            if "variants" in datas:
                btype = "variants"
                values = []
                for v in datas["variants"].values():
                    if type(v) is list:
                        v = v[0]
                    values.append(v)
            else:
                btype = "multipart"
                values = [i for i in datas["multipart"]]
                values = [dict(**i["apply"][0] if type(i["apply"]) is list else i["apply"], **dict(when=i["when"])) if len(i) > 1 else i["apply"] for i in values]
            for v in values:
                for ii, vv in v.items():
                    if ii == "model":
                        model = vv.split(":")
                        va = file[:file.index("blockstates")+1]+(model[-1]+".json").split("/")
                        va[va.index("blockstates")] = "models"
                        if len(model) == 2:
                            va[1] = model[0]
                    if not "/".join(va[va.index("models")+1:])[:-5] in [n["name"] for n in datalist]:
                        data = parents(self, directory, va)
                        datalist.append(data)
        colors = "(black|blue|brown|cyan|gray|green|light_blue|light_gray|lime|magenta|orange|pink|purple|red|white|yellow)"
        materials = []
        vertices = []
        edges = []
        faces = []
        normal = []
        uvs = []
        ratio = []
        texture = []
        uv_rot = []
        megu = {}
        for data in datalist:
            try:
                elements = data["elements"]
            except:
                if not name == "air":
                    self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("There are no elements. It could be a block entity.\nFILE: %s") % ({file[-1]}))
                continue
            axis = {"x": (-1, 0, 0), "y": "Z", "z": "Y"}
            dire = (
                    "east",
                    "south",
                    "west",
                    "north",
                    "down",
                    "up",
            )
            # マテリアル作成
            if "textures" in data:
                textures = data["textures"]
                if "particle" in textures:
                    del textures["particle"]
            else:
                textures = {}
            for key, value in textures.items():
                texfile = folder+["textures"]
                if len(value.split(":")) == 2:
                    texfile[1] = value.split(":")[0]
                    value = value.split(":")[-1]
                else:
                    texfile[1] = "minecraft"
                texfile = texfile+(value+".png").split("/")
                if not value[0] == "#":
                    if value not in bpy.data.materials:
                        if re.fullmatch(f"{colors}_banner", name) and value == "entity/banner/base":
                            material = bpy.data.materials.new(name)
                        else:
                            material = bpy.data.materials.new(value)
                        materials.append(material)
                        if name == "redstone_wire" or re.fullmatch(f"{colors}_banner", name):
                            mat_list.append(material)
                        material.use_nodes = True
                        material.blend_method = 'CLIP'
                        material.shadow_method = 'CLIP'
                        material.show_transparent_back = False
                        material.use_backface_culling = True
                        node_tree = material.node_tree
                        bsdf = node_tree.nodes[0]
                        bsdf.inputs[7].default_value = 0
                        tex_node = node_tree.nodes.new(type="ShaderNodeTexImage")
                        tex_node.interpolation = "Closest"
                        tex_node.location = (-420, 220)
                        node_tree.links.new(tex_node.outputs[0], bsdf.inputs[0])
                        node_tree.links.new(tex_node.outputs[1], bsdf.inputs[4])
                        if not texfile[-1] in bpy.data.images:
                            image, anim = get_pack(directory, texfile)
                            if not image:
                                self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture not found.\nFILE:%s\nTEXTUR:%s") % (file[-1],texfile[-1]))
                                image = None
                        else:
                            image = bpy.data.images[texfile[-1]]
                        tex_node.image = image
                    else:
                        material = bpy.data.materials[value]
                    if material.name not in new_object.data.materials:
                        new_object.data.materials.append(material)
        
            # 頂点作成
            for e in elements:
                ve = [0, 1, 2, 3, 4, 5, 6, 7]
                f = len(vertices)
                frm = ([(e["to"][0]/16-0.5)*-1, e["from"][2]/16-0.5, e["from"][1]/16-0.5])
                to = ([(e["from"][0]/16-0.5)*-1, e["to"][2]/16-0.5, e["to"][1]/16-0.5])
                
                if dire[0] in e["faces"] or dire[3] in e["faces"] or dire[4] in e["faces"]:
                    vertices.append((frm[0], frm[1], frm[2]))
                else:
                    ve = [v-1 if i >= 0 else v for i, v in enumerate(ve)]
                if dire[0] in e["faces"] or dire[3] in e["faces"] or dire[5] in e["faces"]:
                    vertices.append((frm[0], frm[1], to[2]))
                else:
                    ve = [v-1 if i >= 1 else v for i, v in enumerate(ve)]
                if dire[0] in e["faces"] or dire[1] in e["faces"] or dire[4] in e["faces"]:
                    vertices.append((frm[0], to[1], frm[2]))
                else:
                    ve = [v-1 if i >= 2 else v for i, v in enumerate(ve)]
                if dire[0] in e["faces"] or dire[1] in e["faces"] or dire[5] in e["faces"]:
                    vertices.append((frm[0], to[1], to[2]))
                else:
                    ve = [v-1 if i >= 3 else v for i, v in enumerate(ve)]
                if dire[2] in e["faces"] or dire[3] in e["faces"] or dire[4] in e["faces"]:
                    vertices.append((to[0], frm[1], frm[2]))
                else:
                    ve = [v-1 if i >= 4 else v for i, v in enumerate(ve)]
                if dire[2] in e["faces"] or dire[3] in e["faces"] or dire[5] in e["faces"]:
                    vertices.append((to[0], frm[1], to[2]))
                else:
                    ve = [v-1 if i >= 5 else v for i, v in enumerate(ve)]
                if dire[2] in e["faces"] or dire[1] in e["faces"] or dire[4] in e["faces"]:
                    vertices.append((to[0], to[1], frm[2]))
                else:
                    ve = [v-1 if i >= 6 else v for i, v in enumerate(ve)]
                if dire[2] in e["faces"] or dire[1] in e["faces"] or dire[5] in e["faces"]:
                    vertices.append((to[0], to[1], to[2]))
                else:
                    ve = [v-1 if i >= 7 else v for i, v in enumerate(ve)]
                
                dire_val = [
                            (ve[0], ve[1], ve[3], ve[2]),
                            (ve[2], ve[3], ve[7], ve[6]),
                            (ve[6], ve[7], ve[5], ve[4]),
                            (ve[4], ve[5], ve[1], ve[0]),
                            (ve[2], ve[6], ve[4], ve[0]),
                            (ve[5], ve[7], ve[3], ve[1]),
                ]
                if "rotation" in e:
                    for i, v in enumerate(vertices[f:]):
                        v = mathutils.Vector(v)
                        origin = e["rotation"]["origin"]
                        origin = mathutils.Matrix.Translation((-(origin[0]/16-0.5), origin[2]/16-0.5, origin[1]/16-0.5))
                        r = mathutils.Matrix.Rotation(math.radians(e["rotation"]["angle"]), 4, axis[e["rotation"]["axis"]])
                        vertices[f+i] = origin @ r @ mathutils.Matrix.inverted(origin) @ v
                for key, value in zip(dire, dire_val):  # 面作成
                    if key in e["faces"]:
                        normal.append(key)
                        faces.append((f+value[0], f+value[1], f+value[2], f+value[3]))
                        m = e["faces"][key]["texture"][1:]
                        try:
                            pretex = ""
                            for i in range(5):
                                if textures[m][0] == "#":
                                    if pretex == textures[m][1:]:
                                        raise
                                    m = textures[m][1:]
                                    pretex = m
                                if re.fullmatch(f"{colors}_banner", name) and textures[m] == "entity/banner/base":
                                    textures[m] = name
                            texture.append(textures[m].split(":")[-1])
                        except:
                            self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture path is not set.\nFILE:%s") % (file[-1]))
                            texture.append(None)
                        if "uv" in e["faces"][key]:
                            uv = e["faces"][key]["uv"]
                            xfrm = uv[0] / 16.0
                            yfrm = uv[1] / 16.0
                            xto = uv[2] / 16.0
                            yto = uv[3] / 16.0
                            if key == "up":
                                uvs.append((mathutils.Vector((xfrm, yfrm)),
                                            mathutils.Vector((xfrm, yto)),
                                            mathutils.Vector((xto, yto)),
                                            mathutils.Vector((xto, yfrm))
                                            ))
                            elif key == "down":
                                uvs.append((mathutils.Vector((xto, yfrm)),
                                            mathutils.Vector((xfrm, yfrm)),
                                            mathutils.Vector((xfrm, yto)),
                                            mathutils.Vector((xto, yto))
                                            ))
                            else:
                                uvs.append((mathutils.Vector((xto, yto)),
                                            mathutils.Vector((xto, yfrm)),
                                            mathutils.Vector((xfrm, yfrm)),
                                            mathutils.Vector((xfrm, yto))
                                            ))
                        else:
                            uvs.append("SET")
                        if "rotation" in e["faces"][key]:
                            uv_rot.append(e["faces"][key]["rotation"])
                        else:
                            uv_rot.append(0)
                if data["name"] in megu:
                    megu[data["name"]] += len(vertices[f:])
                else:
                    megu[data["name"]] = len(vertices[f:])
                megut = tuple(megu.items())
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        pv = 0
        for i, v in enumerate(megu):
            pv += megut[i][1]
            vertex_group = new_object.vertex_groups.new(name=megut[i][0])
            if i == 0:
                vertex_group.add([ind for ind in range(pv)], 1.0, 'REPLACE')
            else:
                vertex_group.add([ind for ind in range(pv-megut[i][1], pv)], 1.0, 'REPLACE')
        for p, t in zip(new_object.data.polygons, texture):
            if t and bpy.data.materials[t].node_tree.nodes[2].image:
                p.material_index = new_object.data.materials.find(t)
                width, height = bpy.data.materials[t].node_tree.nodes[2].image.size
                ratio.append(height/width)
            else:
                ratio.append(1)
        #  UV作成
        new_uv = new_mesh.uv_layers.new(name='UVMap')
        for ind, p in enumerate(new_object.data.polygons):
            vecuv = []
            if uvs[ind] == "SET":
                vuv = [new_object.data.vertices[i].co for i in p.vertices]
                if normal[ind] == "east":
                    vuv = [(1-v[1]+0.5, ((v[2]+0.5)+ratio[ind])/ratio[ind]) for v in vuv]
                elif normal[ind] == "south":
                    vuv = [(1-v[0]+0.5, ((v[2]+0.5)+ratio[ind])/ratio[ind]) for v in vuv]
                elif normal[ind] == "west":
                    vuv = [(v[1]+0.5, ((v[2]+0.5)+ratio[ind])/ratio[ind]) for v in vuv]
                elif normal[ind] == "north":
                    vuv = [(v[0]+0.5, ((v[2]+0.5)+ratio[ind])/ratio[ind]) for v in vuv]
                elif normal[ind] == "down":
                    vuv = [(1-v[0]+0.5, ((v[1]+0.5)+ratio[ind])/ratio[ind]) for v in vuv]
                elif normal[ind] == "up":
                    vuv = [(1-v[0]+0.5, ((1-v[1]+0.5)+ratio[ind])/ratio[ind]) for v in vuv]
                for uvx, uvy in vuv:
                    vecuv.append(mathutils.Vector((uvx, uvy)))
            else:
                for u in uvs[ind]:
                    u[1] = (abs((1-u[1])/ratio[ind])+1)
                    vecuv.append(u)
            if uv_rot[ind] == 90:
                vecuv = [vecuv[1],vecuv[2],vecuv[3],vecuv[0]]
            elif uv_rot[ind] == 180:
                vecuv = [vecuv[2], vecuv[3],vecuv[0],vecuv[1]]
            elif uv_rot[ind] == 270:
                vecuv = [vecuv[3], vecuv[0],vecuv[1],vecuv[2]]
            for i, u in enumerate(new_uv.uv[ind*4:ind*4+4]):
                u.vector = vecuv[i]
        #  ノード生成
        if types == "block":
            vari = {}
            stjo_inv = []
            value_list = []
            sep_inv = []
            if btype == "variants":
                value_list = [i.split("=") for l in datas["variants"].keys() if l for i in l.split(",") if i]
            else:
                value_list = []
                for val in [i["when"] for i in values if "when" in i]:
                    for k, v in val.items():
                        if k == "OR" or k == "AND":
                            for orv in v:
                                for ok, ov in orv.items():
                                    ov = str(ov)
                                    if "|" in ov:
                                        for s in ov.split("|"):
                                            if not [ok, str(s)] in value_list:
                                                value_list.append([ok, str(s)])
                                    else:
                                        if not [ok, str(ov)] in value_list:
                                            value_list.append([ok, str(ov)])
                        else:
                            v = str(v)
                            if "|" in v:
                                for s in v.split("|"):
                                    if not [k, str(s)] in value_list:
                                        value_list.append([k, str(s)])
                            else:
                                if not [k, str(v)] in value_list:
                                    value_list.append([k, str(v)])
            if name == "redstone_wire":
                for i in range(16):
                    if not ["power", str(i)] in value_list:
                        value_list.append(["power", str(i)])

            for v in value_list:
                if v[0] in vari:
                    if not v[1] in vari[v[0]]:  vari[v[0]].append(v[1])
                elif v[0] != "":
                    vari[v[0]] = [v[1]]
                if v[1] == "true" and "false" not in vari[v[0]]:
                    vari[v[0]].append("false")
                if v[1] == "false" and "true" not in vari[v[0]]:
                    vari[v[0]].append("true")
            value_list = sorted(vari.items(), key=lambda x: x[0])
        elif types == "item":
            value_list = [(i["name"], i["CMD"]) for i in datalist]
            if len(value_list) == 1 and value_list[0][1] == "0":
                value_list = []
        if value_list:
            modi = new_object.modifiers.new("O2MCD", "NODES")
            node_tree = bpy.data.node_groups.new(name="/".join([types, name]), type='GeometryNodeTree')
            node_tree.is_modifier = True
            modi.node_group = node_tree
            node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
            node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
            geo_in = node_tree.nodes.new(type="NodeGroupInput")
            geo_out = node_tree.nodes.new(type="NodeGroupOutput")
            geo_to_ins = node_tree.nodes.new(type="GeometryNodeGeometryToInstance")
            
            node_tree.links.new(geo_to_ins.outputs['Instances'], geo_out.inputs['Geometry'])
            
            geo_in.location = (-600, 0)
            geo_out.location = (1000, 0)
            geo_to_ins.location = (800, 0)
        
            if types == "block":
                tostr = ""
                for i, (k, v) in enumerate(value_list):
                    node_tree.interface.new_socket(k, in_out="INPUT", socket_type="NodeSocketMenu")
                    menu = node_tree.nodes.new(type="GeometryNodeMenuSwitch")
                    if name == "redstone_wire" and k == "power":
                        menu.data_type = "INT"
                        v = [int(vi) for vi in v]
                    else:
                        menu.data_type = "STRING"
                        if len(v) < 2:
                            menu.enum_definition.enum_items.remove(menu.enum_definition.enum_items.get("B"))
                        
                    for e, l in enumerate(v):
                        if e <= 1:
                            menu.enum_definition.enum_items[e].name = str(l)
                        else:
                            menu.enum_definition.enum_items.new(str(l))
                        menu.inputs[e+1].default_value = l
                    node_tree.links.new(geo_in.outputs[k], menu.inputs[0])
                    menu.location = (-400, len(vari)*80-i*160)
                    menu.name = k
                    menu.label = k
                    stjo_inv.insert(0,menu.outputs[0])
                    modi["Socket_"+str(i+2)]=0
                        
                if name == "redstone_wire":
                    tostr = node_tree.nodes.new(type="FunctionNodeValueToString")
                    node_tree.links.new(node_tree.nodes["power"].outputs[0], tostr.inputs[0])
                    node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketInt")
                    node_tree.links.new(node_tree.nodes["power"].outputs[0], geo_out.inputs[1])
                    modi["Socket_7_attribute_name"]="power"
                    
                if btype == "variants":
                    if "variants" not in bpy.data.node_groups:
                        sep = variants(self)
                    else:
                        sep = bpy.data.node_groups["variants"]
                        
                    stjo = node_tree.nodes.new(type="GeometryNodeStringJoin")
                    stjo.inputs[0].default_value = ","
                    stjo.location = (-200, 0)
                    for s in stjo_inv:
                        node_tree.links.new(s, stjo.inputs[1])
                    
                    model_data = tuple(datas["variants"].items())
                    for i, (k, v) in enumerate(model_data[::-1]):
                        if type(v) is list:
                            v = v[0]
                        x = math.radians(v.get("x")) if v.get("x") else 0
                        z = math.radians(v.get("y")) if v.get("y") else 0
                        sep_node = node_tree.nodes.new("GeometryNodeGroup")
                        sep_node.node_tree = sep
                        sep_node.inputs['Attribute'].default_value = v["model"].split(":")[-1] if ":" in v["model"] else v["model"]
                        sep_node.inputs['Rotation'].default_value = (x, 0, -z)
                        sep_node.inputs['Name'].default_value = ",".join(list(map(lambda l: l[l.index("=")+1:] if "=" in l else l, k.split(","))))
                        sep_node.name = k
                        sep_node.label = k
                        sep_node.location = (0, i*200-len(datas["variants"])*100)
                        node_tree.links.new(geo_in.outputs['Geometry'], sep_node.inputs['Geometry'])
                        node_tree.links.new(stjo.outputs['String'], sep_node.inputs['Menu'])
                        node_tree.links.new(sep_node.outputs['Geometry'], geo_to_ins.inputs['Geometry'])
                else:
                    if "multipart" not in bpy.data.node_groups:
                        sep = multipart(self)
                    else:
                        sep = bpy.data.node_groups["multipart"]
                    for i, (k, v) in enumerate(value_list):
                        for e, l in enumerate(v):
                            comp = node_tree.nodes.new(type="FunctionNodeCompare")
                            comp.data_type = "STRING"
                            comp.name = k+"="+l
                            comp.label = k+"="+l
                            comp.inputs["B"].default_value = l
                            comp.location = (-200, (len(value_list)*len(v))*80-(e+(len(v))*i)*160)
                            
                            node_tree.links.new(node_tree.nodes[k].outputs[0], comp.inputs["A"])
                            if name == "redstone_wire" and k == "power":
                                node_tree.links.new(tostr.outputs[0],comp.inputs["A"])
                            else:
                                node_tree.links.new(node_tree.nodes[k].outputs[0], comp.inputs["A"])
                                                        
                    for s in sep_inv:
                        node_tree.links.new(s, geo_to_ins.inputs['Geometry'])
                    model_data = []
                    for da in datas["multipart"]:
                        if type(da["apply"]) is list:
                            da["apply"] = da["apply"][0]
                        if "when" in da:
                            d = []
                            for k, v in da["when"].items():
                                if k == "OR":
                                    for o in v:
                                        d = []
                                        for kk, vv in o.items():
                                            vv = str(vv)
                                            d.append(kk+"="+vv)
                                        model_data.append((d, da["apply"]))
                                    continue
                                elif k == "AND":
                                    for o in v:
                                        vv = str(vv)
                                        for kk, vv in o.items():
                                            d.append(kk+"="+vv)
                                else:
                                    v = str(v)
                                    d.append(k+"="+v)
                        else:
                            d = name
                        model_data.append((d, da["apply"]))
                        
                    for i, (k, v) in enumerate(model_data):
                        x = math.radians(v.get("x")) if v.get("x") else 0
                        z = math.radians(v.get("y")) if v.get("y") else 0
                        sep_node = node_tree.nodes.new("GeometryNodeGroup")
                        sep_node.node_tree = sep
                        sep_node.inputs["active"].default_value = True
                        sep_node.location = (600, len(datas["multipart"])*100-i*200)
                        node_tree.links.new(geo_in.outputs['Geometry'], sep_node.inputs['Geometry'])
                        sep_node.inputs['Attribute'].default_value = v["model"].split(":")[-1] if ":" in v["model"] else v["model"]
                        sep_node.inputs['Rotation'].default_value = (x, 0, -z)
                        node_tree.links.new(sep_node.outputs['Geometry'], geo_to_ins.inputs['Geometry'])
                        if type(k) is list:
                            sep_node.label = str(k).replace("'", "")[1:-1]
                        sep_inv.insert(0, sep_node.outputs['Geometry'])
                        comp_pre = None
                        for kin, w in enumerate(k):
                            if not type(k) is str:
                                if kin == len(k)-1:
                                    if len(k) == 1:     #k一つだけ
                                        if "|" in w:
                                            cor_pre = None
                                            for win, l in enumerate(w.split("=")[-1].split("|")):
                                                if win+1 == len(w.split("|")):      #w最後
                                                    node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor_pre.inputs[1])
                                                else:
                                                    cor = node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                                    cor.operation ='OR'
                                                    node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor.inputs[0])
                                                    if cor_pre:                     #w中間
                                                        node_tree.links.new(cor.outputs[0],cor_pre.inputs[1])
                                                    else:                           #w最初
                                                        node_tree.links.new(cor.outputs[0],sep_node.inputs["active"])
                                                    cor_pre = cor
                                        else:                                       #w一つだけ
                                            node_tree.links.new(node_tree.nodes[w].outputs[0], sep_node.inputs["active"])
                                    else:               #k最後
                                        if "|" in w :
                                            cor_pre = None
                                            for win, l in enumerate(w.split("=")[-1].split("|")):
                                                if win+1 == len(w.split("|")):      #w最後
                                                    node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor_pre.inputs[1])
                                                else:
                                                    cor = node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                                    cor.operation = 'OR'
                                                    node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor.inputs[0])
                                                    if cor_pre:                     #w中間
                                                        node_tree.links.new(cor.outputs[0],cor_pre.inputs[1])
                                                    else:                           #w最初
                                                        node_tree.links.new(cor.outputs[0],comp_pre.inputs[1])
                                                    cor_pre = cor
                                        else:                                       #w一つだけ
                                            node_tree.links.new(node_tree.nodes[w].outputs[0],comp_pre.inputs[1])
                                else:                  #k中間
                                    comp = node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                    if "|" in w :
                                        cor_pre = None
                                        for win, l in enumerate(w.split("=")[-1].split("|")):
                                            if win+1 == len(w.split("|")):          #w最後
                                                node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0],cor_pre.inputs[1])
                                                pre = comp
                                            else:                                   #w中間
                                                cor = node_tree.nodes.new(type="FunctionNodeBooleanMath")
                                                cor.operation = 'OR'
                                                node_tree.links.new(node_tree.nodes[w.split("=")[0]+"="+l].outputs[0], cor.inputs[0])
                                                if cor_pre:                         #w中間
                                                    node_tree.links.new(cor.outputs[0], cor_pre.inputs[1])
                                                else:                               #w最初
                                                    node_tree.links.new(cor.outputs[0], comp.inputs[0])
                                                cor_pre=cor
                                    else:                                           #w一つだけ
                                        comp.label = "one"
                                        node_tree.links.new(node_tree.nodes[w].outputs[0],comp.inputs[0])
                                        pre = comp
                                    if comp_pre:        #k中間
                                        node_tree.links.new(comp.outputs[0],comp_pre.inputs[1])
                                    else:               #k最初
                                        node_tree.links.new(comp.outputs[0],sep_node.inputs["active"])
                                    comp_pre = pre
            elif types == "item":
                node_tree.interface.new_socket("CustomModelData", in_out="INPUT", socket_type="NodeSocketMenu")
                menu = node_tree.nodes.new(type="GeometryNodeMenuSwitch")
                menu.data_type = "STRING"
                menu.location = (-400, 0)
                menu.name = "CustomModelData"
                menu.label = "CustomModelData"
                for i, (n ,c) in enumerate(value_list):
                    if "variants" not in bpy.data.node_groups:
                        sep = variants(self)
                    else:
                        sep = bpy.data.node_groups["variants"]
                    if len(value_list) < 2:
                        menu.enum_definition.enum_items.remove(menu.enum_definition.enum_items.get("B"))
                    if i <= 1:
                        menu.enum_definition.enum_items[i].name = c
                    else:
                        menu.enum_definition.enum_items.new(c)
                    menu.inputs[i+1].default_value = c
                    node_tree.links.new(geo_in.outputs["CustomModelData"], menu.inputs[0])
                    
                    sep_node = node_tree.nodes.new("GeometryNodeGroup")
                    sep_node.node_tree = sep
                    sep_node.inputs['Attribute'].default_value = n
                    sep_node.inputs['Name'].default_value = c
                    modi["Socket_2"] = 0
                    sep_node.location = (0, len(value_list)*80-i*160)
                    node_tree.links.new(geo_in.outputs['Geometry'], sep_node.inputs['Geometry'])
                    node_tree.links.new(sep_node.outputs['Geometry'], geo_to_ins.inputs['Geometry'])
                    node_tree.links.new(menu.outputs[0], sep_node.inputs['Menu'])
        if name == "redstone_wire":
            for ml in mat_list:
                if ml.name == "block/redstone_dust_dot" or ml.name == "block/redstone_dust_line0" or ml.name == "block/redstone_dust_line1":
                    node_tree = ml.node_tree
                    atr = node_tree.nodes.new("ShaderNodeAttribute")
                    atr.attribute_name = "power"
                    add = node_tree.nodes.new("ShaderNodeMath")
                    add.operation = 'ADD'
                    add.inputs[1].default_value = 1
                    div = node_tree.nodes.new("ShaderNodeMath")
                    div.operation = 'DIVIDE'
                    div.inputs[1].default_value = 16
                    tex = node_tree.nodes[2]
                    mult = node_tree.nodes.new("ShaderNodeMix")
                    mult.inputs[0].default_value = 1
                    mult.blend_type = 'MULTIPLY'
                    mult.data_type = 'RGBA'
                    mult.inputs[7].default_value = (1, 0, 0, 1)
                    hsv = node_tree.nodes.new("ShaderNodeHueSaturation")
                    bsdf = node_tree.nodes[0]
                elif ml.name == "block/redstone_dust_overlay":
                    ml.blend_method = 'BLEND'
                
                if ml.name == "block/redstone_dust_dot" or ml.name == "block/redstone_dust_line0" or ml.name == "block/redstone_dust_line1" or ml.name == "block/redstone_dust_overlay":
                    node_tree.links.new(atr.outputs['Fac'], add.inputs[0])
                    node_tree.links.new(add.outputs[0], div.inputs[0])
                    node_tree.links.new(div.outputs[0], hsv.inputs['Value'])
                    
                    node_tree.links.new(tex.outputs[0], mult.inputs['A'])
                    node_tree.links.new(mult.outputs['Result'], hsv.inputs['Color'])
                    node_tree.links.new(hsv.outputs[0], bsdf.inputs[0])
        elif re.fullmatch(f"{colors}_banner", name):
            for ml in mat_list:
                if re.fullmatch(f"{colors}_banner", ml.name):
                    node_tree = ml.node_tree
                    tex = node_tree.nodes[2]
                    mult = node_tree.nodes.new("ShaderNodeMix")
                    mult.inputs[0].default_value = 1
                    mult.blend_type = 'MULTIPLY'
                    mult.data_type = 'RGBA'
                    
                    node_tree.links.new(tex.outputs[0], mult.inputs['A'])
                    node_tree.links.new(mult.outputs['Result'], bsdf.inputs[0])
                    match name:
                        case "white_banner":
                            col = [255, 255, 255]
                        case "orange_banner":
                            col = [216, 127, 51]
                        case "magenta_banner":
                            col = [178, 76, 216]
                        case "light_blue_banner":
                            col = [102, 153, 216]
                        case "yellow_banner":
                            col = [229, 229, 51]
                        case "lime_banner":
                            col = [127, 204, 25]
                        case "pink_banner":
                            col = [242, 127, 165]
                        case "gray_banner":
                            col = [76, 76, 76]
                        case "light_gray_banner":
                            col = [153, 153, 153]
                        case "cyan_banner":
                            col = [76, 127, 153]
                        case "purple_banner":
                            col = [127, 63, 178]
                        case "blue_banner":
                            col = [51, 76, 178]
                        case "brown_banner":
                            col = [102, 76, 51]
                        case "green_banner":
                            col = [102, 127, 51]
                        case "red_banner":
                            col = [153, 51, 51]
                        case "black_banner":
                            col = [255, 255, 255]
                    col = [b/255 for b in col]
                    col[0] = col[0]/12.92 if col[0] <= 0.04045 else math.pow((col[0]+0.055)/1.055, 2.4)
                    col[1] = col[1]/12.92 if col[1] <= 0.04045 else math.pow((col[1]+0.055)/1.055, 2.4)
                    col[2] = col[2]/12.92 if col[2] <= 0.04045 else math.pow((col[2]+0.055)/1.055, 2.4)
                    col.append(1)
                    mult.inputs[7].default_value = ([*col])
    else:
        if "/".join([types, name]) in bpy.data.node_groups: 
            modi = new_object.modifiers.new("O2MCD", "NODES")
            node_tree = bpy.data.node_groups["/".join([types, name])]
            modi.node_group = node_tree
            for m in range(len(list(filter(lambda x: x.type == 'MENU_SWITCH', [n for n in node_tree.nodes])))):
                modi["Socket_"+str(m+2)] = 0
    if types == "item":
        new_object.O2MCD_props.disp_type = "item_display"
    elif types == "block":    
        new_object.O2MCD_props.disp_type = "block_display"
    new_object.O2MCD_props.disp_id = name
    new_object.O2MCD_props.mesh_list.add().mesh = new_mesh
    context.view_layer.objects.active = new_object
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active.select_set(True)
    object.mesh_update(self,context)

# 新しいサブメニューを定義


class OBJECTTOMCDISPLAY_MT_ObjectSub(bpy.types.Menu):
    bl_label = ""
    bl_description = ""
    def draw(self, context):
        layout = self.layout
        i=layout.operator("o2mcd.set_id", text="Item")
        i.action='ITEM'
        i.new=True
        b=layout.operator("o2mcd.set_id", text="Block")
        b.action='BLOCK'
        b.new=True
        layout.operator("o2mcd.add_empty", text="empty")


class OBJECTTOMCDISPLAY_UL_ResourcePacks(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        if index == 0:
            row.operator(OBJECTTOMCDISPLAY_OT_ResourcePackAdd.bl_idname)
        else:
            row = row.row()
            row.alignment = "LEFT"
            row.label(text=item.name)
            row = layout.row()
            row.alignment = "RIGHT"
            row.label(text=item.path)
            if index != len(context.scene.O2MCD_rc_packs)-1:
                row.operator(OBJECTTOMCDISPLAY_OT_ResourcePackRemove.bl_idname, text="", icon='X').index = index


class OBJECTTOMCDISPLAY_OT_ResourcePackAdd(bpy.types.Operator): #追加
    bl_idname = "o2mcd.resource_pack_add"
    bl_label = bpy.app.translations.pgettext_iface("open resource pack")
    bl_description = bpy.app.translations.pgettext_tip("Open a resource pack.\nFolders, zips and jars are supported.")
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename: bpy.props.StringProperty()
    directory: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.zip;*.jar", options={"HIDDEN"})
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        rc_pack = context.scene.O2MCD_rc_packs.add()
        rc_pack.path = self.filepath
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1, 1)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_ResourcePackRemove(bpy.types.Operator): #削除
    bl_idname = "o2mcd.resource_pack_remove"
    bl_label = "Remove"
    bl_description = bpy.app.translations.pgettext_tip("Remove resource packs")
    index: bpy.props.IntProperty(default=0)
    
    def execute(self, context):
        context.scene.O2MCD_rc_packs.remove(self.index)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_ResourcePackMove(bpy.types.Operator): #移動
    bl_idname = "o2mcd.resource_pack_move"
    bl_label = "Move"
    bl_description = bpy.app.translations.pgettext_tip("move resource pack")
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", "")))

    def execute(self, context):
        list = context.scene.O2MCD_rc_packs
        index = bpy.context.scene.O2MCD_rc_index
        if self.action == 'DOWN' and index < len(list)-1:
            list.move(index, index+1)
            bpy.context.scene.O2MCD_rc_index += 1
        elif self.action == 'UP' and index > 1:
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
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_rc_packs = bpy.props.CollectionProperty(type=O2MCD_ResourcePacks)
    bpy.types.Scene.O2MCD_rc_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.VIEW3D_MT_add.append(menu_fn)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_add.remove(menu_fn)
    del bpy.types.Scene.O2MCD_rc_packs
    del bpy.types.Scene.O2MCD_rc_index