# Copyright (c) 2023 200Q

import bpy
import mathutils
import os
from re import *
from math import *
from bpy.app.handlers import persistent

# 関数

def item_regist():  # アイテムをブロックを登録
    file = open(bpy.path.abspath(os.path.dirname(__file__))+'\\item_list.txt', 'r', encoding='UTF-8')
    item = file.read().splitlines()
    bpy.context.scene.item_list.clear()
    for i in item:
        bpy.context.scene.item_list.add().name= i
    file.close()
    
    file = open(bpy.path.abspath(os.path.dirname(__file__))+'\\block_list.txt', 'r', encoding='UTF-8')
    block = file.read().splitlines()
    bpy.context.scene.block_list.clear()
    for i in block:
        bpy.context.scene.block_list.add().name= i
    file.close()
def update(self, context):  # 更新処理
    # アドオンを有効
    if bpy.context.scene.O2MCD_props.enable:
        bpy.app.handlers.depsgraph_update_post.append(chenge_panel)
        # Inputが無ければ作成
        if "Input" not in bpy.data.texts:
            bpy.data.texts.new("Input")
        # 自動更新を有効
        if bpy.context.scene.O2MCD_props.auto_reload:
            bpy.app.handlers.frame_change_post.append(command_generate)
            bpy.app.handlers.depsgraph_update_post.append(command_generate)
        # 自動更新を無効
        else:
            if command_generate in bpy.app.handlers.frame_change_post:
                bpy.app.handlers.frame_change_post.remove(command_generate)
            if command_generate in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    # アドオンを無効
    else:
        try:
            bpy.app.handlers.frame_change_post.remove(command_generate)
            bpy.app.handlers.depsgraph_update_post.remove(command_generate)
            bpy.app.handlers.depsgraph_update_post.remove(chenge_panel)
        except:pass
def setid(self,context):  # idを更新
    if context.scene.prop_list[context.scene.O2MCD_props.list_index].Types == "ITEM":
        context.scene.prop_list[context.scene.O2MCD_props.list_index].id = context.scene.prop_list[context.scene.O2MCD_props.list_index].item_id
    elif context.scene.prop_list[context.scene.O2MCD_props.list_index].Types == "BLOCK":
        context.scene.prop_list[context.scene.O2MCD_props.list_index].id = context.scene.prop_list[context.scene.O2MCD_props.list_index].block_id
def chenge_panel(self, context):  # オブジェクトリストとオブジェクト番号を更新
    active = context.view_layer.objects.active
    scene = bpy.context.scene
    if not active == None:
        if active.O2MCD_props.prop_id > len(scene.prop_list)-1:
            active.O2MCD_props.prop_id = -1
        scene.O2MCD_props.list_index = active.O2MCD_props.prop_id
    
    for i, l in enumerate(scene.object_list):
        if not l.obj.name in context.view_layer.objects or l.obj.O2MCD_props.prop_id ==-1 :
            l.obj.O2MCD_props.number = -1
            scene.object_list.remove(i)
            break
    for i in context.view_layer.objects:
        if i.O2MCD_props.prop_id >= 0 and not i in [i.obj for i in scene.object_list]:
            scene.object_list.add().obj = i
    for i, list in enumerate(scene.object_list):
        list.obj.O2MCD_props.number = i
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D' or 'PROPERTIES':
            area.tag_redraw()
    

def change_name(self,context):  # 名前被りを回避
    if [i.name for i in context.scene.prop_list].count(self.name) > 1:
        name = sub("(.*?)(\.[0-9]+)?","\\1",self.name)
        same_names = [i.name for i in context.scene.prop_list if match(f"{name}(?:\.[0-9]+)?",i.name)]
        same_names.sort()
        if same_names:
            for i in same_names:
                ii = sub(".+?\.([0-9]+)","\\1",i)
                if ii == name:
                    if not name+".001" in same_names:
                        self.name = name+".001"
                        break
                else:
                    ii = str(int(ii)+1).zfill(3)
                    if not name+"."+ii in same_names:
                        self.name = name+"."+ii
                        break

def get_location(context,object):  # 位置取得
    loc = mathutils.Euler((radians(-90), 0, 0),'XYZ').to_matrix().to_4x4() @ object.matrix_world
    rou = context.scene.O2MCD_props.rou
    if context.scene.prop_list[object.O2MCD_props.prop_id].Types == "BLOCK":
        loc = loc @ mathutils.Matrix.Translation(
            mathutils.Vector((0.5, -0.5, -0.5)))
    loc = loc.translation
    loc = (round(loc[0], rou), round(loc[1], rou), round(loc[2], rou))
    return loc

