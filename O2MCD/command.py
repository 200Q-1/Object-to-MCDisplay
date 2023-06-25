# Copyright (c) 2023 200Q

import bpy
import mathutils
from re import *
from math import *

def get_location(context,object):  # 位置取得 
    loc = mathutils.Matrix.Rotation(radians(-90),4,'X') @ object.matrix_world
    rou = context.scene.O2MCD_props.rou
    if context.scene.O2MCD_prop_list[object.O2MCD_props.prop_id].Types == "BLOCK":
        loc = loc @ mathutils.Matrix.Translation(mathutils.Vector((0.5, -0.5, -0.5)))
    loc = loc.translation
    loc = (round(loc[0], rou), round(loc[1], rou), round(loc[2], rou))
    return loc

def get_position(context,object):  # pos取得
    pos = mathutils.Matrix.Rotation(radians(-90),4,'X') @ object.matrix_world
    rou = context.scene.O2MCD_props.rou
    pos = pos.translation
    pos = (round(pos[0], rou), round(pos[1], rou), round(pos[2], rou))
    return pos

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
    scale = (round(scale[0], rou), round(scale[2], rou), round(scale[1], rou))
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
    l_rot_y = mathutils.Matrix.Rotation(l_rot[2],4,'Y')
    if context.scene.O2MCD_prop_list[object.O2MCD_props.prop_id].Types == 'BLOCK':
        inv=mathutils.Matrix.Rotation(radians(180),4,"Y")
        l_rot_x = mathutils.Matrix.Rotation(-l_rot[0],4,'X')
        l_rot_z = mathutils.Matrix.Rotation(l_rot[1],4,'Z')
    else:
        inv=mathutils.Matrix.Identity(4)
        l_rot_x = mathutils.Matrix.Rotation(l_rot[0],4,'X')
        l_rot_z = mathutils.Matrix.Rotation(-l_rot[1],4,'Z')
    l_rot = (inv @ l_rot_y @ l_rot_z @ l_rot_x).to_quaternion()
    
    l_rot = [round(l_rot[1], rou), round(l_rot[2], rou),round(l_rot[3], rou), round(l_rot[0], rou)]
    return l_rot

def get_rotation(context,object):  # 回転取得
    rou = context.scene.O2MCD_props.rou
    if object.parent:
        if object.parent_type == "BONE":
            rot = object.parent.pose.bones[object.parent_bone].matrix
            rot = object.parent.matrix_world @ rot
            rot = rot.to_euler()
            rot = mathutils.Euler((rot[0]-1.5708, rot[1], rot[2]), 'XYZ')
        else:
            rot = object.parent.matrix_world.to_euler()
    else:
        rot = object.matrix_world.to_euler()  
    rot_x = mathutils.Matrix.Rotation(rot[0],4,'X')
    rot_y = mathutils.Matrix.Rotation( -rot[2],4,'X')
    rot_z = mathutils.Matrix.Rotation( -rot[1],4,'X')
    rot = (rot_y @ rot_z @ rot_x).to_euler()
    rot = [round(degrees(rot[1]), rou), round(degrees(rot[2]), rou),round(degrees(rot[0]), rou)]
    return rot

