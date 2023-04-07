# Copyright (c) 2023 200Q

import bpy
import mathutils
import os
from re import *
from math import *
from bpy.app.handlers import persistent

bl_info = {
    "name": "Object to MCDisplay",
    "author": "200Q",
    "version": (0, 0, 1),
    "blender": (3, 4, 1),
    "location": "",
    "support": "COMMUNITY",
    "description": "オブジェクトのトランスフォームをMinecraftのDisplayエンティティのtransformationを設定するコマンドに変換します。",
    "warning": "",
    "doc_url": "https://github.com/200Q-1/Object-to-MCDisplay",
    "tracker_url": "",
    "category": "Object"
}

O2MCD_translation_dict = {
    "ja_JP": {
        ("*", "Display Properties"): "Displayプロパティ",
        ("Operator", "Update"): "更新",
        ("*", "Auto Update"): "自動更新",
        ("*", "Show in header"): "ヘッダーに表示",
        ("*", "Object Number"): "番号"
    }
}

# 関数

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

def chenge_panel(self, context):
    if not context.view_layer.objects.active == None:
        if context.view_layer.objects.active.O2MCD_props.prop_id > len(context.scene.prop_list)-1:
            context.view_layer.objects.active.O2MCD_props.prop_id = -1
        context.scene.O2MCD_props.list_index = context.view_layer.objects.active.O2MCD_props.prop_id
    
    for i in range(len(bpy.context.scene.object_list)):
        if not bpy.context.scene.object_list[i].obj.name in context.view_layer.objects or bpy.context.scene.object_list[i].obj.O2MCD_props.prop_id ==-1 :
            bpy.context.scene.object_list[i].obj.O2MCD_props.number = -1
            bpy.context.scene.object_list.remove(i)
    for i in context.view_layer.objects:
        if i.O2MCD_props.prop_id >= 0 and not i.hide_viewport and not i.hide_render and not i in [i.obj for i in bpy.context.scene.object_list]:
            bpy.context.scene.object_list.add().obj = i
    for i in range(len(bpy.context.scene.object_list)):
        bpy.context.scene.object_list[i].obj.O2MCD_props.number = i
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D' or 'PROPERTIES':
            area.tag_redraw()
    



def get_location(object):  # 位置取得
    loc = mathutils.Euler((radians(-90), 0, 0),'XYZ').to_matrix().to_4x4() @ object.matrix_world
    rou = bpy.context.scene.O2MCD_props.rou
    if bpy.context.scene.prop_list[object.O2MCD_props.prop_id].Types == "BLOCK":
        loc = loc @ mathutils.Matrix.Translation(
            mathutils.Vector((0.5, -0.5, -0.5)))
    loc = loc.translation
    loc = (round(loc[0], rou), round(loc[1], rou), round(loc[2], rou))
    return loc

def get_scale(object):  # スケール取得
    scale = object.matrix_world.to_scale()
    rou = bpy.context.scene.O2MCD_props.rou
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


def get_left_rotation(object):  # 左回転取得
    rou = bpy.context.scene.O2MCD_props.rou
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


def get_right_rotation(object):  # 右回転取得
    rou = bpy.context.scene.O2MCD_props.rou
    if object.parent:
        r_rot = object.rotation_euler
        r_rot = mathutils.Euler(
            (-r_rot[0], r_rot[2], r_rot[1]), 'XYZ').to_quaternion()
    else:
        r_rot = mathutils.Euler((0, 0, 0), 'XYZ').to_quaternion()
    r_rot = [round(r_rot[1], rou), round(r_rot[2], rou),round(r_rot[3], rou), round(r_rot[0], rou)]
    return r_rot