def get_scale(context,object):  # スケール取得
    scale = object.matrix_world.to_scale()
    rou = context.scene.O2MCD_props.rou
    if object.parent:
        if object.parent_type == "BONE":
            pscale = object.parent.pose.bones[object.parent_bone].matrix @ object.matrix_world
            pscale = pscale.to_scale()
        else:
            pscale = object.parent.matrix_world.to_scale()
        if not round(pscale[0], rou) == round(pscale[1], rou) == round(pscale[2], rou):
            object.scale = (1, 1, 1)
            scale = pscale
    scale = (round(scale[0], rou), round(scale[1], rou), round(scale[2], rou))
    return scale


def get_left_rotation(context,object):  # 左回転取得
    rou = context.scene.O2MCD_props.rou
    if object.parent:
        if object.parent_type == "BONE":
            l_rot = object.parent.pose.bones[object.parent_bone].matrix
            l_rot = object.parent.matrix_world @ l_rot
            l_rot = l_rot.to_euler()
            l_rot = mathutils.Euler(
                (l_rot[0]-1.5708, l_rot[1], l_rot[2]), 'XYZ')
        else:
            l_rot = object.parent.matrix_world.to_euler()
    else:
        l_rot = object.matrix_world.to_euler()
    l_rot_x = mathutils.Euler((-l_rot[0], 0, 0), 'XYZ').to_matrix().to_4x4()
    l_rot_y = mathutils.Euler((0, l_rot[2], 0), 'XYZ').to_matrix().to_4x4()
    l_rot_z = mathutils.Euler((0, 0, l_rot[1]), 'XYZ').to_matrix().to_4x4()
    l_rot = (mathutils.Euler((0, radians(180), 0), 'XYZ').to_matrix(
    ).to_4x4() @ l_rot_y @ l_rot_z @ l_rot_x).to_quaternion()
    l_rot = [round(l_rot[1], rou), round(l_rot[2], rou),round(l_rot[3], rou), round(l_rot[0], rou)]
    return l_rot


def get_right_rotation(context,object):  # 右回転取得
    rou = context.scene.O2MCD_props.rou
    if object.parent:
        r_rot = object.rotation_euler
        r_rot = mathutils.Euler(
            (-r_rot[0], r_rot[2], r_rot[1]), 'XYZ').to_quaternion()
    else:
        r_rot = mathutils.Euler((0, 0, 0), 'XYZ').to_quaternion()
    r_rot = [round(r_rot[1], rou), round(r_rot[2], rou),round(r_rot[3], rou), round(r_rot[0], rou)]
    return r_rot


def frame_range(context, com):  # フレーム範囲指定
    for i in range(len(com)):
        # 範囲設定
        if match("^\[[0-9]+\]", com[i]):
            min = int(sub("^\[([0-9]+)\].*", "\\1", com[i]))
            max = min
        elif match("^\[[0-9]+\-[0-9]+\]", com[i]):
            min = int(sub("^\[([0-9]+)\-[0-9]+\].*", "\\1", com[i]))
            max = int(sub("^\[[0-9]+\-([0-9]+)\].*", "\\1", com[i]))
        else:
            min = context.scene.frame_start
            max = context.scene.frame_end
        # 範囲比較
        if min <= context.scene.frame_current <= max:
            com[i] = sub("^\[(?:[0-9]+|[0-9]+\-[0-9]+)\](\s?:\s?)?", "", com[i])
        else:
            com[i] = None
    com = [i for i in com if not i == None]
    return com


