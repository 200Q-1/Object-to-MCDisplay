# Copyright (c) 2023 200Q

import bpy
import mathutils
from re import *
from math import *
from . import object
def cmd_set(self,context):
    active=bpy.context.object
    if bpy.context.scene.O2MCD_object_list: 
        pre=bpy.context.scene.O2MCD_object_list[bpy.context.scene.O2MCD_props.obj_index].obj
    else:
        pre=None
    if pre and pre.O2MCD_command_list:
        pre.O2MCD_command_list[pre.O2MCD_props.pre_cmd].command=bpy.data.texts["Input"].as_string()
    if active:
        active.O2MCD_props.pre_cmd=active.O2MCD_props.command_index
        if active.O2MCD_command_list:
            bpy.data.texts["Input"].from_string(active.O2MCD_command_list[active.O2MCD_props.command_index].command)
        else: bpy.data.texts["Input"].clear()


def get_location(context,obj):  # 位置取得 
    loc = mathutils.Matrix.Rotation(radians(-90),4,'X') @ obj.matrix_world
    rou = context.scene.O2MCD_props.rou
    if obj.O2MCD_props.disp_type=="block_display":
        loc = loc @ mathutils.Matrix.Translation(mathutils.Vector((0.5, -0.5, -0.5)))
    loc = loc.translation
    loc = (round(loc[0], rou), round(loc[1], rou), round(loc[2], rou))
    return loc

def get_position(context,obj):  # pos取得
    pos = mathutils.Matrix.Rotation(radians(-90),4,'X') @ obj.matrix_world
    rou = context.scene.O2MCD_props.rou
    pos = pos.translation
    pos = (round(pos[0], rou), round(pos[1], rou), round(pos[2], rou))
    return pos

def get_scale(context,obj):  # スケール取得
    scale = obj.matrix_world.to_scale()
    rou = context.scene.O2MCD_props.rou
    if obj.parent:
        if obj.parent_type == "BONE":
            pscale = obj.parent.pose.bones[obj.parent_bone].matrix @ obj.matrix_world
            pscale = pscale.to_scale()
        else:
            pscale = obj.parent.matrix_world.to_scale()
        if not round(pscale[0], rou) == round(pscale[1], rou) == round(pscale[2], rou):
            obj.scale = (1, 1, 1)
            scale = pscale
    scale = (round(scale[0], rou), round(scale[2], rou), round(scale[1], rou))
    return scale


def get_left_rotation(context,obj):  # 左回転取得
    rou = context.scene.O2MCD_props.rou
    if obj.parent:
        if obj.parent_type == "BONE":
            l_rot = obj.parent.pose.bones[obj.parent_bone].matrix
            l_rot = obj.parent.matrix_world @ l_rot
            l_rot = l_rot.to_euler()
            l_rot = mathutils.Euler(
                (l_rot[0]-1.5708, l_rot[1], l_rot[2]), 'XYZ')
        else:
            l_rot = obj.parent.matrix_world.to_euler()
    else:
        l_rot = obj.matrix_world.to_euler()
    l_rot_y = mathutils.Matrix.Rotation(l_rot[2],4,'Y')
    if obj.O2MCD_props.disp_type == 'BLOCK' or context.scene.O2MCD_props.mc_version == "1.19":
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

def get_rotation(context,obj):  # 回転取得
    rou = context.scene.O2MCD_props.rou
    if obj.parent:
        if obj.parent_type == "BONE":
            rot = obj.parent.pose.bones[obj.parent_bone].matrix
            rot = obj.parent.matrix_world @ rot
            rot = rot.to_euler()
            rot = mathutils.Euler((rot[0]-1.5708, rot[1], rot[2]), 'XYZ')
        else:
            rot = obj.parent.matrix_world.to_euler()
    else:
        rot = obj.matrix_world.to_euler()  
    rot_y = mathutils.Matrix.Rotation(rot[2],4,'Y')
    if obj.O2MCD_props.disp_type == 'BLOCK' or context.scene.O2MCD_props.mc_version == "1.19":
        rot_x = mathutils.Matrix.Rotation(-rot[0],4,'X')
        rot_z = mathutils.Matrix.Rotation(rot[1],4,'Z')
    else:
        rot_x = mathutils.Matrix.Rotation(rot[0],4,'X')
        rot_z = mathutils.Matrix.Rotation(-rot[1],4,'Z')
    rot = (rot_y @ rot_z @ rot_x).to_euler()
    rot = [round(degrees(rot[1]), rou), round(degrees(rot[2]), rou),round(degrees(rot[0]), rou)]
    return rot