def frame_range(context, com):  # フレーム範囲指定
    for s in range(len(com)):
        # 範囲設定
        if match("^\[[0-9]+\]", com[s]):
            min = int(sub("^\[([0-9]+)\].*", "\\1", com[s]))
            max = min
        elif match("^\[[0-9]+\-[0-9]+\]", com[s]):
            min = int(sub("^\[([0-9]+)\-[0-9]+\].*", "\\1", com[s]))
            max = int(sub("^\[[0-9]+\-([0-9]+)\].*", "\\1", com[s]))
        else:
            min = context.scene.frame_start
            max = context.scene.frame_end
        # 範囲比較
        if min <= context.scene.frame_current <= max:
            com[s] = sub(
                "^\[(?:[0-9]+|[0-9]+\-[0-9]+)\](\s?:\s?)?", "", com[s])
        else:
            com[s] = None
    com = [s for s in com if not s == None]
    return com


def comvert_function(context, object_list, funk_list, com, num):  # 関数変換
    # 現在のフレームを保存
    current_frame = context.scene.frame_current
    # /transfだけ先に変換
    com = com.replace(
        "/transf", "right_rotation:[/r_rot],scale:[/scale],left_rotation:[/l_rot],translation:[/loc]")
    # 入力から関数のリストを作成
    func = findall(
        f'(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)', com)
    # 関数を1つずつ処理
    for f in range(len(func)):
        # 関数名
        var = sub(
            f'/({funk_list})(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?', "\\1", func[f])
        # 引数
        val = sub('/.+?\[(.+)\]', "V\\1", func[f])
        # 引数の中の関数を変換
        if not val == "" and not val == func[f] and match(f".*/{funk_list}.*", val):
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
                obj = eval(str(object_list.index(object_list[num].obj))+obj)
                if len(object_list)-1 < obj:
                    obj = len(object_list)-1
                elif 0 > obj:
                    obj = 0
                obj = object_list[obj].obj
                num = object_list.index(obj)
            elif match("^[0-9]+", obj):
                obj = object_list[int(obj)]
                num = object_list.index(obj)
            else:
                obj = context.scene.objects[obj]
            # transformationを取得
            if var == "loc":
                location = get_location(obj)
            if var == "scale":
                scale = get_scale(obj)
            if var == "r_rot":
                right_rotation = get_right_rotation(obj)
            if var == "l_rot":
                left_rotation = get_left_rotation(obj)
            # 名前を取得
            if var == "name" or var == "id":
                name = obj.name
            # idを取得
            if var == "id":
                id = sub("(\.[0-9]*)*", "", name)
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
    funk_list = "(?:loc|scale|l_rot|r_rot|name|id|type|model|item|prop|tags?|num|math|extra)"
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
    for num in range(len(context.scene.object_list)):
        o = context.scene.object_list[num].obj
        if context.scene.prop_list[o.O2MCD_props.prop_id].Types == "ITEM":
            com = [sub("^item(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!block|extra|start|end\s?:\s?)", s)]
        elif context.scene.prop_list[o.O2MCD_props.prop_id].Types == "BLOCK":
            com = [sub("^block(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!item|extra|start|end\s?:\s?)", s)]
        elif context.scene.prop_list[o.O2MCD_props.prop_id].Types == "EXTRA":
            com = [sub("^extra(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!block|item|start|end\s?:\s?)", s)]
        com = frame_range(context, com)
        if com:
            com = "\n".join(com)
            if match(f".*/({funk_list}).*", com):
                com = comvert_function(
                    context, context.scene.object_list, funk_list, com, num)
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
    output = sub(
        "[,\.][,\.]|([\{\[\(])[,\.]|[,\.]([\]\}\)])", "\\1\\2", output)
    bpy.data.texts["Output"].from_string(output)
    # テキストエディタの表示を更新
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.tag_redraw()