def comvert_function(context, object_list, funk_list, com, num):  # 関数変換
    # 現在のフレームを保存
    current_frame = context.scene.frame_current
    # /transfだけ先に変換
    com = com.replace("/transf", "right_rotation:[/r_rot],scale:[/scale],left_rotation:[/l_rot],translation:[/loc]")
    # 入力から関数のリストを作成
    func = findall(
        f'(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)', com)
    # 関数を1つずつ処理
    for f in func:
        # 関数名
        var = sub(
            f'/({funk_list})(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?', "\\1", f)
        # 引数
        val = sub('/.+?\[(.+)\]', "V\\1", f)
        # 引数の中の関数を変換
        if not val == "" and not val == f and match(f".*/{funk_list}.*", val):
            val = comvert_function(context, object_list, funk_list, val, num)
        # 要素番号
        elm = sub('V?([0-9]*?)(,.*)?', "\\1", val)
        # フレーム数
        frm = sub('V?.*?,((?:\+|\-)?[0-9]*?)(,.*)?', "\\1", val)
        # オブジェクト
        obj = sub('V?.*?,.*?,((?:\+|\-)?.*?)', "\\1", val)
        # math以外の関数を処理
        if not var == "math":
            # フレームを設定
            if frm == "" or frm == val:
                frm = str(current_frame)
            elif match("(?:\+|\-)[0-9]+", frm):
                frm = eval(str(current_frame)+frm)
            context.scene.frame_set(int(frm))
            # オブジェクトを設定
            if obj == "" or obj == val:
                obj = object_list[num].obj
            elif match("(?:\+|\-)[0-9]+", obj):
                obj = eval(str(object_list[num].obj.O2MCD_props.number)+obj)
                if len(object_list)-1 < obj:
                    obj = len(object_list)-1
                elif 0 > obj:
                    obj = 0
                obj = object_list[obj].obj
                num = obj.O2MCD_props.number
            elif match("^[0-9]+", obj):
                obj = object_list[int(obj)].obj
                num = obj.O2MCD_props.number
            else:
                obj = context.scene.objects[obj]
            # transformationを取得
            if var == "loc":
                location = get_location(context,obj)
            if var == "scale":
                scale = get_scale(context,obj)
            if var == "r_rot":
                right_rotation = get_right_rotation(context,obj)
            if var == "l_rot":
                left_rotation = get_left_rotation(context,obj)
            # 名前を取得
            if var == "name" or var == "id":
                name = obj.name
            # idを取得
            if var == "id":
                id = context.scene.prop_list[obj.O2MCD_props.prop_id].id
            # extraNBTを取得
            if var == "extra":
                extra = context.scene.prop_list[obj.O2MCD_props.prop_id].ExtraNBT
            # タイプを取得
            if var == "type":
                if context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    type = "item_display"
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    type = "block_display"
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    type = context.scene.prop_list[obj.O2MCD_props.prop_id].type
            # ブロックのプロパティを取得
            if var == "prop":
                if context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    prop = ""
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    prop = ""
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    prop = ""
            # カスタムモデルデータを取得
            if var == "model":
                if context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    model = str(context.scene.prop_list[obj.O2MCD_props.prop_id].CustomModelData)
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    model = ""
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    model = ""
            # アイテムタグを取得
            if var == "item":
                if context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    item = context.scene.prop_list[obj.O2MCD_props.prop_id].ItemTag
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    item = ""
                elif context.scene.prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    item = ""
            # タグをリスト化
            if var == "tag" or var == "tags":
                tags = split(",", context.scene.prop_list[obj.O2MCD_props.prop_id].tags)
            # 置き換え
            if elm == "" or elm == val:
                if var == "loc": com = sub("/loc(\[.*?(,.*?)?\])?", str(location[0]) +"f,"+str(location[1])+"f,"+str(location[2])+"f", com, 1)
                if var == "scale": com = sub("/scale(\[.*?(,.*?)?\])?", str(scale[0]) +"f,"+str(scale[1])+"f,"+str(scale[2])+"f", com, 1)
                if var == "r_rot": com = sub("/r_rot(\[.*?(,.*?)?\])?", str(right_rotation[0])+"f,"+str(right_rotation[1])+"f,"+str(right_rotation[2])+"f,"+str(right_rotation[3])+"f", com, 1)
                if var == "l_rot": com = sub("/l_rot(\[.*?(,.*?)?\])?", str(left_rotation[0])+"f,"+str(left_rotation[1])+"f,"+str(left_rotation[2])+"f,"+str(left_rotation[3])+"f", com, 1)
                if var == "tag" or var == "tags":
                    if not context.scene.prop_list[obj.O2MCD_props.prop_id].tags == "":
                        if var == "tags": com = sub("/tags(\[.*?(,.*?)?\])?", ",".join(["\""+i+"\"" for i in tags]), com, 1)
                        if var == "tag": com = sub("/tag(\[.*?(,.*?)?\])?", ",".join(["tag="+i for i in tags]), com, 1)
                    else: com = sub("/tags?(\[.*?(,.*?)?\])?", "", com)
            else:
                if var == "loc": com = sub("/loc\[.*?(,.*?)?\]",str(location[int(elm)]), com, 1)
                if var == "scale": com = sub("/scale\[.*?(,.*?)?\]",str(scale[int(elm)]), com, 1)
                if var == "r_rot": com = sub("/r_rot\[.*?(,.*?)?\]",str(right_rotation[int(elm)]), com, 1)
                if var == "l_rot": com = sub("/l_rot\[.*?(,.*?)?\]",str(left_rotation[int(elm)]), com, 1)
                if var == "tag" or var == "tags":
                    if not context.scene.prop_list[obj.O2MCD_props.prop_id].tags == "":
                        if var == "tags": com = sub("/tags\[.*?(,.*?)?\]",tags[int(elm)], com, 1)
                        if var == "tag": com = sub("/tag\[.*?(,.*?)?\]",tags[int(elm)], com, 1)
                    else: com = sub("/tags?(\[.*?(,.*?)?\])?", "", com)
            if var == "prop":
                if not prop == "": com = sub("/prop(\[.*?(,.*?)?\])?", prop, com, 1)
                else: com = sub("/prop?(\[.*?(,.*?)?\])?", "", com)
            if var == "model":
                if not model == "": com = sub("/model(\[.*?(,.*?)?\])?", model, com, 1)
                else: com = sub("/item?(\[.*?(,.*?)?\])?", "", com)
            if var == "item":
                if not item == "": com = sub("/item(\[.*?(,.*?)?\])?", item, com, 1)
                else: com = sub("/item?(\[.*?(,.*?)?\])?", "", com)
            if var == "name": com = sub("/name(\[.*?(,.*?)?\])?", name, com, 1)
            if var == "id": com = sub("/id(\[.*?(,.*?)?\])?", id, com, 1)
            if var == "type": com = sub("/type(\[.*?(,.*?)?\])?", type, com, 1)
            if var == "num": com = sub("/num(\[.*?(,.*?)?\])?", str(num), com, 1)
            if var == "extra": com = sub("/extra(\[.*?(,.*?)?\])?", extra, com, 1)
        # mathを処理
        if var == "math":
            com = sub("/math\[.+\]+",str(eval(sub('V?(.+)', "\\1", val))), com, 1)
    if not current_frame == context.scene.frame_current:
        context.scene.frame_set(current_frame)
    return com