def get_right_rotation(context,object):  # 右回転取得
    rou = context.scene.O2MCD_props.rou
    if object.parent:
        r_rot = object.rotation_euler
        r_rot = mathutils.Euler((-r_rot[0], r_rot[2], r_rot[1]), 'XYZ').to_quaternion()
    else:
        r_rot = mathutils.Matrix.Identity(4).to_quaternion()
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
    func = findall(f'(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)', com)
    # 関数を1つずつ処理
    for f in func:
        # 関数名
        var = sub(f'/({funk_list})(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?', "\\1", f)
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
            if not frm == "" and not frm == val:
                if match("(?:\+|\-)[0-9]+", frm):
                    frm = eval(str(current_frame)+frm)
                context.scene.frame_set(int(frm))
                context.scene.frame_current=int(frm)
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
            elif var == "pos":
                position = get_position(context,obj)
            elif var == "scale":
                scale = get_scale(context,obj)
            elif var == "r_rot":
                right_rotation = get_right_rotation(context,obj)
            elif var == "l_rot":
                left_rotation = get_left_rotation(context,obj)
            elif var == "rot":
                rotation = get_rotation(context,obj)
            # 名前を取得
            elif var == "name":
                name = obj.name
            # idを取得
            elif var == "id":
                id = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].id
            # extraNBTを取得
            elif var == "extra":
                extra = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].ExtraNBT
            # タイプを取得
            elif var == "type":
                if context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    type = "item_display"
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    type = "block_display"
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    type = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].type
            # ブロックのプロパティを取得
            elif var == "prop":
                if context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    prop = ""
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    prop = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Properties
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    prop = ""
            # カスタムモデルデータを取得
            elif var == "model":
                if context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    model = str(context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].CustomModelData)
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    model = ""
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    model = ""
            # アイテムタグを取得
            elif var == "item":
                if context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    item = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].ItemTag
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    item = ""
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    item = ""
            # タグをリスト化
            elif var == "tag" or var == "tags":
                tags = split(",", context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].tags)
            # 置き換え
            if elm == "" or elm == val:
                if var == "loc": com = com.replace(f, str(location[0]) +"f,"+str(location[1])+"f,"+str(location[2])+"f", 1)
                elif var == "pos": com = com.replace(f, "^"+str(position[0]) +" ^"+str(position[1])+" ^"+str(position[2]), 1)
                elif var == "scale": com = com.replace(f, str(scale[0]) +"f,"+str(scale[1])+"f,"+str(scale[2])+"f", 1)
                elif var == "r_rot": com = com.replace(f, str(right_rotation[0])+"f,"+str(right_rotation[1])+"f,"+str(right_rotation[2])+"f,"+str(right_rotation[3])+"f", 1)
                elif var == "l_rot": com = com.replace(f, str(left_rotation[0])+"f,"+str(left_rotation[1])+"f,"+str(left_rotation[2])+"f,"+str(left_rotation[3])+"f", 1)
                elif var == "rot": com = com.replace(f, "~"+str(rotation[0])+" ~"+str(rotation[2]), 1)
                elif var == "tag" or var == "tags":
                    if not context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].tags == "":
                        if var == "tags": com = com.replace(f, ",".join(["\""+i+"\"" for i in tags]), 1)
                        if var == "tag": com = com.replace(f, ",".join(["tag="+i for i in tags]), 1)
                    else: com = com.replace(f, "", 1)
            else:
                if var == "loc": com = sub("/loc\[.*?(,.*?)?\]",str(location[int(elm)]),com, 1)
                elif var == "pos": com = sub("/pos\[.*?(,.*?)?\]",str(position[int(elm)]),com, 1)
                elif var == "scale": com = sub("/scale\[.*?(,.*?)?\]",str(scale[int(elm)]),com, 1)
                elif var == "r_rot": com = sub("/r_rot\[.*?(,.*?)?\]",str(right_rotation[int(elm)]),com, 1)
                elif var == "l_rot": com = sub("/l_rot\[.*?(,.*?)?\]",str(left_rotation[int(elm)]),com, 1)
                elif var == "rot": com = sub("/rot\[.*?(,.*?)?\]",str(rotation[int(elm)]),com, 1)
                elif var == "tag" or var == "tags":
                    if not context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].tags == "":
                        if var == "tags": com = sub("/tags\[.*?(,.*?)?\]",tags[int(elm)],com, 1)
                        if var == "tag": com = sub("/tag\[.*?(,.*?)?\]",tags[int(elm)],com, 1)
                    else: com = com.replace(f, "", 1)
            if var == "prop":
                if not prop == "": com = com.replace(f, prop, 1)
                else: com = com.replace(f, "", 1)
            elif var == "model":
                if not model == "": com = com.replace(f, model, 1)
                else: com = com.replace(f, "", 1)
            elif var == "item":
                if not item == "": com = com.replace(f, item, 1)
                else: com = com.replace(f, "", 1)
            elif var == "name": com = com.replace(f, name, 1)
            elif var == "id": com = com.replace(f, id, 1)
            elif var == "type": com = com.replace(f, type, 1)
            elif var == "num": com = com.replace(f, str(num), 1)
            elif var == "extra": com = com.replace(f, extra, 1)
        # mathを処理
        if var == "math":com = com.replace(f,str(eval(sub('V?(.+)', "\\1", val))), 1)
    if not current_frame == context.scene.frame_current:
        context.scene.frame_set(current_frame)
    return com