def enum_item(self, context):  # プロパティリスト
    enum_items = []
    for i in range(len(context.scene.prop_list)):
        enum_items.append((str(i), str(i)+"."+context.scene.prop_list[i].name, ""))
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
        # box.template_list("OBJECTTOMCDISPLAY_UL_List", "The_List", context.scene,"prop_list", context.scene, "O2MCD_props.list_index", rows=1, type='GRID', columns=2)
        br = layout.row(align=True)
        br.alignment = "LEFT"
        if context.scene.prop_list:
            item = context.scene.prop_list[context.scene.O2MCD_props.list_index]
        br.operator("object.search_popup", text="", icon='DOWNARROW_HLT')
        if context.scene.O2MCD_props.list_index >= 0 and context.scene.prop_list:
            br.prop(item, "name", text="")
            br.operator("render.add_item", icon='ADD')
            br.operator("render.un_ink", icon='PANEL_CLOSE')
            br.operator("render.remove_item", icon='TRASH')
        else:
            br.alignment = "EXPAND"
            br.operator("render.add_item", icon='ADD',text="New")
        if context.scene.prop_list and context.object.O2MCD_props.prop_id >= 0:
            # box.prop_search(context.scene.O2MCD_props, "active",context.scene, "prop_list")
            # layout.prop(context.object.O2MCD_props,"prop_id")
            layout.prop(item, "Types", expand=True)
            row = layout.row()
            row.enabled = False
            row.use_property_split = True
            row.use_property_decorate = False
            row.prop(context.object.O2MCD_props, "number")
            if item.Types == "EXTRA":
                layout.prop(item, "type")
            layout.prop(item, "tags")
            if item.Types == "ITEM":
                layout.prop(item,"CustomModelData")
                layout.prop(item, "ItemTag")
            if item.Types == "BLOCK":
                pass
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
        row.operator("render.reload")
        row.prop(context.scene.O2MCD_props, "auto_reload", toggle=True)
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(context.scene.O2MCD_props, "rou")
        row3 = col.row()
        row3.template_list("OBJECTTOMCDISPLAY_UL_ObjectList", "", context.scene, "object_list", context.scene.O2MCD_props, "obj_index", rows=2)
        col3 = row3.column()
        col3.operator("render.list_action", icon='TRIA_UP', text="").action = 'UP'
        col3.operator("render.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        layout.separator()
        col2 = layout.column(align=True)
        row2 = col2.row()
        row2.prop(context.scene.O2MCD_props, "output", expand=True)
        box = col2.box()
        if context.scene.O2MCD_props.output == "ANIMATION":
            box.prop(context.scene.O2MCD_props, "anim_path")
        else:
            box.prop(context.scene.O2MCD_props, "curr_path")
        box.operator("render.export")
        layout.enabled = context.scene.O2MCD_props.enable

class OBJECTTOMCDISPLAY_OT_actions(bpy.types.Operator): #移動
    bl_idname = "render.list_action"
    bl_label = "List Actions"
    bl_options = {'REGISTER'}
    
    action: bpy.props.EnumProperty(
        items=(('UP', "Up", ""),('DOWN', "Down", "")))

    def invoke(self, context, event):
        try:
            item = context.scene.object_list[context.scene.O2MCD_props.obj_index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and context.scene.O2MCD_props.obj_index < len(context.scene.object_list) - 1:
                context.scene.object_list.move(context.scene.O2MCD_props.obj_index, context.scene.O2MCD_props.obj_index+1)
                context.scene.O2MCD_props.obj_index += 1
            elif self.action == 'UP' and context.scene.O2MCD_props.obj_index >= 1:
                context.scene.object_list.move(context.scene.O2MCD_props.obj_index, context.scene.O2MCD_props.obj_index-1)
                context.scene.O2MCD_props.obj_index -= 1
            chenge_panel(self, context)
            if context.scene.O2MCD_props.auto_reload:command_generate(self, context)
        return {"FINISHED"}
class OBJECTTOMCDISPLAY_OT_AddItem(bpy.types.Operator):  # 追加ボタン
    bl_idname = "render.add_item"
    bl_label = ""

    def execute(self, context):
        context.scene.prop_list.add().name = "New"
        context.scene.O2MCD_props.list_index = len(context.scene.prop_list)-1
        context.object.O2MCD_props.prop_id = context.scene.O2MCD_props.list_index
        chenge_panel(self, context)
        return {'FINISHED'}
    
class OBJECTTOMCDISPLAY_OT_Unlink(bpy.types.Operator):  # リンク解除ボタン
    bl_idname = "render.un_ink"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return context.scene.prop_list

    def execute(self, context):
        context.object.O2MCD_props.prop_id = -1
        chenge_panel(self, context)
        return{'FINISHED'}
class OBJECTTOMCDISPLAY_OT_RemoveItem(bpy.types.Operator):  # 削除ボタン
    bl_idname = "render.remove_item"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return context.scene.prop_list

    def execute(self, context):
        prop_list = context.scene.prop_list
        index = context.scene.O2MCD_props.list_index

        prop_list.remove(index)
        context.scene.O2MCD_props.list_index = min(max(0, index - 1), len(prop_list) - 1)
        context.object.O2MCD_props.prop_id = context.scene.O2MCD_props.list_index
        chenge_panel(self, context)
        return{'FINISHED'}

class OBJECTTOMCDISPLAY_OT_Reload(bpy.types.Operator):  # 更新ボタン
    bl_idname = "render.reload"
    bl_label = "Update"

    def execute(self, context):
        command_generate(self, context)
        return {'FINISHED'}


class OBJECTTOMCDISPLAY_OT_Export(bpy.types.Operator):  # 出力ボタン
    bl_idname = "render.export"
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
                ofset = sub(".*?([0-9]*)$", "\\1",
                            str(os.path.splitext(anim_path)[0]))
                ext = str(os.path.splitext(anim_path)[1])
                if ofset == "":
                    ofset = 1
                if ext == "":
                    ext = ".mcfunction"
                # 出力するファイル名を作成
                output_file = sub(
                    "(.*?)([0-9]*)$", "\\1", str(os.path.splitext(anim_path)[0]))+str(int(ofset)-1+frame)+ext

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
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

class OBJECTTOMCDISPLAY_UL_ObjectList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        layout.prop(item.obj, "name", text="", emboss=False)

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


class O2MCD_ListItem(bpy.types.PropertyGroup):  # リストのプロパティ
    name: bpy.props.StringProperty(name="Name", default="")
    Types: bpy.props.EnumProperty(name="Object Type", items=[('ITEM', "Item", ""), ('BLOCK', "Block", ""), ('EXTRA', "Extra", "")], options={"ANIMATABLE"})
    tags: bpy.props.StringProperty(default="")
    CustomModelData: bpy.props.IntProperty(default=0, min=0)
    ItemTag: bpy.props.StringProperty(default="")
    ExtraNBT: bpy.props.StringProperty(default="")
    type: bpy.props.StringProperty(default="")

class  O2MCD_ObjectList(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(name="Object",type=bpy.types.Object)

classes = (
    OBJECTTOMCDISPLAY_PT_DisplayProperties,
    OBJECTTOMCDISPLAY_PT_MainPanel,
    OBJECTTOMCDISPLAY_OT_Reload,
    OBJECTTOMCDISPLAY_OT_Export,
    OBJECTTOMCDISPLAY_OT_AddItem,
    OBJECTTOMCDISPLAY_OT_Unlink,
    OBJECTTOMCDISPLAY_OT_RemoveItem,
    OBJECTTOMCDISPLAY_OT_searchPopup,
    OBJECTTOMCDISPLAY_UL_ObjectList,
    O2MCD_Meny_Props,
    O2MCD_Obj_Props,
    O2MCD_ListItem,
    O2MCD_ObjectList,
    OBJECTTOMCDISPLAY_OT_actions
)

# blender起動時に実行
@persistent
def load_handler(self, context):
    update(None, bpy.context.scene)

def register():
    bpy.app.translations.register(__name__, O2MCD_translation_dict)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Meny_Props)
    bpy.types.Object.O2MCD_props = bpy.props.PointerProperty(type=O2MCD_Obj_Props)
    bpy.types.Scene.prop_list = bpy.props.CollectionProperty(type=O2MCD_ListItem)
    bpy.types.Scene.object_list = bpy.props.CollectionProperty(type=O2MCD_ObjectList)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.app.translations.unregister(__name__)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.frame_change_post.remove(command_generate)
    bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    bpy.app.handlers.depsgraph_update_post.remove(chenge_panel)


if __name__ == "__main__":
    register()