def command_generate(self, context):  # コマンド生成
    # ループ回避のため更新を停止
    if command_generate in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    # Outputが無ければ作成
    if "Output" not in bpy.data.texts:
        bpy.data.texts.new("Output")
    # 関数名
    funk_list = "(?:transf|loc|scale|l_rot|r_rot|name|id|type|model|item|prop|tags?|num|math|extra)"
    # コマンドをリスト化
    input = list(bpy.data.texts["Input"].as_string().splitlines())
    # エスケープ
    input = [s for s in input if not match('^#(?! +|#+)', s)]
    # 出力をリセット
    output = []

    # startを出力に追加
    com = [sub("^start(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("start(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", s)]
    com = frame_range(context, com)
    if com:
        com = "\n".join(com)
        if match(f".*/({funk_list}).*", com):
            com = comvert_function(context, context.scene.object_list, funk_list, com, None)
        output.append(com)
    # メインコマンドを出力に追加
    for i,l in enumerate(context.scene.object_list):
        o = l.obj
        if not o.hide_viewport and not o.hide_render:
            if context.scene.prop_list[o.O2MCD_props.prop_id].Types == "ITEM":
                com = [sub("^item(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!block|extra|start|end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?)", s)]
            elif context.scene.prop_list[o.O2MCD_props.prop_id].Types == "BLOCK":
                com = [sub("^block(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!item|extra|start|end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?)", s)]
            elif context.scene.prop_list[o.O2MCD_props.prop_id].Types == "EXTRA":
                com = [sub("^extra(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!block|item|start|end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?)", s)]
            com = frame_range(context, com)
            if com:
                com = "\n".join(com)
                if match(f".*/({funk_list}).*", com):
                    com = comvert_function(context, context.scene.object_list, funk_list, com, i)
                output.append(com)
    # endを出力に追加
    com = [sub("^end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", s)]
    com = frame_range(context, com)
    if com:
        com = "\n".join(com)
        if match(f".*/({funk_list}).*", com):
            com = comvert_function(context, context.scene.object_list, funk_list, com, None)
        output.append(com)
    # 更新を再開
    if context.scene.O2MCD_props.auto_reload:
        bpy.app.handlers.frame_change_post.append(command_generate)
        bpy.app.handlers.depsgraph_update_post.append(command_generate)

    # Outputに書き込み
    output = "\n".join(output)
    output = sub("[,\.][,\.]|([\{\[\(])[,\.]|[,\.]([\]\}\)])", "\\1\\2", output)
    bpy.data.texts["Output"].from_string(output)
    # テキストエディタの表示を更新
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.tag_redraw()

def enum_item(self, context):  # プロパティリスト
    enum_items = []
    for i in range(len(context.scene.prop_list)):
        enum_items.append((str(i), str(i)+":"+context.scene.prop_list[i].name, ""))
    return enum_items

# クラス


class OBJECTTOMCDISPLAY_PT_DisplayProperties(bpy.types.Panel):  # プロパティパネル
    bl_label = "Display Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.scene.O2MCD_props.enable

    def draw(self, context):
        layout = self.layout
        br = layout.row(align=True)
        br.alignment = "LEFT"
        if context.scene.prop_list:
            item = context.scene.prop_list[context.scene.O2MCD_props.list_index]
        br.operator("object.search_popup", text="", icon='DOWNARROW_HLT')
        if context.scene.O2MCD_props.list_index >= 0 and context.scene.prop_list:
            br.prop(item, "name", text="")
            br.operator("object.o2mcd_prop_action", icon='DUPLICATE').action = 'DUP'
            br.operator("object.o2mcd_prop_action", icon='PANEL_CLOSE').action = 'UNLINK'
            br.operator("object.o2mcd_prop_action", icon='TRASH').action = 'REMOVE'
        else:
            br.alignment = "EXPAND"
            br.operator("object.o2mcd_prop_action", icon='ADD',text="New").action = 'ADD'
        if context.scene.prop_list and context.object.O2MCD_props.prop_id >= 0:
            row = layout.row()
            row.enabled = False
            row.use_property_split = True
            row.use_property_decorate = False
            row.prop(context.object.O2MCD_props, "number")
            layout.prop(item, "Types", expand=True)
            if item.Types == "EXTRA":
                layout.prop(item, "type")
            if item.Types == "ITEM":
                layout.prop_search(context.scene.prop_list[context.object.O2MCD_props.prop_id], "item_id",context.scene, "item_list",text="id")
                layout.prop(item, "tags")
                layout.prop(item,"CustomModelData")
                layout.prop(item, "ItemTag")
            if item.Types == "BLOCK":
                layout.prop_search(context.scene.prop_list[context.object.O2MCD_props.prop_id], "block_id",context.scene, "block_list",text="id")
                layout.prop(item, "tags")
                layout.prop(item, "Properties",text="properties")
            layout.prop(item, "ExtraNBT")


class OBJECTTOMCDISPLAY_PT_MainPanel(bpy.types.Panel):  # 出力パネル
    bl_label = "O2MCD"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw_header(self, context):
        self.layout.prop(context.scene.O2MCD_props, "enable")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("render.o2mcd_reload")
        row.prop(context.scene.O2MCD_props, "auto_reload", toggle=True)
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene.O2MCD_props, "rou")
        layout.separator()
        col2 = layout.column(align=True)
        row2 = col2.row()
        row2.prop(context.scene.O2MCD_props, "output", expand=True)
        box = col2.box()
        if context.scene.O2MCD_props.output == "ANIMATION":
            box.prop(context.scene.O2MCD_props, "anim_path")
        else:
            box.prop(context.scene.O2MCD_props, "curr_path")
        box.operator("render.o2mcd_export")
        layout.enabled = context.scene.O2MCD_props.enable
        row4 = layout.row(align = True)
        row4.alignment = "LEFT"
        row4.prop(context.scene.O2MCD_props, "toggle_list", icon="TRIA_DOWN" if context.scene.O2MCD_props.toggle_list else "TRIA_RIGHT", emboss=False,text="Object List")
        row3 = layout.row()
        if context.scene.O2MCD_props.toggle_list:
            row3.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "object_list", context.scene.O2MCD_props, "obj_index", rows=3,sort_lock=True)
            col3 = row3.column()
            if len(context.scene.object_list) <= 1:col3.enabled = False
            col3.operator("render.o2mcd_list_move", icon='TRIA_UP', text="").action = 'UP'
            col3.operator("render.o2mcd_list_move", icon='TRIA_DOWN', text="").action = 'DOWN'
            col3.separator()
            col3.operator("render.o2mcd_list_move", icon='SORTALPHA', text="").action = 'SORT'


class OBJECTTOMCDISPLAY_OT_list_move(bpy.types.Operator): #移動
    bl_idname = "render.o2mcd_list_move"
    bl_label = ""
    
    action: bpy.props.EnumProperty(items=(('UP', "Up", ""),('DOWN', "Down", ""),('SORT', "Sort", "")))

    def invoke(self, context, event):
        if self.action == 'DOWN' and context.scene.O2MCD_props.obj_index < len(context.scene.object_list) - 1:
            context.scene.object_list.move(context.scene.O2MCD_props.obj_index, context.scene.O2MCD_props.obj_index+1)
            context.scene.O2MCD_props.obj_index += 1
        elif self.action == 'UP' and context.scene.O2MCD_props.obj_index >= 1:
            context.scene.object_list.move(context.scene.O2MCD_props.obj_index, context.scene.O2MCD_props.obj_index-1)
            context.scene.O2MCD_props.obj_index -= 1
        elif self.action == 'SORT':
            object_list = [i.obj.name for i in context.scene.object_list]
            object_list.sort()
            context.scene.object_list.clear()
            for i in object_list: context.scene.object_list.add().obj=context.scene.objects[i]
        chenge_panel(self, context)
        if context.scene.O2MCD_props.auto_reload:command_generate(self, context)
        return {"FINISHED"}

class OBJECTTOMCDISPLAY_OT_prop_action(bpy.types.Operator): #プロパティ操作
    bl_idname = "object.o2mcd_prop_action"
    bl_label = ""
    action: bpy.props.EnumProperty(items=(('ADD', "Add", ""),('DUP', "dup", ""),('UNLINK', "unlink", ""),('REMOVE', "remove", "")))
    
    def invoke(self,context,event):
        prop_list = context.scene.prop_list
        index = context.scene.O2MCD_props.list_index

        if self.action =='ADD':
            name = "New"
            context.scene.prop_list.add().name = name
            context.scene.O2MCD_props.list_index = len(context.scene.prop_list)-1
            context.object.O2MCD_props.prop_id = context.scene.O2MCD_props.list_index
        elif self.action == 'DUP':
            name = sub("(.*?)(\.[0-9]+)?","\\1",prop_list[context.object.O2MCD_props.prop_id].name)
            add = context.scene.prop_list.add()
            add.name = name
            add.Types= prop_list[context.object.O2MCD_props.prop_id].Types
            add.tags= prop_list[context.object.O2MCD_props.prop_id].tags
            add.CustomModelData= prop_list[context.object.O2MCD_props.prop_id].CustomModelData
            add.ItemTag= prop_list[context.object.O2MCD_props.prop_id].ItemTag
            add.Properties= prop_list[context.object.O2MCD_props.prop_id].Properties
            add.ExtraNBT= prop_list[context.object.O2MCD_props.prop_id].ExtraNBT
            add.type= prop_list[context.object.O2MCD_props.prop_id].type
            context.scene.O2MCD_props.list_index = len(context.scene.prop_list)-1
            context.object.O2MCD_props.prop_id = context.scene.O2MCD_props.list_index
        elif self.action == 'UNLINK':
            context.object.O2MCD_props.prop_id = -1
        elif self.action == 'REMOVE':
            prop_list.remove(index)
            context.scene.O2MCD_props.list_index = min(max(0, index - 1), len(prop_list) - 1)
            context.object.O2MCD_props.prop_id = context.scene.O2MCD_props.list_index

        chenge_panel(self, context)
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_Reload(bpy.types.Operator):  # 更新ボタン
    bl_idname = "render.o2mcd_reload"
    bl_label = "Update"

    def execute(self, context):
        command_generate(self, context)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_Export(bpy.types.Operator):  # 出力ボタン
    bl_idname = "render.o2mcd_export"
    bl_label = "Export"

    def execute(self, context):
        # テキストブロックの名前
        text_name = "Output"
        # シーンのフレーム数を取得
        frame_end = context.scene.frame_end
        # カレントフレームを保存
        current_frame = context.scene.frame_current

        if context.scene.O2MCD_props.output == "ANIMATION":
            # 出力先ディレクトリ
            anim_path = bpy.path.abspath(context.scene.O2MCD_props.anim_path)
            # フレームを1つずつ進めながら出力する
            for frame in range(1, frame_end+1):

                # カレントフレームを設定
                context.scene.frame_set(frame)
                ofset = sub(".*?([0-9]*)$", "\\1",str(os.path.splitext(anim_path)[0]))
                ext = str(os.path.splitext(anim_path)[1])
                if ofset == "":
                    ofset = 1
                if ext == "":
                    ext = ".mcfunction"
                # 出力するファイル名を作成
                output_file = sub("(.*?)([0-9]*)$", "\\1", str(os.path.splitext(anim_path)[0]))+str(int(ofset)-1+frame)+ext

                # テキストブロックを取得
                command_generate(self, context)
                text = bpy.data.texts.get(text_name)

                # 出力
                if text:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(text.as_string())
            # カレントフレームを元に戻す
            context.scene.frame_set(current_frame)
        else:
            # 出力先ディレクトリ
            curr_path = bpy.path.abspath(context.scene.O2MCD_props.curr_path)
            ext = str(os.path.splitext(curr_path)[1])
            if ext == "":
                ext = ".mcfunction"
            output_file = str(os.path.splitext(curr_path)[0])+ext
            # テキストブロックを取得
            command_generate(self, context)
            text = bpy.data.texts.get(text_name)

            # 出力
            if text:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text.as_string())
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_OT_searchPopup(bpy.types.Operator):  # 検索
    bl_idname = "object.search_popup"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(
        name="Objects", description="", items=enum_item)

    def execute(self, context):
        context.object.O2MCD_props.prop_id = int(self.my_enum)
        context.scene.O2MCD_props.list_index = context.object.O2MCD_props.prop_id
        chenge_panel(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_UL_ObjectList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        row = layout.row(align=True)
        row.alignment="LEFT"
        row.label(text=str(item.obj.O2MCD_props.number))
        row.prop(item.obj, "name", text="", emboss=False)
        row2=layout.row()
        row2.alignment="RIGHT"
        row2.prop(item.obj,"hide_render",text="")

class O2MCD_Obj_Props(bpy.types.PropertyGroup):  # オブジェクトのプロパティ
    number: bpy.props.IntProperty(name="Object Number", default=-1, min=-1)
    prop_id: bpy.props.IntProperty(name="prop_id", default=-1, min=-1)


class O2MCD_Meny_Props(bpy.types.PropertyGroup):  # パネルのプロパティ
    rou: bpy.props.IntProperty(name="Round", default=3, max=16, min=1)
    anim_path: bpy.props.StringProperty(name="Path", subtype='FILE_PATH', default="")
    curr_path: bpy.props.StringProperty(name="Path", subtype='FILE_PATH', default="")
    auto_reload: bpy.props.BoolProperty(name="Auto Update", default=False, update=update)
    output: bpy.props.EnumProperty(name="Output", items=[('CURRENT', "Current Frame", ""), ('ANIMATION', "Animation", "")], default='CURRENT')
    enable: bpy.props.BoolProperty(name="", default=False, update=update)
    Enum: bpy.props.EnumProperty(name="Enum", items=enum_item, options={"ANIMATABLE"})
    list_index : bpy.props.IntProperty(name="Index", default=-1)
    obj_index:bpy.props.IntProperty(name="obj_index", default=0)
    toggle_list : bpy.props.BoolProperty(name="")

class O2MCD_ListItem(bpy.types.PropertyGroup):  # リストのプロパティ
    name: bpy.props.StringProperty(name="Name", default="",update=change_name)
    Types: bpy.props.EnumProperty(name="Object Type", items=[('ITEM', "Item", ""), ('BLOCK', "Block", ""), ('EXTRA', "Extra", "")], options={"ANIMATABLE"},update=setid)
    tags: bpy.props.StringProperty(default="")
    CustomModelData: bpy.props.IntProperty(default=0, min=0)
    ItemTag: bpy.props.StringProperty(default="")
    Properties:bpy.props.StringProperty(default="")
    ExtraNBT: bpy.props.StringProperty(default="")
    type: bpy.props.StringProperty(default="")
    id: bpy.props.StringProperty(default="")
    item_id: bpy.props.StringProperty(default="",update=setid)
    block_id: bpy.props.StringProperty(default="",update=setid)

class  O2MCD_ItemList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_BlockList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="")
class  O2MCD_ObjectList(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(name="Object",type=bpy.types.Object)
