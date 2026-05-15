# Copyright (c) 2023 200Q

import bpy
import math
import os
import re
import mathutils
import json
import tempfile
import zipfile
from math import *

from . import output
from . import object
from . import pixel_to_cube

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


def get_pack(directory,fl):
    data = {}
    is_anim = False
    if os.path.splitext(fl[-1])[1] == '.json':
        if os.path.isfile(directory+os.sep.join(fl)):
            file = os.sep.join(fl)
            with open(directory+file, 'r') as js:
                data = json.load(js)
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    file = os.sep.join(fl)
                    if os.path.isfile(p.path+file):
                        with open(p.path+file, 'r') as js:
                            data = json.load(js)
                            break
                else:
                    try:
                        with zipfile.ZipFile(p.path) as zip:
                            data = json.load(zip.open("/".join(fl), 'r'))
                            break
                    except:
                        pass
        return data
    elif os.path.splitext(fl[-1])[1] == '.png':
        if os.path.isfile(directory+os.sep.join(fl)):
            file = os.sep.join(fl)
            data = bpy.data.images.load(directory+file)
            data.name = "/".join(fl[fl.index("textures")+1:])
            is_anim = os.path.isfile(directory+file+".mcmeta")
        else:
            for p in bpy.context.scene.O2MCD_rc_packs[1:]:
                if p.type == 'FOLDER':
                    file = os.sep.join(fl)
                    if os.path.isfile(p.path+file):
                        data = bpy.data.images.load(p.path+file)
                        data.name = "/".join(fl[fl.index("textures")+1:])
                        is_anim = os.path.isfile(p.path+file+".mcmeta")
                        break
                else:
                    try:
                        with zipfile.ZipFile(p.path) as zip:
                            with tempfile.TemporaryDirectory() as temp:
                                zip.extract("/".join(fl),temp)
                                data = bpy.data.images.load(os.path.join(temp, *fl))
                                data.pack()
                                data.name = "/".join(fl[fl.index("textures") + 1:])
                                is_anim = "/".join(fl)+".mcmeta" in zip.namelist()
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


def parents(self, directory,file,data=None):
    blc = ["banner", "chest", "ender_chest", "conduit", "decorated_pot", "shulker_box","skull"]
    colors = "(black|blue|brown|cyan|gray|green|light_blue|light_gray|lime|magenta|orange|pink|purple|red|white|yellow)"
    if not data:
        if file[-1][:-5] in blc and len(file) > 4 and file[3] == "block":
            directory = bpy.path.abspath(os.path.dirname(__file__))+os.sep
            if file[-1][:-5]:
                file = ["model", "player_head"]
            else:
                file = ["model", file[-1]]
        data = get_pack(directory,file)
    if "blockstates" not in file:
        if re.fullmatch(f"{colors}_bed", file[-1][:-5]):
            data["parent"] = "block/bed"
            n = file[-1][:-5].split("_")[0]
            data["textures"] = {}
            data["textures"]["0"] = f"entity/bed/{n}"
        elif re.fullmatch(f"{colors}_shulker_box", file[-1][:-5]):
            col = re.sub(f"{colors}.*", "\\1", file[-1][:-5])
            data["textures"] = {}
            data["textures"]["0"] = f"entity/shulker/shulker_{col}"
            data["parent"] = "block/shulker_box"
        elif file[-1][:-5] == "ender_chest":
            data["textures"]["0"] = "entity/chest/ender"
        if re.fullmatch("bed", file[-1][:-5]) and "elements" not in data:
            data["parent"] = "builtin/entity"
        if not data and not file[-1][:-5] == "air":
            self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("%s was not found.") % (file[-1]))

        if "parent" in data:
            if data["parent"].split(":")[-1] == "builtin/entity":
                parent = {"builtin/entity": "True"}
            else:
                if data["parent"].split(":")[-1] == "builtin/generated":
                    directory = bpy.path.abspath(os.path.dirname(__file__))+os.sep
                    parent_file = ["model", "generated.json"]
                elif data["parent"].split(":")[-1] == "model/chest":
                    parent_file = ["model","chest.json"]
                else:
                    parent_file = data["parent"].split(":")[-1]+".json"
                    if "models" in file:
                        parent_file = file[:file.index("models")+1]+parent_file.split("/")
                    else:
                        parent_file=["assets","minecraft","models"]+parent_file.split("/")
                    if len(data["parent"].split(":")) == 2:
                        parent_file[1] = data["parent"].split(":")[0]
                    else:
                        parent_file[1] = "minecraft"
                parent = parents(self,directory,parent_file)
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
                parent = parents(self,directory,parent_file)
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
                elif not k == "elements":
                    data[k] = v
    elif re.fullmatch(f"{colors}_bed", file[-1][:-5]):
        f = file[-1][:-5]
        data["variants"][""]["model"] = f"block/{f}"
    if "models" in file and file[file.index("models")+1] == "item":
        # data["name"] = "/".join(file[file.index("models")+1:-1]+[file[-1][:-5]])
        data["name"] = file[1]+":"+"/".join([*file[file.index("models")+2:-1],file[-1][:-5]])
    else:
        data["name"] = file[-1][:-5]
    return data

def check_data(name, path, result, link=None, sub=None):
    if name in path:
        data = path[name]
        create = False
    else:
        if sub:
            data = path.new(name,sub)
        else:
            data = path.new(name)
        create = True
        if link != None:
            link.link(data)
    if result:
        return data, create
    else:
        return data

def get_items(self,context,data):
    models = []
    if re.match("(minecraft:)?special",data["model"]["type"]):
        name = ""
        texture=""
        if "texture" in data["model"]["model"]:
            name = data["model"]["model"]["type"].split(":")[-1]
            texture = data["model"]["model"]["texture"].split(":")[-1]
        if "color" in data["model"]["model"]:
            name = ".".join([data["model"]["model"]["type"].split(":")[-1],data["model"]["model"]["color"]])
        elif data["model"]["base"]:
            name = data["model"]["base"].split(":")[-1]
        if re.match("(minecraft:)?(bed|shulker_box|chest)",data["model"]["model"]["type"]):
            model={"special":True,"name":name,"model":data["model"]["model"]["type"].split(":")[-1]}
            texture = data["model"]["model"]["texture"].split(":")
            if len(texture) == 1:
                texture.insert(0, 'minecraft')
            if re.match("(minecraft:)?bed",data["model"]["model"]["type"]):
                model["texture"]= "".join(["entity/bed/",texture[-1]])
            elif re.match("(minecraft:)?shulker_box",data["model"]["model"]["type"]):
                model["texture"]= "".join(["entity/shulker/",texture[-1]])
            elif re.match("(minecraft:)?chest",data["model"]["model"]["type"]):
                model["value"]= data["model"]["model"].get("openness",0)
                model["texture"]= "".join(["entity/chest/",texture[-1]])
            models.append(model)
                
        elif re.match("(minecraft:)?(banner|conduit|decorated_pot|trident)",data["model"]["model"]["type"]):
            models.append({"special":True,"name":name,"model":data["model"]["model"]["type"].split(":")[-1]})
        elif re.match("(minecraft:)?head",data["model"]["model"]["type"]):
            ki = data["model"]["model"]["kind"]
            ty = data["model"]["model"]["type"].split(":")[-1]
            base=data["model"]["base"].split(":")[-1]
            model={"special":True,"model":f"{ki}_{ty}","base":base}
            model["value"]= data["model"]["model"].get("animation",0)
            if texture:
                model["texture"]= texture
            models.append(model)
    else:
        if re.match("(minecraft:)?model",data["model"]["type"]):
            if "tints" in data["model"]:
                models.append({"special":False,"model":data["model"]["model"],"tints":data["model"]["tints"]})
            else:
                models.append({"special":False,"model":data["model"]["model"],"tints":[]})
        elif re.match("(minecraft:)?composite",data["model"]["type"]):
            for m in data["model"]["models"]:
                models += get_items(self,context,{"model":m})
        elif re.match("(minecraft:)?condition",data["model"]["type"]):
            if re.match("(minecraft:)?(broken|has_component|custom_model_data|using_item)",data["model"]["property"]):
                if "on_false" in data["model"]:
                    models += get_items(self,context,{"model":data["model"]["on_false"]})
                if "on_true" in data["model"] and data["model"]["property"] != "minecraft:using_item":
                    models += get_items(self,context,{"model":data["model"]["on_true"]})
        elif re.match("(minecraft:)?select",data["model"]["type"]):
            for m in data["model"]["cases"]:
                models += get_items(self,context,m)
            if "fallback" in data["model"]:
                models += get_items(self,context,{"model":data["model"]["fallback"]})
        elif re.match("(minecraft:)?range_dispatch",data["model"]["type"]):
            for m in data["model"]["entries"]:
                models += get_items(self,context,m)
            if "fallback" in data["model"]:
                models += get_items(self,context,{"model":data["model"]["fallback"]})
    return models