def get_right_rotation(context,obj):  # 右回転取得
    rou = context.scene.O2MCD_props.rou
    if obj.parent:
        r_rot = obj.rotation_euler
        r_rot_y = mathutils.Matrix.Rotation(r_rot[2],4,'Y')
        if obj.O2MCD_props.disp_type == 'BLOCK' or context.scene.O2MCD_props.mc_version == "1.19":
            r_rot_x = mathutils.Matrix.Rotation(-r_rot[0],4,'X')
            r_rot_z = mathutils.Matrix.Rotation(r_rot[1],4,'Z')
        else:
            r_rot_x = mathutils.Matrix.Rotation(r_rot[0],4,'X')
            r_rot_z = mathutils.Matrix.Rotation(-r_rot[1],4,'Z')
        r_rot = (r_rot_y @ r_rot_z @ r_rot_x).to_quaternion()
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


def comvert_function(context, funk_list, com, num):    # 関数変換
    object_list= context.scene.O2MCD_object_list                    #オブジェクトリスト
    current_frame = context.scene.frame_current                     # 現在のフレーム
    com = com.replace("/transf", r"transformation:{right_rotation:[/r_rot],scale:[/scale],left_rotation:[/l_rot],translation:[/loc]}")  # /transfだけ先に変換
    func = findall(f'(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)', com)              # 入力から関数のリストを作成
    for f in func:                                                  # 関数を1つずつ処理
        var = sub(f'/({funk_list})(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?', "\\1", f)          # 関数名
        val = sub('/.+?\[(.+)\]', "V\\1", f)                        # 引数
        if not val == "" and not val == f and match(f".*/{funk_list}.*", val):  # 引数の中の関数を変換
            val = comvert_function(context, funk_list, val, num)
        elm = sub('V?([0-9]*?)(,.*)?', "\\1", val)                  # 要素番号
        frm = sub('V?.*?,((?:\+|\-)?[0-9]*?)(,.*)?', "\\1", val)    # フレーム数
        obj = sub('V?.*?,.*?,((?:\+|\-)?.*?)', "\\1", val)          # オブジェクト
        if not var == "math" and not var == "frame":                                       # math以外の関数を処理
            if not frm == "" and not frm == val:     # フレームを設定
                if match("(?:\+|\-)[0-9]+", frm):
                    frm = eval(str(current_frame)+frm)
                context.scene.frame_set(int(frm))
                context.scene.frame_current=int(frm)
            if obj == "" or obj == val:              # オブジェクトを設定
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
            if var == "loc":                        # transformationを取得
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
            elif var == "name":     # 名前を取得
                name = obj.name
            elif var == "id":       # idを取得
                id = obj.O2MCD_props.disp_id
            # elif var == "extra":    # extraNBTを取得
            #     extra = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].ExtraNBT
            elif var == "prop":     # ブロックのプロパティを取得
                prop=""
                if obj.O2MCD_props.disp_type == "item_display" or obj.O2MCD_props.disp_type == "block_display":
                    modi= list(filter(lambda m : m.type == 'NODES' and match("O2MCD(?:\.[0-9]+)?",m.name) and m.node_group.name == obj.data.name , obj.modifiers))[0]
                    for i,n in enumerate(list(filter(lambda n : n.type=='MENU_SWITCH',modi.node_group.nodes))):
                        if val[1:]== n.name:
                            prop=n.name+":"+"\""+str(obj.modifiers[modi.name][f"Socket_{i+2}"])+"\""
                # elif obj.O2MCD_props.disp_type == "blopck_display":
                #     prop = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Properties
                # elif obj.O2MCD_props.disp_type == "EXTRA":
                #     prop = ""
            elif var == "model":    # カスタムモデルデータを取得
                if context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    model = str(context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].CustomModelData)
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    model = ""
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    model = ""
            elif var == "item":     # アイテムタグを取得
                if context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "ITEM":
                    item = context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].ItemTag
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "BLOCK":
                    item = ""
                elif context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].Types == "EXTRA":
                    item = ""
            elif var == "tag" or var == "tags":     # タグをリスト化
                tags = split(",", context.scene.O2MCD_prop_list[obj.O2MCD_props.prop_id].tags)
            if elm == "" or elm == val:             # 置き換え
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
            if var == "model":
                if not model == "": com = com.replace(f, model, 1)
                else: com = com.replace(f, "", 1)
            elif var == "item":
                if not item == "": com = com.replace(f, item, 1)
                else: com = com.replace(f, "", 1)
            elif var == "name": com = com.replace(f, name, 1)
            elif var == "id": com = com.replace(f, id, 1)
            elif var == "type": com = com.replace(f, obj.O2MCD_props.disp_type, 1)
            elif var == "num": com = com.replace(f, str(num), 1)
            # elif var == "extra": com = com.replace(f, extra, 1)
        elif var == "math":com = com.replace(f,str(eval(sub('V?(.+)', "\\1", val))), 1)   # mathを処理
        elif var == "frame": com = com.replace(f, str(current_frame), 1)
    if not current_frame == context.scene.frame_current:
        context.scene.frame_set(current_frame)
    return com