def command_generate(self, context):  # コマンド生成
    if command_generate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    # Outputが無ければ作成
    if "Output" not in bpy.data.texts:
        bpy.data.texts.new("Output")
    # 関数名
    funk_list = "(?:transf|loc|scale|l_rot|r_rot|name|id|type|model|item|prop|tags?|num|math|extra|pos|rot)"
    # コマンドをリスト化
    input = list(bpy.data.texts["Input"].as_string().splitlines())
    # エスケープ
    input = [s for s in input if not match('^#(?! +|#+)', s)]
    # 出力をリセット
    output = []

    # # startを出力に追加
    com = [sub("^start(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("start(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", s)]
    com = frame_range(context, com)
    if com:
        if [i for i in  com if match(f".*/({funk_list}).*", i)]:
            com = "\n".join(com)
            com = comvert_function(context, context.scene.O2MCD_object_list, funk_list, com, None)
        else:com = "\n".join(com)
        output.append(com)
    # # メインコマンドを出力に追加
    for l in context.scene.O2MCD_object_list:
        o = l.obj
        if not o.hide_viewport and o.O2MCD_props.enable:
            if context.scene.O2MCD_prop_list[o.O2MCD_props.prop_id].Types == "ITEM":
                com = [sub("^item(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!block|extra|start|end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?)", s)]
            elif context.scene.O2MCD_prop_list[o.O2MCD_props.prop_id].Types == "BLOCK":
                com = [sub("^block(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!item|extra|start|end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?)", s)]
            elif context.scene.O2MCD_prop_list[o.O2MCD_props.prop_id].Types == "EXTRA":
                com = [sub("^extra(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("(?!block|item|start|end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?)", s)]
            com = frame_range(context, com)
            if com:
                if [i for i in  com if match(f".*/({funk_list}).*", i)]:
                    com = "\n".join(com)
                    com = comvert_function(context, context.scene.O2MCD_object_list, funk_list, com, o.O2MCD_props.number)
                else:com = "\n".join(com)
                output.append(com)
    # endを出力に追加
    com = [sub("^end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", s)]
    com = frame_range(context, com)
    if com:
        if [i for i in  com if match(f".*/({funk_list}).*", i)]:
            com = "\n".join(com)
            com = comvert_function(context, context.scene.O2MCD_object_list, funk_list, com, None)
        else:com = "\n".join(com)
        output.append(com)

    # Outputに書き込み
    output = "\n".join(output)
    output = sub("[,\.][,\.]|([\{\[\(])[,\.]|[,\.]([\]\}\)])", "\\1\\2", output)
    bpy.data.texts["Output"].from_string(output)
    # テキストエディタの表示を更新
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.tag_redraw()
    if bpy.context.scene.O2MCD_props.auto_reload:  # 自動更新を有効
        bpy.app.handlers.frame_change_post.append(command_generate)
        bpy.app.handlers.depsgraph_update_post.append(command_generate)

def register():
    pass

def unregister():
    if command_generate in bpy.app.handlers.frame_change_post :bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(command_generate)