def decimal_to_rgba(value):
    if type(value) == list:
        rgb=value
    else:
        if value < 0:
            value = (2**32 + value)
        hex_value = f"{value:08X}"
        red = int(hex_value[2:4], 16)
        green = int(hex_value[4:6], 16)
        blue = int(hex_value[6:8], 16)
        rgb= [red/255, green/255, blue/255]
        
    rgb = [c / 12.92 if c <= 0.0404482362771082 else pow(((c + 0.055) / 1.055), 2.4) for c in rgb]
    return rgb
def add_material(self,context, obj, directory, texture, layers):
    def tint(input):
        col_mix = node_tree.nodes.new(type="ShaderNodeMix")
        col_mix.name = f"tex_mix{i}"
        col_mix.data_type = "RGBA"
        col_mix.blend_type='MULTIPLY'
        col_mix.inputs[0].default_value=1
        color= node_tree.nodes.new(type="ShaderNodeAttribute")
        color.attribute_name="color"
        color.attribute_type = 'OBJECT'
        node_tree.links.new(input, col_mix.inputs["A"])
        node_tree.links.new(color.outputs["Color"], col_mix.inputs["B"])
        node_tree.links.new(col_mix.outputs["Result"], bsdf.inputs[0])
    if texture not in bpy.data.materials:
        material = bpy.data.materials.new(texture)
        material.use_nodes = True
        version = context.scene.O2MCD_props.mc_version
        version_list = [v[0] for v in output.version_items(None,context)]
        if not version in version_list[version_list.index("1.21.4"):]:
            material.blend_method = 'CLIP'
            material.shadow_method = 'CLIP'
        material.use_transparency_overlap = True
        material.show_transparent_back = False
        material.use_backface_culling = True
        node_tree = material.node_tree
        bsdf = node_tree.nodes[0]
        bsdf.inputs[7].default_value = 0
        bsdf.inputs[13].default_value= 0
        
        pre_mix = None
        pre_alpha = None
        # obj.O2MCD_props["color"]={"layer0":[1.0,1.0,1.0,1.0],"layer1":[1.0,1.0,1.0,1.0],"layer2":[1.0,1.0,1.0,1.0],"layer3":[1.0,1.0,1.0,1.0],"layer4":[1.0,1.0,1.0,1.0]}
        for i,layer in enumerate(layers):
            tex_node = None
            if not layer["tex"] == None:
                tex_node = node_tree.nodes.new(type="ShaderNodeTexImage")
                tex_node.interpolation = "Closest"
                tex_node.name = "Texture"
                tex_node.location = (-300, 220)
                if not "/".join(layer["tex"][-2:]) in bpy.data.images:
                    image, anim = get_pack(directory,layer["tex"])
                    if not image:
                        self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture not found.\nFILE:%s\nTEXTUR:%s") % (texture+".json",layer["tex"][-1]))
                        image = None
                else:
                    image = bpy.data.images["/".join(layer["tex"][-2:])]
                tex_node.image = image
            if len(layers) == 1 or layer["index"] == -1:
                node_tree.links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])
            if layer["type"] == "tintindex":
                if i == 0:
                    tint(tex_node.outputs["Color"])
            else:
                tex_mix = node_tree.nodes.new(type="ShaderNodeMix")
                tex_mix.name = f"tex_mix{i}"
                tex_mix.data_type = "RGBA"
                tex_mix.blend_type= "ADD"
                tex_mix.inputs['Factor'].default_value=0
                node_tree.links.new(tex_node.outputs["Color"], tex_mix.inputs["A"])
                math = node_tree.nodes.new(type="ShaderNodeMath")
                math.inputs[1].default_value=0
                node_tree.links.new(tex_node.outputs["Alpha"],math.inputs[0])
                if i == 0:
                    tint(tex_mix.outputs["Result"])
                    node_tree.links.new(math.outputs["Value"],bsdf.inputs["Alpha"])
                    pre_mix= tex_mix
                else:
                    node_tree.links.new(tex_mix.outputs["Result"], pre_mix.inputs["B"])
                    node_tree.links.new(tex_node.outputs["Alpha"], pre_mix.inputs["Factor"])
                    node_tree.links.new(tex_node.outputs["Alpha"], pre_alpha)
                pre_mix= tex_mix
                pre_alpha = math.inputs[1]
                # else:
                #     node_tree.links.new(tex_node.outputs["Color"], pre_mix.inputs["B"])
                #     node_tree.links.new(tex_node.outputs["Alpha"], pre_mix.inputs["Factor"])
                #     node_tree.links.new(tex_node.outputs["Alpha"], pre_alpha)
                #     pre_mix= tex_mix
    else:
        material = bpy.data.materials[texture]
    return material


#共通で使用する定数（大文字で定義）
DIRECTIONS = ("east", "south", "west", "north", "down", "up")
COLORS_PATTERN = (
    "(black|blue|brown|cyan|gray|green|light_blue|light_gray|"
    "lime|magenta|orange|pink|purple|red|white|yellow)"
)
AXIS_MAPPING = {"x": (-1, 0, 0), "y": "Z", "z": "Y"}


def _calculate_element_offsets(element, element_idx, padding_offset, is_item_generated):
    """1. エレメントの始点(from)と終点(to)の座標を計算し、位置の微細なズレ（オフセット）を適用する"""
    offset = padding_offset * 0.0000 if is_item_generated else element_idx * 0.0000

    # 始点・終点座標の計算（16分の一スケール化と中心原点への補正）
    x1 = (element["to"][0] / 16 - 0.5) * -1
    y1 = element["from"][2] / 16 - 0.5
    z1 = element["from"][1] / 16 - 0.5
    coord_from = [
        x1 + offset * ((x1 > 0) - (x1 < 0)),
        y1 + offset * ((y1 > 0) - (y1 < 0)),
        z1 + offset * ((z1 > 0) - (z1 < 0)),
    ]

    x2 = (element["from"][0] / 16 - 0.5) * -1
    y2 = element["to"][2] / 16 - 0.5
    z2 = element["to"][1] / 16 - 0.5
    coord_to = [
        x2 + offset * ((x2 > 0) - (x2 < 0)),
        y2 + offset * ((y2 > 0) - (y2 < 0)),
        z2 + offset * ((z2 > 0) - (z2 < 0)),
    ]

    return coord_from, coord_to


def _resolve_texture_path(self, element, face_key, data, model_name):
    """2. ネストされたテクスチャの参照（#バナーやアイテム名など）を解決して正しいキーを返す"""
    textures = data["textures"]
    texture_key = element["faces"][face_key]["texture"][1:]
    
    try:
        previous_texture = ""
        for _ in range(5):
            if textures[texture_key][0] == "#":
                if previous_texture == textures[texture_key][1:]:
                    raise ValueError("Recursive texture reference detected")
                texture_key = textures[texture_key][1:]
                previous_texture = texture_key
                
            if (
                re.fullmatch(f"{COLORS_PATTERN}_banner", model_name)
                and textures[texture_key] == "entity/banner/base"
            ):
                textures[texture_key] = model_name
            elif data["item_generated"]:
                textures[texture_key] = data["name"].split("/")[-1]
                
        return textures[texture_key]
    except Exception:
        self.report(
            {"ERROR_INVALID_INPUT"},
            bpy.app.translations.pgettext("Texture path is not set.\nFILE:%s") % ("***"),
        )
        return None


def _adjust_item_uv(uv_vector, face_key, uv_index):
    """3. item_generated が True の場合の、UV座標の微細なズレを補正する"""
    # 複雑なifネストを排除し、方角とUVインデックスごとのオフセット値を辞書で管理
    offsets_map = {
        "up": [
            (-0.001, -0.001),
            (-0.001, 0.001),
            (0.001, 0.001),
            (0.001, -0.001),
        ],
        "down": [
            (0.001, -0.001),
            (-0.001, -0.001),
            (-0.001, 0.001),
            (0.001, 0.001),
        ],
    }
    default_offsets = [
        (0.001, 0.001),
        (0.001, -0.001),
        (-0.001, -0.001),
        (-0.001, 0.001),
    ]

    selected_offsets = offsets_map.get(face_key, default_offsets)
    offset_x, offset_y = selected_offsets[uv_index]

    return mathutils.Vector((uv_vector[0] + offset_x, uv_vector[1] + offset_y))