def command_generate(self, context):    # コマンド生成
    if command_generate in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(command_generate)
    if "Output" not in bpy.data.texts:  # Outputが無ければ作成
        bpy.data.texts.new("Output")
    object.mesh_update(self, context)
    funk_list = "(?:transf|loc|scale|l_rot|r_rot|name|id|type|model|item|prop|tags?|num|math|extra|pos|rot|frame)"    # 関数名
    # input = list(bpy.data.texts["Input"].as_string().splitlines())  # コマンドをリスト化
    output = []                                                     # 出力をリセット

    # for i,c in enumerate(input) :
    #     if match(f"(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?)(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", c):
    #         f=sub(f"(/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?(?:\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?)\s?:.*", "\\1", c)
    #         f= comvert_function(context, funk_list, f, None)
    #         f=str(int(float(f)))
    #         input[i]=f+":"+sub(f"/{funk_list}(?:\[[^\[\]]*?(?:/{funk_list}(?:\[[^\[\]]*?\])?[^\[\]]*?)*\])?(?:\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:(.*)", "\\1", c)

    # #  startを出力に追加
    # com = [sub("^start(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("start(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", s)]
    # com = frame_range(context, com)
    # if com:
    #     if [i for i in  com if match(f".*/({funk_list}).*", i)]:
    #         com = "\n".join(com)
    #         com = comvert_function(context, funk_list, com, None)
    #     else:com = "\n".join(com)
    #     output.append(com)  
    #   メインコマンドを出力に追加
    for l in context.scene.O2MCD_object_list:
        o = l.obj
        if not o.hide_viewport and o.O2MCD_props.enable:
            input=[]
            input=[c for cl in o.O2MCD_command_list for c in cl.command.split("\n")]
            # for c in o.O2MCD_command_list:
            #     if c.enable: input+=[*c.command.split("\n")]
            input = [s for s in input if not match('^#(?! +|#+)', s)]       # エスケープ
            if input:
                if [i for i in  input if match(f".*/({funk_list}).*", i)]:
                    input = "\n".join(input)
                    input = comvert_function(context, funk_list, input, o.O2MCD_props.number)
                else:input = "\n".join(input)
                output.append(input)
    # # endを出力に追加
    # com = [sub("^end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", "\\1", s)for s in input if match("end(\[(?:[0-9]+|[0-9]+\-[0-9]+)\])?\s?:\s?", s)]
    # com = frame_range(context, com)
    # if com:
    #     if [i for i in  com if match(f".*/({funk_list}).*", i)]:
    #         com = "\n".join(com)
    #         com = comvert_function(context, funk_list, com, None)
    #     else:com = "\n".join(com)
    #     output.append(com)

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

class OBJECTTOMCDISPLAY_OT_CommandListAction(bpy.types.Operator): #移動
    bl_idname = "o2mcd.command_list_action"
    bl_label = ""
    bl_description = ""
    action: bpy.props.EnumProperty(items=(('UP', "up", ""),('DOWN', "down", ""),('ADD',"add",""),('REMOVE',"remove","")))

    def invoke(self, context, event):
        cmd_list=context.view_layer.objects.active.O2MCD_command_list
        cmd_index=context.view_layer.objects.active.O2MCD_props.command_index
        if self.action == 'DOWN':
            cmd_list.move(cmd_index, cmd_index+1)
            context.object.O2MCD_props.command_index += 1
            context.view_layer.objects.active.O2MCD_props.pre_cmd=context.view_layer.objects.active.O2MCD_props.pre_cmd+1
        elif self.action == 'UP':
            cmd_list.move(cmd_index, cmd_index-1)
            context.object.O2MCD_props.command_index -= 1
            context.view_layer.objects.active.O2MCD_props.pre_cmd=context.view_layer.objects.active.O2MCD_props.pre_cmd-1
        elif self.action == 'ADD':
            if "Input" not in bpy.data.texts:
                bpy.data.texts.new("Input")
            newcmd=cmd_list.add()
            newcmd.name = "cmd"+str(len(context.view_layer.objects.active.O2MCD_command_list))
        elif self.action == 'REMOVE':
            cmd_list.remove(cmd_index)
        return {"FINISHED"}
    
    
classes = (
    OBJECTTOMCDISPLAY_OT_CommandListAction,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    if command_generate in bpy.app.handlers.frame_change_post :bpy.app.handlers.frame_change_post.remove(command_generate)
    if command_generate in bpy.app.handlers.depsgraph_update_post :bpy.app.handlers.depsgraph_update_post.remove(command_generate)