def _rotate_uv_list(uv_vectors, rotation_angle):
    """4. UVの回転角度（90, 180, 270）に応じて、4つのUV座標リストの並び順をローテーションする"""
    shift_map = {90: 1, 180: 2, 270: 3}
    shift = shift_map.get(rotation_angle, 0)

    if shift == 0 or len(uv_vectors) < 4:
        return uv_vectors
    return uv_vectors[shift:] + uv_vectors[:shift]


#--- メインの関数 ---
def add_vertex(self, data, name, vertex_count, types, padding_offset):
    """MinecraftのJSONモデルデータを読み込み、Blender用の各種メッシュデータを構築して返す"""
    vertices = []
    faces = []
    normal = []
    uvs = []
    uv_rot = []
    face_tex = []
    vecuvs = []
    ratio = []
    attribute = {}
    mesh_group = {}

    for element_idx, element in enumerate(data["elements"]):
        # 現在のエレメント処理開始時点での頂点数を記録（面インデックスのオフセット用）
        current_vertex_base = vertex_count + len(vertices)
        
        coord_from, coord_to = _calculate_element_offsets(
            element, element_idx, padding_offset, data["item_generated"]
        )

        # 立方体を構成する8つの頂点座標候補
        coords = [
            (coord_from[0], coord_from[1], coord_from[2]),
            (coord_from[0], coord_from[1], coord_to[2]),
            (coord_from[0], coord_to[1], coord_from[2]),
            (coord_from[0], coord_to[1], coord_to[2]),
            (coord_to[0], coord_from[1], coord_from[2]),
            (coord_to[0], coord_from[1], coord_to[2]),
            (coord_to[0], coord_to[1], coord_from[2]),
            (coord_to[0], coord_to[1], coord_to[2]),
        ]
        
        # 各頂点が生成されるために、エレメント内に存在すべき面の方角条件
        conditions = [
            ("east", "north", "down"),
            ("east", "north", "up"),
            ("east", "south", "down"),
            ("east", "south", "up"),
            ("west", "north", "down"),
            ("west", "north", "up"),
            ("west", "south", "down"),
            ("west", "south", "up"),
        ]

        # 条件を満たす頂点のみをメッシュに追加
        vertex_indices = list(range(8))
        for idx, (coord, conds) in enumerate(zip(coords, conditions)):
            if any(c in element["faces"] for c in conds):
                vertices.append(coord)
            else:
                vertex_indices[idx] -= 1

        # エレメント自体に回転(rotation)が定義されている場合の行列計算と適用
        if "rotation" in element:
            for idx, vertex in enumerate(vertices[current_vertex_base:]):
                vertex_vector = mathutils.Vector(vertex)
                origin = element["rotation"]["origin"]
                origin_matrix = mathutils.Matrix.Translation(
                    (
                        -(origin[0] / 16 - 0.5),
                        origin[2] / 16 - 0.5,
                        origin[1] / 16 - 0.5,
                    )
                )
                rotation_matrix = mathutils.Matrix.Rotation(
                    math.radians(element["rotation"]["angle"]),
                    4,
                    AXIS_MAPPING[element["rotation"]["axis"]],
                )
                # 頂点座標の書き換え
                vertices[idx + current_vertex_base] = (
                    origin_matrix
                    @ rotation_matrix
                    @ mathutils.Matrix.inverted(origin_matrix)
                    @ vertex_vector
                )

        # 6つの各面に対応する頂点インデックスの組み合わせ定義
        faces_definition = [
            (vertex_indices[0], vertex_indices[1], vertex_indices[3], vertex_indices[2]),
            (vertex_indices[2], vertex_indices[3], vertex_indices[7], vertex_indices[6]),
            (vertex_indices[6], vertex_indices[7], vertex_indices[5], vertex_indices[4]),
            (vertex_indices[4], vertex_indices[5], vertex_indices[1], vertex_indices[0]),
            (vertex_indices[2], vertex_indices[6], vertex_indices[4], vertex_indices[0]),
            (vertex_indices[5], vertex_indices[7], vertex_indices[3], vertex_indices[1]),
        ]

        # 定義された6方向について、実在する面を処理
        for i, (face_key, vertex_combination) in enumerate(zip(DIRECTIONS, faces_definition)):
            if face_key not in element["faces"]:
                continue

            normal.append(face_key)
            
            # 全体の頂点通し番号（インデックス）に変換して面を追加
            face_indices = (
                current_vertex_base + vertex_combination[0],
                current_vertex_base + vertex_combination[1],
                current_vertex_base + vertex_combination[2],
                current_vertex_base + vertex_combination[3],
            )
            faces.append(face_indices)

            # テクスチャパスの解決
            final_texture = _resolve_texture_path(self, element, face_key, data, name)
            face_tex.append(final_texture)

            # tintindex（色付け属性）の登録
            if not data["item_generated"] and "tintindex" in element["faces"][face_key]:
                tint_key = f"tintindex{element['faces'][face_key]['tintindex']}"
                attribute.setdefault(tint_key, []).append(element_idx * 6 + i)

            # マテリアル画像のアスペクト比（縦横比）を取得してリストへ格納
            try:
                image_node = bpy.data.materials[final_texture].node_tree.nodes["Texture"].image
                ratio.append(image_node.size[1] / image_node.size[0])
            except (KeyError, AttributeError):
                ratio.append(1)

            # UV座標の計算開始
            uv_data = element["faces"][face_key].get("uv", "SET")
            uv_rot.append(element["faces"][face_key].get("rotation", 0))
            resolved_uv_vectors = []

            if uv_data == "SET":
                # UVデータがない場合の自動マッピング生成
                vertex_uvs = [vertices[vi] for vi in face_indices]
                current_ratio = ratio[-1]
                
                if face_key == "east":
                    vertex_uvs = [(1 - v[1] + 0.5, ((v[2] + 0.5) + current_ratio) / current_ratio) for v in vertex_uvs]
                elif face_key == "south":
                    vertex_uvs = [(1 - v[0] + 0.5, ((v[2] + 0.5) + current_ratio) / current_ratio) for v in vertex_uvs]
                elif face_key == "west":
                    vertex_uvs = [(v[1] + 0.5, ((v[2] + 0.5) + current_ratio) / current_ratio) for v in vertex_uvs]
                elif face_key == "north":
                    vertex_uvs = [(v[0] + 0.5, ((v[2] + 0.5) + current_ratio) / current_ratio) for v in vertex_uvs]
                elif face_key == "down":
                    vertex_uvs = [(1 - v[0] + 0.5, ((v[1] + 0.5) + current_ratio) / current_ratio) for v in vertex_uvs]
                elif face_key == "up":
                    vertex_uvs = [(1 - v[0] + 0.5, ((1 - v[1] + 0.5) + current_ratio) / current_ratio) for v in vertex_uvs]
                    
                resolved_uv_vectors = [mathutils.Vector((uv_x, uv_y)) for uv_x, uv_y in vertex_uvs]
            else:
                # 既存のUVデータをパースして初期Vectorを作成
                xfrm, yfrm, xto, yto = [val / 16.0 for val in uv_data]
                if face_key == "up":
                    uv_vectors = [
                        mathutils.Vector((xfrm, yfrm)),
                        mathutils.Vector((xfrm, yto)),
                        mathutils.Vector((xto, yto)),
                        mathutils.Vector((xto, yfrm)),
                    ]
                elif face_key == "down":
                    uv_vectors = [
                        mathutils.Vector((xto, yfrm)),
                        mathutils.Vector((xfrm, yfrm)),
                        mathutils.Vector((xfrm, yto)),
                        mathutils.Vector((xto, yto)),
                    ]
                else:
                    uv_vectors = [
                        mathutils.Vector((xto, yto)),
                        mathutils.Vector((xto, yfrm)),
                        mathutils.Vector((xfrm, yfrm)),
                        mathutils.Vector((xfrm, yto)),
                    ]

                uvs.append(uv_vectors)

                # アスペクト比によるUV座標のスケール変換と、アイテム時の個別ズレ補正
                for uv_index, uv_vector in enumerate(uv_vectors):
                    adjusted_vector = mathutils.Vector((
                        uv_vector[0],
                        (abs((1 - uv_vector[1]) / ratio[-1]) + 1)
                    ))
                    if data["item_generated"]:
                        adjusted_vector = _adjust_item_uv(adjusted_vector, face_key, uv_index)
                    resolved_uv_vectors.append(adjusted_vector)

            # 面ごとのUV回転を適用して最終リストに格納
            resolved_uv_vectors = _rotate_uv_list(resolved_uv_vectors, element["faces"][face_key].get("rotation", 0))
            vecuvs.append(resolved_uv_vectors)

        # メッシュのグループ分け（ブロック名、またはアニメーションキー単位）
        group_key = data["name"] if types == "block" else element.get("animation")
        if group_key:
            generated_indices = list(range(current_vertex_base, vertex_count + len(vertices)))
            mesh_group.setdefault(group_key, []).extend(generated_indices)

    return {
        "vertices": vertices,
        "faces": faces,
        "face_tex": face_tex,
        "attribute": attribute,
        "mesh_group": mesh_group,
        "vecuv": vecuvs,
    }

def create_model(self, context, file, name, types, new, list_data=None):
    version = context.scene.O2MCD_props.mc_version
    version_list = [v[0] for v in output.version_items(None,context)]
    directory=context.preferences.addons[__package__].preferences.jar_path
    # オブジェクト作成
    if version in version_list[version_list.index("1.21.4"):] and types=="item":
        new_collection = check_data("O2MCD_models", bpy.data.collections, True, context.scene.collection.children)
        if new_collection[1]:
            new_collection[0].hide_viewport = True
        new_collection = new_collection[0]
    mesh_name = "/".join([types, name])
    new_mesh,make_mesh = check_data(mesh_name, bpy.data.meshes,True)
    if new:
        new_object = bpy.data.objects.new(mesh_name, new_mesh)
        bpy.context.collection.objects.link(new_object)
    else:
        new_object = context.view_layer.objects.active
        new_object.data = new_mesh
    datas = []
    
    datalist = []
    values = None
    if types == "item" and version in version_list[version_list.index("1.21.4"):]:
        item_model = get_pack(directory,file)
        datas = get_items(self,context,item_model)
        datas.reverse()
        if make_mesh:
            for dt in datas:
                if dt["special"]:
                    directory = bpy.path.abspath(os.path.dirname(__file__))+os.sep
                    file = ["model",dt["model"].split(":")[-1].split("/")[-1]+".json"]
                else:
                    domain = dt["model"].split(":")
                    if len(domain) == 2:
                        domain = domain[0]
                    else:
                        domain = "minecraft"
                    ph = dt["model"].split(":")[-1].split("/")
                    ph[-1] += ".json"
                    file = ["assets",domain,"models",*ph]
                d=get_pack(directory,file)
                if dt.get("base"):
                    d["parent"]=dt["base"]
                d=parents(self,directory,file,d)
                if not "item_generated" in d:
                    d["item_generated"] = False
                if "texture" in dt:
                    d["textures"] = {"0":dt["texture"]}
                if "name" in dt:
                    d["name"] = dt["name"]
                # elif d["name"] == "item/template_spawn_egg":
                #     d["name"] = name
                # d["CMD"] = "0"
                if dt["special"]:
                    if not dt.get("value") == None:
                        d["value"]= dt.get("value")
                    if dt.get("texture"):
                        d["name"] ="".join([d["name"].split("/")[-1],".",dt["texture"].split("/")[-1]])
                        d["textures"]["0"]=dt["texture"]
                if "tints" in dt:
                    d["tints"]= dt["tints"]
                datalist.append(d)
        else:
            datas = parents(self,directory,file)
            if not "item_generated" in datas:
                    datas["item_generated"] = False
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
                            
                            p = parents(self,directory,of)
                            if not "item_generated" in p:
                                p["item_generated"] = False
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
                            data = parents(self,directory,va)
                            if not "item_generated" in data:
                                data["item_generated"] = False
                            datalist.append(data)
                            
        props = []
        materials = []
        colors = "(black|blue|brown|cyan|gray|green|light_blue|light_gray|lime|magenta|orange|pink|purple|red|white|yellow)"
        if not "models" in new_object.O2MCD_props:
            new_object.O2MCD_props["models"] = []
        if types == "item" and version in version_list[version_list.index("1.21.4"):]:
            models=[]
            for data in datalist:
                if "name" in data:
                    n = data["name"].split("/")[-1]
                else:
                    n = name
                mesh,add_mesh = check_data(n, bpy.data.meshes, True)
                obj = check_data(n, bpy.data.objects,False,new_collection.objects,mesh)
                models.append(False)
                props.append({"datalist":[data],"mesh":mesh,"add_mesh":add_mesh,"object":obj,"materials":[],"vertices":[], "faces":[], "normal":[], "face_tex":[], "uv_rot":[], "uvs":[], "attribute":{}, "mesh_group":{},"layers":[],"value":data.get("value",0),"vecuv":[]})
            # new_object.O2MCD_props["models"]=models
            # for m in new_object.O2MCD_props["models"]:
            #     m=False
            new_object.O2MCD_props["models"]=models+new_object.O2MCD_props["models"].to_list()[len(models):]
        else:
            props.append({"datalist":datalist,"mesh":new_mesh,"add_mesh":True,"object":new_object,"materials":[],"vertices":[], "faces":[], "normal":[], "face_tex":[], "uv_rot":[], "uvs":[], "attribute":{}, "mesh_group":{},"layers":[],"vecuv":[]})
        # custom_color={}
        poly_datas={}
        for p_i,prop in enumerate(props):
            # if not prop["add_mesh"]:
            #     continue
            # マテリアル作成
            for data in prop["datalist"]:
                if not "textures" in data:
                    continue
                textures = {}
                for tn,texture in data["textures"].items():
                    if not (tn == "particle" or texture[0] == "#"):
                        texfile = ["assets","minecraft","textures"]
                        if ":" in texture:
                            texfile[1] = texture.split(":")[0]
                            texture = texture.split(":")[-1]
                        else:
                            texfile[1] = "minecraft"
                        # data["textures"][tn] = texture.split("/")[-1]
                        
                        texture=texture.split("/")
                        texture[-1] += ".png"
                        textures[tn] = texfile+texture
                if data["item_generated"]:
                    layer = []
                    if "layer0" in textures:
                        layer.append({"index":0,"type":"layer","tex":textures["layer0"]})
                        if "layer1" in textures:
                            layer.append({"index":1,"type":"layer","tex":textures["layer1"]})
                            if "layer2" in textures:
                                layer.append({"index":2,"type":"layer","tex":textures["layer2"]})
                                if "layer3" in textures:
                                    layer.append({"index":3,"type":"layer","tex":textures["layer3"]})
                                    if "layer4" in textures:
                                        layer.append({"index":4,"type":"layer","tex":textures["layer4"]})
                    for i,l in enumerate(layer):
                        if len(data["tints"])-1 >= i:
                            layer[i]["tint"]=data["tints"][i]
                    mat=add_material(self,context, new_object, directory, data["name"].split("/")[-1], layer)
                    if mat.name not in prop["object"].data.materials:
                        prop["object"].data.materials.append(mat)
                    prop["materials"].append(mat)
                    # for l in layer:
                    #     if not str(l["index"]) in custom_color:
                    #         custom_color[str(l["index"])]=False
                else:
                    for n,texture in textures.items():
                        tex_name = data["textures"][n]
                        layer=[{"index":-1,"type":"tintindex","tex":texture}]
                        for e in data["elements"]:
                            for f in e["faces"].values():
                                if "tintindex" in f and f["tintindex"] != -1 and not f["tintindex"] in [t["index"] for t in layer]:
                                    layer.append({"index":f["tintindex"],"type":"tintindex","tex":None})
                        if re.fullmatch(f"{colors}_banner", name) and tex_name == "entity/banner/base":
                            tex_name = name
                        for i,l in enumerate(layer[1:]):
                            if types == "item":
                                if len(data["tints"])-1 >= l["index"]:
                                    layer[i+1]["tint"]=data["tints"][l["index"]]
                            else:
                                layer[i+1]["tint"]={"type": "minecraft:grass","block":True,"downfall": 0.3,"temperature": 0.1}
                        mat=add_material(self,context, new_object, directory, tex_name, layer)
                        if mat.name not in prop["object"].data.materials:
                            prop["object"].data.materials.append(mat)
                        prop["materials"].append(mat)
                        # for l in layer:
                        #     if l["index"] != -1:
                        #         custom_color[str(l["index"])]=True
                if not name == "air" and not "elements" in data:
                    self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("\"elements\" not found.\nFILE: %s") % ({file[-1]}))
                    continue
                prop["layers"] += layer
                if not prop["add_mesh"]:
                    poly_data=poly_datas[name]
                else:
                    poly_data = add_vertex(self, data, name, len(prop["vertices"]), types,len(props)-p_i)
                    poly_datas[name]=poly_data
                prop["vertices"] += poly_data["vertices"]
                prop["faces"] += poly_data["faces"]
                prop["face_tex"] += poly_data["face_tex"]
                prop["vecuv"] += poly_data["vecuv"]
                for k,v in poly_data["mesh_group"].items():
                    if k in prop["mesh_group"]:
                        prop["mesh_group"][k] += poly_data["mesh_group"][k]
                    else:
                        prop["mesh_group"][k] = poly_data["mesh_group"][k]
                for k,v in poly_data["attribute"].items():
                    if k in prop["attribute"]:
                        prop["attribute"][k] += poly_data["attribute"][k]
                    else:
                        prop["attribute"][k] = poly_data["attribute"][k]
            if data["item_generated"]:
                print(bpy.data)
                # pixel_to_cube.image_to_3d_cubes(bpy.data.images[])
            elif prop["add_mesh"]:
                prop["mesh"].from_pydata(prop["vertices"], [], prop["faces"])
                prop["mesh"].update()
                prop.pop("vertices")
                prop.pop("faces")
                prop["uv"] = prop["mesh"].uv_layers.new(name='UVMap')
            for k,v in prop["mesh_group"].items():
                if k in prop["object"].vertex_groups:
                    vertex_group= prop["object"].vertex_groups[k]
                else:
                    vertex_group = prop["object"].vertex_groups.new(name=k)
                vertex_group.add(v, 1.0, 'REPLACE')
            for k,v in prop["attribute"].items():
                if k in prop["mesh"].attributes:
                    attrbute=prop["mesh"].attributes[k]
                else:
                    attrbute=prop["mesh"].attributes.new(name=k, type='FLOAT', domain='FACE')
                for val in v:
                    attrbute.data[val].value=1
            # UV設定
            if not prop["add_mesh"]:
                continue
            for i, (p,t) in enumerate(zip(prop["object"].data.polygons, prop["face_tex"])):
                if t and bpy.data.materials[t].node_tree.nodes["Texture"].image:
                    p.material_index = prop["object"].data.materials.find(t)
                for vi, u in enumerate(prop["uv"].uv[i*4:i*4+4]):
                    u.vector = prop["vecuv"][i][vi]
                    
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
            if version in version_list[version_list.index("1.21.4"):]:
                value_list = datalist
            else:
                value_list = [(i["name"], i["CMD"]) for i in datalist]
                if len(value_list) == 1 and value_list[0][1] == "0":
                    value_list = []
        if value_list and not "/".join([types, name]) in bpy.data.node_groups:
            modi = new_object.modifiers.new("O2MCD", "NODES")
            node_tree = bpy.data.node_groups.new(name="/".join([types, name]), type='GeometryNodeTree')
            node_tree.is_modifier = True
            modi.node_group = node_tree
            node_tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
            node_tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
            geo_in = node_tree.nodes.new(type="NodeGroupInput")
            geo_out = node_tree.nodes.new(type="NodeGroupOutput")
            geo_to_ins = node_tree.nodes.new(type="GeometryNodeJoinGeometry")
            node_tree.links.new(geo_to_ins.outputs['Geometry'], geo_out.inputs['Geometry'])
            geo_in.location = (-600, 0)
            geo_out.location = (1000, 0)
            geo_to_ins.location = (800, 0)
            
            offset = node_tree.nodes.new(type="ShaderNodeValue")
            if types == "item" and version in version_list[version_list.index("1.21.4"):]:
                if not new_object.O2MCD_props.get("color"):
                    new_object.O2MCD_props["color"]={}
                alphas=[]
                tints=[]
                for p_i,prop in enumerate(props):
                    node_tree.interface.new_socket(prop["object"].name, in_out="INPUT", socket_type="NodeSocketBool")
                    driver = new_object.driver_add(f"{modi.path_from_id()}[\"Socket_{p_i+2}\"]").driver
                    driver.expression = "var"
                    var = driver.variables.new()
                    var.type = "SINGLE_PROP"
                    var.targets[0].id = new_object
                    n=prop["datalist"][0]["name"].split("/")[-1]
                    var.targets[0].data_path = f"O2MCD_props[\"models\"][{p_i}]"
                    obj_node = node_tree.nodes.new(type="GeometryNodeObjectInfo")
                    obj_node.label="obj_node"
                    obj_node.inputs["Object"].default_value= prop["object"]
                    obj_node.inputs["As Instance"].default_value= True
                    obj_node_switch = node_tree.nodes.new(type="GeometryNodeSwitch")
                    obj_node_switch.input_type='GEOMETRY'
                    obj_node_switch.label="obj_node_switch"
                    node_tree.links.new(geo_in.outputs[1+p_i], obj_node_switch.inputs['Switch'])
                    node_tree.links.new(obj_node_switch.outputs['Output'], geo_to_ins.inputs['Geometry'])
                    obj_col_node = node_tree.nodes.new(type="GeometryNodeStoreNamedAttribute")
                    obj_col_node.label= "obj_col_node"
                    obj_col_node.data_type='FLOAT_COLOR'
                    obj_col_node.domain= 'FACE'
                    obj_col_node.inputs['Name'].default_value= "color"
                    obj_col_node.inputs["Value"].default_value=[1,1,1,1]
                    
                    
                    oftra_node = node_tree.nodes.new(type="GeometryNodeTransform")
                    ofadd_node = node_tree.nodes.new(type="ShaderNodeMath")
                    ofadd_node.inputs[1].default_value = 1.0
                    ofmul_node = node_tree.nodes.new(type="ShaderNodeMath")
                    ofmul_node.operation="MULTIPLY"
                    ofmul_node.inputs[1].default_value = p_i
                    node_tree.links.new(offset.outputs['Value'], ofmul_node.inputs[0])
                    node_tree.links.new(ofmul_node.outputs['Value'], ofadd_node.inputs[0])
                    node_tree.links.new(ofadd_node.outputs['Value'], oftra_node.inputs['Scale'])
                    
                    if prop.get("mesh_group"):
                        ins_node = node_tree.nodes.new(type="GeometryNodeGeometryToInstance")
                        rot_node = node_tree.nodes.new(type="GeometryNodeRotateInstances")
                        sep_node = node_tree.nodes.new(type="GeometryNodeSeparateGeometry")
                        axis_node = node_tree.nodes.new(type="FunctionNodeAxisAngleToRotation")
                        radian_node = node_tree.nodes.new(type="ShaderNodeMath")
                        radian_node.operation="RADIANS"
                        node_tree.links.new(axis_node.outputs['Rotation'], rot_node.inputs['Rotation'])
                        node_tree.links.new(radian_node.outputs['Value'], axis_node.inputs['Angle'])
                        node_tree.links.new(obj_node.outputs['Geometry'], sep_node.inputs['Geometry'])
                        node_tree.links.new(rot_node.outputs['Instances'], ins_node.inputs['Geometry'])
                        node_tree.links.new(sep_node.outputs['Inverted'], ins_node.inputs['Geometry'])
                        node_tree.links.new(ins_node.outputs['Instances'], obj_col_node.inputs['Geometry'])
                        group_node = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
                        node_tree.links.new(group_node.outputs['Attribute'], sep_node.inputs['Selection'])
                        if prop.get("mesh_group",{}).get("chest"):
                            group_node.inputs[0].default_value="chest"
                            axis_node.inputs['Axis'].default_value=[1,0,0]
                            rot_node.inputs[3].default_value=[8,-7/16,1/16]
                            mult_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult_node.operation="MULTIPLY"
                            mult_node.inputs[1].default_value=90
                            node_tree.links.new(mult_node.outputs['Value'], radian_node.inputs['Value'])
                            node_tree.links.new(sep_node.outputs['Selection'], rot_node.inputs['Instances'])
                            mult_node.inputs[0].default_value=prop["value"]
                        elif prop.get("mesh_group",{}).get("shulker"):
                            group_node.inputs[0].default_value="shulker"
                            axis_node.inputs['Axis'].default_value=[0,0,1]
                            mult_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult_node.operation="MULTIPLY"
                            mult_node.inputs[1].default_value=270
                            trans_node = node_tree.nodes.new(type="GeometryNodeTranslateInstances")
                            node_tree.links.new(mult_node.outputs['Value'], radian_node.inputs['Value'])
                            node_tree.links.new(sep_node.outputs['Selection'], trans_node.inputs['Instances'])
                            node_tree.links.new(trans_node.outputs['Instances'], rot_node.inputs['Instances'])
                            comb_node = node_tree.nodes.new(type="ShaderNodeCombineXYZ")
                            trmu_node = node_tree.nodes.new(type="ShaderNodeMath")
                            trmu_node.operation="MULTIPLY"
                            trmu_node.inputs[1].default_value=0.5
                            node_tree.links.new(comb_node.outputs['Vector'], trans_node.inputs['Translation'])
                            node_tree.links.new(trmu_node.outputs['Value'], comb_node.inputs['Z'])
                            mult_node.inputs[0].default_value=prop["value"]
                        elif prop.get("mesh_group",{}).get("dragon"):
                            group_node.inputs[0].default_value="dragon"
                            axis_node.inputs['Axis'].default_value=[1,0,0]
                            rot_node.inputs[3].default_value=[1/16,(14-8)/16,(3-8)/16]
                            add_node = node_tree.nodes.new(type="ShaderNodeMath")
                            add_node.operation="ADD"
                            add_node.inputs[1].default_value=-12.5
                            mult_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult_node.operation="MULTIPLY"
                            mult_node.inputs[1].default_value=-12.5
                            sin_node = node_tree.nodes.new(type="ShaderNodeMath")
                            sin_node.operation="SINE"
                            mult2_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult2_node.operation="MULTIPLY"
                            mult2_node.inputs[1].default_value=(2*math.pi)/10
                            node_tree.links.new(sep_node.outputs['Selection'], rot_node.inputs['Instances'])
                            node_tree.links.new(add_node.outputs['Value'], radian_node.inputs['Value'])
                            node_tree.links.new(mult_node.outputs['Value'], add_node.inputs[0])
                            node_tree.links.new(sin_node.outputs['Value'], mult_node.inputs[0])
                            node_tree.links.new(mult2_node.outputs['Value'], sin_node.inputs[0])
                            mult2_node.inputs[0].default_value=prop["value"]
                        elif prop.get("mesh_group",{}).get("piglin_r"):
                            group2_node = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
                            group_node.inputs[0].default_value="piglin_l"
                            group2_node.inputs[0].default_value="piglin_r"
                            sep2_node = node_tree.nodes.new(type="GeometryNodeSeparateGeometry")
                            node_tree.links.new(sep_node.outputs['Inverted'], sep2_node.inputs['Geometry'])
                            rot2_node = node_tree.nodes.new(type="GeometryNodeRotateInstances")
                            rot_node.inputs[3].default_value=[(12.5-8)/16,8,-2/16]
                            rot2_node.inputs[3].default_value=[(3.5-8)/16,8,-2/16]
                            axis2_node = node_tree.nodes.new(type="FunctionNodeAxisAngleToRotation")
                            axis_node.inputs['Axis'].default_value=[0,1,0]
                            axis2_node.inputs['Axis'].default_value=[0,1,0]
                            add_node = node_tree.nodes.new(type="ShaderNodeMath")
                            add_node.operation="ADD"
                            add_node.inputs[1].default_value=-(40+17)/2
                            mult_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult_node.operation="MULTIPLY"
                            mult_node.inputs[1].default_value=-(40-17)/2
                            sin_node = node_tree.nodes.new(type="ShaderNodeMath")
                            sin_node.operation="SINE"
                            mult2_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult2_node.operation="MULTIPLY"
                            mult2_node.inputs[1].default_value=(2*math.pi)/10
                            
                            radian2_node = node_tree.nodes.new(type="ShaderNodeMath")
                            radian2_node.operation="RADIANS"
                            add2_node = node_tree.nodes.new(type="ShaderNodeMath")
                            add2_node.operation="ADD"
                            add2_node.inputs[1].default_value=(40+17)/2
                            mult3_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult3_node.operation="MULTIPLY"
                            mult3_node.inputs[1].default_value=(40-17)/2
                            sin2_node = node_tree.nodes.new(type="ShaderNodeMath")
                            sin2_node.operation="SINE"
                            mult4_node = node_tree.nodes.new(type="ShaderNodeMath")
                            mult4_node.operation="MULTIPLY"
                            mult4_node.inputs[1].default_value=(2*math.pi)/8.333
                            node_tree.links.new(group2_node.outputs['Attribute'], sep2_node.inputs['Selection'])
                            node_tree.links.new(rot2_node.outputs['Instances'], ins_node.inputs['Geometry'])
                            node_tree.links.new(obj_node.outputs['Geometry'], sep2_node.inputs['Geometry'])
                            node_tree.links.new(sep2_node.outputs['Inverted'], sep_node.inputs['Geometry'])
                            node_tree.links.new(sep2_node.outputs['Selection'], rot_node.inputs['Instances'])
                            node_tree.links.new(sep_node.outputs['Selection'], rot2_node.inputs['Instances'])
                            node_tree.links.new(axis2_node.outputs['Rotation'], rot2_node.inputs['Rotation'])
                            
                            node_tree.links.new(add_node.outputs['Value'], radian_node.inputs['Value'])
                            node_tree.links.new(mult_node.outputs['Value'], add_node.inputs[0])
                            node_tree.links.new(sin_node.outputs['Value'], mult_node.inputs[0])
                            node_tree.links.new(mult2_node.outputs['Value'], sin_node.inputs[0])
                            node_tree.links.new(radian2_node.outputs['Value'], axis2_node.inputs['Angle'])
                            node_tree.links.new(add2_node.outputs['Value'], radian2_node.inputs['Value'])
                            node_tree.links.new(mult3_node.outputs['Value'], add2_node.inputs[0])
                            node_tree.links.new(sin2_node.outputs['Value'], mult3_node.inputs[0])
                            node_tree.links.new(mult4_node.outputs['Value'], sin2_node.inputs[0])
                            mult2_node.inputs[0].default_value=prop["value"]
                            mult4_node.inputs[0].default_value=prop["value"]
                    else:
                        node_tree.links.new(obj_node.outputs['Geometry'], obj_col_node.inputs['Geometry'])
                    node_tree.links.new(obj_col_node.outputs['Geometry'], oftra_node.inputs['Geometry'])
                    node_tree.links.new(oftra_node.outputs['Geometry'], obj_node_switch.inputs['True'])
                    # node_tree.links.new(obj_col_node.outputs['Geometry'], obj_node_switch.inputs['True'])
                    pre_node=None
                    for i,layer in enumerate(prop["layers"]):
                        if layer["type"] == "tintindex" :
                            if layer["index"] == -1:
                                continue
                            tint = node_tree.nodes.new(type="GeometryNodeStoreNamedAttribute")
                            tint.label= "tint"
                            tint.data_type='FLOAT_COLOR'
                            tint.domain= 'FACE'
                            tint.inputs['Name'].default_value= "color"
                            tint_out=tint.outputs['Geometry']
                            attr_node = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
                            attr_node.label="tintindex{}".format(layer["index"])
                            attr_node.inputs[0].default_value="tintindex{}".format(layer["index"])
                            attr_node.data_type= 'FLOAT_VECTOR'
                            node_tree.links.new(attr_node.outputs['Attribute'], tint.inputs['Selection'])
                            if pre_node:
                                node_tree.links.new(tint_out,pre_node)
                            else:
                                node_tree.links.new(tint_out, obj_node_switch.inputs['True'])
                            pre_node=tint.inputs['Geometry']
                            if len(prop["layers"])-1 == i:
                                node_tree.links.new(obj_col_node.outputs['Geometry'],tint.inputs['Geometry'])
                            if layer.get("tint"):
                                if re.match("(minecraft:)?constant",layer["tint"]["type"]):
                                    c= decimal_to_rgba(layer["tint"]["value"])
                                    rgb= node_tree.nodes.new(type="FunctionNodeInputColor")
                                    rgb.value= [*c,1]
                                    tint_out=rgb.outputs['Color']
                                    node_tree.links.new(tint_out, tint.inputs['Value'])
                                elif re.match("(minecraft:)?(dye|custom_model_data|firework|map_color|potion|grass)",layer["tint"]["type"]):
                                    layer["tint"]["node"]=tint.inputs['Value']
                                    tints.append(layer["tint"])
                        elif layer.get("tint"):
                            tex_node = None
                            tex_node = node_tree.nodes.new(type="GeometryNodeImageTexture")
                            if layer["tex"] != None:
                                tex_node.label="tex_node"
                                tex_node.interpolation = "Closest"
                                if not "/".join(layer["tex"][-2:]) in bpy.data.images:
                                    image, anim = get_pack(directory,layer["tex"])
                                    if not image:
                                        self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture not found.\nFILE:%s\nTEXTUR:%s") % (texture+".json",layer["tex"][-1]))
                                        image = None
                                else:
                                    image = bpy.data.images["/".join(layer["tex"][-2:])]
                                tex_node.inputs['Image'].default_value = image
                                uv_node = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
                                uv_node.label="uv_node"
                                uv_node.inputs[0].default_value="UVMap"
                                uv_node.data_type= 'FLOAT_VECTOR'
                                node_tree.links.new(uv_node.outputs['Attribute'], tex_node.inputs['Vector'])
                            comp_node = node_tree.nodes.new(type="ShaderNodeMix")
                            comp_node.label="comp_node"
                            comp_node.data_type= "RGBA"
                            comp_node.blend_type = "MULTIPLY"
                            comp_node.inputs['Factor'].default_value = 1
                            comp_node.inputs['A'].default_value=[1,1,1,1]
                            node_tree.links.new(tex_node.outputs['Alpha'], comp_node.inputs['Factor'])
                            if re.match("(minecraft:)?constant",layer["tint"]["type"]):
                                c= decimal_to_rgba(layer["tint"]["value"])
                                rgb= node_tree.nodes.new(type="FunctionNodeInputColor")
                                rgb.value= [*c,1]
                                tint_out=rgb.outputs['Color']
                                node_tree.links.new(tint_out, comp_node.inputs['B'])
                            elif re.match("(minecraft:)?(dye|custom_model_data|firework|map_color|potion|grass)",layer["tint"]["type"]):
                                layer["tint"]["node"]=comp_node.inputs['B']
                                tints.append(layer["tint"])
                            if len(prop["layers"])-1 != i:
                                mix_node= node_tree.nodes.new(type="ShaderNodeMix")
                                mix_node.label= "mix_node"
                                mix_node.data_type= "RGBA"
                                if pre_node:
                                    node_tree.links.new(mix_node.outputs['Result'], pre_node)
                                else:
                                    node_tree.links.new(mix_node.outputs['Result'], obj_col_node.inputs['Value'])
                                node_tree.links.new(comp_node.outputs['Result'], mix_node.inputs['B'])
                                node_tree.links.new(tex_node.outputs['Alpha'], mix_node.inputs['Factor'])
                                pre_node=mix_node.inputs['A']
                            else:
                                if pre_node:
                                    node_tree.links.new(comp_node.outputs['Result'], pre_node)
                                else:
                                    node_tree.links.new(comp_node.outputs['Result'], obj_col_node.inputs['Value'])
                for i,tint in enumerate(tints):
                    driver_list=[]
                    if re.match("(minecraft:)?grass",tint["type"]):
                        if not "colormap/grass.png" in bpy.data.images:
                            image, anim = get_pack(directory,["assets","minecraft","textures","colormap","grass.png"])
                            if not image:
                                self.report({'ERROR_INVALID_INPUT'}, bpy.app.translations.pgettext("Texture not found.\nFILE:%s\nTEXTUR:%s") % (texture+".json","grass.png"))
                                image = None
                        else:
                            image = bpy.data.images["colormap/grass.png"]
                        grass= node_tree.nodes.new(type="GeometryNodeImageTexture")
                        grass.extension='EXTEND'
                        grass.inputs['Image'].default_value=image
                        comb= node_tree.nodes.new(type="ShaderNodeCombineXYZ")
                        sepa= node_tree.nodes.new(type="ShaderNodeSeparateXYZ")
                        sepa.inputs[0].default_value=[tint["downfall"],tint["temperature"],0]
                        x_add= node_tree.nodes.new(type="ShaderNodeMath")
                        x_add.inputs[1].default_value= 1
                        x_mult= node_tree.nodes.new(type="ShaderNodeMath")
                        x_mult.operation= 'MULTIPLY'
                        x_mult.inputs[1].default_value= -1
                        y_mult= node_tree.nodes.new(type="ShaderNodeMath")
                        y_mult.operation= 'MULTIPLY'
                        node_tree.links.new(sepa.outputs["X"], x_mult.inputs[0])
                        node_tree.links.new(x_mult.outputs["Value"], x_add.inputs[0])
                        node_tree.links.new(x_add.outputs["Value"], comb.inputs["X"])
                        node_tree.links.new(sepa.outputs["X"], y_mult.inputs[0])
                        node_tree.links.new(sepa.outputs["Y"], y_mult.inputs[1])
                        node_tree.links.new(y_mult.outputs["Value"], comb.inputs["Y"])
                        node_tree.links.new(comb.outputs["Vector"], grass.inputs["Vector"])
                        node_tree.links.new(grass.outputs["Color"], tint["node"])
                    else:
                        if re.match("(minecraft:)?custom_model_data",tint["type"]):
                            attr_name="{}{}".format(tint["type"].split(":")[-1],tint["index"])
                        elif re.match("(minecraft:)?dye",tint["type"]):
                            attr_name= "dyed_color"
                        elif re.match("(minecraft:)?firework",tint["type"]):
                            attr_name= "firework_explosion"
                        elif re.match("(minecraft:)?map_color",tint["type"]):
                            attr_name= "map_color"
                        elif re.match("(minecraft:)?potion",tint["type"]):
                            attr_name= "potion_contents"
                        if not attr_name in node_tree.interface.items_tree:
                            new_object.O2MCD_props["color"][attr_name]=[1,1,1,1]
                            node_tree.interface.new_socket(attr_name, in_out="INPUT", socket_type="NodeSocketColor")
                            modi[f"Socket_{3+i*2}_attribute_name"]= attr_name
                            node_tree.links.new(geo_in.outputs[1+len(props)+i], tint["node"])
                            driver_list = new_object.driver_add(f"{modi.path_from_id()}[\"Socket_{2+len(props)+i}\"]")
                        for di,fc in enumerate(driver_list[:-1]):
                            driver= fc.driver
                            driver.expression = "var"
                            var = driver.variables.new()
                            var.type = "SINGLE_PROP"
                            var.targets[0].id = new_object
                            n=prop["datalist"][0]["name"].split("/")[-1]
                            var.targets[0].data_path = f"O2MCD_props[\"color\"][\"{attr_name}\"][{di}]"
                    alphas+=[p for p in list(prop["mesh_group"].keys())]
                for i,cc in enumerate(alphas):
                    alpha = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
                    alpha.inputs["Name"].default_value=cc
                    node_tree.interface.new_socket(cc, in_out="OUTPUT", socket_type="NodeSocketFloat").attribute_domain='FACE'
                    node_tree.links.new(alpha.outputs['Attribute'], geo_out.inputs[cc])
                    modi[f"Socket_{i+2+len(alphas)*2}_attribute_name"]=f"alpha{i}"
                    node_tree.interface.new_socket(prop["object"].name, in_out="INPUT", socket_type="NodeSocketBool")
                    obj_node = node_tree.nodes.new(type="GeometryNodeObjectInfo")
                    obj_node.inputs[0].default_value = prop["object"]
                    obj_node_switch = node_tree.nodes.new(type="GeometryNodeSwitch")
                    node_tree.links.new(geo_in.outputs[i+1+len(tints)], obj_node_switch.inputs['Switch'])
                    node_tree.links.new(obj_node_switch.outputs['Output'], geo_to_ins.inputs['Geometry'])
                    node_tree.links.new(obj_node.outputs['Geometry'], obj_node_switch.inputs['True'])
                    driver = new_object.driver_add(f"{modi.path_from_id()}[\"Socket_{i+2+len(tints)*2+len(alphas)}\"]").driver
                    driver.expression = "var"
                    var = driver.variables.new()
                    var.type = "SINGLE_PROP"
                    var.targets[0].id = new_object
                    # n=prop["datalist"][0]["name"].split("/")[-1]
                    var.targets[0].data_path = f"O2MCD_props[\"models\"][{i}]"
            elif types == "block":
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
                alphas=[p for p in list(props[0]["mesh_group"].keys()) if p[:9] == "tintindex"]
                for i,cc in enumerate(alphas):
                    alpha = node_tree.nodes.new(type="GeometryNodeInputNamedAttribute")
                    alpha.inputs["Name"].default_value=cc
                    node_tree.interface.new_socket(cc, in_out="OUTPUT", socket_type="NodeSocketFloat").attribute_domain='FACE'
                    node_tree.links.new(alpha.outputs['Attribute'], geo_out.inputs[cc])
                    modi[f"Socket_{i+2+len(value_list)}_attribute_name"]=f"alpha{i}"
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
            for ml in materials:
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
                    tex = node_tree.nodes["Texture"]
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
        # elif re.fullmatch(f"{colors}_banner", name):
        #     for ml in mat_list:
        #         if re.fullmatch(f"{colors}_banner", ml.name):
        #             node_tree = ml.node_tree
        #             tex = node_tree.nodes[2]
        #             mult = node_tree.nodes.new("ShaderNodeMix")
        #             mult.inputs[0].default_value = 1
        #             mult.blend_type = 'MULTIPLY'
        #             mult.data_type = 'RGBA'
                    
        #             node_tree.links.new(tex.outputs[0], mult.inputs['A'])
        #             node_tree.links.new(mult.outputs['Result'], bsdf.inputs[0])
        #             match name:
        #                 case "white_banner":
        #                     col = [255, 255, 255]
        #                 case "orange_banner":
        #                     col = [216, 127, 51]
        #                 case "magenta_banner":
        #                     col = [178, 76, 216]
        #                 case "light_blue_banner":
        #                     col = [102, 153, 216]
        #                 case "yellow_banner":
        #                     col = [229, 229, 51]
        #                 case "lime_banner":
        #                     col = [127, 204, 25]
        #                 case "pink_banner":
        #                     col = [242, 127, 165]
        #                 case "gray_banner":
        #                     col = [76, 76, 76]
        #                 case "light_gray_banner":
        #                     col = [153, 153, 153]
        #                 case "cyan_banner":
        #                     col = [76, 127, 153]
        #                 case "purple_banner":
        #                     col = [127, 63, 178]
        #                 case "blue_banner":
        #                     col = [51, 76, 178]
        #                 case "brown_banner":
        #                     col = [102, 76, 51]
        #                 case "green_banner":
        #                     col = [102, 127, 51]
        #                 case "red_banner":
        #                     col = [153, 51, 51]
        #                 case "black_banner":
        #                     col = [25, 25, 25]
        #             col = [b/255 for b in col]
        #             col[0] = col[0]/12.92 if col[0] <= 0.04045 else math.pow((col[0]+0.055)/1.055, 2.4)
        #             col[1] = col[1]/12.92 if col[1] <= 0.04045 else math.pow((col[1]+0.055)/1.055, 2.4)
        #             col[2] = col[2]/12.92 if col[2] <= 0.04045 else math.pow((col[2]+0.055)/1.055, 2.4)
        #             col.append(1)
        #             mult.inputs[7].default_value = ([*col])
        else:
            if "/".join([types, name]) in bpy.data.node_groups: 
                modi = new_object.modifiers.new("O2MCD", "NODES")
                node_tree = bpy.data.node_groups["/".join([types, name])]
                modi.node_group = node_tree
                for m in range(len(list(filter(lambda x: x.type == 'MENU_SWITCH', [n for n in node_tree.nodes])))):
                    modi["Socket_"+str(m+2)] = 0
            if version in version_list[version_list.index("1.21.4"):]:
                # if not "models" in new_object.O2MCD_props:
                #     new_object.O2MCD_props["models"] = []
                node_tree = bpy.data.node_groups["/".join([types, name])]
                obj_list = [context.scene.collection.children["O2MCD_models"].all_objects[o.name] for o in node_tree.interface.items_tree[2:]]
                models=[]
                for i,data in enumerate(obj_list):
                    models.append(False)
                    driver = new_object.driver_add(f"{modi.path_from_id()}[\"Socket_{i+2}\"]").driver
                    driver.expression = "var"
                    var = driver.variables.new()
                    var.type = "SINGLE_PROP"
                    var.targets[0].id = new_object
                    var.targets[0].data_path = f"O2MCD_props[\"models\"][{i}]"
                # new_object.O2MCD_props["models"]=models
    new_object.O2MCD_props.disp_id = name
    if not list_data:
        list_data = new_object.O2MCD_props.data_list.add()
        # list_data.data = f"{{id:\"{name}\",count:1,components:{{}}}}"
        object.add_item_data(list_data,"id",'STRING',f"\"{name}\"")
        object.add_item_data(list_data,"count",'INT',1)
        object.add_item_data(list_data,"components",'COMPOUND',None)
    list_data.mesh = new_mesh
    list_data.name = new_mesh.name
    list_data.id = name
    list_data.model_id = f"minecraft:{name}"
    
    if types == "item":
        new_object.O2MCD_props.disp_type = "item_display"
        if not context.scene.O2MCD_props.get(name):
            if not context.scene.O2MCD_props.get("models"):
                context.scene.O2MCD_props["models"]= {}
            context.scene.O2MCD_props["models"][name] = item_model
    elif types == "block":    
        new_object.O2MCD_props.disp_type = "block_display"
    try:
        with open(bpy.path.abspath(os.path.dirname(__file__))+os.sep+"durability_list.json", 'r') as f:
            durability = json.load(f)
    except:
        durability=[]
    if name in durability:
        list_data.max_durability = str(durability[name])
    context.view_layer.objects.active = new_object
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active.select_set(True)
    new_object.update_tag()
    

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
    
    def get_file(self,context,dir,path):
        result=[]
        for f in os.listdir(dir):
            if f.endswith(".json") and not "/".join([path,f[:-5]]) in context.scene.O2MCD_props["model_ids"]:
                result.append("/".join([path,f[:-5]]))
            elif os.path.isdir(os.path.join(dir,f)):
                result+=self.get_file(context,os.path.join(dir,f),"/".join([path,f]))
        return result
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        rc_pack = context.scene.O2MCD_rc_packs.add()
        rc_pack.path = self.filepath
        context.scene.O2MCD_rc_packs.move(len(context.scene.O2MCD_rc_packs)-1, 1)
        context.scene.O2MCD_props["model_ids"]=[":".join(["minecraft",i.name]) for i in context.preferences.addons[__package__].preferences.item_list]
        ap=[]
        for pack in context.scene.O2MCD_rc_packs[1:-1]:
            if pack.type == 'FOLDER':
                for l in [f for f in os.listdir(os.path.join(pack.path,"assets"+os.sep)) if os.path.isdir(os.path.join(pack.path,"assets",f))]:
                    for n in [f for f in os.listdir(os.path.join(pack.path,"assets",l,"items"))]:
                        if n.endswith(".json") and not ":".join([l,n[:-5]]) in context.scene.O2MCD_props["model_ids"]:
                            ap.append(":".join([l,n[:-5]]))
                        elif os.path.isdir(os.path.join(pack.path,"assets",l,"items",n)):
                            ap+=self.get_file(context,os.path.join(pack.path,"assets",l,"items",n),":".join([l,n]))
            else:
                try:
                    with zipfile.ZipFile(pack.path) as zip: 
                        for l in [l for l in zip.namelist() if re.match("assets/[^/]+/items",l)]:
                            lst=l.split("/")
                            if l.endswith(".json") and not lst[1]+":"+"/".join([*lst[3:-1],lst[-1][:-5]]) in context.scene.O2MCD_props["model_ids"]:
                                ap.append(lst[1]+":"+"/".join([*lst[2:-1],lst[-1][:-5]]))
                except:
                    pass
        context.scene.O2MCD_props["model_ids"]=ap+context.scene.O2MCD_props["model_ids"]
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
        if self.action == 'DOWN' and index != 0 and index < len(list)-1:
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